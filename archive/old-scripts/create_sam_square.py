import os
import json
import urllib.request
from pathlib import Path

def get_square_token():
    token = os.environ.get('SQUARE_ACCESS_TOKEN')
    if not token:
        env_path = Path.home() / ".clawdbot" / ".env"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith("SQUARE_ACCESS_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('\"').strip('\'')
    return token

def square_api(endpoint, method="GET", data=None):
    token = get_square_token()
    url = f'https://connect.squareup.com/v2/{endpoint}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Square-Version': '2024-01-18'
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())
    except Exception as e:
        if hasattr(e, 'read'): print(f"Error: {e.read().decode()}")
        else: print(f"Error: {e}")
        return {}

# 1. Create Customer in Square
customer_data = {
    "given_name": "Sam",
    "email_address": "Taha3121999@icloud.com",
    "phone_number": "+61410950886",
    "address": {
        "address_line_1": "43 Pinnacle St",
        "locality": "Sadleir",
        "administrative_district_level_1": "NSW",
        "postal_code": "2168",
        "country": "AU"
    },
    "note": "Fortnightly clean $160 base rate. ABN: 26 443 426 374"
}

print("Creating customer in Square...")
result = square_api("customers", method="POST", data=customer_data)
if result and 'customer' in result:
    print(f"✅ Customer created! ID: {result['customer']['id']}")
else:
    print("❌ Failed to create customer.")
