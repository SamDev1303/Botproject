import os
import json
import subprocess
from datetime import datetime

def run_tool(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout

# 1. Get Square Payments using existing tool
print("Fetching Square payments...")
sq_output = run_tool("~/clawd/.venv/bin/python3 ~/clawd/tools/square_api.py list_payments")
payments = []
current_pay = {}
for line in sq_output.split('\n'):
    if line.startswith('ID: '): current_pay['id'] = line[4:].strip()
    elif line.startswith('Amount: '): current_pay['amount'] = float(line[8:].strip().replace('$', '').replace(',', ''))
    elif line.startswith('Status: '): current_pay['status'] = line[8:].strip()
    elif line.startswith('Created: '): current_pay['date'] = line[9:19].strip()
    elif line.startswith('---'):
        if current_pay.get('status') == 'COMPLETED' and current_pay.get('amount', 0) > 0:
            payments.append(current_pay)
        current_pay = {}

# 2. Get Google Sheet Income using modified google_api tool
print("Fetching Google Sheet income...")
sheet_id = "1Yd87dToNUGbyF7Olo1mXFOtwYxc375Ts7YFOOFXElYM"
gg_output = run_tool(f"~/clawd/.venv/bin/python3 ~/clawd/tools/google_api.py sheets_read {sheet_id} Income!A:E")
income_rows = []
for line in gg_output.split('\n'):
    if '|' in line:
        parts = [p.strip() for p in line.split('|')]
        income_rows.append(parts)

# 3. Reconcile
print(f"\nChecking {len(payments)} Square payments against Google Sheet...\n")
missing = []
for p in payments:
    amt = p['amount']
    date = p['date']
    found = False
    for row in income_rows:
        if len(row) >= 4:
            try:
                sheet_amt = float(row[3].replace('$', '').replace(',', ''))
                if abs(sheet_amt - amt) < 0.01:
                    found = True
                    break
            except: continue
    
    if not found:
        missing.append(p)

if not missing:
    print("✅ All completed Square payments found in Google Sheet.")
else:
    print(f"⚠️ Found {len(missing)} payments in Square that are MISSING from Google Sheet:")
    print("-" * 50)
    for m in missing:
        print(f"Date: {m['date']} | Amount: ${m['amount']:.2f} | ID: {m['id']}")
