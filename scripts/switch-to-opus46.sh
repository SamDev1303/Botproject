#!/usr/bin/env bash
# switch-to-opus46.sh — Reset Bella to Opus 4.6 (clear cooldown, restart gateway)
# Usage: bash ~/Desktop/🦀/scripts/switch-to-opus46.sh

set -euo pipefail

AUTH_FILE="$HOME/.clawdbot/agents/main/agent/auth-profiles.json"
CONFIG_FILE="$HOME/.clawdbot/clawdbot.json"
LOG_DIR="$HOME/.clawdbot/logs"
LOG_FILE="$LOG_DIR/model-monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')

mkdir -p "$LOG_DIR"

log() { echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"; }

# ── Step 1: Clear cooldown in auth-profiles.json ──
if [ ! -f "$AUTH_FILE" ]; then
  log "ERROR: auth-profiles.json not found at $AUTH_FILE"
  exit 1
fi

# Check if there's actually a cooldown or error state
if grep -q '"errorCount"' "$AUTH_FILE" 2>/dev/null || grep -q '"cooldownUntil"' "$AUTH_FILE" 2>/dev/null; then
  log "Found cooldown/errors in auth-profiles.json — clearing usageStats..."

  # Use python3 to safely edit JSON (preserve everything else)
  python3 -c "
import json, sys
with open('$AUTH_FILE', 'r') as f:
    data = json.load(f)
data['usageStats'] = {}
with open('$AUTH_FILE', 'w') as f:
    json.dump(data, f, indent=2)
print('usageStats cleared successfully')
"
  log "Cooldown cleared."
else
  log "No cooldown or errors found — auth-profiles clean."
fi

# ── Step 2: Verify primary model is Opus 4.6 ──
CURRENT_PRIMARY=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    data = json.load(f)
print(data.get('agents',{}).get('defaults',{}).get('model',{}).get('primary','unknown'))
")

if [ "$CURRENT_PRIMARY" = "anthropic/claude-opus-4-6" ]; then
  log "Primary model confirmed: anthropic/claude-opus-4-6"
else
  log "WARNING: Primary model is '$CURRENT_PRIMARY', expected 'anthropic/claude-opus-4-6'"
  log "Fixing primary model..."
  python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    data = json.load(f)
data['agents']['defaults']['model']['primary'] = 'anthropic/claude-opus-4-6'
data['agents']['defaults']['model']['fallbacks'] = ['anthropic/claude-opus-4-5']
with open('$CONFIG_FILE', 'w') as f:
    json.dump(data, f, indent=2)
print('Primary model set to anthropic/claude-opus-4-6')
"
  log "Primary model fixed."
fi

# ── Step 3: Verify no Gemini in fallbacks ──
HAS_GEMINI=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    data = json.load(f)
fallbacks = data.get('agents',{}).get('defaults',{}).get('model',{}).get('fallbacks',[])
print('yes' if any('gemini' in f for f in fallbacks) else 'no')
")

if [ "$HAS_GEMINI" = "yes" ]; then
  log "WARNING: Gemini found in fallbacks — removing..."
  python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    data = json.load(f)
fallbacks = data['agents']['defaults']['model']['fallbacks']
data['agents']['defaults']['model']['fallbacks'] = [f for f in fallbacks if 'gemini' not in f]
# Also remove gemini from models dict
models = data['agents']['defaults'].get('models', {})
for k in list(models.keys()):
    if 'gemini' in k:
        del models[k]
with open('$CONFIG_FILE', 'w') as f:
    json.dump(data, f, indent=2)
print('Gemini removed from fallbacks and models')
"
  log "Gemini removed."
else
  log "Fallback chain clean: Opus 4.6 -> Opus 4.5 only."
fi

# ── Step 4: Restart gateway ──
# Find clawdbot binary
CLAWDBOT_BIN=""
for candidate in \
  "$(command -v clawdbot 2>/dev/null)" \
  "$HOME/.npm-global/bin/clawdbot" \
  "/usr/local/bin/clawdbot" \
  "/opt/homebrew/bin/clawdbot"; do
  if [ -n "$candidate" ] && [ -x "$candidate" ]; then
    CLAWDBOT_BIN="$candidate"
    break
  fi
done

if [ -n "$CLAWDBOT_BIN" ]; then
  log "Restarting gateway via $CLAWDBOT_BIN..."
  # Try gateway restart, fall back to just signalling
  "$CLAWDBOT_BIN" gateway restart 2>&1 | tee -a "$LOG_FILE" || {
    log "Gateway restart command failed — trying process signal..."
    pkill -HUP -f "clawdbot.*gateway" 2>/dev/null || true
  }
else
  log "clawdbot binary not found in PATH — trying process signal..."
  pkill -HUP -f "clawdbot.*gateway" 2>/dev/null || {
    log "No gateway process found to signal. May need manual restart."
  }
fi

# ── Step 5: Summary ──
log "=== Switch to Opus 4.6 complete ==="
log "  Primary: anthropic/claude-opus-4-6"
log "  Fallback: anthropic/claude-opus-4-5"
log "  Gemini: removed"
log "  Cooldown: cleared"
echo ""
echo "Done. Send /new in Telegram to start a fresh session on Opus 4.6."
