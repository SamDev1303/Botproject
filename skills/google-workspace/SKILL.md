---
name: google-workspace
description: Google Workspace operations — Gmail (send, search, draft), Calendar (create/list events), Drive (search, upload, share), Sheets (read, write, append). Use when the user asks about email, calendar events, file management, or spreadsheet operations via Google services.
---

# Google Workspace

Unified access to Gmail, Google Calendar, Google Drive, and Google Sheets.

## Prerequisites

- **OAuth tokens**: `~/.clawdbot/google-oauth-tokens.json` (11 scopes authorized)
- **Env vars**: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`
- **CLI**: `gog` (preferred when available); falls back to direct REST API
- **Refresh script**: `python3 ~/Desktop/🦀/scripts/google-oauth-setup.py` if tokens expire

## Token Refresh

Access tokens expire hourly. Refresh before any API call if stale:

```python
import os, json, urllib.request, urllib.parse
from pathlib import Path

TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"
with open(TOKEN_FILE) as f:
    tokens = json.load(f)

data = urllib.parse.urlencode({
    'client_id': os.environ['GOOGLE_CLIENT_ID'],
    'client_secret': os.environ['GOOGLE_CLIENT_SECRET'],
    'refresh_token': tokens['refresh_token'],
    'grant_type': 'refresh_token'
}).encode()
req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST')
with urllib.request.urlopen(req) as resp:
    new = json.loads(resp.read().decode())
    tokens['access_token'] = new['access_token']
with open(TOKEN_FILE, 'w') as f:
    json.dump(tokens, f, indent=2)
```

## Workflows

### Gmail

#### Send Email
```bash
# Via gog CLI
gog gmail send --to "recipient@example.com" --subject "Subject" --body "Message body"

# Via API
curl -s -X POST "https://gmail.googleapis.com/gmail/v1/users/me/messages/send" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"raw": "<base64-encoded-RFC2822>"}'
```

#### Search Emails
```bash
gog gmail search --query "from:client@example.com is:unread" --max-results 10
```
API: `GET /gmail/v1/users/me/messages?q=<query>&maxResults=10`

#### Draft Email
API: `POST /gmail/v1/users/me/drafts` with `{"message": {"raw": "<base64>"}}`

### Google Calendar

#### List Events
```bash
gog calendar list --max-results 10
```
API: `GET /calendar/v3/calendars/primary/events?maxResults=10&timeMin=<ISO8601>&orderBy=startTime&singleEvents=true`

#### Create Event
```bash
gog calendar create --summary "Client Meeting" --start "2026-02-10T10:00:00+11:00" --end "2026-02-10T11:00:00+11:00" --location "123 Main St"
```
API: `POST /calendar/v3/calendars/primary/events` with event JSON body.

### Google Drive

#### Search Files
```bash
gog drive search --query "name contains 'invoice'"
```
API: `GET /drive/v3/files?q=name+contains+'invoice'&fields=files(id,name,mimeType,modifiedTime)`

#### Upload File
```bash
gog drive upload --file ./report.pdf --folder <FOLDER_ID>
```
API: Resumable upload to `https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable`

### Google Sheets

#### Read Range
```bash
gog sheets get <SHEET_ID> "Sheet1!A1:D20"
```
API: `GET /v4/spreadsheets/<ID>/values/<RANGE>`

#### Write / Update Range
```bash
gog sheets update <SHEET_ID> "Sheet1!A1" --values-json '[["Col1","Col2"],["val1","val2"]]' --input USER_ENTERED
```
API: `PUT /v4/spreadsheets/<ID>/values/<RANGE>?valueInputOption=USER_ENTERED`

#### Append Rows
API: `POST /v4/spreadsheets/<ID>/values/<RANGE>:append?valueInputOption=USER_ENTERED`

## Key Sheet IDs

| Sheet | ID |
|-------|----|
| Master Ops | `1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU` |
| Finance Backup | `1pocJwoOO3emKfQf9mzFHuahZ5nA7KSrehF9fBqn-00Q` |

## Error Handling

- **401 Unauthorized**: Token expired → refresh (see above)
- **403 Forbidden**: Scope not authorized → re-run `google-oauth-setup.py`
- **429 Rate Limit**: Back off exponentially; Sheets allows 60 req/min

## References

- Gmail API: https://developers.google.com/gmail/api/reference/rest
- Calendar API: https://developers.google.com/calendar/api/v3/reference
- Drive API: https://developers.google.com/drive/api/v3/reference
- Sheets API: https://developers.google.com/sheets/api/reference/rest
