#!/usr/bin/env python3
"""
Check whether Bella runtime has access to all required connectors.
"""

import json
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

from google_sheets_api import get_access_token, GoogleSheetsAPI
from square_api import SquareAPI
from sheet_router import client as routed_client

TZ = ZoneInfo("Australia/Sydney")


def ok(cmd: list[str]) -> tuple[bool, str]:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=20).strip()
        return True, out
    except Exception as exc:
        return False, str(exc)


def ok_calendar() -> tuple[bool, str]:
    # Calendar can return -600 when app is not running; activate and retry once.
    activate = ["osascript", "-e", 'tell application "Calendar" to activate']
    check = ["osascript", "-e", 'tell application "Calendar" to get name of every calendar']
    subprocess.run(activate, check=False)
    status, out = ok(check)
    if status:
        return status, out
    subprocess.run(activate, check=False)
    return ok(check)


def main() -> int:
    checks = []
    # Google
    try:
        tok = get_access_token()
        checks.append(("google_oauth", bool(tok), "token present"))
    except Exception as exc:
        checks.append(("google_oauth", False, str(exc)))

    # Sheets
    try:
        gs = routed_client("business")
        info = gs.info()
        checks.append(("google_sheets", "error" not in info, info.get("error", "ok")))
    except Exception as exc:
        checks.append(("google_sheets", False, str(exc)))

    # Square
    try:
        sq = SquareAPI()
        locs = sq.list_locations()
        checks.append(("square", True, f"locations={len(locs)}"))
    except Exception as exc:
        checks.append(("square", False, str(exc)))

    # Connecteam
    c_ok, c_out = ok(["python3", "skills/connecteam-roster/scripts/list_staff.py"])
    checks.append(("connecteam", c_ok, c_out[:120]))

    # Apple Calendar/Reminders/Notes
    ac_ok, ac_out = ok_calendar()
    ar_ok, ar_out = ok(["osascript", "-e", 'tell application "Reminders" to get name of every list'])
    an_ok, an_out = ok(
        [
            "osascript",
            "-e",
            'tell application "Notes"\n'
            "set foundName to \"\"\n"
            "repeat with acc in accounts\n"
            "  repeat with f in folders of acc\n"
            "    if (count of notes of f) > 0 then\n"
            "      set foundName to (name of first note of f) as text\n"
            "      exit repeat\n"
            "    end if\n"
            "  end repeat\n"
            "end repeat\n"
            "return foundName\n"
            "end tell",
        ]
    )
    checks.append(("apple_calendar", ac_ok, ac_out[:120]))
    checks.append(("apple_reminders", ar_ok, ar_out[:120]))
    checks.append(("apple_notes", an_ok, an_out[:120]))

    stamp = datetime.now(TZ).isoformat(timespec="seconds")
    gs = routed_client("business")
    for name, status, detail in checks:
        gs.append("SOT_Health!A:D", [stamp, name, "PASS" if status else "FAIL", detail])

    failed = [c for c in checks if not c[1]]
    soft_names = {"apple_calendar", "apple_reminders", "apple_notes"}
    hard_failed = [c for c in failed if c[0] not in soft_names]
    print(json.dumps({"checks": checks, "failed": len(failed), "hard_failed": len(hard_failed)}, indent=2))
    return 1 if hard_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
