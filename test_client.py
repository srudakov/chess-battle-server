import websockets
import asyncio
import json
from optparse import OptionParser

URL = ""
TEXTS_TO_SEND = []

def check(text):
    return text is not None and len(str(text)) > 0

async def listen():
    async with websockets.connect(URL) as ws:
        for text in TEXTS_TO_SEND:
            await ws.send(text)
        while True:
            msg = await ws.recv()
            print(msg)

opt_parser = OptionParser()
opt_parser.add_option("-a", "--address", dest="address", action="store", default="localhost")
opt_parser.add_option("-p", "--port", dest="port", action="store", default="6969")
opt_parser.add_option("-T", "--text", dest="text", action="store")
opt_parser.add_option("-F", "--file", dest="file", action="store")
opt_parser.add_option("-n", "--name", dest="name", action="store")
opt_parser.add_option("-f", "--move_from", dest="move_from", action="store")
opt_parser.add_option("-t", "--move_to", dest="move_to", action="store")
opt_parser.add_option("-r", "--transform", dest="transform", action="store")
opt_parser.add_option("-w", "--white", dest="white", action="store")
opt_parser.add_option("-b", "--black", dest="black", action="store")
opt_parser.add_option("-s", "--seconds_per_turn", dest="seconds_per_turn", action="store")
options, args = opt_parser.parse_args()

URL = "ws://{}:{}".format(options.address, options.port)
if check(options.name):
    TEXTS_TO_SEND.append(json.dumps({"name": str(options.name)}))
if check(options.move_from) and check(options.move_to):
    move = {"from": str(options.move_from), "to": str(options.move_to)}
    if check(options.transform):
        move["transform"] = str(options.transform)
    TEXTS_TO_SEND.append(json.dumps(move))
if check(options.white) and check(options.black) and check(options.seconds_per_turn):
    TEXTS_TO_SEND.append(json.dumps({"white": str(options.white), "black": str(options.black), "seconds_per_turn": str(options.seconds_per_turn)}))
if check(options.text):
    TEXTS_TO_SEND.append(options.text)
if check(options.file):
    TEXTS_TO_SEND.append(open(options.file, "r").read())

asyncio.get_event_loop().run_until_complete(listen())
