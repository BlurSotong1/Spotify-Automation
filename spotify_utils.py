import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import redirect, url_for, session
from credentials import keys

TOKEN_INFO = 'token_info'


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=keys.CLIENT_ID,
        client_secret=keys.CLIENT_SECRET,
        redirect_uri=url_for('redirect_page', _external=True),
        scope='user-library-read,playlist-read-private,playlist-modify-public,playlist-modify-private',
    )


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


def save_discover_weekly(session):
    source_playlist_id, collated_playlist_id = None, None

    source_playlist = 'Discover Weekly'
    destination_playlist = r'collated'

    try:
        token_info = get_token()
    except:
        print("user not logged in!")
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user = sp.current_user()

    current_playlists = sp.current_user_playlists()['items']

    for playlist in current_playlists:
        if playlist['name'] == source_playlist:
            print(playlist['name'])
            source_playlist_id = playlist['id']
        if playlist['name'] == destination_playlist:
            collated_playlist_id = playlist['id']  # used later to add to this playlist
            print('the found playlist: {} id is: {}'.format(playlist['name'], collated_playlist_id))

    if not source_playlist_id:
        return 'source playlist is not found!'

    if not collated_playlist_id:
        temp = sp.user_playlist_create(
            user['id'],
            name=destination_playlist,
            public=True,
            description="Saving all weekly playlists!"
        )
        collated_playlist_id = temp['id']
        print('the created playlist id is: {}'.format(collated_playlist_id))

    source_playlist = sp.playlist_items(source_playlist_id, limit=50)

    song_uris = []

    for song in source_playlist['items']:
        song_uris.append(song['track']['uri'])

    spilt_tasks = (len(song_uris) + 4) // 5  # Calculate number of chunks needed
    for i in range(spilt_tasks):
        j = i * 5
        k = min(j + 5, len(song_uris))  # Ensure k does not exceed the length of song_uris
        split_tasks_add = song_uris[j:k]
        sp.playlist_add_items(collated_playlist_id, split_tasks_add)
        print(i, "   ", j, "   ", k)

    # Add any remaining songs (less than 5) to the playlist
    remaining_songs = song_uris[k:]
    if remaining_songs:
        sp.playlist_add_items(collated_playlist_id, remaining_songs)

    return "successfully added!"
