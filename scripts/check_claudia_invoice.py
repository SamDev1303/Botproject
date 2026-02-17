
import os
import sys
from square_api import SquareAPI

def check_claudia():
    sq = SquareAPI()
    
    # 1. Get all customers to find Claudia
    print("Fetching customers...")
    customers = sq.list_customers(limit=100)
    claudia = None
    customer_map = {}
    
    for c in customers:
        name = f"{c.get('given_name', '')} {c.get('family_name', '')}".strip()
        cid = c['id']
        customer_map[cid] = name
        if "claudia" in name.lower():
            claudia = c
            print(f"Found Claudia: {name} (ID: {cid})")

    # 2. Get all unpaid invoices
    print("Fetching unpaid invoices...")
    invoices = sq.list_invoices(status="UNPAID")
    
    claudia_invoices = []
    
    for inv in invoices:
        cust_id = inv.get("primary_recipient", {}).get("customer_id")
        inv_num = inv.get("invoice_number", "Unknown")
        
        # Calculate amount
        amt_obj = inv.get("payment_requests", [{}])[0].get("computed_amount_money", {})
        amount = amt_obj.get("amount", 0) / 100.0
        
        cust_name = customer_map.get(cust_id, "Unknown Customer")
        
        if claudia and cust_id == claudia['id']:
            claudia_invoices.append((inv_num, amount, inv.get("status")))
            
        print(f"Invoice #{inv_num}: ${amount:.2f} - {cust_name} ({inv.get('status')})")

    print("-" * 30)
    if claudia_invoices:
        total = sum(i[1] for i in claudia_invoices)
        print(f"CLAUDIA OWES: ${total:.2f}")
        for inv in claudia_invoices:
            print(f" - Invoice #{inv[0]}: ${inv[1]:.2f}")
    else:
        print("Claudia has NO unpaid invoices.")

if __name__ == "__main__":
    check_claudia()
