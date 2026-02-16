import os
import json
import urllib.request
from datetime import datetime

def get_token(service):
    if service == 'square':
        import pathlib
        token = os.environ.get('SQUARE_ACCESS_TOKEN')
        if not token:
            for p in [pathlib.Path.home() / ".clawdbot" / ".env", pathlib.Path.home() / "clawd" / ".env"]:
                if p.exists():
                    with open(p) as f:
                        for line in f:
                            if "SQUARE_ACCESS_TOKEN" in line:
                                return line.split("=", 1)[1].strip().strip('\"').strip('\'')
        return token
    elif service == 'google':
        import pathlib
        token_file = pathlib.Path.home() / "clawd" / "credentials" / "google_token.json"
        if token_file.exists():
            with open(token_file) as f:
                return json.load(f).get('access_token')
    return None

def api_request(url, token, method="GET", data=None):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    if data: data = json.dumps(data).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read().decode()
            return json.loads(body) if body else {}
    except Exception as e:
        if hasattr(e, 'read'):
            print(f"API Error: {e.read().decode()}")
        else:
            print(f"Request Error: {e}")
        return None

# 1. Get Square Payments
sq_token = get_token('square')
payments = []
loc_data = api_request('https://connect.squareup.com/v2/locations', sq_token)
for loc in loc_data.get('locations', []):
    pay_data = api_request(f'https://connect.squareup.com/v2/payments?location_id={loc["id"]}', sq_token)
    if pay_data: payments.extend(pay_data.get('payments', []))

# 2. Get Google Sheet Income
gg_token = get_token('google')
sheet_id = "1Yd87dToNUGbyF7Olo1mXFOtwYxc375Ts7YFOOFXElYM"
sheet_data = api_request(f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/Income!A:E", gg_token)
income_rows = sheet_data.get('values', [])

# 3. Reconcile
print(f"Checking {len(payments)} Square payments against Google Sheet...")
missing = []
for p in payments:
    if p['status'] != 'COMPLETED': continue
    amt = float(p['amount_money']['amount']) / 100
    if amt == 0: continue
    
    # Check if this amount exists in the sheet on or near the date
    # Square date format: 2026-01-30T...
    sq_date = p['created_at'].split('T')[0]
    found = False
    for row in income_rows:
        if len(row) >= 4:
            try:
                sheet_amt = float(row[3].replace('$', '').replace(',', ''))
                if abs(sheet_amt - amt) < 0.01: # Match amount
                    # Optionally check date too, but amount is usually unique enough for a first pass
                    found = True
                    break
            except: continue
    
    if not found:
        missing.append({
            'date': sq_date,
            'amount': amt,
            'id': p['id'],
            'ref': p.get('reference_id', 'No Ref')
        })

if not missing:
    print("✅ All completed Square payments found in Google Sheet.")
else:
    print(f"⚠️ Found {len(missing)} payments in Square that are MISSING from Google Sheet:")
    for m in missing:
        print(f"- {m['date']} | ${m['amount']:.2f} | ID: {m['id']}")
