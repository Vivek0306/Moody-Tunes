import json
import os
import random
import base64
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from requests import post, get
from dotenv import load_dotenv
from urllib.parse import quote
from datetime import datetime

# Environment Variables
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Flask App init
app = Flask(__name__)
socketio = SocketIO(app)


# Database Section
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

class Emotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.String(50))
    song = db.Column(db.String(100))
    name = db.Column(db.String(100))
    duration = db.Column(db.Integer)
    image = db.Column(db.String(100))
    detected_at = db.Column(db.DateTime, default=datetime.now)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song = db.Column(db.String(100))
    name = db.Column(db.String(100))
    duration = db.Column(db.Integer)
    image = db.Column(db.String(100))

def store_emotion(emotion,song, name, duration, image):
    new_emotion = Emotion(emotion=emotion, song=song, name=name, duration=duration, image=image)
    db.session.add(new_emotion)
    db.session.commit()

def add_song(song, name, duration, image):
    new_song = Playlist(song=song, name=name,  duration=duration, image=image)
    db.session.add(new_song)
    db.session.commit()
# End Database Section


# Spotify Fetching
def get_token():
    auth_string = f"{client_id}:{client_secret}"
    auth_base64 = str(base64.b64encode(auth_string.encode("utf-8")), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }

    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_headers(token):
    return {"Authorization": "Bearer " + token}

def get_user_details():
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": "Bearer " + get_token()}
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_songs_for_category(category, limit):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": "Bearer " + get_token()}
    query = f"?q={category}&type=track&limit={24}&market=IN"
    url = url + query
    result = get(url, headers=headers)
    json_result = json.loads(result.content)

    return json_result
# End Spotify Fetching

# Routes
@app.route('/')
def index():
    response = get_songs_for_category("he", 8)
    tracks = response["tracks"]["items"]
    track_data = []
    for track in tracks:
        track_info = {
            'name': track['name'],
            'image_url': track['album']['images'][0]['url'],
            'image_height': track['album']['images'][0]['height'],
            'image_width': track['album']['images'][0]['width'],
            'song_url': f"http://open.spotify.com/track/{track['id']}",
            'duration': track['duration_ms'],
            'artist': track['artists'][0]['name'],
            'uri': track['uri'],

        }
        track_data.append(track_info)
    random.shuffle(track_data)
    return render_template('index.html', track_data=track_data)


@app.route('/fetch_songs')
def fetch_songs():
    emotion = request.args.get('emotion')
    # store_emotion(emotion)
    response = get_songs_for_category(
        f"malayalam songs that are perfect for {emotion} mood", 12)
    print("Fetching songs for EMOTION..............",
          request.args.get('emotion'))
    tracks = response["tracks"]["items"]
    track_data = []
    for track in tracks:
        track_info = {
            'name': track['name'],
            'image_url': track['album']['images'][0]['url'],
            'image_height': track['album']['images'][0]['height'],
            'image_width': track['album']['images'][0]['width'],
            'duration': track['duration_ms'],
            'song_url': f"http://open.spotify.com/track/{track['id']}",
            'artist': track['artists'][0]['name'],
        }
        track_data.append(track_info)
    random.shuffle(track_data)
    track_data = track_data[:12]
    return jsonify(track_data)

@app.route('/store_songs')
def store_songs():
    emotion = request.args.get('emotion')
    song_uri = request.args.get('uri')
    duration = request.args.get('duration')
    image = request.args.get('image')
    name = request.args.get('name')
    try:
        store_emotion(emotion, song_uri, name, duration, image)
        return jsonify({'message': 'Song stored successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/add_playlist')
def add_playlist():
    song_uri = request.args.get('uri')
    name = request.args.get('name')
    duration = request.args.get('duration')
    image = request.args.get('image')
    try:
        add_song(song_uri, name, duration, image)
        return jsonify({'message': 'Song added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/categories')
def categories():
    response = get_songs_for_category("happy malayalam songs", 4)
    tracks = response["tracks"]["items"]
    happy_songs = []
    for track in tracks:
        track_info = {
                'name': track['name'],
                'image_url': track['album']['images'][0]['url'],
                'image_height': track['album']['images'][0]['height'],
                'image_width': track['album']['images'][0]['width'],
                'artist': track['artists'][0]['name'],
                'song_url': f"http://open.spotify.com/track/{track['id']}"
            }
        happy_songs.append(track_info)
    random.shuffle(happy_songs)
    happy_songs = happy_songs[:8]
    response = get_songs_for_category("malayalam songs that can fix my sad mood", 4)
    tracks = response["tracks"]["items"]
    sad_songs = []
    for track in tracks:
        track_info = {
                'name': track['name'],
                'image_url': track['album']['images'][0]['url'],
                'image_height': track['album']['images'][0]['height'],
                'image_width': track['album']['images'][0]['width'],
                'artist': track['artists'][0]['name'],
                'song_url': f"http://open.spotify.com/track/{track['id']}"
        }
        sad_songs.append(track_info)
    random.shuffle(sad_songs)
    sad_songs = sad_songs[:8]

    response = get_songs_for_category("malayalam songs that can fix my surprised mood", 8)
    tracks = response["tracks"]["items"]
    surprised_songs = []
    for track in tracks:
        track_info = {
                'name': track['name'],
                'image_url': track['album']['images'][0]['url'],
                'image_height': track['album']['images'][0]['height'],
                'image_width': track['album']['images'][0]['width'],
                'artist': track['artists'][0]['name'],
                'song_url': f"http://open.spotify.com/track/{track['id']}"

        }
        surprised_songs.append(track_info)
    random.shuffle(surprised_songs)
    surprised_songs = surprised_songs[:8]
    response = get_songs_for_category("malayalam fearful songs", 8)
    tracks = response["tracks"]["items"]
    fear_songs = []
    for track in tracks:
        track_info = {
                'name': track['name'],
                'image_url': track['album']['images'][0]['url'],
                'image_height': track['album']['images'][0]['height'],
                'image_width': track['album']['images'][0]['width'],
                'song_url': f"http://open.spotify.com/track/{track['id']}",
                'artist': track['artists'][0]['name']
        }
        fear_songs.append(track_info)
    random.shuffle(fear_songs)
    fear_songs = fear_songs[:4]
    return render_template('categories.html', happy_songs=happy_songs, surprised_songs=surprised_songs, sad_songs=sad_songs, fear_songs=fear_songs, access_token=get_token())

@app.route('/user_playlist')
def user_playlist():
    playlist = Playlist.query.all()
    return render_template('user_playlist.html', playlist=playlist)

@app.route('/search', methods=['POST', 'GET'])
def search():
    songs = []
    search_term = "Search for songs"
    if request.method == 'POST':
        search_term = request.form.get('searchTerm')
        response = get_songs_for_category(f"{search_term} songs", 32)
        
        tracks = response["tracks"]["items"]
        for track in tracks:
            track_info = {
            'name': track['name'],
            'image_url': track['album']['images'][0]['url'],
            'image_height': track['album']['images'][0]['height'],
            'image_width': track['album']['images'][0]['width'],
            'duration': track['duration_ms'],
            'song_url': f"http://open.spotify.com/track/{track['id']}",
            'artist': track['artists'][0]['name'],
            }
            songs.append(track_info)
    random.shuffle(songs)
    return render_template('search.html', songs=songs, search_term=search_term)

@app.route('/history')
def history():
    emotions = Emotion.query.all()
    return render_template('history.html', emotions=emotions)
    
@app.route('/detect')
def detect():
    print("SERVER STARTED")
    return render_template('detect.html')

@app.route('/play')
def play():
    uri = request.args.get('uri')
    encoded_uri = quote(uri, safe='')
    spotify_oembed_url = f"https://open.spotify.com/oembed?url={encoded_uri}"
    try:
        response = get(spotify_oembed_url)

        if response.status_code == 200:
            data = response.json()
            embed_html = data['html']
            return jsonify({'embed_html': embed_html}), 200
        else:
            return jsonify({'error': 'Failed to fetch embed HTML'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# End Routes

# Socket Connection
@socketio.on('connect')
def test_connect():
    print("SOCKET CONNECTED")


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))

# End Socket Connection

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True)