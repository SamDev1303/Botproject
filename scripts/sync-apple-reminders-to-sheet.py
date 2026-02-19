#!/usr/bin/env python3
"""
Sync Apple Reminders into Ingestion_Reminders.
"""

import subprocess

from universal_sync_helpers import (
    append_ingestion_rows,
    master_client,
    read_existing_external_ids,
    required_row,
)

TAB = "Ingestion_Reminders"


def fetch_reminders() -> list[list[str]]:
    script = r'''
set outLines to ""
tell application "Reminders"
  repeat with rl in lists
    set listName to (name of rl) as text
    repeat with r in reminders of rl
      set rid to (id of r) as text
      set nm to (name of r) as text
      set bodyTxt to ""
      try
        set bodyTxt to (body of r) as text
      end try
      set dueTxt to ""
      try
        if due date of r is not missing value then set dueTxt to (due date of r) as text
      end try
      set doneTxt to "pending"
      try
        if completed of r then set doneTxt to "completed"
      end try
      set outLines to outLines & listName & "	" & rid & "	" & nm & "	" & dueTxt & "	" & doneTxt & "	" & bodyTxt & linefeed
    end repeat
  end repeat
end tell
return outLines
'''
    out = subprocess.check_output(["osascript", "-e", script], text=True).strip()
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 6:
            continue
        rows.append(parts[:6])
    return rows


def main() -> int:
    gs = master_client()
    existing = read_existing_external_ids(gs, TAB)

    rows = []
    for list_name, rid, title, due_at, status, body in fetch_reminders():
        external_id = f"{list_name}:{rid}"
        if external_id in existing:
            continue
        rows.append(
            required_row(
                source="apple_reminders",
                external_id=external_id,
                title=title,
                description=body,
                party=list_name,
                start_at=due_at,
                end_at="",
                status=status,
                location="",
                tags="reminder,todo",
                account_type="business",
            )
        )

    inserted = append_ingestion_rows(gs, TAB, rows)
    print(f"Apple Reminders rows inserted: {inserted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
