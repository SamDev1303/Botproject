#!/usr/bin/env python3
"""
Sync business-relevant Apple Notes into Ingestion_AppleNotes.
"""

import subprocess

from universal_sync_helpers import (
    append_ingestion_rows,
    master_client,
    read_existing_external_ids,
    required_row,
)

TAB = "Ingestion_AppleNotes"
KEYWORDS = ["booking", "airbnb", "air bnb", "client", "invoice", "clean", "roster", "shift"]


def fetch_business_notes() -> list[tuple[str, str, str]]:
    script = r'''
set outLines to ""
tell application "Notes"
  repeat with acc in accounts
    repeat with f in folders of acc
      repeat with n in notes of f
        set nid to (id of n) as text
        set nm to (name of n) as text
        set bd to (body of n) as text
        set outLines to outLines & nid & "	" & nm & "	" & bd & linefeed
      end repeat
    end repeat
  end repeat
end tell
return outLines
'''
    out = subprocess.check_output(["osascript", "-e", script], text=True)
    rows: list[tuple[str, str, str]] = []
    for line in out.splitlines():
        if "\t" not in line:
            continue
        parts = line.split("\t", 2)
        if len(parts) < 3:
            continue
        note_id, name, body = parts
        low = f"{name} {body}".lower()
        if any(k in low for k in KEYWORDS):
            rows.append((note_id.strip(), name.strip(), body.strip()))
    return rows


def main() -> int:
    gs = master_client()
    existing = read_existing_external_ids(gs, TAB)

    rows = []
    for note_id, name, body in fetch_business_notes():
        external_id = f"note:{note_id}"
        if external_id in existing:
            continue
        compact_body = (
            body.replace("\n", " ")
            .replace("<div>", " ")
            .replace("</div>", " ")
            .replace("<br>", " ")
        )[:600]
        rows.append(
            required_row(
                source="apple_notes",
                external_id=external_id,
                title=name,
                description=compact_body,
                party="Apple Notes",
                status="captured",
                tags="notes,intake",
                account_type="business",
            )
        )
    inserted = append_ingestion_rows(gs, TAB, rows)
    print(f"Apple Notes ingestion rows inserted: {inserted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
