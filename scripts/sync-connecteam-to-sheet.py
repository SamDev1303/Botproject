#!/usr/bin/env python3
"""
Sync upcoming Connecteam roster data into Ingestion_Connecteam.
"""

import sys
from datetime import datetime, timedelta, timezone

from universal_sync_helpers import (
    append_ingestion_rows,
    read_existing_external_ids,
    required_row,
)
from sheet_router import client as routed_client

sys.path.insert(0, "/Users/hafsahnuzhat/Desktop/🦀/skills/connecteam-roster/scripts")
from ct_api import list_shifts, list_users, list_jobs  # type: ignore

TAB = "Ingestion_Connecteam"
AEST = timezone(timedelta(hours=11))


def main() -> int:
    gs = routed_client("staff")
    existing = read_existing_external_ids(gs, TAB)

    now = datetime.now(AEST)
    start_ts = int((now - timedelta(days=30)).timestamp())
    end_ts = int((now + timedelta(days=90)).timestamp())
    shifts = list_shifts(start_ts, end_ts)
    users = {u["userId"]: f"{u.get('firstName','')} {u.get('lastName','')}".strip() for u in list_users()}
    jobs = {j["jobId"]: j.get("title", "") for j in list_jobs()}

    rows = []
    for s in shifts:
        shift_id = str(s.get("shiftId", ""))
        if not shift_id or shift_id in existing:
            continue
        assigned_ids = s.get("assignedUserIds", []) or []
        assigned = ", ".join(users.get(uid, str(uid)) for uid in assigned_ids)
        job_name = jobs.get(s.get("jobId", ""), "")
        st = datetime.fromtimestamp(s.get("startTime", 0), AEST).isoformat(timespec="minutes")
        en = datetime.fromtimestamp(s.get("endTime", 0), AEST).isoformat(timespec="minutes")
        title = s.get("title", job_name or "Shift")
        rows.append(
            required_row(
                source="connecteam",
                external_id=shift_id,
                title=title,
                description=f"job={job_name}",
                party=assigned,
                start_at=st,
                end_at=en,
                status="scheduled",
                location=job_name,
                tags="roster,shift,connecteam",
                account_type="business",
            )
        )

    inserted = append_ingestion_rows(gs, TAB, rows)
    print(f"Connecteam rows inserted: {inserted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
