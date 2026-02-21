#!/usr/bin/env bash
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail

ROOT="/Users/hafsahnuzhat/Desktop/🦀"
MAIN="$ROOT/scripts/run-bella-universal-sync.sh"
MARK_HOURLY="# bella-universal-sync-hourly"
MARK_DELTA="# bella-universal-sync-delta"
MARK_DAILY="# bella-universal-sync-daily-format"

chmod +x "$MAIN"

CURRENT="$(crontab -l 2>/dev/null || true)"
FILTERED="$(printf "%s\n" "$CURRENT" | awk -v a="$MARK_HOURLY" -v b="$MARK_DELTA" -v c="$MARK_DAILY" 'index($0,a)==0 && index($0,b)==0 && index($0,c)==0')"

ENTRY1="0 * * * * bash \"$MAIN\" $MARK_HOURLY"
ENTRY2="*/15 * * * * python3 \"$ROOT/scripts/sync-google-calendar-to-sheet.py\" >/dev/null 2>&1; python3 \"$ROOT/scripts/sync-apple-calendar-to-sheet.py\" >/dev/null 2>&1; python3 \"$ROOT/scripts/sync-gmail-to-sheet.py\" >/dev/null 2>&1 $MARK_DELTA"
ENTRY3="10 2 * * * python3 \"$ROOT/scripts/format-master-sheet-theme.py\" >/dev/null 2>&1 $MARK_DAILY"

NEW="$FILTERED"
if [ -n "$NEW" ]; then
  NEW="$NEW"$'\n'
fi
NEW="$NEW$ENTRY1"$'\n'"$ENTRY2"$'\n'"$ENTRY3"

printf "%s\n" "$NEW" | crontab -
echo "Installed universal sync cron entries."
