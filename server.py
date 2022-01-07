import websockets
import asyncio
import json

NAME_KEY = "name"
clients = {}

def remove_client(websocket):
    for name in clients:
        if clients[name] == websocket:
            del clients[name]
            return

async def receive_parsed_json(message, websocket):
    if NAME_KEY in message:
        name = message[NAME_KEY]
        if name in clients:
            print("{} already connected!".format(name))
        else:
            clients[name] = websocket
            await websocket.send("name: {}".format(name))

async def handle_new_client(websocket, path):
    print("A client connected {}".format(websocket.remote_address[0]))
    try:
        async for message in websocket:
            try:
                await receive_parsed_json(json.loads(message), websocket)
            except:
                print("error on message: {}".format(message))
    except websockets.exceptions.ConnectionClosed as e:
        print("A client disconnected {}".format(websocket.remote_address[0]))
    finally:
        remove_client(websocket)


PORT = 6969
print("Running on port {}".format(PORT))

start_server = websockets.serve(handle_new_client, "localhost", PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
