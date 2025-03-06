from flask import jsonify
import requests

class Rain:
    @staticmethod
    def get_rain(response: any, CITY: str):

        try:

            image = response["current"]["condition"]["icon"]
            current_time = response["location"]["localtime"].split(" ")[1]
            current_time_12 = Rain.convert_time_format(current_time)
            precipitation = response["current"]["precip_mm"]
            is_raining = bool(precipitation > 0.5)

            for hour in response["forecast"]["forecastday"][0]["hour"]:
                
                hour_24 = hour["time"].split(" ")[1]
                hour_12 = Rain.convert_time_format(hour_24)

                if is_raining:
                    is_raining_text = "It's raining!"

                    if hour_12 >= current_time_12 and hour["precip_mm"] <= 0:
                        next_event = f"The rain will stop around {hour_12}"
                        break
                    else:
                        next_event = "It will rain all day"
                else:
                    is_raining_text = "It's not raining!"
                    
                    if hour_12 >= current_time_12 and hour["precip_mm"] > 0.5:
                        next_event = f"The rain will start around {hour_12}"
                        break
                    else:
                        next_event = "There is no rain forecast for today"
                

            if is_raining:
                text = f"In Dublin is raining. {next_event}"
            else:
                text = f"In Dublin is not raining. {next_event}"

            alexa_response = {
                "version": "1.0",
                "sessionAttributes": {},
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": f"{text}. Anything else?"
                    },
                    "card": {
                        "type": "Standard",
                        "title": f"{CITY} Weather",
                        "text": f"{is_raining_text}\nPrecipitation: {precipitation}mm",
                        "image": {
                            "smallImageUrl": f"https:{image}",
                            "largeImageUrl": f"https:{image}"
                        }
                    },
                    "shouldEndSession": False
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
                        "text": "I'm sorry, I couldn't retrieve the rain information."
                    },
                    "shouldEndSession": True
                }
            }

            return jsonify(error_response)

    @staticmethod 
    def convert_time_format(hour24: str) -> str:
        hour, minutes = hour24.split(':')
        hour = int(hour)

        period = 'AM' if hour < 12 else 'PM'

        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12
        
        return f"{hour_12}:{minutes} {period}"
