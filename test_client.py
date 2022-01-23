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

usage_text = """Multiple send options set => multiple comands will be sent.
After sending all messages client listen and print messages from server
Examples
1) send some abstact text to server: test_client.py -T "some text to send"
2) send text from file: test_client.py -F file_path
3) register on server: test_client.py -n ololo_client
4) start game(server accepts start game from viewer only: test_client.py -n viewer -w ololo_client -b ululu_client -s 3
5) make move: test_client.py -n ololo_client -f g2 -t g4
6) send many messages(you can do that, but you dont need that): test_client.py -n ololo_client -T "{"key": "value"}" -F /tmp/file -f d2 -t d3
If server works not on localhost:6969 you should add -a <server_address> -p <server_port>
"""
opt_parser = OptionParser(usage=usage_text)
opt_parser.add_option("-a", "--address", dest="address", action="store", default="localhost", help="server address to connect to")
opt_parser.add_option("-p", "--port", dest="port", action="store", default="6969", help="server port to connect to")
opt_parser.add_option("-T", "--text", dest="text", action="store", help="text to send to server(no text => no send)")
opt_parser.add_option("-F", "--file", dest="file", action="store", help="file path to send its content to server(no path => no send)")
opt_parser.add_option("-n", "--name", dest="name", action="store", help="client name. Defined => send self registration command")
opt_parser.add_option("-f", "--move_from", dest="move_from", action="store", help="move from cell in move command")
opt_parser.add_option("-t", "--move_to", dest="move_to", action="store", help="move to cell in move command")
opt_parser.add_option("-r", "--transform", dest="transform", action="store", help="piece type to transform pawn in move command")
opt_parser.add_option("-w", "--white", dest="white", action="store", help="client name to play white in start game command")
opt_parser.add_option("-b", "--black", dest="black", action="store", help="client name to play black in start game command")
opt_parser.add_option("-s", "--seconds_per_turn", dest="seconds_per_turn", action="store", help="seconds per turn in start game command")
options, args = opt_parser.parse_args()

URL = "ws://{}:{}".format(options.address, options.port)
if check(options.name):
    TEXTS_TO_SEND.append(json.dumps({"name": str(options.name)}))
if check(options.move_from) and check(options.move_to):
    move = {"from": str(options.move_from), "to": str(options.move_to)}
    if check(options.transform):
        move["transform"] = str(options.transform)
    TEXTS_TO_SEND.append(json.dumps(move))
if check(options.white) and check(options.black):
    seconds_per_turn = str(options.seconds_per_turn) if check(options.seconds_per_turn) else "2"
    TEXTS_TO_SEND.append(json.dumps({"white": str(options.white), "black": str(options.black), "seconds_per_turn": seconds_per_turn}))
if check(options.text):
    TEXTS_TO_SEND.append(options.text)
if check(options.file):
    TEXTS_TO_SEND.append(open(options.file, "r").read())

asyncio.get_event_loop().run_until_complete(listen())
