#!/usr/bin/env python3
"""List upcoming shifts from Connecteam.

Usage:
  python3 list_roster.py              # Next 7 days
  python3 list_roster.py 14           # Next 14 days
  python3 list_roster.py today        # Today only
"""

import sys, time, json
from datetime import datetime, timedelta, timezone, tzinfo

sys.path.insert(0, __import__("os").path.dirname(__file__))
from ct_api import list_shifts, list_users, list_jobs

AEST = timezone(timedelta(hours=11))

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "7"
    now = datetime.now(AEST)

    if arg == "today":
        start = now.replace(hour=0, minute=0, second=0)
        end = now.replace(hour=23, minute=59, second=59)
    else:
        days = int(arg)
        start = now
        end = now + timedelta(days=days)

    start_ts = int(start.timestamp())
    end_ts = int(end.timestamp())

    shifts = list_shifts(start_ts, end_ts)
    users = {u["userId"]: f"{u['firstName']} {u['lastName']}" for u in list_users()}
    jobs = {j["jobId"]: j["title"] for j in list_jobs()}

    if not shifts:
        print("No shifts scheduled.")
        return

    # Sort by start time
    shifts.sort(key=lambda s: s.get("startTime", 0))

    print(f"{'Date':<12} {'Time':<14} {'Staff':<20} {'Job/Location':<20} {'Title'}")
    print("-" * 80)
    for s in shifts:
        st = datetime.fromtimestamp(s["startTime"], AEST)
        et = datetime.fromtimestamp(s["endTime"], AEST)
        assigned = ", ".join(users.get(uid, str(uid)) for uid in s.get("assignedUserIds", []))
        job = jobs.get(s.get("jobId", ""), "—")
        title = s.get("title", "—")
        date_str = st.strftime("%a %d/%m")
        time_str = f"{st.strftime('%H:%M')}-{et.strftime('%H:%M')}"
        print(f"{date_str:<12} {time_str:<14} {assigned:<20} {job:<20} {title}")

if __name__ == "__main__":
    main()
