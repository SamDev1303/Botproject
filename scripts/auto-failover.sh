#!/usr/bin/env bash
set -euo pipefail
# auto-failover.sh — Test all models in priority order, switch to first working one
# Usage: bash auto-failover.sh
# Can be run by heartbeat, cron, or manually when bot crashes
set -euo pipefail

CLAW_HOME="${CLAW_HOME:-$HOME/.clawdbot}"
CONFIG="$CLAW_HOME/clawdbot.json"
AUTH_FILE="$CLAW_HOME/agents/main/agent/auth-profiles.json"
SWITCHER="$HOME/Desktop/🦀/scripts/openclaw-model-switcher-pack.sh"
LOG_FILE="$CLAW_HOME/logs/auto-failover.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] $1" | tee -a "$LOG_FILE"; }

# Model priority order
MODELS=("sonnet46" "gemini" "codex53" "opus46")
MODEL_NAMES=("Claude Sonnet 4.6" "Gemini 3 Flash" "Codex GPT-5.3" "Claude Opus 4.6")
MODEL_IDS=("anthropic/claude-sonnet-4-6" "google/gemini-3-flash-preview" "openai-codex/gpt-5.3-codex" "anthropic/claude-opus-4-6")

# Step 1: Clear all cooldowns first
log "=== Auto-Failover Starting ==="
log "Clearing all cooldowns..."
bash "$SWITCHER" cooldown-bypass 2>/dev/null || true

# Step 2: Check token health before testing
log "Checking token health..."
python3 - "$AUTH_FILE" << 'PYEOF'
import json, time, sys

with open(sys.argv[1]) as f:
    data = json.load(f)

now = int(time.time() * 1000)
expired = []
valid = []

for name, prof in data.get("profiles", {}).items():
    expires = prof.get("expires", 0)
    if expires and expires < now:
        expired.append(name)
        print(f"  ❌ {name}: EXPIRED")
    elif expires:
        hours_left = (expires - now) // 3600000
        valid.append(name)
        print(f"  ✅ {name}: {hours_left}h remaining")
    else:
        ptype = prof.get("type", "?")
        valid.append(name)
        print(f"  ✅ {name}: {ptype} (no expiry)")
PYEOF

# Step 3: Test each model in priority order
log "Testing models in priority order..."
FOUND_WORKING=false

for i in "${!MODELS[@]}"; do
    model="${MODELS[$i]}"
    name="${MODEL_NAMES[$i]}"
    model_id="${MODEL_IDS[$i]}"

    log "Testing $name ($model_id)..."

    # Switch to this model temporarily
    python3 -c "
import json
with open('$CONFIG') as f:
    data = json.load(f)
data['agents']['defaults']['model']['primary'] = '$model_id'
with open('$CONFIG', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
" 2>/dev/null

    # Restart gateway quickly
    clawdbot gateway restart >/dev/null 2>&1 || true
    sleep 2

    # Test with a simple prompt
    RESULT=$(timeout 45 clawdbot agent --local --agent main \
        --message "Reply with exactly one word: OK" \
        --thinking low --json 2>&1 || echo "TIMEOUT_OR_FAIL")

    if echo "$RESULT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    provider = data.get('meta',{}).get('agentMeta',{}).get('provider','')
    if provider:
        print(f'PASS:{provider}')
        sys.exit(0)
except:
    pass
sys.exit(1)
" 2>/dev/null; then
        PROVIDER=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('meta',{}).get('agentMeta',{}).get('provider','unknown'))" 2>/dev/null)
        ACTUAL_MODEL=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('meta',{}).get('agentMeta',{}).get('model','unknown'))" 2>/dev/null)
        log "✅ $name WORKING — responding on $PROVIDER/$ACTUAL_MODEL"

        # Now set this as primary with proper fallback chain
        # Build fallbacks from remaining models
        FALLBACKS=()
        for j in "${!MODELS[@]}"; do
            if [ "$j" != "$i" ]; then
                FALLBACKS+=("${MODEL_IDS[$j]}")
            fi
        done

        python3 -c "
import json
with open('$CONFIG') as f:
    data = json.load(f)
data['agents']['defaults']['model']['primary'] = '$model_id'
data['agents']['defaults']['model']['fallbacks'] = $(python3 -c "import json; print(json.dumps([$(printf '"%s",' "${FALLBACKS[@]}" | sed 's/,$//')]))")
with open('$CONFIG', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
" 2>/dev/null

        clawdbot gateway restart >/dev/null 2>&1 || true

        log "=== Auto-Failover Complete ==="
        log "Primary: $name ($model_id)"
        log "Fallbacks: ${FALLBACKS[*]}"
        echo ""
        echo "✅ AUTO-FAILOVER: Switched to $name"
        echo "   Primary: $model_id"
        echo "   Fallbacks: ${FALLBACKS[*]}"
        FOUND_WORKING=true
        break
    else
        log "❌ $name FAILED"
    fi
done

if [ "$FOUND_WORKING" = false ]; then
    log "🚨 ALL MODELS FAILED — no working model found"
    echo ""
    echo "🚨 ALL MODELS FAILED"
    echo "Possible causes:"
    echo "  - All OAuth tokens expired (run: claude login)"
    echo "  - Gemini API quota exhausted (wait or upgrade)"
    echo "  - Codex rate limited (wait ~4h)"
    echo "  - Network issue"
    echo ""
    echo "Manual recovery:"
    echo "  1. Run 'claude login' in terminal to refresh Anthropic token"
    echo "  2. Run 'bash ~/Desktop/🦀/scripts/model-switch.sh sonnet'"
    exit 1
fi
