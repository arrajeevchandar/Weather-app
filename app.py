from flask import Flask, render_template,send_file, request
import requests 
import json 
import geocoder
import speech_recognition as sr
from gtts import gTTS

app = Flask(__name__)

def get_weather(city):
    api_key = '6e228af54aa2dd096b8b4aa0e8ce8712' 
    api_request = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}") 
    api = json.loads(api_request.content) 
    if 'main' in api:
        y = api['main'] 
        current_temperature = y['temp'] 
        humidity = y['humidity'] 
        temp_min = y['temp_min'] 
        temp_max = y['temp_max'] 
        city_name = api['name']
        return city_name, current_temperature, humidity, temp_min, temp_max
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/weather', methods=['POST'])
def weather():
    city = request.form['city']
    if city:
        weather_data = get_weather(city)
        if weather_data:
            city_name, temperature, humidity, temp_min, temp_max = weather_data
            return render_template('index.html', city=city_name, temperature=temperature, 
                                   humidity=humidity, temp_min=temp_min, temp_max=temp_max)
        else:
            return render_template('index.html', error="City not found.")
    else:
        return render_template('index.html', error="City name cannot be empty.")

@app.route('/gps')
def gps():
    g = geocoder.ip('me')
    city = g.city
    if city:
        api_key='6e228af54aa2dd096b8b4aa0e8ce8712'
        api_request = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}") 
        api = json.loads(api_request.content) 
        y = api['main'] 
        current_temperature = y['temp'] 
        humidity = y['humidity'] 
        temp_min = y['temp_min'] 
        temp_max = y['temp_max'] 
        city_name = api['name']
        return render_template('index.html', city=city_name, temperature=current_temperature, 
                               humidity=humidity, temp_min=temp_min, temp_max=temp_max)
    else:
        return render_template('index.html', error="Unable to fetch location.")

@app.route('/voice_weather', methods=['POST'])
def voice_weather():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            city = r.recognize_google(audio)
            print("You said:", city)
            weather_data = get_weather(city)
            if weather_data:
                city_name, temperature, humidity, temp_min, temp_max = weather_data
                weather_text = f"The current temperature in {city_name} is {temperature} degrees Celsius. " \
                               f"Humidity is {humidity} percent. Minimum temperature is {temp_min} degrees Celsius " \
                               f"and maximum temperature is {temp_max} degrees Celsius."
                tts = gTTS(text=weather_text, lang='en')
                audio_file_path = "weather.mp3"
                tts.save(audio_file_path)
                
                audio_url = "/" + audio_file_path
                return render_template('index.html',city=city_name, temperature=temperature, 
                                   humidity=humidity, temp_min=temp_min, temp_max=temp_max, success="Weather data retrieved successfully.", audio_url=audio_url)
            else:
                return render_template('index.html', error="City not found.")
        except Exception as e:
            print("Error:", e)
            return render_template('index.html', error="Error processing voice input.")
        
@app.route('/audio')
def audio():
    return send_file('weather.mp3', mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(debug=True)
