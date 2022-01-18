import websockets
import asyncio
import json
import logging
import sys

from game import WINNER_KEY, REASON_KEY, FROM_KEY, TO_KEY
from game import Color, get_all_colors, get_color_to_move, start, make_move

NAME_KEY = "name"
SECS_PER_TURN_KEY = "seconds_per_turn"
VIEWER_NAME = "viewer"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler()])

clients = {}
players = {}
secs_per_turn = 2.0

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
            await clients[VIEWER_NAME].send(json.dumps({"names": get_client_names()}))

async def start_game(message, client_name):
    if client_name != VIEWER_NAME:
        logger.warning("new game requested not from viewer!")
        return
    global secs_per_turn
    secs_per_turn = message.get(SECS_PER_TURN_KEY, 2.0)
    for color in get_all_colors():
        player_name = message.get(color.key_name, None)
        if player_name is None or player_name not in clients:
            logger.warning("can not start game, request: {}".format(message))
            return
        players[color] = player_name
    start()
    for color in players:
        out_message = {"color": color.key_name, SECS_PER_TURN_KEY: secs_per_turn}
        await clients[players[color]].send(json.dumps(out_message)) # TODO timer

def get_player_color(player_name):
    for color in players:
        if players[color] == player_name:
            return color
    return None

async def send_to_all(message, except_name):
    for color in players:
        name = players[color]
        if name != except_name and name in clients:
            await clients[name].send(json.dumps(message))
    if VIEWER_NAME != except_name and VIEWER_NAME in clients:
        await clients[VIEWER_NAME].send(json.dumps(message))

async def handle_move(message, client_name):
    color = get_player_color(client_name)
    if color is None:
        logger.warning("move from spy: {}".format(client_name))
        return
    if get_color_to_move() is None:
        logger.warning("move from {}, but no game available".format(client_name))
        return
    if color != get_color_to_move():
        logger.warning("received move from {}, but its time for {}".format(color.key_name, get_color_to_move().key_name))
        return
    await send_to_all(message, client_name) # TODO timer
    result = make_move(message)
    if result is not None and WINNER_KEY in result:
      await send_to_all(result, None)


async def receive_parsed_json(message, websocket):
    if NAME_KEY in message:
        await handle_registration(message[NAME_KEY], websocket)
    if SECS_PER_TURN_KEY in message:
        await start_game(message, get_name(websocket))
    if FROM_KEY in message and TO_KEY in message:
        await handle_move(message, get_name(websocket))

async def handle_new_client(websocket, path):
    logger.info("A client connected {}".format(websocket.remote_address[0]))
    try:
        async for message in websocket:
            try:
                await receive_parsed_json(json.loads(message), websocket)
            except:
                logger.error("error on message: {}".format(message))
    except websockets.exceptions.ConnectionClosed as e:
        logger.info("A client disconnected {}".format(websocket.remote_address[0]))
    finally:
        remove_client(websocket)


port = 6969 if len(sys.argv) < 2 else sys.argv[1]
logger.info("Running on port {}".format(port))

start_server = websockets.serve(handle_new_client, "localhost", port)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
