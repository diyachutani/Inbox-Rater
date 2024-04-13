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
    number_spam_emails = 0  # Counter for spam emails
    number_unread_emails = 0 # Counter for unread emails
    number_read_emails = 0 # Counter for read emails
    carbon_emissions = 0 # Define initial carbon emissions as 0
    spam_senders = {}  # Dictionary to store sender email addresses in the spam and their email freqeuncy
    unread_senders = {} # Dictionary to store sender email addresses in the unread mailbox and their email freqeuncy

    # Process a limited number of emails for the demo
    for message in messages[:10]:  # Limit to first 10 for demo purposes
        read = True
        message_id = message['id']
        message_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?fields=sizeEstimate'
        message_response = requests.get(message_url, headers=headers)
        if message_response.status_code == 200:
            message_data = message_response.json()
            # Finds the sender email adress from the header
            snippet = message_data.get('snippet', '')
            headers = message_data.get('payload', {}).get('headers', [])
            sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
            
            # Finds the size of the email and adds to the total size of all the emails
            email_size = message_data.get('sizeEstimate', 0)
            total_size += email_size

            label_ids = message_data.get('labelIds', [])
            if 'SPAM' in label_ids:  # Check if the message is labeled as spam
                number_spam_emails += 1
                # Append the sender to the list of spam senders 
                if sender:
                    spam_senders[sender] = spam_senders.get(sender, 0) + 1
                
            if 'UNREAD' in label_ids:  # Check if the message is unread
                number_unread_emails += 1
                read = False
                # Append the sender to the list of senders in the unread mailbox 
                if sender:
                    unread_senders[sender] = unread_senders.get(sender, 0) + 1
            else:
                number_read_emails += 1
  

        carbon_emissions += calculate_carbon_footprint(total_size, read, email_size)
    # Calculates CO2e due to spam mail, 0.03 g of CO2 per spam email. This value is taken from: https://carbonliteracy.com/the-carbon-cost-of-an-email/
    CO2e_spam = 0.03 * number_spam_emails
    
    CO2e_read = carbon_emissions[0]
    CO2e_unread = carbon_emissions[1]

    top_3_spam_senders, \
    top_3_unread_senders, \
    percent_top_spam, \
    percent_second_spam, \
    percent_third_spam, \
    percent_top_unread, \
    percent_second_unread, \
    percent_third_unread = sort_senders(spam_senders, unread_senders)
    
    return jsonify({
        'total_emails': total_emails,
        'total_size': total_size,
        'number_unread_emails': number_unread_emails,
        'number_read_emails': number_read_emails,
        'CO2e_read_emails_g':CO2e_read,
        'CO2e_unread_emails_g':CO2e_unread,
        'CO2e_spam_g': CO2e_spam,
        'top_spam_address': top_3_spam_senders[0][0],
        'top_percent_spam_address': percent_top_spam,
        'second_spam_address': top_3_spam_senders[1][0],
        'second_percent_spam_address': percent_second_spam,
        'third_spam_address': top_3_spam_senders[2][0],
        'third_percent_spam_address': percent_third_spam,
        'top_unread_address': top_3_unread_senders[0][0],
        'top_percent_unread_address': percent_top_unread,
        'second_unread_address': top_3_unread_senders[1][0],
        'second_percent_unread_address': percent_second_unread,
        'third_unread_address': top_3_unread_senders[2][0],
        'third_percent_unread_address': percent_third_unread,
    })

def calculate_carbon_footprint(read, email_size):
    # Defines boundary of small email as 100000 bytes (100 KB)
    small_email = 100000
    
    # Add 0.3 g of CO2e if file size is small and 17 g of CO2e if file size is large
    # These values taken from: https://carbonliteracy.com/the-carbon-cost-of-an-email/
    if read == True:
        if email_size < small_email:
            CO2e_read = 0.3
            CO2e_unread = 0
        elif email_size > small_email:
            CO2e_read = 17
            CO2e_unread = 0
    elif read == False:
        if email_size < small_email:
            CO2e_unread = 0.3
            CO2e_read = 0
        elif email_size < small_email:
            CO2e_unread = 17
            CO2e_read = 0

    return CO2e_read, CO2e_unread

def sort_senders(spam_senders, unread_senders):
    
    # Sort the email adresses in the spam mailbox by the number of emails sent
    sorted_spam_senders = sorted(spam_senders.items(), key=lambda x: x[1], reverse=True)
    # Get the top 3 most frequent email addresses in the spam mail box
    top_3_spam_senders = sorted_spam_senders[:3]
    
    # Calculate the percentage of emails that the top 3 addresses take up within the spam folder
    total_spam = len(sorted_spam_senders)
    percent_top_spam = top_3_spam_senders[0][1] / total_spam
    percent_second_spam = top_3_spam_senders[1][1] / total_spam
    percent_third_spam = top_3_spam_senders[2][1] / total_spam
    
    # Sort the email adresses in the unread mailbox by the number of emails sent
    sorted_unread_senders = sorted(unread_senders.items(), key=lambda x: x[1], reverse=True)
    # Get the top 3 most frequent email addresses in the unread mail box
    top_3_unread_senders = sorted_unread_senders[:3]
    
    # Calculate the percentage of emails that the top 3 addresses take up within the unread folder
    total_unread = len(sorted_unread_senders)
    percent_top_unread = top_3_unread_senders[0][0] / total_unread
    percent_second_unread = top_3_unread_senders[0][1] / total_unread
    percent_third_unread = top_3_unread_senders[0][2] / total_unread
    
    return  top_3_spam_senders, \
            top_3_unread_senders, \
            percent_top_spam, \
            percent_second_spam, \
            percent_third_spam, \
            percent_top_unread, \
            percent_second_unread, \
            percent_third_unread
    

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