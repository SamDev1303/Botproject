
import os
import sys
from square_api import SquareAPI

def check_meshach():
    sq = SquareAPI()
    
    print("Fetching customers...")
    customers = sq.list_customers(limit=100)
    meshach = None
    
    for c in customers:
        name = f"{c.get('given_name', '')} {c.get('family_name', '')}".strip()
        if "meshach" in name.lower():
            meshach = c
            print(f"Found Client: {name} (ID: {c['id']})")
            break
            
    if not meshach:
        print("Meshach not found in Square customers.")
        return

    print(f"Fetching ALL invoices for {meshach.get('given_name')}...")
    # Get all invoices regardless of status
    invoices = sq.list_invoices()
    
    client_invoices = []
    total_paid = 0
    total_outstanding = 0
    
    for inv in invoices:
        cust_id = inv.get("primary_recipient", {}).get("customer_id")
        if cust_id == meshach['id']:
            inv_num = inv.get("invoice_number", "Unknown")
            status = inv.get("status")
            amt_obj = inv.get("payment_requests", [{}])[0].get("computed_amount_money", {})
            amount = amt_obj.get("amount", 0) / 100.0
            
            # Check for remaining balance
            total_money = inv.get("payment_requests", [{}])[0].get("total_completed_amount_money", {"amount": 0})
            paid_amount = total_money.get("amount", 0) / 100.0
            remaining = amount - paid_amount
            
            date = inv.get("created_at", "")[:10]
            
            client_invoices.append(f"#{inv_num} ({date}): Total: ${amount:.2f} | Paid: ${paid_amount:.2f} | Due: ${remaining:.2f} [{status}]")
            
            total_outstanding += remaining

    print("\n--- INVOICE HISTORY ---")
    if not client_invoices:
        print("No invoices found for this client.")
    
    for record in client_invoices:
        print(record)
        
    print(f"\nTotal Paid: ${total_paid:.2f}")
    print(f"Current Balance Due: ${total_outstanding:.2f}")

if __name__ == "__main__":
    check_meshach()
