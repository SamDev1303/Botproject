#!/usr/bin/env python3
"""
Square Payments MCP Server
For Clean Up Bros invoicing and payments
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Load environment
def load_env():
    env_file = Path.home() / ".clawdbot" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))

load_env()

ACCESS_TOKEN = os.environ.get('SQUARE_ACCESS_TOKEN', '')
LOCATION_ID = os.environ.get('SQUARE_LOCATION_ID', '')
BASE_URL = "https://connect.squareup.com/v2"

def api_request(endpoint, method="GET", data=None):
    """Make Square API request"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Square-Version": "2024-01-18"
    }

    if data:
        data = json.dumps(data).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:200]}"}

# Create MCP server
mcp = FastMCP("Square")

@mcp.tool()
def square_list_locations() -> str:
    """List all Square locations"""
    result = api_request("/locations")

    if "error" in result:
        return f"Error: {result['error']}"

    locations = result.get('locations', [])
    output = []
    for loc in locations:
        output.append(f"• {loc['name']} ({loc['status']}) - ID: {loc['id']}")

    return "Locations:\n" + "\n".join(output)

@mcp.tool()
def square_create_invoice(customer_email: str, amount_dollars: float, description: str, due_days: int = 7) -> str:
    """Create and send an invoice to a customer"""
    import uuid
    from datetime import timedelta

    # First, get or create customer
    customer_result = api_request("/customers/search", method="POST", data={
        "query": {"filter": {"email_address": {"exact": customer_email}}}
    })

    customer_id = None
    if customer_result.get('customers'):
        customer_id = customer_result['customers'][0]['id']
    else:
        # Create customer
        create_result = api_request("/customers", method="POST", data={
            "email_address": customer_email,
            "idempotency_key": str(uuid.uuid4())
        })
        if create_result.get('customer'):
            customer_id = create_result['customer']['id']

    if not customer_id:
        return "Error: Could not create/find customer"

    # Get location ID
    loc_result = api_request("/locations")
    location_id = loc_result.get('locations', [{}])[0].get('id', LOCATION_ID)

    # Create invoice
    due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d")
    amount_cents = int(amount_dollars * 100)

    invoice_data = {
        "invoice": {
            "location_id": location_id,
            "primary_recipient": {"customer_id": customer_id},
            "payment_requests": [{
                "request_type": "BALANCE",
                "due_date": due_date,
                "automatic_payment_source": "NONE"
            }],
            "delivery_method": "EMAIL",
            "accepted_payment_methods": {
                "card": True,
                "bank_account": True
            }
        },
        "idempotency_key": str(uuid.uuid4())
    }

    result = api_request("/invoices", method="POST", data=invoice_data)

    if "error" in result:
        return f"Error: {result['error']}"

    invoice = result.get('invoice', {})

    # Add line item
    invoice_id = invoice.get('id')
    if invoice_id:
        # Update invoice with line item
        update_data = {
            "invoice": {
                "version": invoice.get('version', 0),
                "line_items": [{
                    "name": description,
                    "quantity": "1",
                    "base_price_money": {
                        "amount": amount_cents,
                        "currency": "AUD"
                    }
                }]
            },
            "idempotency_key": str(uuid.uuid4())
        }
        api_request(f"/invoices/{invoice_id}", method="PUT", data=update_data)

        # Publish invoice
        publish_data = {
            "version": invoice.get('version', 0) + 1,
            "idempotency_key": str(uuid.uuid4())
        }
        api_request(f"/invoices/{invoice_id}/publish", method="POST", data=publish_data)

    return f"Invoice created for {customer_email}\nAmount: ${amount_dollars:.2f}\nDue: {due_date}\nInvoice ID: {invoice_id}"

@mcp.tool()
def square_list_invoices(status: str = "UNPAID") -> str:
    """List invoices. Status can be: UNPAID, PAID, SCHEDULED, CANCELED"""
    loc_result = api_request("/locations")
    location_id = loc_result.get('locations', [{}])[0].get('id', LOCATION_ID)

    result = api_request(f"/invoices?location_id={location_id}")

    if "error" in result:
        return f"Error: {result['error']}"

    invoices = result.get('invoices', [])
    if not invoices:
        return "No invoices found."

    output = []
    for inv in invoices:
        if status and inv.get('status') != status:
            continue
        amount = inv.get('payment_requests', [{}])[0].get('computed_amount_money', {})
        amount_str = f"${amount.get('amount', 0) / 100:.2f}" if amount else "N/A"
        output.append(f"• {inv.get('invoice_number', 'N/A')} - {inv.get('status')} - {amount_str}")

    return f"Invoices ({status}):\n" + "\n".join(output) if output else f"No {status} invoices."

@mcp.tool()
def square_list_payments(days: int = 7) -> str:
    """List recent payments from the last N days"""
    from datetime import timedelta

    end_time = datetime.utcnow().isoformat() + 'Z'
    start_time = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'

    result = api_request(f"/payments?begin_time={start_time}&end_time={end_time}")

    if "error" in result:
        return f"Error: {result['error']}"

    payments = result.get('payments', [])
    if not payments:
        return f"No payments in the last {days} days."

    total = 0
    output = []
    for pay in payments:
        amount = pay.get('amount_money', {})
        amount_val = amount.get('amount', 0) / 100
        total += amount_val
        status = pay.get('status', 'UNKNOWN')
        created = pay.get('created_at', '')[:10]
        output.append(f"• {created} - ${amount_val:.2f} - {status}")

    return f"Payments (last {days} days):\n" + "\n".join(output) + f"\n\nTotal: ${total:.2f}"

@mcp.tool()
def square_get_balance() -> str:
    """Get current Square account balance"""
    loc_result = api_request("/locations")
    location_id = loc_result.get('locations', [{}])[0].get('id', LOCATION_ID)

    result = api_request(f"/cash-drawers/shifts?location_id={location_id}&limit=1")

    # Alternative: get from payments
    payments_result = api_request("/payments?limit=100")
    payments = payments_result.get('payments', [])

    total_completed = sum(
        p.get('amount_money', {}).get('amount', 0)
        for p in payments
        if p.get('status') == 'COMPLETED'
    ) / 100

    return f"Recent completed payments total: ${total_completed:.2f}"

@mcp.tool()
def square_create_payment_link(amount_dollars: float, description: str) -> str:
    """Create a payment link that can be shared with customers"""
    import uuid

    amount_cents = int(amount_dollars * 100)

    data = {
        "checkout_options": {
            "ask_for_shipping_address": False
        },
        "quick_pay": {
            "name": description,
            "price_money": {
                "amount": amount_cents,
                "currency": "AUD"
            },
            "location_id": LOCATION_ID or api_request("/locations").get('locations', [{}])[0].get('id', '')
        },
        "idempotency_key": str(uuid.uuid4())
    }

    result = api_request("/online-checkout/payment-links", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    link = result.get('payment_link', {})
    return f"Payment link created:\n{link.get('url', 'N/A')}\nAmount: ${amount_dollars:.2f}\nDescription: {description}"

if __name__ == "__main__":
    mcp.run()
