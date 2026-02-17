#!/usr/bin/env python3
"""
Create the Clean Up Bros Master Operations Sheet with 4 tabs:
1. Client Log - All clients, jobs, payments, status
2. Bookkeeping - Income, expenses, receipts, GST
3. Task Log - Every task Bella performs, timestamped
4. Accounts - API connections reference
"""

import os
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

# Load environment
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

TOKEN_FILE = os.path.expanduser("~/.clawdbot/google-oauth-tokens.json")
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

def load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)

def save_tokens(tokens):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)

def refresh_token():
    tokens = load_tokens()
    data = urllib.parse.urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': tokens['refresh_token'],
        'grant_type': 'refresh_token'
    }).encode()
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST')
    with urllib.request.urlopen(req) as resp:
        new_tokens = json.loads(resp.read().decode())
    tokens['access_token'] = new_tokens['access_token']
    save_tokens(tokens)
    return tokens['access_token']

def api_request(url, method='GET', body=None, retry=True):
    tokens = load_tokens()
    headers = {
        'Authorization': f'Bearer {tokens["access_token"]}',
        'Content-Type': 'application/json'
    }
    req = urllib.request.Request(url, headers=headers, method=method)
    if body:
        req.data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry:
            print("Token expired, refreshing...")
            refresh_token()
            return api_request(url, method, body, retry=False)
        error_body = e.read().decode()
        print(f"API Error {e.code}: {error_body[:500]}")
        raise

def create_spreadsheet():
    """Create the master spreadsheet with 4 tabs"""
    body = {
        "properties": {
            "title": "Clean Up Bros - Master Operations Log"
        },
        "sheets": [
            {
                "properties": {
                    "title": "Client Log",
                    "index": 0,
                    "sheetId": 0,
                    "gridProperties": {"frozenRowCount": 1}
                }
            },
            {
                "properties": {
                    "title": "Bookkeeping",
                    "index": 1,
                    "sheetId": 1,
                    "gridProperties": {"frozenRowCount": 1}
                }
            },
            {
                "properties": {
                    "title": "Task Log",
                    "index": 2,
                    "sheetId": 2,
                    "gridProperties": {"frozenRowCount": 1}
                }
            },
            {
                "properties": {
                    "title": "Accounts",
                    "index": 3,
                    "sheetId": 3,
                    "gridProperties": {"frozenRowCount": 1}
                }
            }
        ]
    }
    
    result = api_request(
        'https://sheets.googleapis.com/v4/spreadsheets',
        method='POST',
        body=body
    )
    
    sheet_id = result['spreadsheetId']
    print(f"✅ Created spreadsheet: {sheet_id}")
    print(f"📎 URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
    return sheet_id

def setup_headers(sheet_id):
    """Add headers to all 4 tabs"""
    
    # Client Log headers
    client_headers = [["Date", "Client Name", "Phone", "Email", "Service Type", "Location/Suburb", "Quote Amount", "Invoice #", "Payment Status", "Amount Paid", "Source", "Notes"]]
    
    # Bookkeeping headers
    bookkeeping_headers = [["Date", "Type", "Category", "Description", "Amount (Inc GST)", "GST Component", "Amount (Ex GST)", "Payment Method", "Receipt #", "Supplier/Client", "Notes"]]
    
    # Task Log headers
    task_headers = [["Timestamp", "Task Type", "Description", "Platform/Tool Used", "Status", "Duration", "Triggered By", "Notes"]]
    
    # Accounts headers
    accounts_headers = [["Service", "Type", "Status", "Account/ID", "Last Verified", "Capabilities", "Notes"]]
    
    # Batch update all headers
    body = {
        "valueInputOption": "RAW",
        "data": [
            {"range": "Client Log!A1:L1", "values": client_headers},
            {"range": "Bookkeeping!A1:K1", "values": bookkeeping_headers},
            {"range": "Task Log!A1:H1", "values": task_headers},
            {"range": "Accounts!A1:G1", "values": accounts_headers}
        ]
    }
    
    api_request(
        f'https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values:batchUpdate',
        method='POST',
        body=body
    )
    print("✅ Headers added to all 4 tabs")

def populate_accounts(sheet_id):
    """Populate the Accounts tab with all known integrations"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    accounts_data = [
        [now, "Square", "Payments & Invoicing", "Active", "Production", now, "Payments, invoices, clients, catalogue", "Primary SOT for financials"],
        [now, "Connecteam", "Staff Management", "Active", "Company: 1899328", now, "Roster, shifts, timeclock, forms, schedule, chat, documents", "Primary SOT for rostering"],
        [now, "Google Calendar", "Scheduling", "Active", "cleanupbros.au@gmail.com", now, "Events, bookings, reminders, tasks", "Primary SOT for schedule"],
        [now, "Gmail", "Communication", "Active", "cleanupbros.au@gmail.com", now, "Send, read, search, draft, reply emails", "Primary SOT for comms"],
        [now, "Google Sheets", "Data Backup", "Active", "Multiple sheets", now, "Read, write, append, sync data", "Backup for all services"],
        [now, "Meta (Facebook)", "Social Media", "Active", "Page: 707617919097782", now, "Post text, images, videos to FB page", "Clean Up Bros page"],
        [now, "Meta (Instagram)", "Social Media", "Active", "IG: 17841475542958087", now, "Post images, reels, stories to IG", "Linked to FB page"],
        [now, "Twilio", "SMS/Voice", "Active", "AU number configured", now, "Send/receive SMS, voice calls", "Client comms"],
        [now, "Nano Banana Pro", "Image Generation", "Active", "Gemini API", now, "Generate/edit images via AI", "Social media assets"],
        [now, "OpenAI Whisper", "Transcription", "Active", "API key", now, "Audio transcription", "Voice messages"],
        [now, "Brave Search", "Web Search", "Active", "API key", now, "Web search, research", "Trending content"],
        [now, "ElevenLabs (sag)", "Text-to-Speech", "Active", "API key", now, "Voice generation, TTS", "Voice content"],
        [now, "GitHub", "Code Repository", "Active", "SamDev1303/Botproject", now, "Git push/pull, CI/CD", "Workspace repo"],
        [now, "Vercel", "Deployment", "Active", "bella-dashboard", now, "Dashboard hosting, auto-deploy", "Telegram Mini App"],
        [now, "WhatsApp (wacli)", "Messaging", "Available", "Configured", now, "Send/search WA messages", "Client outreach"],
    ]
    
    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": f"Accounts!A2:H{2+len(accounts_data)}", "values": accounts_data}
        ]
    }
    
    api_request(
        f'https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values:batchUpdate',
        method='POST',
        body=body
    )
    print(f"✅ Populated Accounts tab with {len(accounts_data)} integrations")

def log_task(sheet_id, task_type, description, platform, status="Completed", triggered_by="Bella Auto"):
    """Log a task to the Task Log tab"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [[now, task_type, description, platform, status, "", triggered_by, ""]]
    
    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [{"range": "Task Log!A:H", "majorDimension": "ROWS", "values": row}]
    }
    
    # Use append instead
    api_request(
        f'https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/Task%20Log!A:H:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS',
        method='POST',
        body={"values": row}
    )

if __name__ == '__main__':
    print("🏗️ Creating Clean Up Bros Master Operations Sheet...")
    sheet_id = create_spreadsheet()
    setup_headers(sheet_id)
    populate_accounts(sheet_id)
    
    # Log the creation itself
    log_task(sheet_id, "System Setup", "Created Master Operations Sheet with 4 tabs", "Google Sheets API")
    
    print(f"\n🎉 DONE! Sheet ID: {sheet_id}")
    print(f"📎 URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
    
    # Save sheet ID for reference
    ref_file = os.path.expanduser("~/Desktop/🦀/references/master-sheet-id.txt")
    with open(ref_file, 'w') as f:
        f.write(sheet_id)
    print(f"💾 Sheet ID saved to {ref_file}")
