#!/usr/bin/env python3
"""
Google OAuth Setup for Clean Up Bros
Run this once to get OAuth tokens for Gmail, Sheets, Drive, Calendar access
"""

import os
import json
import webbrowser
import http.server
import socketserver
import urllib.parse
import urllib.request
from pathlib import Path

# Load environment variables from ~/.clawdbot/.env
def load_env():
    env_file = Path.home() / ".clawdbot" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))

load_env()

# OAuth Config - NEVER hardcode credentials!
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET")
    print("Add them to ~/.clawdbot/.env")
    exit(1)

REDIRECT_URI = "http://localhost:8080/"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/calendar",
]

TOKEN_FILE = os.path.expanduser("~/.clawdbot/google-oauth-tokens.json")

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        if 'code' in params:
            code = params['code'][0]

            # Exchange code for tokens
            data = urllib.parse.urlencode({
                'code': code,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'
            }).encode()

            req = urllib.request.Request(
                'https://oauth2.googleapis.com/token',
                data=data,
                method='POST'
            )

            try:
                with urllib.request.urlopen(req) as response:
                    tokens = json.loads(response.read().decode())

                    # Save tokens
                    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
                    with open(TOKEN_FILE, 'w') as f:
                        json.dump(tokens, f, indent=2)
                    os.chmod(TOKEN_FILE, 0o600)

                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"<h1>Success!</h1><p>Tokens saved. You can close this window.</p>")
                    print(f"\nTokens saved to {TOKEN_FILE}")
                    print(f"Refresh token: {tokens.get('refresh_token', 'N/A')[:20]}...")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No code received")

def main():
    # Build auth URL
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent'
    })

    print("Opening browser for Google OAuth...")
    print(f"URL: {auth_url}")
    webbrowser.open(auth_url)

    # Start local server to receive callback
    with socketserver.TCPServer(("", 8080), OAuthHandler) as httpd:
        print("\nWaiting for OAuth callback on http://localhost:8080...")
        httpd.handle_request()

if __name__ == "__main__":
    main()
