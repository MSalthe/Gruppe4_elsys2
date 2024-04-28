from flask import Flask, render_template, jsonify
import random
import json

app = Flask(__name__)

data_file = 'data.json'

def load_data():
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"numbers": [], "tilt_angles": []}

def save_data(data):
    with open(data_file, 'w') as file:
        json.dump(data, file)

@app.route('/')
def index():
    return render_template('forside.html')
    
@app.route('/forside.html')
def forside():
    return render_template('forside.html')

# Ruter til HTML sider under pasient
@app.route('/pasient.html')
def pasient():
    return render_template('pasient.html')

@app.route('/glass.html')
def glass_view():
    return render_template('glass.html')

@app.route('/graf.html')
def graf_view():
    return render_template('graf.html')

# Ruter til HTML sider under behandler
@app.route('/behandler.html')
def behandler():
    return render_template('behandler.html')

@app.route('/grafBehandler.html')
def graf_behandler(): 
    return render_template('grafBehandler.html')

# Generatorer
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
    data = load_data()
    tilt_angle = [random.randint(-100,100)]
    graph_number = [random.randint(0,100)]
    # Append new data to the existing data
    data['numbers'].extend(graph_number)
    data['tilt_angles'].extend(tilt_angle)
    save_data(data)
    return jsonify(data)

@app.route('/api/newbutton2', methods=['GET'])
def send_data():
    data = load_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)