#!/usr/bin/env python3

from __future__ import annotations

from google_sheets_api import GoogleSheetsAPI
from sot_policy import load_policy

def ids() -> dict:
    p = load_policy().get("source_of_truth", {})
    business = p.get("business_ops_sheet_id", "")
    staff = p.get("staff_properties_sheet_id", "")
    personal = p.get("personal_sheet_id", "")
    return {
        "business": business,
        "staff": staff or business,
        "personal": personal or business,
    }


def client(kind: str) -> GoogleSheetsAPI:
    m = ids()
    sid = m.get(kind) or m.get("business")
    if not sid:
        raise RuntimeError("No business_ops_sheet_id configured in config/bella-sot-policy.json")
    return GoogleSheetsAPI(spreadsheet_id=sid)


def mirror_enabled() -> bool:
    p = load_policy().get("rules", {})
    return bool(p.get("mirror_old_master", False))
