# Complete API Keys Reference
## Hafsah Nuzhat - All Projects

> **Last Updated:** 2026-02-03 02:50 AEST
> **Total APIs:** 100+ environment variables
> **OAuth Scopes:** 11 authorized
> **Health Status:** Tested & Working

---

## Quick Test Commands

```bash
# Test all APIs
python3 ~/Desktop/🦀/scripts/api_health_check.py

# Test Google services only
python3 ~/Desktop/🦀/scripts/test_google_services.py

# Re-authorize Google OAuth (if tokens expire)
python3 ~/Desktop/🦀/google-oauth-setup.py
```

---

## HOW OAUTH LOCALHOST WORKS

### The OAuth Flow (Port 8080)

When you run `google-oauth-setup.py`, here's what happens:

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Script starts a LOCAL web server on PORT 8080                │
│    Server listens at: http://localhost:8080/                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Browser opens Google's OAuth consent page                    │
│    URL: accounts.google.com/o/oauth2/v2/auth?...                │
│    You sign in and grant permissions                            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Google redirects back to localhost:8080 with AUTH CODE       │
│    URL: http://localhost:8080/?code=4/0ASc3gC...&scope=...      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Script exchanges code for ACCESS TOKEN + REFRESH TOKEN       │
│    POST to: oauth2.googleapis.com/token                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Tokens saved to: ~/.clawdbot/google-oauth-tokens.json        │
│    - access_token (expires in 1 hour)                           │
│    - refresh_token (long-lived, use to get new access tokens)   │
└─────────────────────────────────────────────────────────────────┘
```

### Port 8080 Details

| Setting | Value |
|---------|-------|
| **Port** | 8080 |
| **Protocol** | HTTP (not HTTPS) |
| **Bind Address** | localhost (127.0.0.1) |
| **Redirect URI** | `http://localhost:8080/` |
| **Server Type** | Python socketserver.TCPServer |

**If Port 8080 is busy:**
```bash
# Find what's using port 8080
lsof -i :8080

# Kill the process
kill <PID>

# Or kill all on port 8080
lsof -i :8080 | grep -v COMMAND | awk '{print $2}' | xargs kill
```

### Token File Location

```
~/.clawdbot/google-oauth-tokens.json
```

**Contents:**
```json
{
  "access_token": "ya29.a0...",     // Expires in 1 hour
  "expires_in": 3599,
  "refresh_token": "1//0g...",      // Long-lived, use to refresh
  "scope": "https://www.googleapis.com/auth/youtube ...",
  "token_type": "Bearer"
}
```

### How to Refresh Tokens (Code)

```python
import os
import json
import urllib.request
import urllib.parse

# Load current tokens
with open(os.path.expanduser('~/.clawdbot/google-oauth-tokens.json')) as f:
    tokens = json.load(f)

# Refresh the access token
data = urllib.parse.urlencode({
    'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
    'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
    'refresh_token': tokens['refresh_token'],
    'grant_type': 'refresh_token'
}).encode()

req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST')
with urllib.request.urlopen(req) as resp:
    new_tokens = json.loads(resp.read().decode())
    print(f"New access token: {new_tokens['access_token'][:20]}...")
```

---

## CURRENTLY AUTHORIZED OAUTH SCOPES (11 Total)

| Scope | Service | Access Level |
|-------|---------|--------------|
| `gmail.send` | Gmail | Send emails |
| `gmail.readonly` | Gmail | Read emails |
| `gmail.modify` | Gmail | Mark read/unread, labels |
| `spreadsheets` | Google Sheets | Full access |
| `drive` | Google Drive | Full access |
| `calendar` | Google Calendar | Full access |
| `adwords` | Google Ads | API access |
| `youtube` | YouTube | Manage account |
| `youtube.readonly` | YouTube | View account |
| `youtube.upload` | YouTube | Upload videos |
| `youtube.force-ssl` | YouTube | Manage content |

---

## 1. GOOGLE SERVICES

### OAuth Credentials
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `GOOGLE_CLIENT_ID` | OAuth app ID | accounts.google.com |
| `GOOGLE_CLIENT_SECRET` | OAuth app secret | accounts.google.com |
| `GOOGLE_REFRESH_TOKEN` | Token refresh | oauth2.googleapis.com |

### Token File
| File | Location | Permissions |
|------|----------|-------------|
| OAuth Tokens | `~/.clawdbot/google-oauth-tokens.json` | 600 (owner only) |
| Environment | `~/.clawdbot/.env` | 600 (owner only) |

### API Keys
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `GOOGLE_API_KEY` | Gemini/AI services | generativelanguage.googleapis.com |
| `GEMINI_API_KEY` | Gemini AI (same) | generativelanguage.googleapis.com |
| `GOOGLE_API_KEY_SECONDARY` | Backup key | - |
| `GOPLACES_API_KEY` | Places API | maps.googleapis.com |
| `NANO_BANANA_PRO_API_KEY` | Custom app | - |

### Google Ads
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Ads API access | googleads.googleapis.com/v18 |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Customer account | googleads.googleapis.com |
| `GOOGLE_ADS_CLIENT_SECRET` | Ads OAuth | - |

### Google Cloud / Compute
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `GOOGLE_PROJECT_ID` | Cloud project | console.cloud.google.com |
| `GOOGLE_COMPUTE_KEY` | Compute Engine | compute.googleapis.com |
| `GOOGLE_COMPUTE_ENGINE_EMAIL` | Service account | - |
| `GOOGLE_SERVICE_ACCOUNT_EMAIL` | Service account | - |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | Service key | - |
| `GOOGLE_SERVICE_ACCOUNT_NAME` | Account name | - |
| `GOOGLE_SERVICE_ACCOUNT_UNIQUE_ID` | Unique ID | - |

### Google Sheets
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `GOOGLE_SHEETS_ID` | Spreadsheet ID | sheets.googleapis.com |

### Gmail
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `GMAIL_ADDRESS` | Email address | gmail.googleapis.com |
| `GMAIL_APP_PASSWORD` | App password | smtp.gmail.com |

#### Usage Script - Google Services
```python
#!/usr/bin/env python3
"""Google Services - Gmail, Calendar, Sheets, Drive"""
import os
import json
import urllib.request
from pathlib import Path

# Load tokens
TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"
with open(TOKEN_FILE) as f:
    tokens = json.load(f)
ACCESS_TOKEN = tokens['access_token']

def google_request(url):
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Gmail - List messages
messages = google_request('https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=5')
print(f"Gmail: {len(messages.get('messages', []))} messages")

# Calendar - List events
events = google_request('https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=5')
print(f"Calendar: {len(events.get('items', []))} events")

# Drive - List files
files = google_request('https://www.googleapis.com/drive/v3/files?pageSize=5')
print(f"Drive: {len(files.get('files', []))} files")

# Sheets - Get spreadsheet
SHEET_ID = os.environ.get('GOOGLE_SHEETS_ID', '')
if SHEET_ID:
    sheet = google_request(f'https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}')
    print(f"Sheets: {sheet['properties']['title']}")
```

---

## 1B. YOUTUBE API

### OAuth Scopes (Authorized)
| Scope | Purpose | Access |
|-------|---------|--------|
| `youtube` | Manage YouTube account | Full |
| `youtube.readonly` | View account info | Read |
| `youtube.upload` | Upload videos | Write |
| `youtube.force-ssl` | Manage content | Full |

### YouTube API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `youtube.googleapis.com/youtube/v3/channels` | GET | Get channel info |
| `youtube.googleapis.com/youtube/v3/videos` | GET | List/get videos |
| `youtube.googleapis.com/youtube/v3/videos` | POST | Upload video |
| `youtube.googleapis.com/youtube/v3/playlists` | GET | List playlists |
| `youtube.googleapis.com/youtube/v3/subscriptions` | GET | List subscriptions |
| `youtube.googleapis.com/youtube/v3/search` | GET | Search YouTube |
| `youtube.googleapis.com/youtube/v3/comments` | GET | Get comments |
| `youtube.googleapis.com/youtube/v3/commentThreads` | GET | Get comment threads |

#### Usage Script - YouTube
```python
#!/usr/bin/env python3
"""YouTube API - Full Access"""
import os
import json
import urllib.request
import urllib.parse
from pathlib import Path

# Load OAuth tokens
TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"
with open(TOKEN_FILE) as f:
    tokens = json.load(f)
ACCESS_TOKEN = tokens['access_token']

def youtube_request(endpoint, params=None):
    """Make YouTube API request"""
    base_url = f"https://www.googleapis.com/youtube/v3/{endpoint}"
    if params:
        base_url += '?' + urllib.parse.urlencode(params)

    req = urllib.request.Request(base_url, headers={
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Get your channel info
channel = youtube_request('channels', {'part': 'snippet,statistics', 'mine': 'true'})
if channel.get('items'):
    ch = channel['items'][0]
    print(f"Channel: {ch['snippet']['title']}")
    print(f"Subscribers: {ch['statistics'].get('subscriberCount', 'Hidden')}")
    print(f"Views: {ch['statistics']['viewCount']}")
    print(f"Videos: {ch['statistics']['videoCount']}")

# List your videos
videos = youtube_request('search', {
    'part': 'snippet',
    'forMine': 'true',
    'type': 'video',
    'maxResults': 5
})
print(f"\nYour Videos ({len(videos.get('items', []))}):")
for v in videos.get('items', []):
    print(f"  - {v['snippet']['title']}")

# List your playlists
playlists = youtube_request('playlists', {
    'part': 'snippet',
    'mine': 'true',
    'maxResults': 5
})
print(f"\nYour Playlists ({len(playlists.get('items', []))}):")
for p in playlists.get('items', []):
    print(f"  - {p['snippet']['title']}")

# Search YouTube (public)
search = youtube_request('search', {
    'part': 'snippet',
    'q': 'cleaning business tips',
    'type': 'video',
    'maxResults': 3
})
print(f"\nSearch Results:")
for s in search.get('items', []):
    print(f"  - {s['snippet']['title']}")
```

#### Upload Video to YouTube
```python
#!/usr/bin/env python3
"""Upload video to YouTube"""
import os
import json
import urllib.request
from pathlib import Path

TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"
with open(TOKEN_FILE) as f:
    ACCESS_TOKEN = json.load(f)['access_token']

def upload_video(file_path, title, description, tags=None, privacy='private'):
    """
    Upload a video to YouTube
    privacy: 'private', 'unlisted', or 'public'
    """
    # Step 1: Start resumable upload
    metadata = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or [],
            'categoryId': '22'  # People & Blogs
        },
        'status': {
            'privacyStatus': privacy,
            'selfDeclaredMadeForKids': False
        }
    }

    # Initialize upload
    init_url = 'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status'
    req = urllib.request.Request(init_url,
        headers={
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json',
            'X-Upload-Content-Type': 'video/*'
        },
        data=json.dumps(metadata).encode(),
        method='POST'
    )

    with urllib.request.urlopen(req) as resp:
        upload_url = resp.headers.get('Location')

    # Step 2: Upload the file
    with open(file_path, 'rb') as f:
        video_data = f.read()

    upload_req = urllib.request.Request(upload_url,
        headers={
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'video/*',
            'Content-Length': str(len(video_data))
        },
        data=video_data,
        method='PUT'
    )

    with urllib.request.urlopen(upload_req) as resp:
        result = json.loads(resp.read().decode())
        print(f"Uploaded! Video ID: {result['id']}")
        print(f"URL: https://youtube.com/watch?v={result['id']}")
        return result

# Example usage (uncomment to use):
# upload_video(
#     file_path='~/Desktop/my_video.mp4',
#     title='Clean Up Bros - Professional Cleaning',
#     description='See how we transform spaces!',
#     tags=['cleaning', 'sydney', 'professional'],
#     privacy='unlisted'
# )
```

#### Get Video Analytics
```python
#!/usr/bin/env python3
"""Get YouTube video details and statistics"""
import json
import urllib.request
from pathlib import Path

TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"
with open(TOKEN_FILE) as f:
    ACCESS_TOKEN = json.load(f)['access_token']

def get_video_stats(video_id):
    """Get detailed stats for a video"""
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={video_id}'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    })
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        if data.get('items'):
            v = data['items'][0]
            print(f"Title: {v['snippet']['title']}")
            print(f"Views: {v['statistics'].get('viewCount', 0)}")
            print(f"Likes: {v['statistics'].get('likeCount', 0)}")
            print(f"Comments: {v['statistics'].get('commentCount', 0)}")
            print(f"Duration: {v['contentDetails']['duration']}")
            return v
    return None

# Example: get_video_stats('dQw4w9WgXcQ')
```

---

## 2. SQUARE PAYMENTS

| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `SQUARE_ACCESS_TOKEN` | Production token | connect.squareup.com |
| `SQUARE_APPLICATION_ID` | App ID | connect.squareup.com |
| `SQUARE_ENVIRONMENT` | production/sandbox | - |
| `SQUARE_SANDBOX_ACCESS_TOKEN` | Test token | connect.squareupsandbox.com |
| `SQUARE_SANDBOX_APP_ID` | Test app ID | connect.squareupsandbox.com |

#### Usage Script - Square
```python
#!/usr/bin/env python3
"""Square Payments API"""
import os
import json
import urllib.request

TOKEN = os.environ.get('SQUARE_ACCESS_TOKEN', '')
ENV = os.environ.get('SQUARE_ENVIRONMENT', 'production')
BASE = "https://connect.squareup.com" if ENV == "production" else "https://connect.squareupsandbox.com"

def square_request(endpoint):
    req = urllib.request.Request(f"{BASE}{endpoint}", headers={
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# List locations
locations = square_request('/v2/locations')
print(f"Locations: {len(locations.get('locations', []))}")

# List customers
customers = square_request('/v2/customers')
print(f"Customers: {len(customers.get('customers', []))}")

# List invoices
invoices = square_request('/v2/invoices')
print(f"Invoices: {len(invoices.get('invoices', []))}")
```

---

## 3. TWILIO (SMS/VOICE)

| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `TWILIO_ACCOUNT_SID` | Main account | api.twilio.com |
| `TWILIO_AUTH_TOKEN` | Auth token | api.twilio.com |
| `TWILIO_API_KEY_SID` | API key | api.twilio.com |
| `TWILIO_FROM_NUMBER_AU` | AU phone (+614...) | - |
| `TWILIO_AU_AUTH_TOKEN` | AU auth | - |
| `TWILIO_OAUTH_CLIENT_ID` | OAuth client | - |
| `TWILIO_OAUTH_CLIENT_SECRET` | OAuth secret | - |
| `TWILIO_TEST_ACCOUNT_SID` | Test account | - |
| `TWILIO_TEST_AUTH_TOKEN` | Test auth | - |
| `TWILIO_USA_AUTH_TOKEN` | USA auth | - |
| `TWILIO_USA_TEST_AUTH` | USA test | - |

#### Usage Script - Twilio
```python
#!/usr/bin/env python3
"""Twilio SMS/Voice API"""
import os
import base64
import json
import urllib.request
import urllib.parse

SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER_AU', '')

def twilio_request(endpoint, method='GET', data=None):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{SID}{endpoint}"
    credentials = base64.b64encode(f"{SID}:{TOKEN}".encode()).decode()
    req = urllib.request.Request(url, headers={
        'Authorization': f'Basic {credentials}'
    }, method=method)
    if data:
        req.data = urllib.parse.urlencode(data).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Get account info
account = twilio_request('.json')
print(f"Account status: {account.get('status')}")

# Send SMS (uncomment to use)
# sms = twilio_request('/Messages.json', 'POST', {
#     'From': FROM_NUMBER,
#     'To': '+61400000000',
#     'Body': 'Test message from Twilio'
# })
# print(f"SMS SID: {sms.get('sid')}")
```

---

## 4. META / WHATSAPP / FACEBOOK / INSTAGRAM

| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `META_APP_ID` | Meta app ID | graph.facebook.com |
| `META_APP_SECRET` | App secret | graph.facebook.com |
| `META_BUSINESS_ID` | Business account | graph.facebook.com |
| `META_SYSTEM_USER_TOKEN` | Long-lived token | graph.facebook.com |
| `WHATSAPP_BUSINESS_ACCOUNT_ID` | WhatsApp business | graph.facebook.com |
| `WHATSAPP_PHONE_NUMBER_ID` | Phone number ID | graph.facebook.com |
| `WHATSAPP_TEST_PHONE` | Test phone | - |
| `FB_SYSTEM_USER_ID` | System user | - |
| `FB_SYSTEM_USER_NAME` | User name | - |
| `INSTAGRAM_APP_ID` | Instagram app | graph.facebook.com |
| `INSTAGRAM_APP_NAME` | App name | - |
| `INSTAGRAM_APP_SECRET` | App secret | - |

#### Usage Script - WhatsApp
```python
#!/usr/bin/env python3
"""WhatsApp Business API"""
import os
import json
import urllib.request

TOKEN = os.environ.get('META_SYSTEM_USER_TOKEN', '')
PHONE_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')

def whatsapp_request(endpoint, method='GET', data=None):
    url = f"https://graph.facebook.com/v18.0{endpoint}"
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }, method=method)
    if data:
        req.data = json.dumps(data).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Get phone number info
phone_info = whatsapp_request(f'/{PHONE_ID}')
print(f"Phone: {phone_info.get('display_phone_number')}")

# Send WhatsApp message (uncomment to use)
# message = whatsapp_request(f'/{PHONE_ID}/messages', 'POST', {
#     'messaging_product': 'whatsapp',
#     'to': '61400000000',
#     'type': 'text',
#     'text': {'body': 'Hello from WhatsApp API!'}
# })
# print(f"Message ID: {message.get('messages', [{}])[0].get('id')}")
```

---

## 5. AI SERVICES

### OpenAI
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `OPENAI_API_KEY` | Main key | api.openai.com |
| `OPENAI_WHISPER_API_KEY` | Whisper (same) | api.openai.com |

#### Usage Script - OpenAI
```python
#!/usr/bin/env python3
"""OpenAI API - GPT, Whisper, Embeddings"""
import os
import json
import urllib.request

KEY = os.environ.get('OPENAI_API_KEY', '')

def openai_request(endpoint, data):
    req = urllib.request.Request(f"https://api.openai.com/v1{endpoint}",
        headers={
            'Authorization': f'Bearer {KEY}',
            'Content-Type': 'application/json'
        }, method='POST')
    req.data = json.dumps(data).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Chat completion
response = openai_request('/chat/completions', {
    'model': 'gpt-4o-mini',
    'messages': [{'role': 'user', 'content': 'Say hello'}],
    'max_tokens': 50
})
print(response['choices'][0]['message']['content'])

# Embeddings
embeddings = openai_request('/embeddings', {
    'model': 'text-embedding-3-small',
    'input': 'Hello world'
})
print(f"Embedding dimensions: {len(embeddings['data'][0]['embedding'])}")
```

### Anthropic (Claude)
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `ANTHROPIC_API_KEY` | Claude API | api.anthropic.com |
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code | - |

#### Usage Script - Anthropic
```python
#!/usr/bin/env python3
"""Anthropic Claude API"""
import os
import json
import urllib.request

KEY = os.environ.get('ANTHROPIC_API_KEY', '')

def claude_request(messages, model='claude-3-5-sonnet-20241022'):
    req = urllib.request.Request('https://api.anthropic.com/v1/messages',
        headers={
            'x-api-key': KEY,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }, method='POST')
    req.data = json.dumps({
        'model': model,
        'max_tokens': 100,
        'messages': messages
    }).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

response = claude_request([{'role': 'user', 'content': 'Say hello'}])
print(response['content'][0]['text'])
```

### OpenRouter
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `OPENROUTER_API_KEY` | LLM router | openrouter.ai |

#### Usage Script - OpenRouter
```python
#!/usr/bin/env python3
"""OpenRouter - Access 100+ LLMs"""
import os
import json
import urllib.request

KEY = os.environ.get('OPENROUTER_API_KEY', '')

def openrouter_request(messages, model='google/gemini-2.0-flash-001'):
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {KEY}',
            'Content-Type': 'application/json'
        }, method='POST')
    req.data = json.dumps({
        'model': model,
        'messages': messages
    }).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Free models: google/gemini-2.0-flash-001, meta-llama/llama-3.2-3b-instruct:free
response = openrouter_request([{'role': 'user', 'content': 'Hello'}])
print(response['choices'][0]['message']['content'])
```

### Google Gemini
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `GEMINI_API_KEY` | Gemini AI | generativelanguage.googleapis.com |

#### Usage Script - Gemini
```python
#!/usr/bin/env python3
"""Google Gemini API"""
import os
import json
import urllib.request

KEY = os.environ.get('GEMINI_API_KEY', '')
MODEL = 'gemini-2.0-flash'

def gemini_request(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"
    req = urllib.request.Request(url, headers={'Content-Type': 'application/json'}, method='POST')
    req.data = json.dumps({
        'contents': [{'parts': [{'text': prompt}]}]
    }).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

response = gemini_request('Say hello')
print(response['candidates'][0]['content']['parts'][0]['text'])
```

---

## 6. VOICE & MEDIA

### ElevenLabs
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `ELEVENLABS_API_KEY` | Voice generation | api.elevenlabs.io |

#### Usage Script - ElevenLabs
```python
#!/usr/bin/env python3
"""ElevenLabs Voice API"""
import os
import json
import urllib.request

KEY = os.environ.get('ELEVENLABS_API_KEY', '')
VOICE_ID = 'EXAVITQu4vr4xnSDxMaL'  # Default voice

def elevenlabs_tts(text, output_file='output.mp3'):
    req = urllib.request.Request(
        f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}',
        headers={
            'xi-api-key': KEY,
            'Content-Type': 'application/json'
        }, method='POST')
    req.data = json.dumps({
        'text': text,
        'model_id': 'eleven_monolingual_v1'
    }).encode()
    with urllib.request.urlopen(req) as resp:
        with open(output_file, 'wb') as f:
            f.write(resp.read())
    print(f"Audio saved to {output_file}")

# Get user info
req = urllib.request.Request('https://api.elevenlabs.io/v1/user',
    headers={'xi-api-key': KEY})
with urllib.request.urlopen(req) as resp:
    user = json.loads(resp.read().decode())
    print(f"Tier: {user['subscription']['tier']}")

# Generate speech (uncomment to use)
# elevenlabs_tts("Hello from ElevenLabs!")
```

### Kie AI (Video)
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `KIE_AI_API_KEY` | Video generation | api.kie.ai |

---

## 7. SEARCH & SCRAPING

### Brave Search
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `BRAVE_API_KEY` | Web search | api.search.brave.com |

#### Usage Script - Brave Search
```python
#!/usr/bin/env python3
"""Brave Search API"""
import os
import json
import urllib.request
import urllib.parse

KEY = os.environ.get('BRAVE_API_KEY', '')

def brave_search(query, count=5):
    url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count={count}"
    req = urllib.request.Request(url, headers={'X-Subscription-Token': KEY})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

results = brave_search('Sydney cleaning services')
for r in results.get('web', {}).get('results', [])[:3]:
    print(f"- {r['title']}: {r['url']}")
```

### Apify
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `APIFY_API_KEY` | Main key | api.apify.com |
| `APIFY_CLI_KEY` | CLI key | api.apify.com |
| `APIFY_CUB_KEY` | CUB project | api.apify.com |
| `APIFY_HAFSAH_KEY` | Hafsah's key | api.apify.com |
| `APIFY_USER_ID` | User ID | - |
| `APIFY_CUB_USER_ID` | CUB user | - |
| `APIFY_THEOPBROS_USER_ID` | Theopbros user | - |
| `APIFY_EXTRA_USER_ID` | Extra user | - |

#### Usage Script - Apify
```python
#!/usr/bin/env python3
"""Apify Web Scraping"""
import os
import json
import urllib.request

KEY = os.environ.get('APIFY_API_KEY', '')

def apify_request(endpoint):
    url = f"https://api.apify.com/v2{endpoint}?token={KEY}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode())

# Get user info
user = apify_request('/users/me')
print(f"User: {user['data']['username']}")

# List actors
actors = apify_request('/acts')
print(f"Actors: {len(actors['data']['items'])}")
```

---

## 8. COMMUNICATION

### Telegram
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token | api.telegram.org |
| `TELEGRAM_BOT_USERNAME` | Bot username | - |

#### Usage Script - Telegram
```python
#!/usr/bin/env python3
"""Telegram Bot API"""
import os
import json
import urllib.request

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')

def telegram_request(method, data=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
    if data:
        req.data = json.dumps(data).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Get bot info
me = telegram_request('getMe')
print(f"Bot: @{me['result']['username']}")

# Get updates
updates = telegram_request('getUpdates')
print(f"Updates: {len(updates['result'])}")

# Send message (uncomment to use)
# telegram_request('sendMessage', {'chat_id': CHAT_ID, 'text': 'Hello!'})
```

### LinkedIn
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `LINKEDIN_CLIENT_ID` | OAuth client | api.linkedin.com |
| `LINKEDIN_CLIENT_SECRET` | OAuth secret | api.linkedin.com |

---

## 9. INFRASTRUCTURE

### AWS
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `AWS_ACCESS_KEY_ID` | Access key | Various AWS endpoints |
| `AWS_SECRET_ACCESS_KEY` | Secret key | - |
| `AWS_REGION` | Region (ap-southeast-2) | - |
| `AWS_SERVER_IP` | EC2 IP | - |

#### Usage Script - AWS (boto3)
```python
#!/usr/bin/env python3
"""AWS Services (requires boto3)"""
import os
# pip install boto3

import boto3

session = boto3.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION', 'ap-southeast-2')
)

# S3
s3 = session.client('s3')
buckets = s3.list_buckets()
print(f"S3 Buckets: {len(buckets['Buckets'])}")

# EC2
ec2 = session.client('ec2')
instances = ec2.describe_instances()
print(f"EC2 Instances: {len(instances['Reservations'])}")
```

### Convex
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `CONVEX_DEPLOY_KEY` | Deploy key | convex.cloud |
| `CONVEX_TEAM_ID` | Team ID | - |

### Sentry
| Variable | Purpose | Endpoint |
|----------|---------|----------|
| `SENTRY_ORG_TOKEN` | Org token | sentry.io |
| `SENTRY_PERSONAL_TOKEN` | Personal token | sentry.io |
| `SENTRY_CLIENT_ID` | OAuth client | sentry.io |
| `SENTRY_CLIENT_SECRET` | OAuth secret | sentry.io |

---

## 10. BUSINESS CONFIG

| Variable | Value | Purpose |
|----------|-------|---------|
| `BUSINESS_PHONE` | 0406 764 585 | Display phone |
| `BUSINESS_PHONE_INTL` | +61406764585 | International format |
| `BUSINESS_EMAIL` | cleanupbros.au@gmail.com | Business email |
| `BUSINESS_WEBSITE` | cleanupbros.com.au | Website |
| `BANK_NAME` | Clean Up Bros | Account name |
| `BANK_BSB` | 062-000 | BSB |
| `BANK_ACCOUNT` | 1234567 | Account number |
| `HAFSAH_PERSONAL_EMAIL` | hafsahnuzhat1303@gmail.com | Personal email |
| `HAFSAH_BUSINESS_EMAIL` | cleanupbros.au@gmail.com | Business email |
| `HAFSAH_PHONE` | +61... | Personal phone |

---

## 11. MISC / INTERNAL

| Variable | Purpose |
|----------|---------|
| `CLAWDBOT_GATEWAY_TOKEN` | Clawdbot auth |
| `CLAWDBOT_GATEWAY_URL` | Gateway URL |
| `MCP_TWILIO_COMMAND` | MCP path |
| `MCP_TWILIO_ARGS` | MCP args |
| `MCP_KIE_COMMAND` | MCP path |
| `MCP_KIE_ARGS` | MCP args |
| `MCP_REF_URL` | REF tools URL |
| `REF_API_KEY` | REF tools key |
| `SAG_API_KEY` | SAG key |
| `GITHUB_SSH_KEY_FINGERPRINT` | SSH key |
| `GITHUB_KEY_NAME` | Key name |

---

## File Locations

| File | Purpose |
|------|---------|
| `~/.clawdbot/.env` | All credentials |
| `~/.clawdbot/google-oauth-tokens.json` | Google OAuth tokens |

---

## Health Check Results (2026-02-03 02:50 AEST)

### Google Services (OAuth - Port 8080)
| Service | Scope | Status |
|---------|-------|--------|
| Gmail | gmail.send, readonly, modify | ✅ Working |
| Calendar | calendar | ✅ Working (3 upcoming bookings) |
| Sheets | spreadsheets | ✅ Working |
| Drive | drive (full) | ✅ Working |
| YouTube | youtube, upload, readonly, force-ssl | ✅ Authorized |
| Google Ads | adwords | ⚠️ Enable API in Cloud Console |

### Other Services
| Service | Status |
|---------|--------|
| Square | ✅ Working (production, 1 location) |
| Twilio | ✅ Working (active) |
| WhatsApp | ⚠️ Check phone ID |
| Brave Search | ✅ Working |
| ElevenLabs | ✅ Working (starter tier) |
| OpenRouter | ⚠️ Check key |
| Telegram | ✅ Working (@CubsBookKeeperBot) |
| Apify | ✅ Working |

### OAuth Details
| Setting | Value |
|---------|-------|
| Redirect URI | `http://localhost:8080/` |
| Port | 8080 |
| Token File | `~/.clawdbot/google-oauth-tokens.json` |
| Scopes Authorized | 11 |
| Last Refresh | 2026-02-03 02:49 AEST |

---

*100+ environment variables | 11 OAuth scopes | 14+ services tested*
