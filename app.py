from flask import Flask, jsonify, request
import requests
import logging

app = Flask(__name__)

# Configuração de logs
logging.basicConfig(level=logging.DEBUG)

API_KEY = "4732991db4683111396788a5f7cefd05"
CITY = "Dublin,IE"

@app.route('/', methods=['GET'])
def home():
    return jsonify({"response": "Welcome to Alexa API!"})

@app.route('/weather', methods=['GET'])
def weather():
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
                    "text": "Welcome to Dublin Weather. You can ask for the current temperature!"
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

def get_weather():
    URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
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

        app.logger.debug(f"Error Response: {error_response}")
        return jsonify(error_response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)