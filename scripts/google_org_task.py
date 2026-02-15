#!/usr/bin/env python3
import os
import sys
import json
import base64
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta

TOKEN_FILE = Path.home() / "clawd" / "credentials" / "google_token.json"
CLIENT_ID = "789855447864-npndu9bcoebs9ogvcipagu40vntianms.apps.googleusercontent.com"
CLIENT_SECRET = "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"

def load_tokens():
    if not TOKEN_FILE.exists():
        print("Error: Not authorized.")
        sys.exit(1)
    with open(TOKEN_FILE) as f:
        return json.load(f)

def save_tokens(tokens):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)

def refresh_access_token(refresh_token):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    req = urllib.request.Request(
        'https://oauth2.googleapis.com/token',
        data=urllib.parse.urlencode(data).encode(),
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def api_request(url, method="GET", data=None, content_type="application/json"):
    tokens = load_tokens()
    access_token = tokens.get('access_token')
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': content_type
    }

    if data and content_type == "application/json":
        data = json.dumps(data).encode()
    elif data:
        data = data.encode() if isinstance(data, str) else data

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode()
            return json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        if e.code == 401:
            if 'refresh_token' in tokens:
                new_tokens = refresh_access_token(tokens['refresh_token'])
                tokens['access_token'] = new_tokens['access_token']
                save_tokens(tokens)
                headers['Authorization'] = f"Bearer {new_tokens['access_token']}"
                req = urllib.request.Request(url, data=data, headers=headers, method=method)
                with urllib.request.urlopen(req) as response:
                    res_body = response.read().decode()
                    return json.loads(res_body) if res_body else {}
        error_body = e.read().decode()
        print(f"Error {e.code}: {error_body}")
        return None

# --- Gmail ---
def gmail_org():
    # 1. Archive marketing emails > 30 days
    date_limit = (datetime.now() - timedelta(days=30)).strftime('%Y/%m/%d')
    # Marketing keywords
    keywords = ["Kmart", "JD Sports", "Pinterest", "Target", "Catch", "The Iconic"]
    for kw in keywords:
        query = f"from:{kw} before:{date_limit} label:inbox"
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={urllib.parse.quote(query)}"
        res = api_request(url)
        if res and 'messages' in res:
            ids = [m['id'] for m in res['messages']]
            print(f"Archiving {len(ids)} emails from {kw}")
            batch_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify"
            api_request(batch_url, method="POST", data={"ids": ids, "removeLabelIds": ["INBOX"]})

    # 2. Mark unread social/promotions as read
    # category:social is:unread, category:promotions is:unread
    for cat in ["social", "promotions"]:
        query = f"category:{cat} is:unread"
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={urllib.parse.quote(query)}"
        res = api_request(url)
        if res and 'messages' in res:
            ids = [m['id'] for m in res['messages']]
            print(f"Marking {len(ids)} unread {cat} emails as read")
            batch_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify"
            api_request(batch_url, method="POST", data={"ids": ids, "removeLabelIds": ["UNREAD"]})

# --- Drive ---
def drive_org():
    # Create folders
    folders = ['Clean Up Bros', 'Projects', 'AI & Workflows', 'Archives']
    folder_ids = {}
    for name in folders:
        # Check if exists
        query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(query)}"
        res = api_request(url)
        if res and res.get('files'):
            folder_ids[name] = res['files'][0]['id']
            print(f"Folder '{name}' already exists: {folder_ids[name]}")
        else:
            url = "https://www.googleapis.com/drive/v3/files"
            body = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
            res = api_request(url, method="POST", data=body)
            folder_ids[name] = res['id']
            print(f"Created folder '{name}': {folder_ids[name]}")

    # Move files
    moves = [
        # (Keywords, Target Folder Name)
        (["cleanupbros accounts", "competitor pricing"], 'Clean Up Bros'),
        (["Rent-a-sari", "ASHIKA"], 'Projects'),
        (["Claude", "prompt"], 'AI & Workflows')
    ]

    for keywords, folder_name in moves:
        target_id = folder_ids[folder_name]
        for kw in keywords:
            query = f"name contains '{kw}' and trashed=false"
            url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(query)}"
            res = api_request(url)
            if res and res.get('files'):
                for f in res['files']:
                    # Move to folder
                    file_id = f['id']
                    # Get current parents
                    f_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=parents"
                    f_data = api_request(f_url)
                    current_parents = ",".join(f_data.get('parents', []))
                    
                    update_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?addParents={target_id}&removeParents={current_parents}"
                    api_request(update_url, method="PATCH")
                    print(f"Moved '{f['name']}' to '{folder_name}'")

# --- Sheets ---
def sheets_org():
    # Find 'cleanupbros accounts'
    # Try case-insensitive or partial match
    query = "name contains 'cleanupbros accounts' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
    url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(query)}"
    res = api_request(url)
    if not res or not res.get('files'):
        print("Spreadsheet 'cleanupbros accounts' not found.")
        return
    ss_id = res['files'][0]['id']
    print(f"Found spreadsheet ID: {ss_id}")

    # Get sheet details
    ss_url = f"https://sheets.googleapis.com/v4/spreadsheets/{ss_id}"
    ss_data = api_request(ss_url)
    sheets = ss_data.get('sheets', [])
    
    # 1. Add frozen header
    # We'll assume the first sheet is the one to modify or we'll create/rename
    sheet1 = sheets[0]
    sheet1_id = sheet1['properties']['sheetId']
    sheet1_name = sheet1['properties']['title']
    
    header = ["Date", "Client/Job", "Description", "Amount", "Payment Method", "Reference"]
    
    # Update header and freeze
    batch_url = f"https://sheets.googleapis.com/v4/spreadsheets/{ss_id}:batchUpdate"
    requests = [
        # Update first row
        {
            "updateCells": {
                "rows": [
                    {
                        "values": [{"userEnteredValue": {"stringValue": h}} for h in header]
                    }
                ],
                "fields": "userEnteredValue",
                "range": {
                    "sheetId": sheet1_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": len(header)
                }
            }
        },
        # Freeze first row
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet1_id,
                    "gridProperties": {"frozenRowCount": 1}
                },
                "fields": "gridProperties.frozenRowCount"
            }
        }
    ]
    api_request(batch_url, method="POST", data={"requests": requests})
    print("Header updated and frozen.")

    # 2. Archive 2025 data
    # Read current data
    read_url = f"https://sheets.googleapis.com/v4/spreadsheets/{ss_id}/values/{sheet1_name}!A:Z"
    data = api_request(read_url)
    rows = data.get('values', [])
    if len(rows) <= 1:
        print("No data to archive.")
        return

    header_row = rows[0]
    data_rows = rows[1:]
    
    rows_2025 = []
    rows_2026 = []
    
    for row in data_rows:
        if not row: continue
        date_str = row[0]
        if "2025" in date_str:
            rows_2025.append(row)
        else:
            rows_2026.append(row)

    # Create 'Archive 2025' and '2026' tabs
    # We can rename current to '2026' and create 'Archive 2025'
    rename_req = {
        "updateSheetProperties": {
            "properties": {"sheetId": sheet1_id, "title": "2026"},
            "fields": "title"
        }
    }
    add_req = {
        "addSheet": {"properties": {"title": "Archive 2025"}}
    }
    api_request(batch_url, method="POST", data={"requests": [rename_req, add_req]})
    
    # Write data
    # 2026 (overwrite current)
    clear_url = f"https://sheets.googleapis.com/v4/spreadsheets/{ss_id}/values/2026!A2:Z1000:clear"
    api_request(clear_url, method="POST")
    
    if rows_2026:
        write_url = f"https://sheets.googleapis.com/v4/spreadsheets/{ss_id}/values/2026!A2?valueInputOption=USER_ENTERED"
        api_request(write_url, method="PUT", data={"values": rows_2026})

    # Archive 2025
    if rows_2025:
        write_url = f"https://sheets.googleapis.com/v4/spreadsheets/{ss_id}/values/{urllib.parse.quote('Archive 2025')}!A1?valueInputOption=USER_ENTERED"
        api_request(write_url, method="PUT", data={"values": [header_row] + rows_2025})
    
    print("Data organized into 2026 and Archive 2025.")

if __name__ == "__main__":
    import time
    print("Starting organization...", flush=True)
    try:
        print("Starting Gmail organization...", flush=True)
        gmail_org()
        print("Gmail organization complete.", flush=True)
        
        print("Starting Drive organization...", flush=True)
        drive_org()
        print("Drive organization complete.", flush=True)
        
        print("Starting Sheets organization...", flush=True)
        sheets_org()
        print("Sheets organization complete.", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
    print("Organization complete.", flush=True)
