#!/usr/bin/env python3
"""
Ensure canonical ingestion/source-of-truth tabs exist in Master Ops sheet.
"""

import argparse

from google_sheets_api import GoogleSheetsAPI
from sheet_router import client as routed_client


INGEST_HEADERS = [
    "source",
    "external_id",
    "title",
    "description",
    "party",
    "start_at",
    "end_at",
    "status",
    "amount",
    "currency",
    "location",
    "tags",
    "account_type",
    "updated_at",
    "ingested_at",
]

STANDARD_TABS = {
    "Ingestion_Gmail": INGEST_HEADERS,
    "Ingestion_GCal": INGEST_HEADERS,
    "Ingestion_AppleCal": INGEST_HEADERS,
    "Ingestion_Reminders": INGEST_HEADERS,
    "Ingestion_Connecteam": INGEST_HEADERS,
    "Ingestion_AppleNotes": INGEST_HEADERS,
    "Unified_Bookings": [
        "record_key", "source", "title", "party", "date", "start_at", "end_at",
        "status", "location", "tags", "last_updated", "resolution_note",
    ],
    "Unified_Clients": [
        "client_key", "client_name", "phone", "email", "source", "latest_event",
        "latest_date", "status", "notes",
    ],
    "Business_Expenses": [
        "date", "description", "category", "amount_inc_gst", "gst", "amount_ex_gst",
        "payment_method", "supplier", "source", "notes",
    ],
    "Personal_Expenses": [
        "date", "description", "category", "amount", "payment_method", "source", "notes",
    ],
    "SOT_Dashboard": [
        "metric", "value", "updated_at", "source",
    ],
    "SOT_Health": [
        "timestamp", "check", "status", "details",
    ],
    "Sync_Errors": [
        "timestamp", "source", "stage", "error", "run_id",
    ],
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sheet-id", default="")
    args = p.parse_args()
    gs = GoogleSheetsAPI(spreadsheet_id=args.sheet_id) if args.sheet_id else routed_client("business")
    meta = gs.info()
    if "error" in meta:
        raise RuntimeError(meta["error"])

    existing = {
        s["properties"]["title"]: s["properties"]["sheetId"]
        for s in meta.get("sheets", [])
    }

    requests = []
    for name in STANDARD_TABS:
        if name not in existing:
            requests.append({"addSheet": {"properties": {"title": name}}})

    if requests:
        gs.batch_update_spreadsheet(requests)
        meta = gs.info()
        existing = {
            s["properties"]["title"]: s["properties"]["sheetId"]
            for s in meta.get("sheets", [])
        }

    updates = []
    for name, headers in STANDARD_TABS.items():
        updates.append({"range": f"{name}!A1:{chr(64 + len(headers))}1", "values": [headers]})
    gs._request("/values:batchUpdate?valueInputOption=RAW", method="POST", data={"data": updates})
    print(f"Ensured {len(STANDARD_TABS)} canonical tabs with headers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
