import websockets
import asyncio
import json
import logging
from functools import partial
from optparse import OptionParser

from game import MESSAGE_KEY, WINNER_KEY, REASON_KEY, FROM_KEY, TO_KEY
from game import Game, Color, get_all_colors
from timer import Timer

NAME_KEY = "name"
SECS_PER_TURN_KEY = "seconds_per_turn"
GAME_KEY = "game"
TIMER_KEY = "timer"
VIEWER_NAME = "viewer"
WITH_TIME_CHECKS = True

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler()])

clients = {}
games = []

def get_name(websocket):
    for name in clients:
        if clients[name] == websocket:
            return name
    return None

def remove_client(websocket):
    name = get_name(websocket)
    if name is not None:
        del clients[name]

def get_client_names():
    names = []
    for name in clients:
        if name != VIEWER_NAME:
            names.append(name)
    return names

async def handle_registration(name, websocket):
    logger.info("registration for {}".format(name))
    if name in clients:
        logger.warning("{} already connected!".format(name))
    else:
        clients[name] = websocket
        if VIEWER_NAME in clients:
            await clients[VIEWER_NAME].send(json.dumps({"names": get_client_names(), MESSAGE_KEY: "players"}))

def find_game(name):
    for game_data in games:
        for color in get_all_colors():
            if game_data.get(color, "") == name:
                return game_data
    return None

def make_float(number, default):
    if isinstance(number, float):
        return number
    try:
        return float(number)
    except:
        return default

def remove_game(game_to_remove):
    for index in range(len(games)):
        game_data = games[index]
        remove = True
        for color in get_all_colors():
            if game_data[color] != game_to_remove[color]:
                remove = False
        if remove:
            timer = game_data.get(TIMER_KEY, None)
            if timer is not None:
                timer.cancel()
            games.pop(index)
            return

async def send_to_all(game_data, message, except_name):
    for color in get_all_colors():
        name = game_data[color]
        if name != except_name and name in clients:
            await clients[name].send(json.dumps(message))
    if VIEWER_NAME != except_name and VIEWER_NAME in clients:
        await clients[VIEWER_NAME].send(json.dumps(message))

async def on_timeout(game_data):
    cur_game = game_data.get(GAME_KEY, None)
    if cur_game is None or cur_game.get_color_to_move() is None:
        logger.error("timeout when game not in process")
        return
    winner_color = cur_game.get_color_to_move().next_to_move()
    winner = game_data.get(winner_color, "no player for color {}".format(winner_color.key_name))
    result = {WINNER_KEY: winner, REASON_KEY: "просрочка времени", MESSAGE_KEY: "end_game"}
    remove_game(game_data)
    await send_to_all(game_data, result, None)

async def start_game(message, client_name):
    if client_name != VIEWER_NAME:
        logger.warning("new game requested not from viewer!")
        return
    secs_per_turn = message.get(SECS_PER_TURN_KEY, 2.0)
    new_game = {SECS_PER_TURN_KEY: make_float(secs_per_turn, 2.0)}
    for color in get_all_colors():
        player_name = message.get(color.key_name, None)
        if player_name is None or player_name not in clients:
            logger.warning("can not start game, request: {}".format(message))
            return
        game_data = find_game(player_name)
        if game_data is not None:
            logger.warning("can not start game: {} already in game".format(player_name))
            return
        new_game[color] = player_name
    new_game[GAME_KEY] = Game()
    games.append(new_game)
    for color in get_all_colors():
        out_message = {"color": color.key_name, SECS_PER_TURN_KEY: secs_per_turn, MESSAGE_KEY: "start_game"}
        await clients[new_game[color]].send(json.dumps(out_message))
    if WITH_TIME_CHECKS:
        new_game[TIMER_KEY] = Timer(new_game.get(SECS_PER_TURN_KEY, 2.0), partial(on_timeout, new_game))

def get_player_color(player_name):
    game_data = find_game(player_name)
    if game_data is None:
        return None
    for color in get_all_colors():
        if game_data[color] == player_name:
            return color
    return None

async def handle_move(message, client_name):
    color = get_player_color(client_name)
    game_data = find_game(client_name)
    if color is None or game_data is None:
        logger.warning("move from spy: {}".format(client_name))
        return
    cur_game = game_data[GAME_KEY]
    if cur_game.get_color_to_move() is None:
        logger.warning("move from {}, but no game available".format(client_name))
        return
    if color != cur_game.get_color_to_move():
        logger.warning("received move from {}, but its time for {}".format(color.key_name, cur_game.get_color_to_move().key_name))
        return
    await send_to_all(game_data, message, client_name)
    result = cur_game.make_move(message)
    if result is not None and WINNER_KEY in result:
        winner_color = result[WINNER_KEY]
        if isinstance(winner_color, Color):
            result[WINNER_KEY] = game_data.get(winner_color, winner_color.key_name)
        await send_to_all(game_data, result, None)
        remove_game(game_data)
    else:
        timer = game_data.get(TIMER_KEY, None)
        if timer is not None:
            timer.cancel()
            game_data[TIMER_KEY] = Timer(game_data.get(SECS_PER_TURN_KEY, 2.0), partial(on_timeout, game_data))


async def receive_parsed_json(message, websocket):
    if message.get(MESSAGE_KEY, "") == "registration" and NAME_KEY in message:
        await handle_registration(message[NAME_KEY], websocket)
        return
    if message.get(MESSAGE_KEY, "") == "start_game":
        await start_game(message, get_name(websocket))
        return
    if message.get(MESSAGE_KEY, "") == "move" and FROM_KEY in message and TO_KEY in message:
        await handle_move(message, get_name(websocket))
        return


async def handle_new_client(websocket, path):
    logger.info("A client connected {}".format(websocket.remote_address[0]))
    try:
        async for message in websocket:
            try:
                await receive_parsed_json(json.loads(message), websocket)
            except Exception as e:
                logger.error("error on message: {}\n{}".format(message, e))
    except websockets.exceptions.ConnectionClosed as e:
        logger.info("A client disconnected {}".format(websocket.remote_address[0]))
    finally:
        remove_client(websocket)


opt_parser = OptionParser()
opt_parser.add_option("-p", "--port", dest="port", action="store", default=6969, help="server port to run on")
opt_parser.add_option("-t", "--no_time_checks", action="store_true", help="flag if no time checks on move needed")
options, args = opt_parser.parse_args()

port = int(options.port)
WITH_TIME_CHECKS = not bool(options.no_time_checks)
logger.info("Running on port {} with time checks: {}".format(port, WITH_TIME_CHECKS))

start_server = websockets.serve(handle_new_client, "localhost", port)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
