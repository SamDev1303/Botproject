#!/usr/bin/env python3
"""
Sync Apple Calendar events into Ingestion_AppleCal.
"""

import subprocess
import sys
import time

from universal_sync_helpers import (
    append_ingestion_rows,
    master_client,
    read_existing_external_ids,
    required_row,
)

TAB = "Ingestion_AppleCal"


def _run_osascript(script: str, retries: int = 3) -> str:
    for attempt in range(1, retries + 1):
        try:
            return subprocess.check_output(["osascript", "-e", script], text=True).strip()
        except subprocess.CalledProcessError as exc:
            message = (exc.output or str(exc)).lower()
            # macOS returns -600 when Calendar is not running yet.
            if "-600" in message or "isn’t running" in message or "isn't running" in message:
                subprocess.run(["osascript", "-e", 'tell application "Calendar" to activate'], check=False)
                time.sleep(min(2 * attempt, 5))
                continue
            if attempt < retries:
                time.sleep(min(2 * attempt, 5))
                continue
            print(f"WARN: Apple Calendar unavailable after retries: {exc}", file=sys.stderr)
            return ""


def fetch_events() -> list[list[str]]:
    script = r'''
set outLines to ""
tell application "Calendar"
  repeat with c in calendars
    set calName to (name of c) as text
    repeat with ev in (every event of c)
      set eid to (uid of ev) as text
      set ttl to (summary of ev) as text
      set stTxt to (start date of ev) as text
      set enTxt to (end date of ev) as text
      set loc to ""
      try
        set loc to (location of ev) as text
      end try
      set nte to ""
      set outLines to outLines & calName & "	" & eid & "	" & ttl & "	" & stTxt & "	" & enTxt & "	" & loc & "	" & nte & linefeed
    end repeat
  end repeat
end tell
return outLines
'''
    out = _run_osascript(script)
    if not out:
        return []
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 7:
            continue
        rows.append(parts[:7])
    return rows


def main() -> int:
    gs = master_client()
    existing = read_existing_external_ids(gs, TAB)

    rows = []
    for cal_name, eid, title, start_at, end_at, location, notes in fetch_events():
        external_id = f"{cal_name}:{eid}"
        if external_id in existing:
            continue
        rows.append(
            required_row(
                source="apple_calendar",
                external_id=external_id,
                title=title,
                description=notes,
                party=cal_name,
                start_at=start_at,
                end_at=end_at,
                status="scheduled",
                location=location,
                tags="apple-calendar,booking",
                account_type="business",
            )
        )

    inserted = append_ingestion_rows(gs, TAB, rows)
    print(f"Apple Calendar rows inserted: {inserted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
