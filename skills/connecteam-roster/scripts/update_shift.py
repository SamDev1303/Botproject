#!/usr/bin/env python3
"""Update an existing shift on Connecteam.

Usage:
  python3 update_shift.py <shiftId> --title "New Title"
  python3 update_shift.py <shiftId> --start 10:00 --end 15:00 --date 2026-02-20
  python3 update_shift.py <shiftId> --staff "Teenay,Shamal"
  python3 update_shift.py <shiftId> --job "AIRBNB 2"
  python3 update_shift.py <shiftId> --notes "Updated notes"
"""

import argparse, sys, json
from datetime import datetime, timedelta, timezone

sys.path.insert(0, __import__("os").path.dirname(__file__))
from ct_api import update_shift, resolve_user, resolve_job, TZ

AEST = timezone(timedelta(hours=11))

def to_unix(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt = dt.replace(tzinfo=AEST)
    return int(dt.timestamp())

def main():
    p = argparse.ArgumentParser(description="Update a Connecteam shift")
    p.add_argument("shift_id", help="Shift ID to update")
    p.add_argument("--title", help="New shift title")
    p.add_argument("--staff", help="New staff assignment(s), comma-separated")
    p.add_argument("--date", help="New date YYYY-MM-DD (requires --start and --end)")
    p.add_argument("--start", help="New start time HH:MM")
    p.add_argument("--end", help="New end time HH:MM")
    p.add_argument("--job", help="New job/location name")
    p.add_argument("--notes", help="New shift notes")
    p.add_argument("--publish", action="store_true", help="Publish the shift")
    p.add_argument("--unpublish", action="store_true", help="Unpublish (draft)")
    args = p.parse_args()

    updates = {}
    if args.title:
        updates["title"] = args.title
    if args.staff:
        updates["assignedUserIds"] = [resolve_user(n.strip()) for n in args.staff.split(",")]
    if args.date and args.start and args.end:
        updates["startTime"] = to_unix(args.date, args.start)
        updates["endTime"] = to_unix(args.date, args.end)
        updates["timezone"] = TZ
    elif args.start or args.end:
        print("ERROR: --date, --start, and --end must all be provided together", file=sys.stderr)
        sys.exit(1)
    if args.job:
        updates["jobId"] = resolve_job(args.job)
    if args.notes:
        updates["notes"] = [{"text": args.notes}]
    if args.publish:
        updates["isPublished"] = True
    if args.unpublish:
        updates["isPublished"] = False

    if not updates:
        print("ERROR: No updates specified", file=sys.stderr)
        sys.exit(1)

    result = update_shift(args.shift_id, updates)
    print(json.dumps(result, indent=2))
    print(f"\n✅ Shift {args.shift_id} updated")

if __name__ == "__main__":
    main()
