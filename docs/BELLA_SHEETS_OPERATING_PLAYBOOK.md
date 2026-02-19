# Bella Sheets Operating Playbook

Canonical sheets (no new spreadsheets):
- Master Ops: `1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU`
- Finance Backup: `1pocJwoOO3emKfQf9mzFHuahZ5nA7KSrehF9fBqn-00Q`

## Step-by-step actions Bella should run

1. Sync Square payments into Finance Backup
```bash
python3 scripts/square_sheets_sync.py sync --days 60
```

2. Reconcile overdue/unpaid statuses in Master Client Log
```bash
python3 scripts/reconcile-unpaid-client-log.py
python3 scripts/sync-square-unpaid-to-client-log.py
```

3. Add expense instantly (receipt flow)
Business:
```bash
python3 scripts/add-expense-entry.py \
  --account-type business \
  --description \"Receipt description\" \
  --amount 55.00 \
  --category \"Cleaning Supplies\" \
  --payment-method \"Card\" \
  --supplier \"Bunnings\"
```
Personal:
```bash
python3 scripts/add-expense-entry.py \
  --account-type personal \
  --description \"Personal expense\" \
  --amount 35.00 \
  --category \"Personal\" \
  --payment-method \"Card\"
```

4. Rebuild dashboard data from live sheets + Square
```bash
python3 scripts/build-dashboard-control-center.py
```

5. Push dashboard totals back into Master P&L + logs
```bash
python3 scripts/push-dashboard-to-master-sheet.py
```

6. Validate accuracy (mandatory after any Sheets write)
```bash
python3 scripts/check-sheets-accuracy.py --task \"describe operation\"
```

## Full hourly pipeline
```bash
bash scripts/hourly-accounting-dashboard-sync.sh
```

Installed cron:
```bash
bash scripts/install-hourly-accounting-cron.sh
```
