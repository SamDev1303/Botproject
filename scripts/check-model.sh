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
# check-model.sh — Monitor active model, auto-fix to GPT Codex + Gemini fallback
# Usage: bash ~/Desktop/🦀/scripts/check-model.sh
# Runs every heartbeat (30 min) or manually

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
EXPECTED_PRIMARY="openai-codex/gpt-5.3-codex"
EXPECTED_FALLBACK="openai-codex/gpt-5.2-codex"
CLAW_HOME="${CLAW_HOME:-$HOME/.clawdbot}"
CONFIG_FILE="$CLAW_HOME/clawdbot.json"
AUTH_FILE_PRIMARY="$CLAW_HOME/agents/main/agent/auth-profiles.json"
AUTH_FILE_FALLBACK="$CLAW_HOME/auth-profiles.json"
LOG_DIR="${MODEL_CHECK_LOG_DIR:-$CLAW_HOME/logs}"
STATE_FILE="${MODEL_CHECK_STATE_FILE:-$CLAW_HOME/logs/model-state.json}"
SWITCHER="${MODEL_SWITCHER_SCRIPT:-$HOME/.clawdbot/skills/model-switcher/scripts/switch-model.sh}"

if [ ! -d "$LOG_DIR" ] || [ ! -w "$LOG_DIR" ]; then
  LOG_DIR="${TMPDIR:-/tmp}"
fi

LOG_FILE="$LOG_DIR/model-monitor.log"
if [ ! -d "$(dirname "$STATE_FILE")" ] || [ ! -w "$(dirname "$STATE_FILE")" ]; then
  STATE_FILE="$LOG_DIR/model-state.json"
fi

mkdir -p "$LOG_DIR"

log() { echo "[$TIMESTAMP] $1" >> "$LOG_FILE" 2>/dev/null || true; }

if [ ! -x "$SWITCHER" ]; then
  SWITCHER="$SCRIPT_DIR/openclaw-model-switcher-pack.sh"
fi

if [ ! -f "$CONFIG_FILE" ]; then
  echo "ERROR: missing config file $CONFIG_FILE"
  exit 1
fi

NEEDS_FIX=false
REASONS=""
MODEL_CHANGED=false
CHANGED_REASON=""

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

# ── Check 3: Is Codex auth profile currently in cooldown? ──
AUTH_FILE="$AUTH_FILE_PRIMARY"
if [ ! -f "$AUTH_FILE" ] && [ -f "$AUTH_FILE_FALLBACK" ]; then
  AUTH_FILE="$AUTH_FILE_FALLBACK"
fi

CODEX_COOLDOWN_ACTIVE=$(python3 -c "
import json, time
from pathlib import Path
p = Path('$AUTH_FILE')
if not p.exists():
    print('no')
    raise SystemExit(0)
with open(p) as f:
    data = json.load(f)
now = int(time.time() * 1000)
active = False
for key, entry in (data.get('usageStats') or {}).items():
    if not isinstance(entry, dict):
        continue
    if 'openai-codex' not in str(key):
        continue
    if int(entry.get('cooldownUntil') or 0) > now:
        active = True
        break
print('yes' if active else 'no')
" 2>/dev/null || echo "unknown")

if [ "$CODEX_COOLDOWN_ACTIVE" = "yes" ]; then
  NEEDS_FIX=true
  REASONS="${REASONS:+$REASONS, }openai-codex cooldown active"
fi

# ── Check 4: Surface config model changes for user notifications ──
CURRENT_FALLBACKS=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    data = json.load(f)
fallbacks = data.get('agents',{}).get('defaults',{}).get('model',{}).get('fallbacks',[])
print(','.join(fallbacks))
" 2>/dev/null || echo "")

PREV_PRIMARY=""
PREV_FALLBACKS=""
if [ -f "$STATE_FILE" ]; then
  PREV_PRIMARY=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    d = json.load(f)
print(d.get('primary',''))
" 2>/dev/null || echo "")
  PREV_FALLBACKS=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    d = json.load(f)
print(','.join(d.get('fallbacks',[])))
" 2>/dev/null || echo "")
fi

if [ -n "$PREV_PRIMARY" ] && [ "$PREV_PRIMARY" != "$CURRENT_PRIMARY" ]; then
  MODEL_CHANGED=true
  CHANGED_REASON="primary: $PREV_PRIMARY -> $CURRENT_PRIMARY"
fi
if [ -n "$PREV_FALLBACKS" ] && [ "$PREV_FALLBACKS" != "$CURRENT_FALLBACKS" ]; then
  MODEL_CHANGED=true
  CHANGED_REASON="${CHANGED_REASON:+$CHANGED_REASON, }fallbacks: [$PREV_FALLBACKS] -> [$CURRENT_FALLBACKS]"
fi

# ── Act on findings ──
if [ "$NEEDS_FIX" = true ]; then
  log "MODEL CHECK FAILED: $REASONS — running auto-fix..."
  bash "$SWITCHER" cooldown-bypass 2>&1 | while read -r line; do log "  cooldown: $line"; done
  bash "$SWITCHER" codex53 2>&1 | while read -r line; do log "  fix: $line"; done
  log "Auto-fix completed."

  python3 - "$STATE_FILE" "$EXPECTED_PRIMARY" "$EXPECTED_FALLBACK" << 'PYEOF'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
payload = {"primary": sys.argv[2], "fallbacks": [sys.argv[3]]}
path.write_text(json.dumps(payload, indent=2) + "\n")
PYEOF

  # Output for heartbeat to pick up
  echo "FIXED: $REASONS"
  exit 0
else
  python3 - "$STATE_FILE" "$CURRENT_PRIMARY" "$CURRENT_FALLBACKS" << 'PYEOF'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
fallbacks = [x for x in sys.argv[3].split(",") if x]
payload = {"primary": sys.argv[2], "fallbacks": fallbacks}
path.write_text(json.dumps(payload, indent=2) + "\n")
PYEOF

  if [ "$MODEL_CHANGED" = true ]; then
    log "MODEL CHANGED: $CHANGED_REASON"
    echo "CHANGED: $CHANGED_REASON"
    exit 0
  fi

  log "MODEL CHECK OK: primary=$EXPECTED_PRIMARY, fallback includes $EXPECTED_FALLBACK"
  echo "OK"
  exit 0
fi
