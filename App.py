from flask import Flask, request, redirect, session
import requests

app = Flask(__name__)

# Secure secret key for session management. This should be a complex, hard-to-guess string in production.
app.secret_key = 'a_very_secure_secret_key_change_this_in_production'

# Replace these with your client details and desired scopes
CLIENT_ID = '458998972467-80d0l7fsn038uurfrnc6tcnlu8qospmd.apps.googleusercontent.com'
CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:8080/callback'
SCOPE = 'https://mail.google.com/'  # Adjust based on the provider and needed permissions
AUTHORIZATION_BASE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'

@app.route('/')
def index():
    return '<a href="/login">Log in with Email Provider</a>'

@app.route('/login')
def login():
    authorization_url = f"{AUTHORIZATION_BASE_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&access_type=offline"
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(TOKEN_URL, data=token_data)
    if response.status_code == 200:
        session['access_token'] = response.json().get('access_token')
        session['refresh_token'] = response.json().get('refresh_token', None)  # Store refresh token if available
        return 'Access token stored in session. You are now logged in.'
    else:
        return 'Failed to retrieve access token', 500

@app.route('/logout')
def logout():
    session.pop('access_token', None)
    session.pop('refresh_token', None)
    return 'You have been logged out.'

if __name__ == '__main__':
    app.run(port=8080, debug=True)
