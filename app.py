import time
from flask import Flask, request, redirect, url_for, session
from spotify_utils import create_spotify_oauth, get_token, save_discover_weekly
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
    return redirect(url_for('save_discover_weekly_route', _external=True))


@app.route('/saveDiscoverWeekly')
def save_discover_weekly_route():
    return save_discover_weekly(session)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
