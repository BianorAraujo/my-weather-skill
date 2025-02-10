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
        
    return jsonify({
        "version": "1.0",
        "sessionAttributes": {},
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "I'm not sure how to handle that request."
            },
            "shouldEndSession": True
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
                    "text": "Welcome my weather. What are you would to know about the weather?"
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

# Old methods         

def get_weather_old():
    LAT = "53.408082"
    LON = "-6.165503"

    URL = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    
    app.logger.debug(f"URL: {URL}")

    response = requests.get(URL).json()

    app.logger.debug(f"OpenWeatherMap Response: {response}")

    if response.get("main"):
        temp = round(response["main"]["temp"])
        feels_like = round(response["main"]["feels_like"])
        temp_min = round(response["main"]["temp_min"])
        temp_max = round(response["main"]["temp_max"])

        alexa_response = {
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": f"The temperature in Dublin is {temp} degrees, but it feels like {feels_like} degrees. Today, the temperature will be between a minimum of {temp_min} degrees and a maximum of {temp_max} degrees."
                },
                "card": {
                    "type": "Simple",
                    "title": "Dublin Weather",
                    "content": f"Temperature: {temp}°C\nFeels like: {feels_like}°C\nMin: {temp_min}°C, Max: {temp_max}°C"
                },
                "shouldEndSession": True
            }
        }

        app.logger.debug(f"Alexa Response: {alexa_response}")
        return jsonify(alexa_response)
    
    else:
        error_response = {
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "I'm sorry, I couldn't retrieve the weather information."
                },
                "shouldEndSession": True
            }
        }

        #app.logger.debug(f"Error Response: {error_response}")
        return jsonify(error_response)

# App run

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)