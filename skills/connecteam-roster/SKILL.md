---
name: connecteam-roster
description: Manage Clean Up Bros staff rosters via the Connecteam API. Use when Hafsah asks to view, add, update, delete, or manage staff shifts, rosters, schedules, job locations, or staff assignments. Triggers on "roster", "shift", "schedule staff", "add a shift", "Teenay's shifts", "who's working", "Connecteam", or any staff scheduling request.
---

# Connecteam Roster Management

Manage staff shifts, rosters, and job locations via Connecteam API.

## Quick Reference

- **Scheduler ID:** `13218868` (Clean Up Bros Schedule)
- **Timezone:** `Australia/Sydney`
- **API Key env var:** `CONNECTEAM_API_ID` (stored in `.env`)
- **Base URL:** `https://api.connecteam.com`

### Staff
| Name | userId | Role |
|------|--------|------|
| Hafsah Nuzhat | 11925732 | Owner |
| Shamal Krishna | 11925807 | Manager |
| Teenay Josh | 13917939 | Worker |

### Job Locations
| Job | Code |
|-----|------|
| AIRBNB (Unit 3, Atkinson St) | UNIT3 |
| AIRBNB 2 (Unit 4, Atkinson St) | UNIT4 |
| AIRBNB 3 (Unit 2, Nigal St) | UNIT 2 NIGAL |
| HOME (41 Wonga Rd, Lurnea) | HOME SITE |

> Staff and jobs may change. Run `list_staff.py` or `list_jobs.py` to get current data before assuming.

## Scripts

All scripts are in `skills/connecteam-roster/scripts/`. They auto-load the API key from `.env`.

### View Roster
```bash
python3 skills/connecteam-roster/scripts/list_roster.py          # Next 7 days
python3 skills/connecteam-roster/scripts/list_roster.py 14       # Next 14 days
python3 skills/connecteam-roster/scripts/list_roster.py today    # Today only
```

### List Staff
```bash
python3 skills/connecteam-roster/scripts/list_staff.py
```

### List Job Locations
```bash
python3 skills/connecteam-roster/scripts/list_jobs.py
```

### Create Shift
```bash
python3 skills/connecteam-roster/scripts/create_shift.py \
  --title "End of Lease Clean" \
  --staff "Teenay" \
  --date 2026-02-20 \
  --start 09:00 \
  --end 14:00 \
  --job "AIRBNB" \
  --notes "3BR house, bring steam cleaner"
```

**Flags:**
- `--title` (required): Shift name
- `--staff` (required): Staff name(s), comma-separated (partial match works: "Teenay", "Shamal")
- `--date` (required): YYYY-MM-DD
- `--start` / `--end` (required): HH:MM (24hr, AEST)
- `--job`: Job/location name (partial match)
- `--notes`: Shift notes
- `--draft`: Save as draft instead of publishing

### Update Shift
```bash
python3 skills/connecteam-roster/scripts/update_shift.py <shiftId> \
  --title "Updated Title" \
  --staff "Teenay,Shamal" \
  --date 2026-02-20 --start 10:00 --end 15:00 \
  --job "AIRBNB 2" \
  --notes "New instructions"
```

All flags are optional — only provide what's changing. For time changes, `--date`, `--start`, and `--end` must all be provided together.

### Delete Shift
```bash
python3 skills/connecteam-roster/scripts/delete_shift.py <shiftId>
```

## Direct API Usage

For operations not covered by scripts, use the `ct_api.py` module directly:

```python
import sys
sys.path.insert(0, "skills/connecteam-roster/scripts")
from ct_api import list_shifts, create_shifts, update_shift, delete_shift, resolve_user, resolve_job

# Get shifts for next 7 days
import time
shifts = list_shifts(int(time.time()), int(time.time()) + 7*86400)

# Create shift programmatically
create_shifts([{
    "title": "Deep Clean",
    "startTime": 1740000000,
    "endTime": 1740010800,
    "timezone": "Australia/Sydney",
    "assignedUserIds": [resolve_user("Teenay")],
    "jobId": resolve_job("AIRBNB"),
    "isPublished": True,
}])
```

## API Details

See `references/api-reference.md` for full endpoint documentation, field definitions, and shift object schema.

## Workflow

1. **Before creating/updating:** Always confirm shift details with Hafsah (staff, date, time, location)
2. **After creating:** Report back the shift ID in case she needs to modify it later
3. **When listing:** Format as a clean table showing date, time, staff, and location
4. **Staff names:** Use partial matching ("Teenay" → Teenay Josh, "Shamal" → Shamal Krishna)
5. **Refresh data:** If staff or jobs seem stale, re-run `list_staff.py` or `list_jobs.py`
