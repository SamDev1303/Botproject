#!/usr/bin/env bash
# check-model.sh — Monitor active model, auto-fix to GPT Codex + Gemini fallback
# Usage: bash ~/Desktop/🦀/scripts/check-model.sh
# Runs every heartbeat (30 min) or manually

set -euo pipefail

CONFIG_FILE="$HOME/.clawdbot/clawdbot.json"
LOG_DIR="$HOME/.clawdbot/logs"
LOG_FILE="$LOG_DIR/model-monitor.log"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
EXPECTED_PRIMARY="openai-codex/gpt-5.3-codex"
EXPECTED_FALLBACK="google/gemini-3-flash-preview"

mkdir -p "$LOG_DIR"

log() { echo "[$TIMESTAMP] $1" >> "$LOG_FILE"; }

NEEDS_FIX=false
REASONS=""

# ── Check 1: Is primary model correct? ──
CURRENT_PRIMARY=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    data = json.load(f)
print(data.get('agents',{}).get('defaults',{}).get('model',{}).get('primary','unknown'))
" 2>/dev/null || echo "unknown")

if [ "$CURRENT_PRIMARY" != "$EXPECTED_PRIMARY" ]; then
  NEEDS_FIX=true
  REASONS="primary=$CURRENT_PRIMARY (expected $EXPECTED_PRIMARY)"
fi

# ── Check 2: Does fallback include expected Gemini model? ──
HAS_EXPECTED_FALLBACK=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    data = json.load(f)
fallbacks = data.get('agents',{}).get('defaults',{}).get('model',{}).get('fallbacks',[])
print('yes' if '$EXPECTED_FALLBACK' in fallbacks else 'no')
" 2>/dev/null || echo "unknown")

if [ "$HAS_EXPECTED_FALLBACK" != "yes" ]; then
  NEEDS_FIX=true
  REASONS="${REASONS:+$REASONS, }fallback missing $EXPECTED_FALLBACK"
fi

# ── Act on findings ──
if [ "$NEEDS_FIX" = true ]; then
  log "MODEL CHECK FAILED: $REASONS — running auto-fix..."
  bash "$HOME/.clawdbot/skills/model-switcher/scripts/switch-model.sh" codex53 2>&1 | while read -r line; do log "  fix: $line"; done
  log "Auto-fix completed."

  # Output for heartbeat to pick up
  echo "FIXED: $REASONS"
  exit 0
else
  log "MODEL CHECK OK: primary=$EXPECTED_PRIMARY, fallback includes $EXPECTED_FALLBACK"
  echo "OK"
  exit 0
fi
