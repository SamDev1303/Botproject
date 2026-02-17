#!/usr/bin/env python3
"""List all jobs/locations from Connecteam."""

import sys, json

sys.path.insert(0, __import__("os").path.dirname(__file__))
from ct_api import list_jobs

def main():
    jobs = list_jobs()
    print(f"{'Title':<20} {'Code':<15} {'Address':<45} {'JobID'}")
    print("-" * 110)
    for j in jobs:
        addr = j.get("gps", {}).get("address", "—") or "—"
        print(f"{j['title']:<20} {j.get('code','—'):<15} {addr:<45} {j['jobId']}")

if __name__ == "__main__":
    main()
