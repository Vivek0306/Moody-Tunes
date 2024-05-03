from flask import Flask, render_template, session, jsonify, Response, request
from flask_socketio import SocketIO, emit
import json
import os
import random
import base64
from requests import post, get
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


app = Flask(__name__)
socketio = SocketIO(app)

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
    query = f"?q={category}&type=track&limit={24}"
    url = url + query
    result = get(url, headers=headers)
    json_result = json.loads(result.content)

    return json_result


# Routes
@app.route('/')
def index():
    response = get_songs_for_category("happy songs", 8)
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
    return render_template('index.html', track_data=track_data)


@app.route('/fetch_songs')
def fetch_songs():
    emotion = request.args.get('emotion')
    response = get_songs_for_category(
        f"songs that are perfect for {emotion} mood", 12)
    print("Fetching songs for EMOTION..............",
          request.args.get('emotion'))
    tracks = response["tracks"]["items"]
    total = response["tracks"]["total"]
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


@app.route('/playlists')
def playlists():
    response = get_songs_for_category("happy songs", 4)
    tracks = response["tracks"]["items"]
    happy_songs = []
    for track in tracks:
        track_info = {
                'name': track['name'],
                'image_url': track['album']['images'][0]['url'],
                'image_height': track['album']['images'][0]['height'],
                'image_width': track['album']['images'][0]['width'],
                'song_url': f"http://open.spotify.com/track/{track['id']}"
            }
        happy_songs.append(track_info)
    random.shuffle(happy_songs)
    happy_songs = happy_songs[:4]
    response = get_songs_for_category("songs that can fix my sad mood", 4)
    tracks = response["tracks"]["items"]
    sad_songs = []
    for track in tracks:
        track_info = {
                'name': track['name'],
                'image_url': track['album']['images'][0]['url'],
                'image_height': track['album']['images'][0]['height'],
                'image_width': track['album']['images'][0]['width'],
                'song_url': f"http://open.spotify.com/track/{track['id']}"
        }
        sad_songs.append(track_info)
    random.shuffle(sad_songs)
    sad_songs = sad_songs[:4]

    response = get_songs_for_category("songs that can fix my surprised mood", 4)
    tracks = response["tracks"]["items"]
    surprised_songs = []
    for track in tracks:
        track_info = {
                'name': track['name'],
                'image_url': track['album']['images'][0]['url'],
                'image_height': track['album']['images'][0]['height'],
                'image_width': track['album']['images'][0]['width'],
                'song_url': f"http://open.spotify.com/track/{track['id']}"

        }
        surprised_songs.append(track_info)
    random.shuffle(surprised_songs)
    surprised_songs = surprised_songs[:4]
    response = get_songs_for_category("fearful songs", 4)
    tracks = response["tracks"]["items"]
    fear_songs = []
    for track in tracks:
        track_info = {
                'name': track['name'],
                'image_url': track['album']['images'][0]['url'],
                'image_height': track['album']['images'][0]['height'],
                'image_width': track['album']['images'][0]['width'],
                'song_url': f"http://open.spotify.com/track/{track['id']}"

        }
        fear_songs.append(track_info)
    random.shuffle(fear_songs)
    fear_songs = fear_songs[:4]
    return render_template('playlists.html', happy_songs=happy_songs, surprised_songs=surprised_songs, sad_songs=sad_songs, fear_songs=fear_songs, access_token=get_token())

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

@socketio.on('connect')
def test_connect():
    print("SOCKET CONNECTED")


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))


if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True)
