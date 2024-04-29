from flask import Flask, request, render_template, jsonify
import random
import json
import time 
import socket
from math import sqrt
import asyncio


    

# Create a UDP socket i website1
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server address and port
address = ('127.0.0.1', 8148)
try:
    client_socket.bind(('127.0.0.1', 8148))
except:
    print("wtf")

client_socket.settimeout(1)

client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server address and port
address = ('127.0.0.1', 8011)
try:
    client_socket2.bind(('127.0.0.1', 8011))
except:
    print("wtf")

client_socket2.settimeout(20)

game_start = 0

data_file = 'pasient1.json'

def load_data():
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"numbers": [], "tilt_angles": []}

def save_data(data):
    with open(data_file, 'w') as file:
        json.dump(data, file)

def website():
    global client_socket
    print("started backend")
    app = Flask(__name__)
    @app.route('/')
    def index():
        return render_template('forside.html')

    @app.route('/glass.html')
    def glass_view():
        return render_template('glass.html')

    @app.route('/graf.html')
    def graf_view():
        return render_template('graf.html')

    @app.route('/pasient.html')
    def pasient():
        return render_template('pasient.html')
    
    @app.route('/behandler.html')
    def behandler_view():
        return render_template('behandler.html')

    @app.route('/grafBehandler.html')
    def graf_behandler(): 
        return render_template('grafBehandler.html')

    @app.route('/api/hello', methods=['POST'])
    def hello():
        print('Hello, World!')
        return '', 200

    @app.route('/api/name', methods=['POST'])
    def handle_text():
        text_data = request.form['text']  # Assuming the data is sent as form data
        print(text_data)  # Print the received text to the console
        return 'Text received', 200  # Respond to the client that the text was received

    @app.route('/api/newbutton', methods=['GET'])
    def init():
    #    try:
        a, adress = client_socket.recvfrom(1024)
        a = a.decode("utf-8")
        a = a.split(' ')
        print(a)
        tilt = str(sqrt(float(a[0])**2 + float(a[1])**2 + float(a[2])**2) -90)
        graph = str(sqrt(float(a[3])**2 + float(a[4])**2 + float(a[5])**2))
        tilt_angle = tilt
        graph_number = graph
        return jsonify({
            "tilt": tilt_angle,
            "number": graph_number
    })
    #    except: 
    #        print("Harm done") 
    #        return ""

    @app.route('/api/game_start', methods=['POST'])
    def game_start():
        data = request.json
        print("data json: " + str(data))
        address = ('127.0.0.1', 8004)
        Reading = "1 pasient1"
        Reading = str.encode(Reading) #codek register encoding
        for i in range(4):
            print("sending")
            client_socket2.sendto(Reading, address) 
            time.sleep(1)
        return "Button clicked"

    if __name__ == '__main__':
        app.run(debug=False)
'''
def website2(address):
    app = Flask(__name__)

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    @app.route('/')
    def index():
        return render_template('forside.html')

    @app.route('/glass.html')
    def glass_view():
        return render_template('glass.html')

    @app.route('/graf.html')
    def graf_view():
        return render_template('graf.html')

    @app.route('/pasient.html')
    def pasient():
        return render_template('pasient.html')

    @app.route('/api/hello', methods=['POST'])
    def hello():
        print('Hello, World!')
        return '', 200

    @app.route('/api/name', methods=['POST'])
    def handle_text():
        text_data = request.form['text']  # Assuming the data is sent as form data
        print(text_data)  # Print the received text to the console
        return 'Text received', 200  # Respond to the client that the text was received

    @app.route('/api/newbutton', methods=['GET'])
    def init():
        print(str(client_socket.recvfrom(1024)))
        messagereicived = client_socket.recvfrom(1024)

        a = messagereicived[0]
        a = a.split(' ')
        tilt = sqrt(int(a[0])^2 + int(a[1])^2 + int(a[2])^2)
        graph = sqrt(int(a[3])^2 + int(a[4])^2 + int(a[5])^2)
        tilt_angle = a[2]
        graph_number = a[4] 
        return jsonify({
            "tilt": tilt_angle,
            "number": graph_number
        })


    if __name__ == '__main__':
        app.run(debug=True, host=address[0], port=address[1])

if __name__ == '__main__':
    website2(('127.0.0.1', 8009))

'''
website()