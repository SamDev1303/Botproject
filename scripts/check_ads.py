import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

TOKEN_FILE = Path.home() / "clawd" / "credentials" / "google_token.json"
CLIENT_ID = "789855447864-npndu9bcoebs9ogvcipagu40vntianms.apps.googleusercontent.com"
CLIENT_SECRET = "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"
DEVELOPER_TOKEN = "plEjzTYXG7HgEbc9TkVt-Q"
CUSTOMER_ID = "1164039680"

def load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)

def refresh_token(tokens):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': tokens['refresh_token'],
        'grant_type': 'refresh_token'
    }
    req = urllib.request.Request(
        'https://oauth2.googleapis.com/token',
        data=urllib.parse.urlencode(data).encode(),
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    with urllib.request.urlopen(req) as response:
        new_tokens = json.loads(response.read().decode())
        tokens.update(new_tokens)
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        return tokens['access_token']

def check_ads():
    tokens = load_tokens()
    access_token = tokens['access_token']
    
    # Simple GAQL query to list campaigns
    query = "SELECT campaign.id, campaign.name, campaign.status FROM campaign"
    url = f"https://googleads.googleapis.com/v19/customers/{CUSTOMER_ID}/googleAds:search"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'developer-token': DEVELOPER_TOKEN,
        'login-customer-id': CUSTOMER_ID,
        'Content-Type': 'application/json'
    }
    
    data = json.dumps({'query': query}).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            if 'results' in result:
                print(json.dumps(result['results'], indent=2))
            else:
                print("No campaigns found.")
    except Exception as e:
        if hasattr(e, 'code') and e.code == 401:
            access_token = refresh_token(tokens)
            headers['Authorization'] = f'Bearer {access_token}'
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                print(json.dumps(result.get('results', []), indent=2))
        else:
            print(f"Error: {e}")
            if hasattr(e, 'read'):
                print(e.read().decode())

if __name__ == "__main__":
    check_ads()
