import socket
import json
import random
import time

# Server's IP address and port for the TCP connection
SERVER_HOST = 'localhost'
SERVER_PORT = 3000

while True:
    # Generate a random number
    data = {"number": random.randint(1, 100)}
    data_bytes = json.dumps(data).encode('utf-8')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        s.sendall(data_bytes)

    print(f"Sent: {data}")
    time.sleep(5)  # Send data every 5 seconds