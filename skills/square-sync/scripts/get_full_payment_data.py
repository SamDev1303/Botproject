import os
import json
import urllib.request

def square_api(endpoint):
    token = os.environ.get('SQUARE_ACCESS_TOKEN')
    if not token:
        import pathlib
        for p in [pathlib.Path.home() / ".clawdbot" / ".env", pathlib.Path.home() / "clawd" / ".env"]:
            if p.exists():
                with open(p) as f:
                    for line in f:
                        if "SQUARE_ACCESS_TOKEN" in line:
                            token = line.split("=", 1)[1].strip().strip('\"').strip('\'')
                            break
            if token: break

    url = f'https://connect.squareup.com/v2/{endpoint}'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    })
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())
    except Exception as e:
        return {"error": str(e)}

# Fetch all invoices and payments to prepare for sheet sync
locations = square_api('locations').get('locations', [])
all_invoices = []
for loc in locations:
    data = square_api(f'invoices?location_id={loc["id"]}').get('invoices', [])
    all_invoices.extend(data)

# Print summary for the agent to use in the sheet creation
for inv in all_invoices:
    inv_num = inv.get('invoice_number', 'N/A')
    status = inv.get('status')
    total = float(inv.get('next_payment_amount_money', {}).get('amount', 0)) / 100
    # For partially paid, we need to calculate total vs paid
    # Simple summary for now
    print(f"{inv_num} | {status} | {total}")
