
from square_api import SquareAPI

def list_debtors():
    sq = SquareAPI()
    print("Fetching customers...")
    customers = {c['id']: f"{c.get('given_name','')} {c.get('family_name','')}".strip() 
                 for c in sq.list_customers(limit=100)}

    print("Fetching unpaid invoices...")
    invoices = sq.list_invoices(status="UNPAID")
    
    total_outstanding = 0
    debtors = {}

    for inv in invoices:
        cust_id = inv.get("primary_recipient", {}).get("customer_id")
        name = customers.get(cust_id, "Unknown Customer")
        inv_num = inv.get("invoice_number", "?")
        
        amt_obj = inv.get("payment_requests", [{}])[0].get("computed_amount_money", {})
        amount = amt_obj.get("amount", 0) / 100.0
        
        due_date = inv.get("payment_requests", [{}])[0].get("due_date", "No due date")
        
        if name not in debtors:
            debtors[name] = []
        debtors[name].append({"id": inv_num, "amount": amount, "due": due_date})
        total_outstanding += amount

    print(f"\nTotal Outstanding: ${total_outstanding:.2f}\n")
    
    for name, invs in debtors.items():
        total_client = sum(i['amount'] for i in invs)
        print(f"🔴 {name}: ${total_client:.2f}")
        for i in invs:
            print(f"   - #{i['id']} due {i['due']}: ${i['amount']:.2f}")
        print("")

if __name__ == "__main__":
    list_debtors()
