import os
import json
import urllib.request

def square_api(endpoint):
    # Try to find the token in known locations
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
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}

data = square_api('locations')
locations = data.get('locations', [])
unpaid = []

for loc in locations:
    loc_id = loc['id']
    print(f"Checking location: {loc.get('name')} ({loc_id})")
    inv_data = square_api(f'invoices?location_id={loc_id}')
    loc_invoices = inv_data.get('invoices', [])
    unpaid.extend([i for i in loc_invoices if i.get('status') not in ['PAID', 'REFUNDED', 'CANCELED']])

if not unpaid:
    print("No unpaid invoices found.")
else:
    print(f"Found {len(unpaid)} unpaid invoices:")
    for i in unpaid:
        amt_data = i.get('next_payment_amount_money', i.get('payment_requests', [{}])[0].get('total_completed_amount_money', {'amount': 0}))
        amt = float(amt_data.get('amount', 0)) / 100
        print(f"- Invoice {i.get('invoice_number', 'N/A')} ({i['id']}): {i['status']} - ${amt:.2f}")
