import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, session, url_for
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    code = request.args.get('code')
    sp_oauth = create_spotify_oauth()
    token_info = sp_oauth.get_access_token(code)
    session['TOKEN_INFO'] = token_info
    return redirect(url_for('search_and_play'))

@app.route('/searchAndPlay')
def search_and_play():
    try:
        token_info = get_token()
        sp = spotipy.Spotify(auth=token_info['access_token'])
        mood = request.args.get('mood')
        if mood == 'sad':
            # Example: Search for a sad song and play the first result
            results = sp.search(q='mood:sad', limit=1, type='track')
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                sp.start_playback(uris=[track_uri])
                return f"Playing a sad song: {results['tracks']['items'][0]['name']}"
            else:
                return "No sad songs found."
        else:
            return "No mood specified or unsupported mood."
    except:
        print("User not logged in.")
        return redirect('/')

def get_token():
    token_info = session.get('TOKEN_INFO', None)
    if not token_info:
        return None
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id='your_client_id',
        client_secret='your_client_secret',
        redirect_uri=url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private'
    )

if __name__ == "__main__":
    app.run(debug=True)
