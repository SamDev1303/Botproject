#!/usr/bin/env python3
"""
Import booking data from Apple Notes into Master Ops Google Sheet.

Targets:
- Apple Note: "Air bnb booking" -> "Airbnb Cleans" tab
- Apple Note: "Claudia’s booking" -> "Client Log" summary row
"""

import re
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

from google_sheets_api import GoogleSheetsAPI
from sheet_router import client as routed_client

TZ = ZoneInfo("Australia/Sydney")

MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

PROPERTY_MAP = [
    ("pinnacle", ("PROP-001", "Pinnacle")),
    ("nagle", ("PROP-002", "Nagle St")),
    ("unit 3", ("PROP-003", "Atkinson U3")),
    ("u3", ("PROP-003", "Atkinson U3")),
    ("unit 4", ("PROP-004", "Atkinson U4")),
    ("u4", ("PROP-004", "Atkinson U4")),
]


def run_osascript(script: str) -> str:
    return subprocess.check_output(["osascript", "-e", script], text=True).strip()


def fetch_note(name: str) -> str:
    script = (
        'tell application "Notes"\n'
        f'  set targetName to "{name}"\n'
        '  repeat with acc in accounts\n'
        '    repeat with f in folders of acc\n'
        '      repeat with n in notes of f\n'
        '        if (name of n as text) is targetName then\n'
        '          return (body of n as text)\n'
        '        end if\n'
        '      end repeat\n'
        '    end repeat\n'
        '  end repeat\n'
        'end tell\n'
        'return ""'
    )
    return run_osascript(script)


def strip_html(s: str) -> str:
    s = re.sub(r"<br\\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</div>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("\xa0", " ")
    return s


def parse_date_from_line(line: str) -> str:
    text = line.lower()
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s*(?:of\s*)?([a-z]{3,9})\b", text)
    if not m:
        m = re.search(r"\b([a-z]{3,9})\s*(\d{1,2})(?:st|nd|rd|th)?\b", text)
        if not m:
            return ""
        month_name = m.group(1)
        day = int(m.group(2))
    else:
        day = int(m.group(1))
        month_name = m.group(2)

    month = MONTHS.get(month_name[:3], MONTHS.get(month_name))
    if not month:
        return ""

    now = datetime.now(TZ)
    year = now.year
    # Handle Dec/Jan historical planning entries by choosing nearest plausible year.
    if month >= 11 and now.month <= 2:
        year -= 1
    try:
        dt = datetime(year, month, day)
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return ""


def parse_property(line: str) -> tuple[str, str]:
    l = line.lower()
    for key, value in PROPERTY_MAP:
        if key in l:
            return value
    return ("", "Unknown")


def unique_rows(existing: list[list], rows: list[list], note_tag: str) -> list[list]:
    existing_notes = {str(r[14]).strip() for r in existing[1:] if len(r) > 14}
    out = []
    for r in rows:
        if r[14] in existing_notes:
            continue
        out.append(r)
    return out


def import_airbnb(gs: GoogleSheetsAPI) -> int:
    body = fetch_note("Air bnb booking")
    if not body:
        return 0
    text = strip_html(body)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    lines = [ln for ln in lines if "air bnb booking" not in ln.lower()]

    existing = gs.read("Airbnb Cleans!A:O")
    rows = []
    counter = len(existing)
    for ln in lines:
        date = parse_date_from_line(ln)
        prop_id, prop_name = parse_property(ln)
        counter += 1
        clean_id = f"APN-{datetime.now(TZ).strftime('%Y%m%d')}-{counter}"
        note_tag = f"AppleNote:Air bnb booking::{ln}"
        rows.append([
            clean_id,                 # Clean_ID
            date,                     # Date
            prop_id,                  # Property_ID
            prop_name,                # Property Name
            "", "",                   # Check-In, Check-Out
            "Airbnb Turnover",        # Service Type
            "", "",                   # Staff, Hours
            "", "", "", "",           # Fee/GST/Total/Invoice
            "Imported",               # Status
            note_tag,                 # Notes
        ])

    deduped = unique_rows(existing, rows, "AppleNote:Air bnb booking")
    if deduped:
        gs.append_rows("Airbnb Cleans!A:O", deduped)
    return len(deduped)


def import_claudia(gs: GoogleSheetsAPI) -> int:
    body = fetch_note("Claudia’s booking")
    if not body:
        return 0
    text = strip_html(body)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    lines = [ln for ln in lines if "claudia" not in ln.lower()]
    if not lines:
        return 0

    existing = gs.read("Client Log!A:L")
    note_blob = "AppleNote:Claudia’s booking::" + ", ".join(lines)
    for r in existing[1:]:
        if len(r) > 11 and note_blob == str(r[11]).strip():
            return 0

    row = [
        datetime.now(TZ).strftime("%Y-%m-%d"),
        "Claudia",
        "",
        "",
        "Recurring Clean",
        "",
        "",
        "",
        "Active Client",
        "",
        "Apple Notes",
        note_blob,
    ]
    gs.append("Client Log!A:L", row)
    return 1


def main() -> int:
    gs = routed_client("business")
    airbnb_added = import_airbnb(gs)
    claudia_added = import_claudia(gs)
    print(f"Airbnb rows added: {airbnb_added}")
    print(f"Claudia rows added: {claudia_added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
