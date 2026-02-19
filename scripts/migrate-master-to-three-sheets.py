#!/usr/bin/env python3
"""
Migrate data from old Master sheet into the new 3-sheet model.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from google_sheets_api import GoogleSheetsAPI
from sot_policy import load_policy

OLD_MASTER = "1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU"
TZ = ZoneInfo("Australia/Sydney")

BUSINESS_MAP = {
    "Client Log": "Client Log",
    "Bookkeeping": "Bookkeeping",
    "Income Ledger": "Income Ledger",
    "Expenses": "Expenses",
    "Business_Expenses": "Business_Expenses",
    "P&L Summary": "P&L Summary",
    "Airbnb Cleans": "Airbnb Cleans",
    "Non-Airbnb Jobs": "Non-Airbnb Jobs",
    "Task Log": "Task Log",
    "Bot_Change_Log": "Bot_Change_Log",
    "Ingestion_Gmail": "Ingestion_Gmail",
    "Ingestion_GCal": "Ingestion_GCal",
    "Ingestion_AppleCal": "Ingestion_AppleCal",
    "Ingestion_Reminders": "Ingestion_Reminders",
    "Ingestion_AppleNotes": "Ingestion_AppleNotes",
    "Unified_Bookings": "Unified_Bookings",
    "Unified_Clients": "Unified_Clients",
    "SOT_Dashboard": "SOT_Dashboard",
    "SOT_Health": "SOT_Health",
    "Sync_Errors": "Sync_Errors",
}

STAFF_MAP = {
    "Properties": "Properties",
    "Staff & Wages": "Staff & Wages",
    "Ingestion_Connecteam": "Ingestion_Connecteam",
    "Task Log": "Task Log",
    "Bot_Change_Log": "Bot_Change_Log",
}

PERSONAL_MAP = {
    "Personal_Expenses": "Personal_Expenses",
    "Personal Budget": "Personal_Budget",
    "Task Log": "Task Log",
    "Bot_Change_Log": "Bot_Change_Log",
}


def clone_tab(src: GoogleSheetsAPI, dst: GoogleSheetsAPI, src_tab: str, dst_tab: str) -> int:
    try:
        rows = src.read(f"{src_tab}!A:Z")
    except Exception:
        return 0
    if not rows:
        return 0
    # keep destination header and append body rows only
    body = rows[1:] if len(rows) > 1 else []
    if body:
        dst.append_rows(f"{dst_tab}!A:Z", body)
    return len(body)


def main() -> int:
    p = load_policy()
    b_id = p["source_of_truth"]["business_ops_sheet_id"]
    s_id = p["source_of_truth"]["staff_properties_sheet_id"]
    per_id = p["source_of_truth"]["personal_sheet_id"]

    old = GoogleSheetsAPI(spreadsheet_id=OLD_MASTER)
    b = GoogleSheetsAPI(spreadsheet_id=b_id)
    s = GoogleSheetsAPI(spreadsheet_id=s_id)
    per = GoogleSheetsAPI(spreadsheet_id=per_id)

    counts = {"business": 0, "staff": 0, "personal": 0}
    for st, dt in BUSINESS_MAP.items():
        counts["business"] += clone_tab(old, b, st, dt)
    for st, dt in STAFF_MAP.items():
        counts["staff"] += clone_tab(old, s, st, dt)
    for st, dt in PERSONAL_MAP.items():
        counts["personal"] += clone_tab(old, per, st, dt)

    stamp = datetime.now(TZ).isoformat(timespec="seconds")
    b.append("Task Log!A:H", [stamp, "Migration", f"Old master -> Business rows={counts['business']}", "migrate-master-to-three-sheets.py", "SUCCESS", "", "Bella Auto", ""])
    s.append("Task Log!A:H", [stamp, "Migration", f"Old master -> Staff rows={counts['staff']}", "migrate-master-to-three-sheets.py", "SUCCESS", "", "Bella Auto", ""])
    per.append("Task Log!A:H", [stamp, "Migration", f"Old master -> Personal rows={counts['personal']}", "migrate-master-to-three-sheets.py", "SUCCESS", "", "Bella Auto", ""])

    print(counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
