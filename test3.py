import asyncio
import socket
import time
import websockets

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('127.0.0.1', 8209))

async def retransmit(websocket, path):
	message = client_socket.recvfrom(1024)
	print("Retransmitting!")
	await websocket.send(message)

start_server = websockets.serve(retransmit, "10.42.0.1", 8008)

while True:
	print(client_socket.recvfrom(1024))

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
