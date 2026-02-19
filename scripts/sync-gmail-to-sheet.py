#!/usr/bin/env python3
"""
Sync booking/client-related Gmail messages into Ingestion_Gmail.
"""

import json
import urllib.parse
import urllib.request

from universal_sync_helpers import (
    append_ingestion_rows,
    master_client,
    read_existing_external_ids,
    required_row,
)
from google_sheets_api import get_access_token

TAB = "Ingestion_Gmail"


def gmail_get(path: str) -> dict:
    token = get_access_token()
    req = urllib.request.Request(
        f"https://gmail.googleapis.com/gmail/v1/users/me/{path}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    gs = master_client()
    existing = read_existing_external_ids(gs, TAB)

    q = 'newer_than:180d (booking OR invoice OR client OR clean OR Airbnb OR "payment reminder")'
    query = urllib.parse.urlencode({"q": q, "maxResults": "200"})
    data = gmail_get(f"messages?{query}")
    messages = data.get("messages", [])

    rows = []
    for m in messages:
        mid = m.get("id", "")
        if not mid or mid in existing:
            continue
        md = gmail_get(f"messages/{mid}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date")
        headers = {
            h.get("name", ""): h.get("value", "")
            for h in md.get("payload", {}).get("headers", [])
        }
        snippet = md.get("snippet", "")
        row = required_row(
            source="gmail",
            external_id=mid,
            title=headers.get("Subject", "(no subject)"),
            description=snippet,
            party=headers.get("From", ""),
            start_at=headers.get("Date", ""),
            status="unread" if "UNREAD" in md.get("labelIds", []) else "read",
            tags="gmail,client-intake",
            account_type="business",
            updated_at=md.get("internalDate", ""),
        )
        rows.append(row)

    inserted = append_ingestion_rows(gs, TAB, rows)
    print(f"Gmail rows inserted: {inserted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
