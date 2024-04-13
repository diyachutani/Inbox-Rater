from flask import Flask, request, redirect, session
import requests
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/email-metadata')
def email_metadata():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'Access token is missing. Please log in again.'}), 401
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    # Fetches only the IDs of the messages for simplicity; modify as needed
    messages_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages?fields=messages/id,nextPageToken'
    response = requests.get(messages_url, headers=headers)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch messages'}), response.status_code

    messages = response.json().get('messages', [])
    total_emails = len(messages)
    total_size = 0

    # Process a limited number of emails for the demo
    for message in messages[:10]:  # Limit to first 10 for demo purposes
        message_id = message['id']
        message_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?fields=sizeEstimate'
        message_response = requests.get(message_url, headers=headers)
        if message_response.status_code == 200:
            message_data = message_response.json()
            total_size += message_data.get('sizeEstimate', 0)

    carbon_emissions = calculate_carbon_footprint(total_size)
    return jsonify({
        'total_emails': total_emails,
        'total_size': total_size,
        'carbon_emissions_kg': carbon_emissions
    })


def calculate_carbon_footprint(total_size):
    # Example: Assume 1 GB of email data emits 32 kg of CO2 per year
    size_in_gb = total_size / (1024**3)  # Convert bytes to gigabytes
    carbon_emissions = size_in_gb * 32  # example coefficient
    return carbon_emissions


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
