
import json
from square_api import SquareAPI

sq = SquareAPI()
invoices = sq.list_invoices()
for inv in invoices:
    if inv.get("invoice_number") == "000005":
        print(json.dumps(inv, indent=2))
