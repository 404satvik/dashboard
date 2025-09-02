import os
import random
import json
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, session


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')

if not app.secret_key:
    raise ValueError("No secret key")

try:
    with open("albums.json", "r", encoding='utf-8') as f:
        ALBUM_DATA = json.load(f)
except FileNotFoundError:
    print("Error file not found")
    ALBUM_DATA = []


@app.route('/')
def entry_page():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    track_id = session.get('spotify_track_id', '3kxfsds8_6w5A8ls6gMRo2')
    return render_template('dashboard.html')


@app.route('/api/get-album-puzzle')
def get_album_puzzle():
    valid_albums = [album for album in ALBUM_DATA if "answer" in album and "options" in album]
    if not valid_albums:
        return jsonify({"error": "No valid album data available"}), 500

    chosen_album = random.choice(valid_albums)
    
    session['correct_answer'] = chosen_album['answer']
    session['track_id'] = chosen_album['spotify_track_id']
    return jsonify({
        'image': chosen_album['image'],
        'options': random.sample(chosen_album['options'], len(chosen_album['options']))
    })


@app.route('/api/submit-guess', methods=['POST'])
def submit_guess():
    """Receives the user's guess and checks if it's correct."""
    data = request.get_json()
    user_guess = data.get('guess')
    
    correct_answer = session.get('correct_answer', None)
    
    if user_guess and user_guess == correct_answer:
        session.pop('correct_answer', None)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@app.route('/api/weather')
def get_weather():
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        print("ERROR: WEATHER_API_KEY not found in .env file")
        return jsonify({"error": "Weather API key not configured"}), 500

    city = "Chennai" 
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        weather_data = response.json()
        
        simplified_data = {
            "temp": weather_data["main"]["temp"],
            "feels_like": weather_data["main"]["feels_like"],
            "description": weather_data["weather"][0]["description"].title(),
            "city": weather_data["name"]
        }
        return jsonify(simplified_data)

    except requests.exceptions.RequestException as e:
        print(f"ERROR fetching weather data: {e}")
        return jsonify({"error": "Failed to fetch weather data from API"}), 500


if __name__ == '__main__':
    app.run(debug=True)