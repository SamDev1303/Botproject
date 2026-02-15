#!/usr/bin/env python3
"""
Google OAuth Setup - Authorizes full Google access for Clawdbot including Ads

Run this once to authorize:
    python google_oauth_setup_ads.py

This will:
1. Open a browser for you to log in to Google
2. Grant permissions for Gmail, Calendar, Drive, Sheets, and Google Ads
3. Save the tokens to ~/clawd/credentials/google_token.json
"""
import os
import json
import webbrowser
import http.server
import urllib.parse
import urllib.request
from pathlib import Path

# Configuration
CLIENT_ID = "789855447864-npndu9bcoebs9ogvcipagu40vntianms.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8080/"
TOKEN_FILE = Path.home() / "clawd" / "credentials" / "google_token.json"

# Scopes for full access including Google Ads
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",      # Read/send/delete emails
    "https://www.googleapis.com/auth/gmail.send",        # Send emails
    "https://www.googleapis.com/auth/calendar",          # Full calendar access
    "https://www.googleapis.com/auth/drive",             # Full drive access
    "https://www.googleapis.com/auth/spreadsheets",      # Full sheets access
    "https://www.googleapis.com/auth/contacts",          # Contacts access
    "https://www.googleapis.com/auth/adwords",           # Google Ads access
]

authorization_code = None

class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        if 'code' in params:
            authorization_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>Authorization Successful!</h1>
                <p>You can close this window now.</p>
                <p>Clawdbot now has access to your Google account including Google Ads.</p>
                </body></html>
            """)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization failed. Please try again.")

    def log_message(self, format, *args):
        pass  # Suppress logging

def get_authorization_url():
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

def exchange_code_for_tokens(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }

    req = urllib.request.Request(
        'https://oauth2.googleapis.com/token',
        data=urllib.parse.urlencode(data).encode(),
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def save_tokens(tokens):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)
    print(f"Tokens saved to: {TOKEN_FILE}")

def main():
    global authorization_code

    print("=" * 60)
    print("GOOGLE OAUTH SETUP (ADS) FOR CLAWDBOT")
    print("=" * 60)
    
    # Start local server
    server = http.server.HTTPServer(('localhost', 8080), OAuthHandler)

    # Authorization URL
    auth_url = get_authorization_url()
    print("Authorization URL generated.")
    print(f"\nURL: {auth_url}\n")
    
    # Wait for callback
    print("Waiting for authorization code from browser...")
    while authorization_code is None:
        server.handle_request()

    server.server_close()

    # Exchange code for tokens
    print("\nExchanging code for tokens...")
    tokens = exchange_code_for_tokens(authorization_code)

    # Save tokens
    save_tokens(tokens)

    print("\nSUCCESS! Google Ads access enabled.")

if __name__ == "__main__":
    main()
