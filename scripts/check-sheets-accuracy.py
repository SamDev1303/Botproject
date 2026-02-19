#!/usr/bin/env python3
"""
Google Sheets accuracy guard:
- verifies Square payments are reconciled
- compares unpaid invoice snapshot vs sheet overdue/unpaid snapshot
"""

import argparse
import re
import subprocess

from google_sheets_api import GoogleSheetsAPI
from square_api import SquareAPI
from sheet_router import client as routed_client



def parse_money(value) -> float:
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except Exception:
        return 0.0


def square_sheet_reconcile(days: int) -> tuple[bool, str]:
    out = subprocess.check_output(
        ["python3", "scripts/square_sheets_sync.py", "check", "--days", str(days)],
        text=True,
    )
    ok = "All Square payments found in Google Sheets" in out
    if ok:
        return True, "Square payments reconciled"
    m = re.search(r"(\d+)\s+Square payment\(s\) MISSING", out)
    missing = m.group(1) if m else "unknown"
    return False, f"Square reconciliation mismatch: {missing} missing payment(s)"


def unpaid_compare() -> tuple[bool, str]:
    sq = SquareAPI()
    unpaid = sq.list_invoices(status="UNPAID")
    square_count = len(unpaid)
    square_total = 0.0
    for inv in unpaid:
        amt_obj = inv.get("payment_requests", [{}])[0].get("computed_amount_money", {})
        square_total += (amt_obj.get("amount", 0) or 0) / 100

    gs = routed_client("business")
    rows = gs.read("Client Log!A:L")
    sheet_unpaid = [
        r for r in rows[1:]
        if len(r) > 8 and str(r[8]).strip().lower() in {"overdue", "unpaid"}
    ]
    sheet_total = sum(parse_money(r[6] if len(r) > 6 else 0) for r in sheet_unpaid)

    delta_count = abs(square_count - len(sheet_unpaid))
    delta_total = abs(square_total - sheet_total)
    ok = delta_count <= 1 and delta_total <= 5.0
    msg = (
        f"Square unpaid {square_count} (${square_total:.2f}) vs "
        f"Sheet overdue {len(sheet_unpaid)} (${sheet_total:.2f})"
    )
    return ok, msg


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=90)
    p.add_argument("--task", default="Google Sheets operation")
    args = p.parse_args()

    checks = []
    checks.append(("reconciliation", *square_sheet_reconcile(args.days)))
    checks.append(("unpaid_compare", *unpaid_compare()))

    failed = [c for c in checks if not c[1]]
    print(f"Task: {args.task}")
    for name, ok, msg in checks:
        print(f"- {name}: {'PASS' if ok else 'FAIL'} | {msg}")

    if failed:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
