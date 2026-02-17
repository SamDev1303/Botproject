#!/usr/bin/env bash
# check-model.sh — Monitor active model, auto-fix if drifted from Opus 4.6
# Usage: bash ~/Desktop/🦀/scripts/check-model.sh
# Runs every heartbeat (30 min) or manually

set -euo pipefail

AUTH_FILE="$HOME/.clawdbot/agents/main/agent/auth-profiles.json"
CONFIG_FILE="$HOME/.clawdbot/clawdbot.json"
LOG_DIR="$HOME/.clawdbot/logs"
LOG_FILE="$LOG_DIR/model-monitor.log"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')

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

if [ "$CURRENT_PRIMARY" != "anthropic/claude-opus-4-6" ]; then
  NEEDS_FIX=true
  REASONS="primary=$CURRENT_PRIMARY (expected opus-4-6)"
fi

# ── Check 2: Is Anthropic in cooldown? ──
IN_COOLDOWN=$(python3 -c "
import json, time
with open('$AUTH_FILE') as f:
    data = json.load(f)
stats = data.get('usageStats', {}).get('anthropic:claude-cli', {})
cooldown = stats.get('cooldownUntil', 0)
errors = stats.get('errorCount', 0)
now_ms = int(time.time() * 1000)
if cooldown > now_ms or errors >= 3:
    print('yes')
else:
    print('no')
" 2>/dev/null || echo "unknown")

if [ "$IN_COOLDOWN" = "yes" ]; then
  NEEDS_FIX=true
  REASONS="${REASONS:+$REASONS, }anthropic in cooldown"
fi

# ── Check 3: Is Gemini in fallbacks? (should not be) ──
HAS_GEMINI=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    data = json.load(f)
fallbacks = data.get('agents',{}).get('defaults',{}).get('model',{}).get('fallbacks',[])
print('yes' if any('gemini' in f for f in fallbacks) else 'no')
" 2>/dev/null || echo "unknown")

if [ "$HAS_GEMINI" = "yes" ]; then
  NEEDS_FIX=true
  REASONS="${REASONS:+$REASONS, }gemini in fallbacks"
fi

# ── Act on findings ──
if [ "$NEEDS_FIX" = true ]; then
  log "MODEL CHECK FAILED: $REASONS — running auto-fix..."
  bash "$SCRIPT_DIR/switch-to-opus46.sh" 2>&1 | while read -r line; do log "  fix: $line"; done
  log "Auto-fix completed."

  # Output for heartbeat to pick up
  echo "FIXED: $REASONS"
  exit 0
else
  log "MODEL CHECK OK: primary=opus-4-6, no cooldown, no gemini"
  echo "OK"
  exit 0
fi
