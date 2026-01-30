import os
import json
import subprocess
from datetime import datetime

def run_tool(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout

# 1. Get Square Payments
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

# 2. Get Google Sheet Income
print("Fetching Google Sheet income...")
sheet_id = "1Yd87dToNUGbyF7Olo1mXFOtwYxc375Ts7YFOOFXElYM"
gg_output = run_tool(f"~/clawd/.venv/bin/python3 ~/clawd/tools/google_api.py sheets_read {sheet_id} Income!A:E")
income_rows = []
for line in gg_output.split('\n'):
    if '|' in line:
        parts = [p.strip() for p in line.split('|')]
        income_rows.append(parts)

# 3. Identify Missing
missing = []
for p in payments:
    amt = p['amount']
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

# 4. Add Missing to Sheet
if not missing:
    print("No missing items to add.")
else:
    print(f"Adding {len(missing)} missing items to Google Sheet...")
    for m in missing:
        date = m['date']
        amt = f"{m['amount']:.2f}" # Remove $ for simple csv parsing
        desc = f"Square Payment {m['id'][-6:]}"
        # Construct the comma-separated string for the tool
        # tool expects: sheets_append <id> <sheet_name> <values_comma_sep>
        values = f"{date},Square Customer,{desc},{amt},Square"
        
        cmd = f"~/clawd/.venv/bin/python3 ~/clawd/tools/google_api.py sheets_append {sheet_id} Income '{values}'"
        print(f"Syncing: {date} | ${amt}")
        run_tool(cmd)

print("\nSync complete. Your Google Sheet is now up to date with Square!")
