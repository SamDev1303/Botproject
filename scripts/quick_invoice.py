#!/usr/bin/env python3
"""
Quick Invoice Creator — Create Square invoice from command line
Usage: python3 ~/Desktop/🦀/scripts/quick_invoice.py "Client Name" 380 "2BR End of Lease Clean"
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from square_api import SquareAPI

def create_invoice(client_name, amount, description):
    sq = SquareAPI()

    # Find or create customer
    customers = sq.search_customers(client_name) or []
    if customers:
        customer_id = customers[0]['id']
        print(f"✅ Found customer: {customers[0].get('given_name', '')} {customers[0].get('family_name', '')}")
    else:
        print(f"⚠️ No customer found for '{client_name}'. Create one first:")
        print(f"  python3 scripts/create_square_customer.py")
        return

    # Create invoice
    result = sq.create_invoice(
        customer_id=customer_id,
        amount_cents=int(float(amount) * 100),
        description=description
    )

    if result:
        inv_id = result.get('id', 'unknown')
        print(f"\n📧 Invoice Created!")
        print(f"  • ID: {inv_id}")
        print(f"  • Amount: ${float(amount):.2f} (inc. GST)")
        print(f"  • GST: ${float(amount)/11:.2f}")
        print(f"  • Description: {description}")
        print(f"  • Customer: {client_name}")
    else:
        print("❌ Failed to create invoice")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 quick_invoice.py 'Client Name' amount 'Description'")
        print("Example: python3 quick_invoice.py 'Sarah Jones' 380 '2BR End of Lease Clean'")
        sys.exit(1)
    create_invoice(sys.argv[1], sys.argv[2], sys.argv[3])
