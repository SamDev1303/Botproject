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

ROOT="/Users/hafsahnuzhat/Desktop/🦀"
LOG_DIR="$ROOT/logs"
LOG_FILE="$LOG_DIR/universal-sync.log"
RUN_ID="$(date '+%Y%m%d%H%M%S')"

mkdir -p "$LOG_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

append_error() {
  local source="$1"
  local stage="$2"
  local err="$3"
  python3 - <<PY >/dev/null 2>&1 || true
from scripts.sheet_router import client
gs = client("business")
gs.append("Sync_Errors!A:E", ["$(date '+%Y-%m-%d %H:%M:%S')", "$source", "$stage", "$err", "$RUN_ID"])
PY
}

run_step() {
  local source="$1"
  local stage="$2"
  shift 2
  log "RUN $source/$stage"
  if "$@" >>"$LOG_FILE" 2>&1; then
    log "OK $source/$stage"
  else
    log "FAIL $source/$stage"
    append_error "$source" "$stage" "command failed"
  fi
}

log "START universal sync run_id=$RUN_ID"

run_step "sheet" "ensure-tabs" python3 "$ROOT/scripts/ensure-master-tabs.py"
run_step "access" "parity" python3 "$ROOT/scripts/check-access-parity.py"

run_step "square" "payments-sync" python3 "$ROOT/scripts/square_sheets_sync.py" sync --days 90
run_step "square" "unpaid-reconcile" python3 "$ROOT/scripts/reconcile-unpaid-client-log.py"
run_step "square" "unpaid-add" python3 "$ROOT/scripts/sync-square-unpaid-to-client-log.py"

run_step "gmail" "ingest" python3 "$ROOT/scripts/sync-gmail-to-sheet.py"
run_step "gcal" "ingest" python3 "$ROOT/scripts/sync-google-calendar-to-sheet.py"
run_step "apple-calendar" "ingest" python3 "$ROOT/scripts/sync-apple-calendar-to-sheet.py"
run_step "reminders" "ingest" python3 "$ROOT/scripts/sync-apple-reminders-to-sheet.py"
run_step "connecteam" "ingest" python3 "$ROOT/scripts/sync-connecteam-to-sheet.py"
run_step "notes" "ingest" python3 "$ROOT/scripts/sync-apple-notes-to-sheet.py"
run_step "notes" "dedupe-ingestion" python3 "$ROOT/scripts/dedupe-ingestion-tab.py" --tab Ingestion_AppleNotes
run_step "notes" "booking-import" python3 "$ROOT/scripts/import-apple-notes-bookings.py"
run_step "notes" "neno-hours-import" python3 "$ROOT/scripts/import-neno-hours-from-notes.py"

run_step "unify" "merge" python3 "$ROOT/scripts/unify-sources-into-master.py"
run_step "theme" "format" bash "$ROOT/scripts/style-three-sheets.sh"

run_step "dashboard" "build" python3 "$ROOT/scripts/build-dashboard-control-center.py"
run_step "dashboard" "push-to-sheet" python3 "$ROOT/scripts/push-dashboard-to-master-sheet.py"

run_step "validate" "accuracy" python3 "$ROOT/scripts/check-sheets-accuracy.py" --task "universal sync"
run_step "validate" "integrity" python3 "$ROOT/scripts/check-universal-sync-integrity.py"

log "DONE universal sync run_id=$RUN_ID"
