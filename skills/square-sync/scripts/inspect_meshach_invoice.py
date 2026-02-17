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

# Fetch the specific invoice for Meshach
invoice_id = "inv:0-ChCoCr3Rh5me8nbYoK0n4s1QEOoK"
invoice = square_api(f'invoices/{invoice_id}')
print(json.dumps(invoice, indent=2))
