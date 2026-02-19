#!/usr/bin/env python3
"""
Create 3 canonical sheets and copy sharing permissions from old Master sheet.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from google_sheets_api import get_access_token
from sot_policy import load_policy, save_policy

MASTER_OLD_ID = "1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU"

BUSINESS_TABS = [
    "Client Log",
    "Bookkeeping",
    "Income Ledger",
    "Expenses",
    "Business_Expenses",
    "Tax_GST_BAS",
    "P&L Summary",
    "Outstanding Invoices",
    "Airbnb Cleans",
    "Non-Airbnb Jobs",
    "Task Log",
    "Bot_Change_Log",
    "SOT_Dashboard",
    "SOT_Health",
    "Sync_Errors",
    "Ingestion_Gmail",
    "Ingestion_GCal",
    "Ingestion_AppleCal",
    "Ingestion_Reminders",
    "Ingestion_AppleNotes",
    "Unified_Bookings",
    "Unified_Clients",
]

STAFF_TABS = [
    "Staff Registry",
    "Staff_Hours",
    "Staff & Wages",
    "Payroll_Calculations",
    "Properties",
    "Property_Schedule",
    "Connecteam_Roster",
    "Ingestion_Connecteam",
    "Roster_Audit_Log",
    "Task Log",
    "Bot_Change_Log",
]

PERSONAL_TABS = [
    "Personal_Expenses",
    "Personal_Budget",
    "Personal_Income",
    "Personal_Reminders",
    "Personal_Calendar",
    "Personal_Notes_Intake",
    "Task Log",
    "Bot_Change_Log",
]


def req(url: str, method: str = "GET", data: dict | None = None) -> dict[str, Any]:
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, headers=headers, data=body, method=method)
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())


def create_spreadsheet(title: str, tabs: list[str]) -> str:
    payload = {
        "properties": {"title": title},
        "sheets": [{"properties": {"title": t}} for t in tabs],
    }
    d = req("https://sheets.googleapis.com/v4/spreadsheets", "POST", payload)
    return d["spreadsheetId"]


def drive_permissions(file_id: str) -> list[dict]:
    d = req(
        "https://www.googleapis.com/drive/v3/files/"
        + file_id
        + "?fields=permissions(id,type,emailAddress,role)"
    )
    return d.get("permissions", [])


def copy_permissions(src_id: str, dst_id: str) -> None:
    for p in drive_permissions(src_id):
        ptype = p.get("type")
        role = p.get("role")
        if role == "owner":
            continue
        payload: dict[str, Any] = {"role": role, "type": ptype}
        if ptype in {"user", "group"} and p.get("emailAddress"):
            payload["emailAddress"] = p["emailAddress"]
        try:
            req(
                f"https://www.googleapis.com/drive/v3/files/{dst_id}/permissions?sendNotificationEmail=false",
                "POST",
                payload,
            )
        except urllib.error.HTTPError:
            # ignore duplicates/unsupported inherited permissions
            pass


def write_headers(sheet_id: str, tab: str, headers: list[str]) -> None:
    rng = f"{tab}!A1:{chr(64 + len(headers))}1"
    req(
        f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values:batchUpdate?valueInputOption=RAW",
        "POST",
        {"data": [{"range": rng, "values": [headers]}]},
    )


def bootstrap_headers(sheet_id: str, tabs: list[str]) -> None:
    default_headers = ["record_id", "created_at", "updated_at", "status", "notes"]
    for tab in tabs:
        if tab in {"Task Log"}:
            headers = ["timestamp", "task_type", "description", "tool", "status", "duration", "triggered_by", "notes"]
        elif tab in {"Bot_Change_Log"}:
            headers = ["timestamp", "user", "tab", "row", "action", "before", "after", "reason"]
        elif tab.startswith("Ingestion_"):
            headers = [
                "source", "external_id", "title", "description", "party", "start_at", "end_at",
                "status", "amount", "currency", "location", "tags", "account_type", "updated_at", "ingested_at",
            ]
        elif tab in {"SOT_Dashboard"}:
            headers = ["metric", "value", "updated_at", "source"]
        elif tab in {"SOT_Health", "Sync_Errors"}:
            headers = ["timestamp", "check", "status", "details", "run_id"]
        else:
            headers = default_headers
        write_headers(sheet_id, tab, headers)


def main() -> int:
    business_id = create_spreadsheet("Clean Up Bros - Business Ops", BUSINESS_TABS)
    staff_id = create_spreadsheet("Clean Up Bros - Staff & Properties", STAFF_TABS)
    personal_id = create_spreadsheet("Hafsah - Personal Ledger", PERSONAL_TABS)

    copy_permissions(MASTER_OLD_ID, business_id)
    copy_permissions(MASTER_OLD_ID, staff_id)
    copy_permissions(MASTER_OLD_ID, personal_id)

    bootstrap_headers(business_id, BUSINESS_TABS)
    bootstrap_headers(staff_id, STAFF_TABS)
    bootstrap_headers(personal_id, PERSONAL_TABS)

    policy = load_policy()
    sot = policy.setdefault("source_of_truth", {})
    sot["business_ops_sheet_id"] = business_id
    sot["staff_properties_sheet_id"] = staff_id
    sot["personal_sheet_id"] = personal_id
    rules = policy.setdefault("rules", {})
    rules["mirror_old_master"] = True
    save_policy(policy)

    print(json.dumps({
        "business_ops_sheet_id": business_id,
        "staff_properties_sheet_id": staff_id,
        "personal_sheet_id": personal_id,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
