#!/usr/bin/env python3
"""
Reconcile Master Client Log unpaid/overdue statuses with live Square unpaid invoices.
"""

from google_sheets_api import GoogleSheetsAPI
from square_api import SquareAPI
from sheet_router import client as routed_client



def norm_invoice(value: str) -> str:
    v = str(value or "").strip().upper()
    v = v.replace("INVOICE", "").replace("#", "").strip()
    return v


def main() -> int:
    sq = SquareAPI()
    gs = routed_client("business")

    unpaid = sq.list_invoices(status="UNPAID")
    unpaid_map: dict[str, float] = {}
    for inv in unpaid:
        num = norm_invoice(inv.get("invoice_number", ""))
        amt_obj = inv.get("payment_requests", [{}])[0].get("computed_amount_money", {})
        amt = (amt_obj.get("amount", 0) or 0) / 100
        if num:
            unpaid_map[num] = amt

    rows = gs.read("Client Log!A:L")
    updates = 0
    closed = 0
    matched = 0
    for i, row in enumerate(rows[1:], start=2):
        status = str(row[8]).strip().lower() if len(row) > 8 else ""
        if status not in {"overdue", "unpaid"}:
            continue
        inv = norm_invoice(row[7] if len(row) > 7 else "")
        if inv in unpaid_map:
            gs.update(f"Client Log!I{i}", [["Overdue"]])
            gs.update(f"Client Log!G{i}", [[f"${unpaid_map[inv]:.2f}"]])
            matched += 1
            updates += 1
        else:
            gs.update(f"Client Log!I{i}", [["Closed-Legacy"]])
            closed += 1
            updates += 1

    print(f"Updated rows: {updates}")
    print(f"Matched to live unpaid: {matched}")
    print(f"Closed legacy overdue rows: {closed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
