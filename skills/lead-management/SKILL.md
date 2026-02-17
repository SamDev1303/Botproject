---
name: lead-management
description: Lead database management — query Apollo lead sheets (1616 Master, 68 Top Leads, 400 Strata), search/filter/prioritize leads, track outreach status. Use when the user asks about leads, prospects, outreach, strata contacts, or sales pipeline.
---

# Lead Management

Query, filter, and manage Clean Up Bros lead databases across three Google Sheets.

## Prerequisites

- **Google Sheets access** via `google-workspace` skill
- **Three lead sheets** (see below)

## Lead Sheets

| Sheet | Records | ID | Use |
|-------|---------|----|-----|
| 1616 MASTER | 1,616 leads | `1RWhp2GhJgSDQ0LaM7R0uj0xBuxGu_UT_dbk43TM7QXQ` | Full Apollo database |
| 68 TOP LEADS | 68 leads | `1PdyK4_FpNGP9e7m9LKT2r_dLVTDiM2kX6LjvCc3Lw0` | Pre-qualified hot leads |
| 400 STRATA | 400 leads | `1Oxv5aggSI5Wfmvl8TKc3UHJekJt1-V7nLqWN1VNCmI` | Strata managers |

## Workflows

### 1. Read All Leads from a Sheet

```bash
# Top Leads (small, fast)
gog sheets get 1PdyK4_FpNGP9e7m9LKT2r_dLVTDiM2kX6LjvCc3Lw0 "Sheet1!A1:Z100"

# Strata leads
gog sheets get 1Oxv5aggSI5Wfmvl8TKc3UHJekJt1-V7nLqWN1VNCmI "Sheet1!A1:Z500"

# Master list (large — use range limits)
gog sheets get 1RWhp2GhJgSDQ0LaM7R0uj0xBuxGu_UT_dbk43TM7QXQ "Sheet1!A1:Z200"
```

Via API:
```python
import json, urllib.request
from pathlib import Path

TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"
with open(TOKEN_FILE) as f:
    ACCESS_TOKEN = json.load(f)['access_token']

def get_sheet_data(sheet_id, range_name):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{range_name}"
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Example: get top leads
data = get_sheet_data('1PdyK4_FpNGP9e7m9LKT2r_dLVTDiM2kX6LjvCc3Lw0', 'Sheet1!A1:Z100')
headers = data['values'][0]
rows = data['values'][1:]
```

### 2. Search / Filter Leads

After loading data, filter in Python:

```python
# Search by company name
matches = [r for r in rows if 'strata' in r[headers.index('Company')].lower()]

# Filter by location (e.g., Sydney CBD)
sydney = [r for r in rows if 'sydney' in ' '.join(r).lower()]

# Filter by outreach status (if column exists)
not_contacted = [r for r in rows if r[headers.index('Status')] == '']
```

### 3. Prioritize Leads

Priority scoring heuristic:

| Factor | Weight | Logic |
|--------|--------|-------|
| Strata manager | +3 | Multiple properties = recurring contracts |
| Sydney location | +2 | Within service area |
| Has email | +1 | Can do email outreach |
| Has phone | +1 | Can do SMS/call outreach |
| Company size >10 | +1 | Larger = higher contract value |
| Not yet contacted | +2 | Fresh lead |

### 4. Track Outreach Status

Update the sheet with outreach tracking columns:

```bash
# Add status to a specific lead (row 5, column for Status)
gog sheets update 1PdyK4_FpNGP9e7m9LKT2r_dLVTDiM2kX6LjvCc3Lw0 "Sheet1!<STATUS_COL>5" \
  --values-json '[["Contacted - SMS sent 2026-02-10"]]' --input USER_ENTERED
```

Status values: `New` → `Contacted` → `Responded` → `Meeting Booked` → `Quote Sent` → `Won` / `Lost`

### 5. Export Priority List

Generate a summary for outreach:

```python
# Top 20 prioritized leads
priority = sorted(leads_with_scores, key=lambda x: x['score'], reverse=True)[:20]
for lead in priority:
    print(f"Score: {lead['score']} | {lead['company']} | {lead['name']} | {lead['email']} | {lead['phone']}")
```

## Outreach Templates

Use with `twilio-comms` (SMS) or `google-workspace` (email):

**Cold SMS:**
> Hi [Name], I'm Hafsah from Clean Up Bros. We specialize in commercial cleaning for strata & office buildings in Sydney. Would you be open to a quick chat about your cleaning needs? 🧹

**Cold Email Subject:** `Professional Cleaning Quote — [Company Name]`

## Important Notes

- 1616 Master is large — always use range limits, never pull all at once
- Top Leads sheet is pre-qualified — start outreach here
- Strata leads are high-value (recurring contracts)
- Always log outreach in the sheet to avoid double-contacting
- Cross-reference with `client-onboarding` skill for deeper lead research

## References

- Master Leads: `1RWhp2GhJgSDQ0LaM7R0uj0xBuxGu_UT_dbk43TM7QXQ`
- Top Leads: `1PdyK4_FpNGP9e7m9LKT2r_dLVTDiM2kX6LjvCc3Lw0`
- Strata Leads: `1Oxv5aggSI5Wfmvl8TKc3UHJekJt1-V7nLqWN1VNCmI`
