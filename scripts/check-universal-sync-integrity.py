#!/usr/bin/env python3
"""
Validate ingestion/unified sheet integrity.
"""

from google_sheets_api import GoogleSheetsAPI
from sheet_router import client as routed_client

BUSINESS_TABS = [
    "Ingestion_Gmail",
    "Ingestion_GCal",
    "Ingestion_AppleCal",
    "Ingestion_Reminders",
    "Ingestion_AppleNotes",
]
STAFF_TABS = ["Ingestion_Connecteam"]


def main() -> int:
    gs = routed_client("business")
    failed = []
    for tab in BUSINESS_TABS:
        rows = gs.read(f"{tab}!A:O")
        ext_ids = []
        for r in rows[1:]:
            if len(r) < 2:
                failed.append(f"{tab}: malformed row")
                continue
            ext = str(r[1]).strip()
            if not ext:
                failed.append(f"{tab}: missing external_id")
            ext_ids.append(ext)
            acct = str(r[12]).strip().lower() if len(r) > 12 else ""
            if acct not in {"business", "personal"}:
                failed.append(f"{tab}: invalid account_type={acct or 'empty'}")
        if len(ext_ids) != len(set(ext_ids)):
            failed.append(f"{tab}: duplicate external_id detected")

    for tab in STAFF_TABS:
        sgs = routed_client("staff")
        rows = sgs.read(f"{tab}!A:O")
        ext_ids = []
        for r in rows[1:]:
            if len(r) < 2:
                failed.append(f"{tab}: malformed row")
                continue
            ext = str(r[1]).strip()
            if not ext:
                failed.append(f"{tab}: missing external_id")
            ext_ids.append(ext)
        if len(ext_ids) != len(set(ext_ids)):
            failed.append(f"{tab}: duplicate external_id detected")

    ub = gs.read("Unified_Bookings!A:L")
    if len(ub) <= 1:
        failed.append("Unified_Bookings: empty")

    if failed:
        print("FAIL")
        for f in failed[:100]:
            print(f"- {f}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
