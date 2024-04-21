from flask import Flask, request, render_template
import random
import json
import socket


    

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server address and port
server_address = ('localhost', 8004)

try:
    # Get user input and send it to the server
    message = input("Enter message to send to server: ")
    client_socket.sendto(message.encode(), server_address)


def website():
    print("started backend")
        
    app = Flask(__name__)

    @app.route('/forside.html')
    def forside():
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
    def behandler():
        return render_template('behandler.html')

    @app.route('/')
    def intro():
        return render_template('forside.html')

    @app.route('/api/hello', methods=['SEND'])
    def hello():
        print('Hello, World!')
        return '', 200

    @app.route('/api/name', methods=['POST'])
    def handle_text():
        text_data = request.form['text']  # Assuming the data is sent as form data
        print(text_data)  # Print the received text to the console
        return 'Text received', 200  # Respond to the client that the text was received

    @app.route('/api/newbutton', methods=['GET'])
    def respond():
        a = random.randint(-100,100)
        returnvalue = "{\"tilt\": " + str(a) + "}"
        print(returnvalue)
        return returnvalue

    if __name__ == '__main__':
        app.run(debug=True)

website()
