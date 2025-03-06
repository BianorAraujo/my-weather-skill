from flask import Flask, jsonify, request
import math
import requests
import logging
from rain import Rain
from temperature import Temperature

app = Flask(__name__)

# Configuração de logs
logging.basicConfig(level=logging.DEBUG)

API_KEY = "7999d32be4ad4e719d3170053250802"
CITY = "Dublin"
IS_DAY = True

# Endpoints

@app.route('/', methods=['GET'])
def home():
    return jsonify({"response": "My Weather API is running!"})

@app.route('/temperature', methods=['GET'])
def weather():
    response = call_api()
    return Temperature.get_temperature(response, CITY)

@app.route('/rain', methods=['GET'])
def rain():
    response = call_api()
    return Rain.get_rain(response, CITY)
    
@app.route('/weather', methods=['POST'])
def alexa_handler():
    data = request.get_json()

    # Verifica o tipo de requisição da Alexa
    request_type = data.get("request", {}).get("type")

    if request_type == "LaunchRequest":
        return launch_request()

    elif request_type == "IntentRequest":
        intent_name = data["request"]["intent"]["name"]

        response = call_api()

        if intent_name == "GetWeatherIntent":
            return Temperature.get_temperature(response, CITY)
        
        if intent_name == "GetRainIntent":
            return Rain.get_rain(response, CITY)
        
        if intent_name == "GetTemperatureIntent":
            return Temperature.get_temperature(response, CITY)
        
        if intent_name == "AMAZON.StopIntent":
            return finish_conversation()
        
        if intent_name == "GetFarewellIntent":
            return byebye_conversation()
        
    return jsonify({
        "version": "1.0",
        "sessionAttributes": {},
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "I'm sorry, I couldn't understand you. Could you repeat, please?"
            },
            "shouldEndSession": False
        }
    })

# Methods

def launch_request():
    return jsonify({
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Welcome to my weather skill. What would you like to know about the weather?"
                },
                "shouldEndSession": False
            }
        })

def finish_conversation():
    try:
        response = call_api()

        if response["location"]["name"] == CITY:
            IS_DAY = bool(response["current"]["is_day"])
                    
        if IS_DAY:
            farewell = "day"
        else:
            farewell = "night"

        alexa_response = {
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": f"Have a good {farewell}"
                },
                "shouldEndSession": True
            }
        }
        
        return jsonify(alexa_response)
    
    except requests.exceptions.RequestException as e:
        error_response = {
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "I'm sorry, I couldn't retrieve the information from Weather API."
                },
                "shouldEndSession": True
            }
        }

        return jsonify(error_response)

def byebye_conversation():
    try:
        alexa_response = {
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Bye bye!"
                },
                "shouldEndSession": True
            }
        }
        
        return jsonify(alexa_response)
    
    except requests.exceptions.RequestException as e:
        error_response = {
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Sorry, I'm not having a good day today."
                },
                "shouldEndSession": True
            }
        }

        return jsonify(error_response)

def call_api():

    try:
        URL = f"https://api.weatherapi.com/v1/forecast.json?q={CITY}&days=1&key={API_KEY}"
        
        #app.logger.debug(f"URL: {URL}")

        response = requests.get(URL).json()

        if response["location"]["name"] == CITY:
            return response
        else:
            return None
        
    except requests.exceptions.RequestException as e:
        error_response = {
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "I'm sorry, I couldn't retrieve the weather information from Weather API."
                },
                "shouldEndSession": True
            }
        }

        return jsonify(error_response)


# App run

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)