---
name: square-sync
description: Synchronize live Square payment and invoice data with Google Sheets backup. Use when checking unpaid invoices, updating financial records, or cross-referencing Square balances with local documentation.
---

# Square Sync

Use this skill to ensure financial data is accurate and backed up.

## Core Principles
1. **Live Data Only**: Never trust local memory files for money. Always run a live Square API check.
2. **Sheet as Backup**: Use the "Clean Up Bros - Finance Backup" Google Sheet (ID: `1pocJwoOO3emKfQf9mzFHuahZ5nA7KSrehF9fBqn-00Q`) as the secondary source.
3. **Automated Sync**: If the sheet is out of date, update it immediately.

## Workflows

### 1. Check Unpaid Invoices
Run the script to see who owes money right now.
```bash
python3 scripts/check_unpaid_invoices.py
```

### 2. Full Backup Sync
Update the Google Sheet with the latest data from Square.
```bash
python3 -c 'import sys, json; data = json.load(sys.stdin); print(json.dumps(data))' < <(python3 scripts/sync_square_to_sheets.py) > /tmp/sheet_data.json && gog sheets update 1pocJwoOO3emKfQf9mzFHuahZ5nA7KSrehF9fBqn-00Q "Sheet1!A1" --values-json "$(cat /tmp/sheet_data.json)" --input USER_ENTERED
```

### 3. Inspect Specific Invoice
Get the full JSON data for a specific invoice.
```bash
# Edit script with specific ID first
python3 scripts/inspect_meshach_invoice.py
```

## Bundled Resources

### Scripts
- `scripts/check_unpaid_invoices.py`: Quick terminal summary of unpaid items.
- `scripts/sync_square_to_sheets.py`: Formats all 50+ invoices for Google Sheets import.
- `scripts/get_full_payment_data.py`: Detailed console output of all records.
- `scripts/inspect_meshach_invoice.py`: Deep dive into specific invoice payment requests.
