import os, json, urllib.request, urllib.error

TOKEN = os.environ.get('SQUARE_ACCESS_TOKEN')
if not TOKEN:
    print('Error: SQUARE_ACCESS_TOKEN not found')
    exit(1)

BASE = 'https://connect.squareup.com'

def sq_request(method, endpoint, body=None):
    try:
        url = f'{BASE}{endpoint}'
        headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f'HTTP Error {e.code}: {e.read().decode()}')
        return {}
    except Exception as e:
        print(f'Error: {str(e)}')
        return {}

# 1. Search for customer 'Claudia'
print("Searching for customer 'Claudia'...")
# First try precise search
search_body = {
    "query": {
        "filter": {
            "creation_source": {
                "values": ["THIRD_PARTY"],
                "rule": "INCLUDE"
            }
        },
        "sort": {
            "field": "CREATED_AT",
            "order": "DESC"
        }
    }
}

# The specific search endpoint is tricky, let's just grab customers and filter in Python for reliability
all_customers_resp = sq_request('GET', '/v2/customers')
all_customers = all_customers_resp.get('customers', [])

target_customers = []
for c in all_customers:
    full_name = (c.get('given_name', '') + ' ' + c.get('family_name', '')).strip().lower()
    if 'claudia' in full_name:
        target_customers.append(c)

if not target_customers:
    print("No customer found matching 'Claudia'.")
    exit(0)

print(f"Found {len(target_customers)} customer(s) matching 'Claudia'.")

total_grand_outstanding = 0

for cust in target_customers:
    c_name = f"{cust.get('given_name', '')} {cust.get('family_name', '')}".strip()
    c_id = cust['id']
    print(f"\nChecking invoices for: {c_name} ({c_id})")

    # 2. Get invoices for this customer
    # We need a location ID to filter invoices effectively usually
    locs = sq_request('GET', '/v2/locations')
    if not locs.get('locations'):
        print("No locations found.")
        continue
        
    location_id = locs['locations'][0]['id']

    inv_body = {
        "query": {
            "filter": {
                "customer_ids": [c_id],
                "location_ids": [location_id]
            },
            "sort": {
                "field": "INVOICE_SORT_DATE",
                "order": "DESC"
            }
        }
    }

    invoices_resp = sq_request('POST', '/v2/invoices/search', inv_body)
    invoices = invoices_resp.get('invoices', [])

    cust_outstanding = 0
    unpaid_count = 0

    if not invoices:
        print(f"No invoices found for {c_name}.")
    else:
        for inv in invoices:
            status = inv['status']
            # safely get amount
            amt_money = inv.get('payment_requests', [{}])[0].get('computed_amount_money', {})
            amt = amt_money.get('amount', 0) / 100
            inv_num = inv.get('invoice_number', 'N/A')
            date = inv.get('created_at', '')[:10]
            
            if status in ('UNPAID', 'SENT', 'PARTIALLY_PAID', 'SCHEDULED'):
                print(f"  [PENDING] #{inv_num} - ${amt:.2f} ({status}) - {date}")
                cust_outstanding += amt
                unpaid_count += 1
            # elif status == 'PAID':
            #     print(f"  [PAID] #{inv_num} - ${amt:.2f} - {date}")
    
    print(f"  -> Total Owed by {c_name}: ${cust_outstanding:.2f}")
    total_grand_outstanding += cust_outstanding

print(f"\nTotal Outstanding across all 'Claudia' matches: ${total_grand_outstanding:.2f}")
