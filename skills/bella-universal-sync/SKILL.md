---
name: bella-universal-sync
description: Unified source-of-truth sync for Bella. Pulls Gmail, Google Calendar, Apple Calendar, Apple Reminders, Apple Notes, Connecteam, and Square into canonical Google Sheets tabs, then validates and updates dashboard data.
---

# Bella Universal Sync

Use this skill whenever user asks to update Sheets/dashboard/source-of-truth.

## Required command

```bash
bash scripts/run-bella-universal-sync.sh
```

## What it enforces

- Uses Master Ops + Finance Backup as canonical data stores.
- Never creates a new spreadsheet.
- Applies dual-calendar merge rules.
- Runs account separation (`business` vs `personal`).
- Runs mandatory validation:
  - `scripts/check-sheets-accuracy.py`
  - `scripts/check-universal-sync-integrity.py`

## Setup command

```bash
bash scripts/install-universal-sync-cron.sh
```

