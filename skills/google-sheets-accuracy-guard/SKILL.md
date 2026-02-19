---
name: google-sheets-accuracy-guard
description: Mandatory post-action validation for any Google Sheets write/update. Runs reconciliation checks, verifies unpaid invoice consistency, and blocks completion if checks fail.
---

# Google Sheets Accuracy Guard

Use this skill every time Bella writes to Google Sheets.

## Mandatory flow

1. Perform the requested Sheets operation.
2. Immediately run:

```bash
python3 scripts/check-sheets-accuracy.py --task "describe operation"
```

3. If validation fails:
- do not mark task complete,
- explain mismatch,
- run corrective sync:

```bash
python3 scripts/square_sheets_sync.py sync --days 90
python3 scripts/build-dashboard-control-center.py
python3 scripts/push-dashboard-to-master-sheet.py
```

4. Re-run accuracy check until pass.

## Account separation rule

- `business` expenses go to `Expenses` + `Bookkeeping`.
- `personal` expenses go to `Bookkeeping` only with `PERSONAL_ACCOUNT_DO_NOT_MIX` tag.
- Always use `scripts/add-expense-entry.py --account-type ...`.
