#!/usr/bin/env python3
"""
Sync Google Calendar events into Ingestion_GCal.
"""

import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from universal_sync_helpers import (
    append_ingestion_rows,
    master_client,
    read_existing_external_ids,
    required_row,
)
from google_sheets_api import get_access_token

TAB = "Ingestion_GCal"


def gcal_get(path: str) -> dict:
    token = get_access_token()
    req = urllib.request.Request(
        f"https://www.googleapis.com/calendar/v3/calendars/primary/{path}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    gs = master_client()
    existing = read_existing_external_ids(gs, TAB)

    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=90)).isoformat()
    end = (now + timedelta(days=365)).isoformat()
    qs = urllib.parse.urlencode(
        {
            "timeMin": start,
            "timeMax": end,
            "singleEvents": "true",
            "orderBy": "startTime",
            "maxResults": "2500",
        }
    )
    data = gcal_get(f"events?{qs}")
    items = data.get("items", [])

    rows = []
    for e in items:
        eid = e.get("id", "")
        if not eid or eid in existing:
            continue
        start_at = e.get("start", {}).get("dateTime", e.get("start", {}).get("date", ""))
        end_at = e.get("end", {}).get("dateTime", e.get("end", {}).get("date", ""))
        attendees = ", ".join([a.get("email", "") for a in e.get("attendees", [])[:5]])
        rows.append(
            required_row(
                source="google_calendar",
                external_id=eid,
                title=e.get("summary", "(no title)"),
                description=e.get("description", ""),
                party=attendees,
                start_at=start_at,
                end_at=end_at,
                status=e.get("status", ""),
                location=e.get("location", ""),
                tags="calendar,booking",
                account_type="business",
                updated_at=e.get("updated", ""),
            )
        )

    inserted = append_ingestion_rows(gs, TAB, rows)
    print(f"Google Calendar rows inserted: {inserted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
