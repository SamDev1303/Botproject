#!/usr/bin/env python3
"""Connecteam API helper — thin wrapper for roster management."""

import json, os, sys, time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = "https://api.connecteam.com"
SCHEDULER_ID = "13218868"
TZ = "Australia/Sydney"

def _key():
    # Try .env file first, then environment
    key = os.environ.get("CONNECTEAM_API_ID")
    if not key:
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("CONNECTEAM_API_ID="):
                        key = line.split("=", 1)[1].strip()
                        break
    if not key:
        print("ERROR: CONNECTEAM_API_ID not set", file=sys.stderr)
        sys.exit(1)
    return key

def _req(method, path, body=None, _retries=3):
    url = f"{BASE}{path}"
    headers = {
        "X-API-KEY": _key(),
        "Content-Type": "application/json",
        "User-Agent": "CleanUpBros/1.0",
        "Accept": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        if e.code == 429 and _retries > 0:
            wait = 10 * (4 - _retries)  # 10s, 20s, 30s
            print(f"Rate limited, waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)
            return _req(method, path, body, _retries - 1)
        err = e.read().decode()
        print(f"API Error {e.code}: {err}", file=sys.stderr)
        sys.exit(1)

# ── Users ──
def list_users():
    return _req("GET", "/users/v1/users")["data"]["users"]

def get_user(user_id):
    return _req("GET", f"/users/v1/users?userId={user_id}")["data"]["users"]

# ── Jobs ──
def list_jobs():
    return _req("GET", "/jobs/v1/jobs")["data"]["jobs"]

# ── Shifts ──
def list_shifts(start_ts, end_ts, scheduler_id=SCHEDULER_ID):
    return _req("GET", f"/scheduler/v1/schedulers/{scheduler_id}/shifts?startTime={start_ts}&endTime={end_ts}")["data"]["shifts"]

def get_shift(shift_id, scheduler_id=SCHEDULER_ID):
    return _req("GET", f"/scheduler/v1/schedulers/{scheduler_id}/shifts/{shift_id}")["data"]

def create_shifts(shifts, scheduler_id=SCHEDULER_ID):
    """Create one or more shifts. `shifts` is a list of shift dicts. Body is sent as a plain list."""
    url = f"{BASE}/scheduler/v1/schedulers/{scheduler_id}/shifts"
    headers = {
        "X-API-KEY": _key(),
        "Content-Type": "application/json",
        "User-Agent": "CleanUpBros/1.0",
        "Accept": "application/json",
    }
    data = json.dumps(shifts).encode()
    req = Request(url, data=data, headers=headers, method="POST")
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        err = e.read().decode()
        print(f"API Error {e.code}: {err}", file=sys.stderr)
        sys.exit(1)

def update_shift(shift_id, updates, scheduler_id=SCHEDULER_ID):
    """Update a shift. `updates` is a dict of fields to change."""
    return _req("PUT", f"/scheduler/v1/schedulers/{scheduler_id}/shifts/{shift_id}", updates)

def delete_shift(shift_id, scheduler_id=SCHEDULER_ID):
    return _req("DELETE", f"/scheduler/v1/schedulers/{scheduler_id}/shifts/{shift_id}")

# ── Helpers ──
USER_MAP = None
def resolve_user(name_or_id):
    """Resolve a staff name (partial match) or ID to userId."""
    global USER_MAP
    if USER_MAP is None:
        USER_MAP = {u["userId"]: u for u in list_users()}
    if isinstance(name_or_id, int) or str(name_or_id).isdigit():
        return int(name_or_id)
    name_lower = name_or_id.lower()
    for u in USER_MAP.values():
        full = f"{u['firstName']} {u['lastName']}".lower()
        if name_lower in full or name_lower == u["firstName"].lower():
            return u["userId"]
    print(f"ERROR: Could not resolve user '{name_or_id}'", file=sys.stderr)
    sys.exit(1)

JOB_MAP = None
def resolve_job(name_or_id):
    """Resolve a job name (partial match) or ID to jobId."""
    global JOB_MAP
    if JOB_MAP is None:
        JOB_MAP = {j["jobId"]: j for j in list_jobs()}
    if len(str(name_or_id)) > 20:  # Looks like a UUID
        return str(name_or_id)
    name_lower = name_or_id.lower()
    for j in JOB_MAP.values():
        if name_lower in j["title"].lower() or name_lower in j.get("code", "").lower():
            return j["jobId"]
    print(f"ERROR: Could not resolve job '{name_or_id}'", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    print("Connecteam API helper loaded. Import this module to use.")
