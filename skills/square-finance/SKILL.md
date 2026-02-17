---
name: square-finance
description: Square financial operations — list invoices (paid/unpaid), list customers, create invoices, create payment links, check account balance, and manage payments. Use when the user asks about invoicing, payment tracking, customer records, payment links, or financial summaries from Square.
---

# Square Finance

Manage Clean Up Bros financials through the Square API (production).

## Prerequisites

- **Env vars**: `SQUARE_ACCESS_TOKEN`, `SQUARE_APPLICATION_ID`, `SQUARE_ENVIRONMENT` (production)
- **Base URL**: `https://connect.squareup.com` (production)
- **Existing sync skill**: `square-sync` handles backup to Google Sheets — this skill handles direct Square operations

## API Helper

```python
import os, json, urllib.request

TOKEN = os.environ['SQUARE_ACCESS_TOKEN']
BASE = "https://connect.squareup.com"

def sq(method, endpoint, body=None):
    req = urllib.request.Request(f"{BASE}{endpoint}",
        headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'},
        method=method)
    if body:
        req.data = json.dumps(body).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())
```

## Workflows

### List Invoices (All / Filtered)

```python
# All invoices for primary location
location = sq('GET', '/v2/locations')['locations'][0]['id']
invoices = sq('POST', '/v2/invoices/search', {
    'query': {'filter': {'location_ids': [location]}},
    'limit': 100
})

# Filter unpaid
unpaid = [i for i in invoices.get('invoices', []) if i['status'] in ('SENT', 'UNPAID', 'PARTIALLY_PAID')]
for inv in unpaid:
    amt = inv['payment_requests'][0]['computed_amount_money']['amount'] / 100
    print(f"Invoice #{inv['invoice_number']} — ${amt:.2f} — {inv['status']}")
```

### List Customers

```python
customers = sq('GET', '/v2/customers')
for c in customers.get('customers', []):
    name = f"{c.get('given_name', '')} {c.get('family_name', '')}".strip()
    print(f"{name} — {c.get('email_address', 'no email')} — {c.get('phone_number', 'no phone')}")
```

### Create Invoice

```python
import uuid
invoice = sq('POST', '/v2/invoices', {
    'invoice': {
        'location_id': '<LOCATION_ID>',
        'order_id': '<ORDER_ID>',  # Create order first if needed
        'payment_requests': [{
            'request_type': 'BALANCE',
            'due_date': '2026-03-01',
            'automatic_payment_source': 'NONE'
        }],
        'delivery_method': 'EMAIL',
        'primary_recipient': {'customer_id': '<CUSTOMER_ID>'}
    },
    'idempotency_key': str(uuid.uuid4())
})
# Then publish it
sq('POST', f"/v2/invoices/{invoice['invoice']['id']}/publish", {
    'version': invoice['invoice']['version'],
    'idempotency_key': str(uuid.uuid4())
})
```

### Create Payment Link

```python
import uuid
link = sq('POST', '/v2/online-checkout/payment-links', {
    'quick_pay': {
        'name': 'Cleaning Service — [Client Name]',
        'price_money': {'amount': 35000, 'currency': 'AUD'},  # $350.00
        'location_id': '<LOCATION_ID>'
    },
    'idempotency_key': str(uuid.uuid4())
})
print(f"Payment link: {link['payment_link']['url']}")
```

### Check Balance / Payments

```python
# Recent payments
payments = sq('GET', '/v2/payments?sort_order=DESC&limit=10')
for p in payments.get('payments', []):
    amt = p['amount_money']['amount'] / 100
    print(f"${amt:.2f} — {p['status']} — {p['created_at'][:10]}")
```

## Key Sheet IDs

| Sheet | ID | Purpose |
|-------|----|---------|
| Master Ops | `1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU` | Central operations |
| Finance Backup | `1pocJwoOO3emKfQf9mzFHuahZ5nA7KSrehF9fBqn-00Q` | Square data mirror |

## Important Notes

- All amounts in Square are in **cents** (divide by 100 for display)
- Currency is **AUD**
- Always use `idempotency_key` (uuid4) for create/update operations
- Invoice flow: Create Order → Create Invoice → Publish Invoice
- Use `square-sync` skill to keep Google Sheets backup current after changes

## References

- Square Invoices API: https://developer.squareup.com/reference/square/invoices-api
- Square Payments API: https://developer.squareup.com/reference/square/payments-api
- Square Customers API: https://developer.squareup.com/reference/square/customers-api
- Square Checkout API: https://developer.squareup.com/reference/square/checkout-api
