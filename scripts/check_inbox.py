#!/usr/bin/env python3
"""
Check Gmail Inbox — List unread emails
Usage: python3 ~/Desktop/🦀/scripts/check_inbox.py
       python3 ~/Desktop/🦀/scripts/check_inbox.py 20  (show 20 messages)
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

def load_env():
    env_file = Path.home() / ".clawdbot" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))

def get_token():
    token_file = Path.home() / ".clawdbot" / "google-oauth-tokens.json"
    if not token_file.exists():
        return None
    with open(token_file) as f:
        tokens = json.load(f)
    return tokens.get('access_token')

load_env()

def check_inbox(limit=10):
    token = get_token()
    if not token:
        print("❌ No Google OAuth token. Run google-oauth-setup.py first.")
        return

    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q=is:unread&maxResults={limit}"
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read().decode())
            messages = data.get('messages', [])
            print(f"\n📧 Unread emails: {data.get('resultSizeEstimate', 0)}\n")

            for msg in messages[:limit]:
                msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}?format=metadata&metadataHeaders=From&metadataHeaders=Subject"
                msg_req = urllib.request.Request(msg_url, headers=headers)
                with urllib.request.urlopen(msg_req) as mr:
                    msg_data = json.loads(mr.read().decode())
                    hdrs = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}
                    frm = hdrs.get('From', 'Unknown')
                    subj = hdrs.get('Subject', '(no subject)')
                    print(f"  • {frm[:40]:40s} | {subj[:50]}")
    except Exception as e:
        print(f"❌ Gmail error: {e}")

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    check_inbox(limit)
