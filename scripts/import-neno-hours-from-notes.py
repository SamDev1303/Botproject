#!/usr/bin/env python3
"""
Import Neno/Teenay worked hours from Apple Notes into Master Ops -> Staff & Wages.
"""

import re
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

from google_sheets_api import GoogleSheetsAPI
from sheet_router import client as routed_client

TZ = ZoneInfo("Australia/Sydney")


def run_osascript(script: str) -> str:
    return subprocess.check_output(["osascript", "-e", script], text=True).strip()


def fetch_note_body() -> str:
    # Primary note name per latest rename, fallback to old.
    for note_name in ["teenay sadka", "Staffs hours"]:
        script = (
            'tell application "Notes"\n'
            f'  set targetName to "{note_name}"\n'
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
        body = run_osascript(script)
        if body:
            return body
    return ""


def strip_html(s: str) -> str:
    s = re.sub(r"<br\\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</div>", "\n", s, flags=re.I)
    s = re.sub(r"</h1>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("\xa0", " ")
    return s


def parse_date(text: str) -> str:
    text_l = text.lower()
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s*([a-z]{3,9})\b", text_l)
    if not m:
        m = re.search(r"\b([a-z]{3,9})\s*(\d{1,2})(?:st|nd|rd|th)?\b", text_l)
        if not m:
            return ""
        month_str = m.group(1)
        day = int(m.group(2))
    else:
        day = int(m.group(1))
        month_str = m.group(2)

    months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    month = months.get(month_str[:3])
    if not month:
        return ""
    year = datetime.now(TZ).year
    try:
        return datetime(year, month, day).strftime("%Y-%m-%d")
    except ValueError:
        return ""


def extract_hours(line: str) -> float:
    vals = re.findall(r"(\d+(?:\.\d+)?)\s*hours?", line.lower())
    if not vals:
        return 0.0
    return sum(float(v) for v in vals)


def main() -> int:
    body = fetch_note_body()
    if not body:
        print("No note body found for teenay/Staffs hours.")
        return 1

    text = strip_html(body)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    gs = routed_client("staff")
    existing = gs.read("Staff & Wages!A:N")
    existing_tags = {str(r[13]).strip() for r in existing[1:] if len(r) > 13}

    rows = []
    in_target_section = False
    pay_counter = len(existing)

    for raw in lines:
        line = raw.strip()
        low = line.lower()

        # Section markers by name
        if low in {"teenay", "neno", "teenay "} or "teenay" == low:
            in_target_section = True
            continue
        if low in {"cara"}:
            in_target_section = False
            continue

        if not in_target_section:
            continue

        hrs = extract_hours(line)
        if hrs <= 0:
            continue

        date = parse_date(line)
        note_tag = f"AppleNote:teenay sadka::{line}"
        if note_tag in existing_tags:
            continue

        pay_counter += 1
        pay_id = f"NENO-{datetime.now(TZ).strftime('%Y%m%d')}-{pay_counter}"
        row = [
            pay_id,                 # Pay_ID
            "Neno",                 # Staff Name
            "Cleaner",              # Role
            "Employee",             # Type
            date,                   # Period Start
            date,                   # Period End
            f"{hrs:.2f}",           # Hours Worked
            "",                     # Hourly Rate
            "",                     # Gross Pay
            "",                     # PAYG
            "",                     # Super
            "",                     # Net Pay
            "",                     # ABN
            note_tag,               # Notes
        ]
        rows.append(row)
        existing_tags.add(note_tag)

    if rows:
        gs.append_rows("Staff & Wages!A:N", rows)

    print(f"Neno hour rows added: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
