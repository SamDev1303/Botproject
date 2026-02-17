
import os
import sys
from square_api import SquareAPI

def check_claudia_history():
    sq = SquareAPI()
    
    print("Fetching customers...")
    customers = sq.list_customers(limit=100)
    claudia = None
    for c in customers:
        name = f"{c.get('given_name', '')} {c.get('family_name', '')}".strip()
        if "claudia" in name.lower():
            claudia = c
            print(f"Found Claudia: {name} (ID: {c['id']})")
            break
            
    if not claudia:
        print("Claudia not found.")
        return

    print("Fetching ALL invoices for Claudia...")
    # Get all invoices regardless of status
    invoices = sq.list_invoices()
    
    claudia_invoices = []
    total_paid = 0
    total_unpaid = 0
    
    for inv in invoices:
        cust_id = inv.get("primary_recipient", {}).get("customer_id")
        if cust_id == claudia['id']:
            inv_num = inv.get("invoice_number", "Unknown")
            status = inv.get("status")
            amt_obj = inv.get("payment_requests", [{}])[0].get("computed_amount_money", {})
            amount = amt_obj.get("amount", 0) / 100.0
            date = inv.get("created_at", "")[:10]
            
            claudia_invoices.append(f"#{inv_num} ({date}): ${amount:.2f} [{status}]")
            
            if status == "PAID":
                total_paid += amount
            elif status == "UNPAID":
                total_unpaid += amount

    print("\n--- CLAUDIA'S INVOICE HISTORY ---")
    for record in claudia_invoices:
        print(record)
        
    print(f"\nTotal Paid: ${total_paid:.2f}")
    print(f"Current Balance: ${total_unpaid:.2f}")

if __name__ == "__main__":
    check_claudia_history()
