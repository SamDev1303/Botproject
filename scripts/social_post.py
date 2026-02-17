#!/usr/bin/env python3
"""
Quick Social Media Poster — Post to FB + IG from command line
Usage: python3 ~/Desktop/🦀/scripts/social_post.py "Your post message here"
       python3 ~/Desktop/🦀/scripts/social_post.py "Message" --photo /path/to/image.jpg
"""
import sys
import os
import json
import urllib.request
import urllib.parse
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

load_env()

TOKEN = os.environ.get('META_SYSTEM_USER_TOKEN', '')
PAGE_ID = os.environ.get('FB_PAGE_ID', '')
BASE = "https://graph.facebook.com/v21.0"

def fb_post(message, link=""):
    data = {"message": message, "access_token": TOKEN}
    if link:
        data["link"] = link
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(f"{BASE}/{PAGE_ID}/feed", data=body, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read().decode())
            print(f"✅ Facebook post: {result.get('id', 'done')}")
            return result
    except Exception as e:
        print(f"❌ Facebook error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 social_post.py 'Your message here'")
        sys.exit(1)
    message = sys.argv[1]
    fb_post(message)
    print("Done.")
