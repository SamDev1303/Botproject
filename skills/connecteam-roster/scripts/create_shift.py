#!/usr/bin/env python3
"""Create a shift on Connecteam.

Usage:
  python3 create_shift.py --title "End of Lease" --staff "Teenay" --date 2026-02-20 --start 09:00 --end 14:00 --job "AIRBNB"
  python3 create_shift.py --title "General Clean" --staff "Teenay,Shamal" --date 2026-02-20 --start 10:00 --end 12:00 --notes "3BR, bring steam cleaner"
"""

import argparse, sys, json
from datetime import datetime, timedelta, timezone

sys.path.insert(0, __import__("os").path.dirname(__file__))
from ct_api import create_shifts, resolve_user, resolve_job, SCHEDULER_ID, TZ

AEST = timezone(timedelta(hours=11))

def to_unix(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt = dt.replace(tzinfo=AEST)
    return int(dt.timestamp())

def main():
    p = argparse.ArgumentParser(description="Create a Connecteam shift")
    p.add_argument("--title", required=True, help="Shift title")
    p.add_argument("--staff", required=True, help="Staff name(s), comma-separated")
    p.add_argument("--date", required=True, help="Date YYYY-MM-DD")
    p.add_argument("--start", required=True, help="Start time HH:MM")
    p.add_argument("--end", required=True, help="End time HH:MM")
    p.add_argument("--job", default=None, help="Job/location name")
    p.add_argument("--notes", default=None, help="Shift notes")
    p.add_argument("--publish", action="store_true", default=True, help="Publish immediately")
    p.add_argument("--draft", action="store_true", help="Save as draft (don't publish)")
    args = p.parse_args()

    user_ids = [resolve_user(n.strip()) for n in args.staff.split(",")]
    start_ts = to_unix(args.date, args.start)
    end_ts = to_unix(args.date, args.end)

    shift = {
        "title": args.title,
        "startTime": start_ts,
        "endTime": end_ts,
        "timezone": TZ,
        "assignedUserIds": user_ids,
        "isPublished": not args.draft,
        "allDay": False,
        "isOpenShift": False,
    }

    if args.job:
        shift["jobId"] = resolve_job(args.job)
    if args.notes:
        shift["notes"] = [{"text": args.notes}]

    result = create_shifts([shift])
    print(json.dumps(result, indent=2))
    print(f"\n✅ Shift '{args.title}' created for {args.date} {args.start}-{args.end}")

if __name__ == "__main__":
    main()
