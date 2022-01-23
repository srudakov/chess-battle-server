# chess-battle-server  
python server for chess bot battles  

using python chess module: https://python-chess.readthedocs.io/en/latest  

We will write our own chess bots and see who's better.  
Bots should be able to communicate with web socket server by json protocol described in this repo.  
This repo is mainly web socket server with chess checks(python).  
Plus here is simple python client for testing server and other clients. You can even play with some bot with that test client.  
And here is bot that makes random moves.  

Fedor will do browser visualization and match history storing with C#.  

Примерный алгоритм  
1. запустить сервер (server.py) можно через консоль  
2. Подключение по websocket - дефолтный порт 6969  
3. Кидаем команды - команда это JSON(см protocol.txt)  
4. Принимаем команды хода противника  
5. Ждем команду окончания партии  
