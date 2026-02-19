#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from google_sheets_api import GoogleSheetsAPI, get_access_token
from sheet_router import client as routed_client

TZ = ZoneInfo("Australia/Sydney")
MASTER_ID = "1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU"


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def master_client() -> GoogleSheetsAPI:
    return routed_client("business")


def read_existing_external_ids(gs: GoogleSheetsAPI, tab: str) -> set[str]:
    try:
        rows = gs.read(f"{tab}!A:B")
    except Exception:
        return set()
    return {str(r[1]).strip() for r in rows[1:] if len(r) > 1 and str(r[1]).strip()}


def append_ingestion_rows(gs: GoogleSheetsAPI, tab: str, rows: list[list[str]]) -> int:
    if not rows:
        return 0
    gs.append_rows(f"{tab}!A:O", rows)
    return len(rows)


def required_row(
    source: str,
    external_id: str,
    title: str = "",
    description: str = "",
    party: str = "",
    start_at: str = "",
    end_at: str = "",
    status: str = "",
    amount: str = "",
    currency: str = "AUD",
    location: str = "",
    tags: str = "",
    account_type: str = "business",
    updated_at: str = "",
) -> list[str]:
    return [
        source,
        external_id,
        title,
        description,
        party,
        start_at,
        end_at,
        status,
        amount,
        currency,
        location,
        tags,
        account_type,
        updated_at or now_iso(),
        now_iso(),
    ]
