#!/usr/bin/env python3
"""
Validate row-count parity for key tabs between old master and new sheets.
"""

from google_sheets_api import GoogleSheetsAPI
from sot_policy import load_policy

OLD_MASTER = "1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU"

CHECKS = [
    ("Client Log", "business_ops_sheet_id", "Client Log"),
    ("Bookkeeping", "business_ops_sheet_id", "Bookkeeping"),
    ("Airbnb Cleans", "business_ops_sheet_id", "Airbnb Cleans"),
    ("Non-Airbnb Jobs", "business_ops_sheet_id", "Non-Airbnb Jobs"),
    ("Staff & Wages", "staff_properties_sheet_id", "Staff & Wages"),
    ("Properties", "staff_properties_sheet_id", "Properties"),
    ("Personal_Expenses", "personal_sheet_id", "Personal_Expenses"),
]


def row_count(gs: GoogleSheetsAPI, tab: str) -> int:
    rows = gs.read(f"{tab}!A:Z")
    if not rows:
        return 0
    body = rows[1:] if len(rows) > 1 else []
    count = 0
    for r in body:
        if any(str(c).strip() for c in r):
            count += 1
    return count


def main() -> int:
    policy = load_policy()
    old = GoogleSheetsAPI(spreadsheet_id=OLD_MASTER)
    id_map = policy.get("source_of_truth", {})

    fails = []
    for src_tab, role, dst_tab in CHECKS:
        dst_id = id_map.get(role, "")
        if not dst_id:
            fails.append(f"missing policy id for {role}")
            continue
        dst = GoogleSheetsAPI(spreadsheet_id=dst_id)
        c_src = row_count(old, src_tab)
        c_dst = row_count(dst, dst_tab)
        print(f"{src_tab} -> {dst_tab}: old={c_src} new={c_dst}")
        if c_dst < c_src:
            fails.append(f"{src_tab}: new<{c_src} old, got {c_dst}")

    if fails:
        print("FAIL")
        for f in fails:
            print("-", f)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
