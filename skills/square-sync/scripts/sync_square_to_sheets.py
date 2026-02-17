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

def get_data():
    locations = square_api('locations').get('locations', [])
    rows = [["Invoice #", "Customer", "Status", "Total Amount", "Paid Amount", "Balance Owed", "Due Date"]]
    
    for loc in locations:
        loc_id = loc['id']
        inv_data = square_api(f'invoices?location_id={loc_id}')
        invoices = inv_data.get('invoices', [])
        
        for inv in invoices:
            num = inv.get('invoice_number', 'N/A')
            recipient = inv.get('primary_recipient', {})
            name = f"{recipient.get('given_name', '')} {recipient.get('family_name', '')}".strip() or recipient.get('company_name', 'N/A')
            status = inv.get('status')
            
            # Extract money info
            # Payment requests often have the breakdown
            total_money = 0
            paid_money = 0
            due_date = "N/A"
            
            for req in inv.get('payment_requests', []):
                total_money += req.get('computed_amount_money', {}).get('amount', 0)
                paid_money += req.get('total_completed_amount_money', {}).get('amount', 0)
                if req.get('request_type') == 'BALANCE':
                    due_date = req.get('due_date', 'N/A')
            
            balance = (total_money - paid_money) / 100
            total = total_money / 100
            paid = paid_money / 100
            
            rows.append([num, name, status, f"${total:.2f}", f"${paid:.2f}", f"${balance:.2f}", due_date])
            
    return rows

if __name__ == "__main__":
    data = get_data()
    print(json.dumps(data))
