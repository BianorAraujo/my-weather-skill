from flask import Flask, jsonify, request
import math
import requests
import logging

app = Flask(__name__)

# Configuração de logs
logging.basicConfig(level=logging.DEBUG)

API_KEY = "7999d32be4ad4e719d3170053250802"
CITY = "Dublin"

# Endpoints

@app.route('/', methods=['GET'])
def home():
    return jsonify({"response": "Welcome to Alexa API!"})

@app.route('/weather', methods=['GET'])
def weather():
    #return get_weather()
    return get_weather()

@app.route('/weather', methods=['POST'])
def alexa_handler():
    data = request.get_json()
    app.logger.debug(f"Alexa Request: {data}")

    # Verifica o tipo de requisição da Alexa
    request_type = data.get("request", {}).get("type")

    if request_type == "LaunchRequest":
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

    elif request_type == "IntentRequest":
        intent_name = data["request"]["intent"]["name"]

        if intent_name == "GetWeatherIntent":
            return get_weather()

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

def get_weather():
    try:

        URL = f"https://api.weatherapi.com/v1/forecast.json?q={CITY}&days=1&key={API_KEY}"
        
        app.logger.debug(f"URL: {URL}")

        response = requests.get(URL).json()

        #app.logger.debug(f"Weatherapi Response: {response}")

        if response["location"]["name"] == CITY:
            
            current_temp = math.floor(response["current"]["temp_c"])
            feels_like = math.floor(response["current"]["windchill_c"])
            min_temp = math.floor(response["forecast"]["forecastday"][0]["day"]["mintemp_c"])
            max_temp = round(response["forecast"]["forecastday"][0]["day"]["maxtemp_c"])

            alexa_response = {
                "version": "1.0",
                "sessionAttributes": {},
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": f"The temperature in Dublin is {current_temp} degrees, but it feels like {feels_like} degrees. Today, the temperature will be between a minimum of {min_temp} degrees and a maximum of {max_temp} degrees. Anything else?"
                    },
                    "card": {
                        "type": "Simple",
                        "title": "Dublin Weather",
                        "content": f"Temperature: {current_temp}°C\nFeels like: {feels_like}°C\nMin: {min_temp}°C, Max: {max_temp}°C"
                    },
                    "shouldEndSession": False
                }
            }
            
            return jsonify(alexa_response)
        
        else:
            alexa_response = {
                "version": "1.0",
                "sessionAttributes": {},
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": f"I'm sorry, I couldn't retrieve the weather information for {CITY}."
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
                    "text": "I'm sorry, I couldn't retrieve the weather information from Weather API."
                },
                "shouldEndSession": True
            }
        }

        return jsonify(error_response)

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