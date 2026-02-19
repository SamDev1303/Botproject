#!/usr/bin/env python3
"""
Instant expense logger for Bella accounting book.

Writes expense rows to:
1) Master Ops -> Expenses
2) Master Ops -> Bookkeeping
"""

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from google_sheets_api import GoogleSheetsAPI
from sheet_router import client as routed_client, mirror_enabled, ids
TZ = ZoneInfo("Australia/Sydney")


def gst_parts(total: float) -> tuple[float, float]:
    gst = round(total / 11, 2)
    net = round(total - gst, 2)
    return gst, net


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--date", default=datetime.now(TZ).strftime("%Y-%m-%d"))
    p.add_argument("--description", required=True)
    p.add_argument("--amount", required=True, type=float)
    p.add_argument("--account-type", choices=["business", "personal"], default="business")
    p.add_argument("--category", default="Cleaning Supplies")
    p.add_argument("--payment-method", default="Card")
    p.add_argument("--supplier", default="Unknown")
    p.add_argument("--notes", default="")
    p.add_argument("--source", default="Receipt")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    business_gs = routed_client("business")
    personal_gs = routed_client("personal")
    old_master_gs = GoogleSheetsAPI(spreadsheet_id=ids()["old_master"])
    gst, net = gst_parts(args.amount)

    expenses_row = [
        args.date,
        args.category,
        args.description,
        f"${args.amount:.2f}",
        f"${gst:.2f}",
        f"${net:.2f}",
        args.payment_method,
        args.supplier,
        args.source,
        args.notes,
    ]
    bookkeeping_row = [
        args.date,
        "Expense" if args.account_type == "business" else "Personal Expense",
        args.category,
        args.description,
        f"${args.amount:.2f}",
        f"${gst:.2f}",
        f"${net:.2f}",
        args.payment_method,
        "",
        args.supplier,
        args.notes if args.account_type == "business" else f"{args.notes} | PERSONAL_ACCOUNT_DO_NOT_MIX",
    ]

    target_bookkeeping = business_gs if args.account_type == "business" else personal_gs
    r2 = target_bookkeeping.append("Bookkeeping!A:K", bookkeeping_row) if args.account_type == "business" else target_bookkeeping.append("Personal_Expenses!A:G", [
        args.date, args.description, args.category, f"${args.amount:.2f}", args.payment_method, args.source, args.notes
    ])
    if "error" in r2:
        print("ERROR", r2.get("error", ""))
        return 1

    if args.account_type == "business":
        r1 = business_gs.append("Expenses!A:J", expenses_row)
        if "error" in r1:
            print("ERROR", r1.get("error", ""))
            return 1
        if mirror_enabled():
            old_master_gs.append("Expenses!A:J", expenses_row)
            old_master_gs.append("Bookkeeping!A:K", bookkeeping_row)
        print("Business expense logged to Master Ops: Expenses + Bookkeeping")
    else:
        if mirror_enabled():
            old_master_gs.append("Personal_Expenses!A:G", [args.date, args.description, args.category, f"${args.amount:.2f}", args.payment_method, args.source, args.notes])
        print("Personal expense logged to Bookkeeping only (not mixed into business Expenses tab)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
