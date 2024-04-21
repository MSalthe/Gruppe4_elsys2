from flask import Flask, request, render_template, jsonify
import random
import json
import time 
import socket

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
    tilt_angle = random.randint(-100, 100)  
    graph_number = random.randint(0, 100)  
    return jsonify({
        "tilt": tilt_angle,
        "number": graph_number
    })

if __name__ == '__main__':
    app.run(debug=True)