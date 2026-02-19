#!/usr/bin/env python3
"""
Sync live Square unpaid invoices into Master Client Log as current overdue entries.
"""

from google_sheets_api import GoogleSheetsAPI
from square_api import SquareAPI
from sheet_router import client as routed_client



def norm_invoice(value: str) -> str:
    return str(value or "").upper().replace("INVOICE", "").replace("#", "").strip()


def main() -> int:
    gs = routed_client("business")
    sq = SquareAPI()

    rows = gs.read("Client Log!A:L")
    existing = {norm_invoice(r[7] if len(r) > 7 else "") for r in rows[1:]}

    unpaid = sq.list_invoices(status="UNPAID")
    to_add = []
    for inv in unpaid:
        inv_num_raw = str(inv.get("invoice_number", "")).strip()
        inv_num_norm = norm_invoice(inv_num_raw)
        if not inv_num_norm or inv_num_norm in existing:
            continue

        payment_req = inv.get("payment_requests", [{}])[0]
        amount = (payment_req.get("computed_amount_money", {}).get("amount", 0) or 0) / 100
        due_date = payment_req.get("due_date", "")
        created = inv.get("created_at", "")[:10]
        invoice_display = inv_num_raw if "#" in inv_num_raw else f"#{inv_num_raw}"
        row = [
            due_date or created,          # Date
            "Square Invoice",             # Client Name
            "", "",                       # Phone, Email
            "Cleaning",                   # Service Type
            "",                           # Location/Suburb
            f"${amount:.2f}",             # Quote Amount
            invoice_display,              # Invoice #
            "Overdue",                    # Payment Status
            "$0.00",                      # Amount Paid
            "Square Live Sync",           # Source
            "Auto-synced from Square unpaid invoices",
        ]
        to_add.append(row)

    if to_add:
        gs.append_rows("Client Log!A:L", to_add)
    print(f"Added overdue rows: {len(to_add)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
