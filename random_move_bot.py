import websockets
import asyncio
import json
import random
import chess
import game
from optparse import OptionParser

URL = ""
NAME = "random moves"
COLOR = None
GAME_DATA = None

def check(text):
    return text is not None and len(str(text)) > 0

def get_peice(piece_type):
    piece_map = {chess.QUEEN: "Queen", chess.ROOK: "Rook", chess.KNIGHT: "Knight", chess.BISHOP: "Bishop"}
    return piece_map.get(piece_type, None)

def trans_move(move_from_lib):
    move = {"from": chess.square_name(move_from_lib.from_square).upper(), "to": chess.square_name(move_from_lib.to_square).upper(), game.MESSAGE_KEY: "move"}
    if move_from_lib.promotion is not None:
        piece = get_peice(move_from_lib.promotion)
        if piece is not None:
            move["transform"] = piece
    return move

async def make_move(ws):
    if GAME_DATA is None or COLOR != GAME_DATA.get_color_to_move():
        return
    moves = [move for move in GAME_DATA.board.legal_moves]
    index = random.randrange(len(moves))
    move = trans_move(moves[index])
    GAME_DATA.make_move(move)
    await ws.send(json.dumps(move))

def parse_json(message):
    try:
        return json.loads(message)
    except:
        return None

def check_type(message, command_type):
    return message.get(game.MESSAGE_KEY, None) == command_type

async def receive(message_str, ws):
    print(message_str)
    message = parse_json(message_str)
    global GAME_DATA
    if message is None:
        return
    if check_type(message, "end_game"):
        print("winner/reason: {}/{}".format(message.get("winner", ""), message.get("reason", "")))
        print(GAME_DATA.board)
    if check_type(message, "start_game"):
        global COLOR
        COLOR = game.Color.WHITE if message["color"].lower() == "white" else game.Color.BLACK
        GAME_DATA = game.Game()
        await make_move(ws)
    if check_type(message, "move") and GAME_DATA.board is not None:
        GAME_DATA.make_move(message)
        await make_move(ws)

async def listen():
    async with websockets.connect(URL) as ws:
        await ws.send(json.dumps({"name": NAME, game.MESSAGE_KEY: "registration"}))
        while True:
            msg = await ws.recv()
            await receive(msg, ws)

opt_parser = OptionParser()
opt_parser.add_option("-a", "--address", dest="address", action="store", default="localhost", help="server address to connect to")
opt_parser.add_option("-p", "--port", dest="port", action="store", default="6969", help="server port to connect to")
opt_parser.add_option("-n", "--name", dest="name", action="store", help="self name to register on server")
options, args = opt_parser.parse_args()

URL = "ws://{}:{}".format(options.address, options.port)
if check(options.name):
    NAME = str(options.name)

asyncio.get_event_loop().run_until_complete(listen())
