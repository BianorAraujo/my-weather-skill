from flask import jsonify
import math
import requests

class Temperature:
    @staticmethod
    def get_temperature(response: any, CITY: str):
        try:

            if response["location"]["name"] == CITY:
                
                current_temp = math.floor(response["current"]["temp_c"])
                feels_like = math.floor(response["current"]["windchill_c"])
                min_temp = math.floor(response["forecast"]["forecastday"][0]["day"]["mintemp_c"])
                max_temp = round(response["forecast"]["forecastday"][0]["day"]["maxtemp_c"])
                image = response["current"]["condition"]["icon"]

                alexa_response = {
                    "version": "1.0",
                    "sessionAttributes": {},
                    "response": {
                        "outputSpeech": {
                            "type": "PlainText",
                            "text": f"The temperature in Dublin is {current_temp} degrees, but it feels like {feels_like} degrees. Today, the temperature will be between a maximum of {max_temp} degrees and a minimum of {min_temp} degrees. Anything else?"
                        },
                        "card": {
                            "type": "Standard",
                            "title": f"{CITY} Weather",
                            "text": f"Temperature: {current_temp}°C\nFeels like: {feels_like}°C\nMax: {max_temp}°C / Min: {min_temp}°C",
                            "image": {
                                "smallImageUrl": f"https:{image}",
                                "largeImageUrl": f"https:{image}"
                            }
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
