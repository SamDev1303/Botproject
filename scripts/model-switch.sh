#!/usr/bin/env bash
set -euo pipefail
# model-switch.sh — Universal model switcher for Bella
# Usage: bash model-switch.sh <sonnet|opus|gemini|codex|status>
# Called by /model Telegram command or manually
set -euo pipefail

SWITCHER="$HOME/Desktop/🦀/scripts/openclaw-model-switcher-pack.sh"
CLAW_HOME="${CLAW_HOME:-$HOME/.clawdbot}"
CONFIG="$CLAW_HOME/clawdbot.json"
AUTH_FILE="$CLAW_HOME/agents/main/agent/auth-profiles.json"
LOG_FILE="$CLAW_HOME/logs/model-switch.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] $1" | tee -a "$LOG_FILE"; }

TARGET="${1:-status}"

# Normalize input (case insensitive)
TARGET=$(echo "$TARGET" | tr '[:upper:]' '[:lower:]' | xargs)

get_status() {
    python3 -c "
import json
with open('$CONFIG') as f:
    data = json.load(f)
m = data.get('agents',{}).get('defaults',{}).get('model',{})
primary = m.get('primary','unknown')
fallbacks = m.get('fallbacks',[])
print(f'Primary: {primary}')
print(f'Fallbacks: {\", \".join(fallbacks) or \"none\"}')
"
}

test_model() {
    local model_name="$1"
    log "Testing $model_name..."
    # Quick test via clawdbot agent
    local result
    result=$(timeout 30 clawdbot agent --local --agent main --message "Reply with exactly one word: OK" --thinking low --json 2>&1 || echo "FAIL")
    if echo "$result" | grep -q '"provider"'; then
        local provider=$(echo "$result" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('meta',{}).get('agentMeta',{}).get('provider','unknown'))" 2>/dev/null || echo "unknown")
        local model=$(echo "$result" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('meta',{}).get('agentMeta',{}).get('model','unknown'))" 2>/dev/null || echo "unknown")
        log "✅ $model_name OK — responding on $provider/$model"
        return 0
    else
        log "❌ $model_name FAILED"
        return 1
    fi
}

case "$TARGET" in
    status|s)
        echo "=== Bella Model Status ==="
        get_status
        echo ""
        # Show token expiry
        python3 - "$AUTH_FILE" << 'PYEOF'
import json, time, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
now = int(time.time() * 1000)
for name, prof in data.get("profiles", {}).items():
    expires = prof.get("expires", 0)
    if expires:
        remaining = (expires - now) // 3600000
        status = f"{remaining}h remaining" if expires > now else f"EXPIRED {abs(remaining)}h ago"
        print(f"Token {name}: {status}")
    else:
        ptype = prof.get("type", "?")
        print(f"Token {name}: {ptype} (no expiry)")
PYEOF
        ;;

    sonnet|sonnet46|claude)
        log "Switching to Sonnet 4.6 (primary) + Gemini (fallback) + Codex (last resort)..."
        bash "$SWITCHER" sonnet46
        log "Model switched to Sonnet 4.6"
        echo ""
        echo "✅ Model: Claude Sonnet 4.6"
        echo "   Fallback 1: Gemini 3 Flash Preview"
        echo "   Fallback 2: Codex GPT-5.3"
        ;;

    opus|opus46)
        log "Switching to Opus 4.6 (primary) + Sonnet (fallback)..."
        python3 - "$CONFIG" << 'PYEOF'
import json
with open("/Users/hafsahnuzhat/.clawdbot/clawdbot.json") as f:
    data = json.load(f)
data["agents"]["defaults"]["model"]["primary"] = "anthropic/claude-opus-4-6"
data["agents"]["defaults"]["model"]["fallbacks"] = ["anthropic/claude-sonnet-4-6", "google/gemini-3-flash-preview"]
with open("/Users/hafsahnuzhat/.clawdbot/clawdbot.json", "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PYEOF
        clawdbot gateway restart >/dev/null 2>&1 || true
        log "Model switched to Opus 4.6"
        echo ""
        echo "✅ Model: Claude Opus 4.6"
        echo "   Fallback 1: Claude Sonnet 4.6"
        echo "   Fallback 2: Gemini 3 Flash Preview"
        ;;

    gemini|gemini3)
        log "Switching to Gemini 3 Flash (primary) + Sonnet (fallback) + Codex (last resort)..."
        python3 - "$CONFIG" << 'PYEOF'
import json
with open("/Users/hafsahnuzhat/.clawdbot/clawdbot.json") as f:
    data = json.load(f)
data["agents"]["defaults"]["model"]["primary"] = "google/gemini-3-flash-preview"
data["agents"]["defaults"]["model"]["fallbacks"] = ["anthropic/claude-sonnet-4-6", "openai-codex/gpt-5.3-codex"]
with open("/Users/hafsahnuzhat/.clawdbot/clawdbot.json", "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PYEOF
        clawdbot gateway restart >/dev/null 2>&1 || true
        log "Model switched to Gemini 3 Flash"
        echo ""
        echo "⚠️ Model: Gemini 3 Flash Preview (FREE TIER — conserve usage)"
        echo "   Fallback 1: Claude Sonnet 4.6"
        echo "   Fallback 2: Codex GPT-5.3"
        ;;

    codex|codex53|gpt)
        log "Switching to Codex GPT-5.3 (primary) + Sonnet (fallback) + Gemini (last resort)..."
        bash "$SWITCHER" cooldown-bypass 2>/dev/null || true
        python3 - "$CONFIG" << 'PYEOF'
import json
with open("/Users/hafsahnuzhat/.clawdbot/clawdbot.json") as f:
    data = json.load(f)
data["agents"]["defaults"]["model"]["primary"] = "openai-codex/gpt-5.3-codex"
data["agents"]["defaults"]["model"]["fallbacks"] = ["anthropic/claude-sonnet-4-6", "google/gemini-3-flash-preview"]
with open("/Users/hafsahnuzhat/.clawdbot/clawdbot.json", "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PYEOF
        clawdbot gateway restart >/dev/null 2>&1 || true
        log "Model switched to Codex GPT-5.3"
        echo ""
        echo "✅ Model: Codex GPT-5.3"
        echo "   Fallback 1: Claude Sonnet 4.6"
        echo "   Fallback 2: Gemini 3 Flash Preview"
        ;;

    test)
        echo "=== Testing current model ==="
        test_model "current"
        ;;

    *)
        echo "Unknown model: $TARGET"
        echo ""
        echo "Usage: bash model-switch.sh <model>"
        echo ""
        echo "Available models:"
        echo "  sonnet  — Claude Sonnet 4.6 (recommended)"
        echo "  opus    — Claude Opus 4.6"
        echo "  gemini  — Gemini 3 Flash Preview (free tier)"
        echo "  codex   — Codex GPT-5.3"
        echo "  status  — Show current model + token health"
        echo "  test    — Test if current model responds"
        exit 1
        ;;
esac
