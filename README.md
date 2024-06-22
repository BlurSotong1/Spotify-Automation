# Spotify-Automation
Automation of adding spotify's weekly playlist into a separate playlist

This Flask application allows users to automatically save their "Discover Weekly" Spotify playlist into a separate "collated" playlist. The application uses the Spotify API to handle user authentication, retrieve playlists, and manage playlist contents.

Features
OAuth 2.0 Authentication: Securely authenticate users with Spotify.
Playlist Management: Retrieve and create playlists.
Track Management: Add tracks from the "Discover Weekly" playlist to a designated "collated" playlist.
Requirements
Python 3.6+
Flask
Spotipy
Setup
1. Clone the repository
bash
Copy code
git clone <repository_url>
cd <repository_folder>
2. Install the dependencies
bash
Copy code
pip install -r requirements.txt
3. Configure Spotify Credentials
Create a file named credentials.py and add your Spotify API credentials.

python
Copy code
keys = {
    'CLIENT_ID': 'your_spotify_client_id',
    'CLIENT_SECRET': 'your_spotify_client_secret',
    'SECRET_KEY': 'your_flask_secret_key'
}
4. Run the Application
bash
Copy code
python app.py
The application will start running on http://127.0.0.1:8080.

Usage
Login: Navigate to http://127.0.0.1:8080 in your browser. You will be redirected to Spotify for authentication.
Authorize: Authorize the application to access your Spotify account.
Save Playlist: The application will automatically save tracks from your "Discover Weekly" playlist to the "collated" playlist.
Routes
/: Redirects to the Spotify login page.
/redirect: Handles the redirect from Spotify after authentication and exchanges the authorization code for an access token.
/saveDiscoverWeekly: Saves the tracks from the "Discover Weekly" playlist to the "collated" playlist.

Code Explanation
Flask Application
Login Route (/): Redirects the user to Spotify's authorization URL.
Redirect Route (/redirect): Handles Spotify's callback, exchanges the authorization code for an access token, and saves it in the session.
Save Discover Weekly Route (/saveDiscoverWeekly): Retrieves the user's playlists, finds the "Discover Weekly" and "collated" playlists, and adds tracks from the former to the latter.
Helper Functions
get_token(): Retrieves the access token from the session and refreshes it if necessary.
create_spotify_oauth(): Creates an instance of SpotifyOAuth with the necessary credentials and scopes.
Example Code
python
Copy code
from flask import Flask, request, redirect, url_for, session
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from credentials import keys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Spotify Cookie'
app.secret_key = keys.SECRET_KEY
TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('save_discover_weekly', _external=True))

@app.route('/saveDiscoverWeekly')
def save_discover_weekly():
    source_playlist_id, collated_playlist_id = None, None
    source_playlist = 'Discover Weekly'
    destination_playlist = 'collated'

    try:
        token_info = get_token()
    except:
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user = sp.current_user()
    current_playlists = sp.current_user_playlists()['items']

    for playlist in current_playlists:
        if playlist['name'] == source_playlist:
            source_playlist_id = playlist['id']
        if playlist['name'] == destination_playlist:
            collated_playlist_id = playlist['id']

    if not source_playlist_id:
        return 'source playlist not found!'

    if not collated_playlist_id:
        temp = sp.user_playlist_create(
            user['id'],
            name=destination_playlist,
            public=True,
            description="Saving all weekly playlists!"
        )
        collated_playlist_id = temp['id']

    source_playlist = sp.playlist_items(source_playlist_id, limit=50)
    song_uris = [song['track']['uri'] for song in source_playlist['items']]
    
    for i in range(0, len(song_uris), 5):
        sp.playlist_add_items(collated_playlist_id, song_uris[i:i+5])

    return "successfully added!"

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('/'))
    now = time.time()
    is_expired = token_info['expires_at'] - now < 180

    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=keys.CLIENT_ID,
        client_secret=keys.CLIENT_SECRET,
        redirect_uri=url_for('redirect_page', _external=True),
        scope='user-library-read,playlist-read-private,playlist-modify-public,playlist-modify-private',
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
Troubleshooting
Ensure your Spotify API credentials are correctly set in credentials.py.
Verify the redirect URI in the Spotify Developer Dashboard matches the one defined in the application.
License
This project is licensed under the MIT License. See the LICENSE file for details.
