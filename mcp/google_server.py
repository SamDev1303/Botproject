#!/usr/bin/env python3
"""
Google MCP Server - Gmail, Sheets, Drive, Calendar
For Clean Up Bros business operations
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

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

TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID', '')

def get_access_token():
    """Get valid access token, refreshing if needed"""
    if not TOKEN_FILE.exists():
        return None

    with open(TOKEN_FILE) as f:
        tokens = json.load(f)

    # Try to use existing token
    access_token = tokens.get('access_token')

    # Check if we need to refresh
    if 'refresh_token' in tokens:
        # Always refresh to be safe
        data = urllib.parse.urlencode({
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': tokens['refresh_token'],
            'grant_type': 'refresh_token'
        }).encode()

        try:
            req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
            with urllib.request.urlopen(req) as response:
                new_tokens = json.loads(response.read().decode())
                tokens['access_token'] = new_tokens['access_token']
                with open(TOKEN_FILE, 'w') as f:
                    json.dump(tokens, f, indent=2)
                return new_tokens['access_token']
        except:
            pass

    return access_token

def api_request(url, method="GET", data=None):
    """Make authenticated API request"""
    token = get_access_token()
    if not token:
        return {"error": "No access token. Run google-oauth-setup.py first."}

    headers = {"Authorization": f"Bearer {token}"}
    if data:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:200]}"}

import urllib.parse

# Create MCP server
mcp = FastMCP("Google")

# ============== GMAIL ==============

@mcp.tool()
def gmail_search(query: str, max_results: int = 10) -> str:
    """Search Gmail messages. Query examples: 'from:client@email.com', 'is:unread', 'subject:booking'"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={urllib.parse.quote(query)}&maxResults={max_results}"
    result = api_request(url)

    if "error" in result:
        return f"Error: {result['error']}"

    messages = result.get('messages', [])
    if not messages:
        return "No messages found."

    # Get details for each message
    output = []
    for msg in messages[:5]:
        detail_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date"
        detail = api_request(detail_url)

        headers = {h['name']: h['value'] for h in detail.get('payload', {}).get('headers', [])}
        output.append(f"• {headers.get('Subject', 'No subject')} - From: {headers.get('From', 'Unknown')}")

    return f"Found {len(messages)} messages:\n" + "\n".join(output)

@mcp.tool()
def gmail_read(message_id: str) -> str:
    """Read a specific Gmail message by ID"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
    result = api_request(url)

    if "error" in result:
        return f"Error: {result['error']}"

    headers = {h['name']: h['value'] for h in result.get('payload', {}).get('headers', [])}
    snippet = result.get('snippet', '')

    return f"From: {headers.get('From', 'Unknown')}\nSubject: {headers.get('Subject', 'No subject')}\nDate: {headers.get('Date', 'Unknown')}\n\n{snippet}"

@mcp.tool()
def gmail_send(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail"""
    import base64

    message = f"To: {to}\nSubject: {subject}\nContent-Type: text/plain; charset=utf-8\n\n{body}"
    raw = base64.urlsafe_b64encode(message.encode()).decode()

    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    result = api_request(url, method="POST", data={"raw": raw})

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Email sent successfully! Message ID: {result.get('id', 'unknown')}"

@mcp.tool()
def gmail_mark_read(message_id: str) -> str:
    """Mark a Gmail message as read"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/modify"
    result = api_request(url, method="POST", data={"removeLabelIds": ["UNREAD"]})

    if "error" in result:
        return f"Error: {result['error']}"
    return "Message marked as read."

@mcp.tool()
def gmail_unread_count() -> str:
    """Get count of unread emails"""
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages?q=is:unread&maxResults=1"
    result = api_request(url)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Unread emails: {result.get('resultSizeEstimate', 0)}"

# ============== GOOGLE SHEETS ==============

@mcp.tool()
def sheets_read(range: str, spreadsheet_id: str = "") -> str:
    """Read data from Google Sheets. Range format: 'Sheet1!A1:D10' or just 'Income!A:E'"""
    sheet_id = spreadsheet_id or SHEETS_ID
    if not sheet_id:
        return "Error: No spreadsheet ID configured"

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{urllib.parse.quote(range)}"
    result = api_request(url)

    if "error" in result:
        return f"Error: {result['error']}"

    values = result.get('values', [])
    if not values:
        return "No data found."

    # Format as table
    output = []
    for row in values[:20]:  # Limit to 20 rows
        output.append(" | ".join(str(cell) for cell in row))

    return f"Data from {range}:\n" + "\n".join(output)

@mcp.tool()
def sheets_append(range: str, values: list, spreadsheet_id: str = "") -> str:
    """Append a row to Google Sheets. Values should be a list like ['value1', 'value2', ...]"""
    sheet_id = spreadsheet_id or SHEETS_ID
    if not sheet_id:
        return "Error: No spreadsheet ID configured"

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{urllib.parse.quote(range)}:append?valueInputOption=USER_ENTERED"
    result = api_request(url, method="POST", data={"values": [values]})

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Row appended successfully to {result.get('updates', {}).get('updatedRange', range)}"

@mcp.tool()
def sheets_list() -> str:
    """List all sheets in the configured spreadsheet"""
    if not SHEETS_ID:
        return "Error: No spreadsheet ID configured"

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEETS_ID}"
    result = api_request(url)

    if "error" in result:
        return f"Error: {result['error']}"

    title = result.get('properties', {}).get('title', 'Unknown')
    sheets = [s['properties']['title'] for s in result.get('sheets', [])]

    return f"Spreadsheet: {title}\nSheets: {', '.join(sheets)}"

# ============== GOOGLE DRIVE ==============

@mcp.tool()
def drive_list(query: str = "", max_results: int = 10) -> str:
    """List files in Google Drive. Optional query like 'name contains invoice'"""
    url = f"https://www.googleapis.com/drive/v3/files?pageSize={max_results}&fields=files(id,name,mimeType,modifiedTime)"
    if query:
        url += f"&q={urllib.parse.quote(query)}"

    result = api_request(url)

    if "error" in result:
        return f"Error: {result['error']}"

    files = result.get('files', [])
    if not files:
        return "No files found."

    output = []
    for f in files:
        output.append(f"• {f['name']} ({f['mimeType'].split('.')[-1]})")

    return "Files:\n" + "\n".join(output)

@mcp.tool()
def drive_search(filename: str) -> str:
    """Search for a file by name in Google Drive"""
    return drive_list(query=f"name contains '{filename}'")

# ============== GOOGLE CALENDAR ==============

@mcp.tool()
def calendar_list_events(days: int = 7) -> str:
    """List upcoming calendar events for the next N days"""
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=days)).isoformat() + 'Z'

    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin={time_min}&timeMax={time_max}&maxResults=20&singleEvents=true&orderBy=startTime"
    result = api_request(url)

    if "error" in result:
        return f"Error: {result['error']}"

    events = result.get('items', [])
    if not events:
        return f"No events in the next {days} days."

    output = []
    for event in events:
        start = event.get('start', {})
        date_str = start.get('dateTime', start.get('date', 'Unknown'))
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            date_display = dt.strftime('%a %d %b, %I:%M %p')
        else:
            date_display = date_str

        output.append(f"• {event.get('summary', 'No title')} - {date_display}")

    return f"Upcoming events:\n" + "\n".join(output)

@mcp.tool()
def calendar_create_event(title: str, date: str, time: str = "09:00", duration_hours: int = 1, description: str = "") -> str:
    """Create a calendar event. Date format: YYYY-MM-DD, Time format: HH:MM"""
    try:
        start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(hours=duration_hours)
    except ValueError as e:
        return f"Error parsing date/time: {e}"

    event = {
        "summary": title,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Australia/Sydney"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "Australia/Sydney"},
    }
    if description:
        event["description"] = description

    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    result = api_request(url, method="POST", data=event)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Event created: {result.get('summary', title)} on {date} at {time}\nLink: {result.get('htmlLink', 'N/A')}"

@mcp.tool()
def calendar_check_availability(date: str) -> str:
    """Check availability for a specific date (YYYY-MM-DD)"""
    try:
        check_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Error: Date must be in YYYY-MM-DD format"

    time_min = check_date.isoformat() + 'Z'
    time_max = (check_date + timedelta(days=1)).isoformat() + 'Z'

    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin={time_min}&timeMax={time_max}&singleEvents=true"
    result = api_request(url)

    if "error" in result:
        return f"Error: {result['error']}"

    events = result.get('items', [])
    if not events:
        return f"{date} is completely free!"

    busy_times = []
    for event in events:
        start = event.get('start', {}).get('dateTime', '')
        end = event.get('end', {}).get('dateTime', '')
        if start and end:
            start_time = datetime.fromisoformat(start.replace('Z', '+00:00')).strftime('%I:%M %p')
            end_time = datetime.fromisoformat(end.replace('Z', '+00:00')).strftime('%I:%M %p')
            busy_times.append(f"  {start_time} - {end_time}: {event.get('summary', 'Busy')}")

    return f"Busy times on {date}:\n" + "\n".join(busy_times)

if __name__ == "__main__":
    mcp.run()
