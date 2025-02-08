from flask import Flask, jsonify
import requests

app = Flask(__name__)

API_KEY = "4732991db4683111396788a5f7cefd05"
CITY = "Dublin,IE"

@app.route('/', methods=['GET'])
def home():
    return jsonify({"response": "Welcome to Alexa API!"})

@app.route('/weather', methods=['GET'])
def get_weather():
    URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(URL).json()

    if response.get("main"):
        temp = round(response["main"]["temp"])
        feels_like = round(response["main"]["feels_like"])
        return jsonify({"response": f"The temperature in Dublin is {temp} degrees, but it feels like {feels_like} degrees."})
    else:
        return jsonify({"response": "Sorry, I couldn't get the weather."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)