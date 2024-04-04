from flask import Flask, request, render_template
import random
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('frontend.html')

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
def respond():
    a = random.randint(-100,100)
    returnvalue = "{\"tilt\": " + str(a) + "}"
    print(returnvalue)
    return returnvalue

if __name__ == '__main__':
    app.run(debug=True)