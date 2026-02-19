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
#!/bin/bash
# OpenClaw Universal Model Switcher Pack
# Usage:
#   bash openclaw-model-switcher-pack.sh status
#   bash openclaw-model-switcher-pack.sh codex53
#   bash openclaw-model-switcher-pack.sh codex52
#   bash openclaw-model-switcher-pack.sh gemini
#   bash openclaw-model-switcher-pack.sh opus46
#   bash openclaw-model-switcher-pack.sh opus45
#   bash openclaw-model-switcher-pack.sh sonnet46
#   bash openclaw-model-switcher-pack.sh cooldown-bypass
#   bash openclaw-model-switcher-pack.sh patch-codex53
#
# Optional:
#   CLAW_HOME=/path/to/.clawdbot bash openclaw-model-switcher-pack.sh codex53

set -euo pipefail

CLAW_HOME="${CLAW_HOME:-}"
if [ -z "$CLAW_HOME" ]; then
    for candidate in "$HOME/.clawdbot" "$HOME/Desktop/"*"CLAWD"*; do
        if [ -f "$candidate/clawdbot.json" ] || [ -f "$candidate/config/clawdbot.json" ]; then
            CLAW_HOME="$candidate"
            break
        fi
    done
fi

if [ -z "$CLAW_HOME" ]; then
    echo "Could not locate OpenClaw/Clawdbot home."
    echo "Set CLAW_HOME and rerun."
    exit 1
fi

if [ -f "$CLAW_HOME/config/clawdbot.json" ]; then
    CONFIG="$CLAW_HOME/config/clawdbot.json"
elif [ -f "$CLAW_HOME/clawdbot.json" ]; then
    CONFIG="$CLAW_HOME/clawdbot.json"
else
    echo "Could not find clawdbot.json."
    exit 1
fi

AUTH_FILES=()
[ -f "$CLAW_HOME/auth-profiles.json" ] && AUTH_FILES+=("$CLAW_HOME/auth-profiles.json")
[ -f "$CLAW_HOME/agents/main/agent/auth-profiles.json" ] && AUTH_FILES+=("$CLAW_HOME/agents/main/agent/auth-profiles.json")
[ -f "$CLAW_HOME/state/agents/main/agent/auth-profiles.json" ] && AUTH_FILES+=("$CLAW_HOME/state/agents/main/agent/auth-profiles.json")

find_models_file() {
    for candidate in \
        "$HOME/.npm-global/lib/node_modules/clawdbot/node_modules/@mariozechner/pi-ai/dist/models.generated.js" \
        "/usr/local/lib/node_modules/clawdbot/node_modules/@mariozechner/pi-ai/dist/models.generated.js" \
        "/usr/lib/node_modules/clawdbot/node_modules/@mariozechner/pi-ai/dist/models.generated.js" \
        "$(npm root -g 2>/dev/null)/clawdbot/node_modules/@mariozechner/pi-ai/dist/models.generated.js"; do
        [ -f "$candidate" ] && { echo "$candidate"; return 0; }
    done
    return 1
}

MODELS_FILE="$(find_models_file || true)"

is_model_available() {
    local model_id="$1"
    local short_id="${model_id##*/}"
    [ -n "${MODELS_FILE:-}" ] && (grep -q "\"$model_id\"" "$MODELS_FILE" || grep -q "\"$short_id\"" "$MODELS_FILE")
}

patch_codex53() {
    if [ -z "${MODELS_FILE:-}" ]; then
        echo "No models.generated.js found. Cannot patch codex53."
        return 1
    fi

    python3 - "$MODELS_FILE" << 'PYEOF'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text()

if '"gpt-5.3-codex"' in text:
    print("gpt-5.3-codex already present")
    raise SystemExit(0)

anchor = '''        "gpt-5.2-codex": {
            id: "gpt-5.2-codex",
            name: "GPT-5.2 Codex",
            api: "openai-codex-responses",
            provider: "openai-codex",
            baseUrl: "https://chatgpt.com/backend-api",
            reasoning: true,
            input: ["text", "image"],
            cost: {
                input: 1.75,
                output: 14,
                cacheRead: 0.175,
                cacheWrite: 0,
            },
            contextWindow: 272000,
            maxTokens: 128000,
        },'''

insert = '''        "gpt-5.2-codex": {
            id: "gpt-5.2-codex",
            name: "GPT-5.2 Codex",
            api: "openai-codex-responses",
            provider: "openai-codex",
            baseUrl: "https://chatgpt.com/backend-api",
            reasoning: true,
            input: ["text", "image"],
            cost: {
                input: 1.75,
                output: 14,
                cacheRead: 0.175,
                cacheWrite: 0,
            },
            contextWindow: 272000,
            maxTokens: 128000,
        },
        "gpt-5.3-codex": {
            id: "gpt-5.3-codex",
            name: "GPT-5.3 Codex",
            api: "openai-codex-responses",
            provider: "openai-codex",
            baseUrl: "https://chatgpt.com/backend-api",
            reasoning: true,
            input: ["text", "image"],
            cost: {
                input: 1.75,
                output: 14,
                cacheRead: 0.175,
                cacheWrite: 0,
            },
            contextWindow: 272000,
            maxTokens: 128000,
        },'''

if anchor not in text:
    print("Could not find gpt-5.2-codex insertion anchor")
    raise SystemExit(1)

path.write_text(text.replace(anchor, insert, 1))
print("Patched gpt-5.3-codex into models.generated.js")
PYEOF
}

set_model() {
    local primary="$1"
    local fallback="$2"
    local fallback2="${3:-}"

    python3 - "$CONFIG" "$primary" "$fallback" "$fallback2" << 'PYEOF'
import json, sys
path, primary, fallback, fallback2 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with open(path) as f:
    data = json.load(f)

defaults = data.setdefault("agents", {}).setdefault("defaults", {})
model = defaults.setdefault("model", {})
model["primary"] = primary
fallbacks = [x for x in [fallback, fallback2] if x]
model["fallbacks"] = fallbacks

models = defaults.setdefault("models", {})
alias_map = {
    "openai-codex/gpt-5.3-codex": "codex53",
    "openai-codex/gpt-5.2-codex": "codex52",
    "google/gemini-3-flash-preview": "gemini",
    "anthropic/claude-opus-4-6": "opus46",
    "anthropic/claude-opus-4-5": "opus45",
    "anthropic/claude-sonnet-4-6": "sonnet46",
}
for model_id, alias in alias_map.items():
    entry = models.get(model_id)
    if not isinstance(entry, dict):
        models[model_id] = {"alias": alias}
        continue
    if not entry.get("alias"):
        entry["alias"] = alias

with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
print(f"Set primary={primary}")
print(f"Set fallbacks={fallbacks}")
PYEOF
}

cooldown_bypass() {
    if [ "${#AUTH_FILES[@]}" -eq 0 ]; then
        echo "No auth-profiles.json found; skipping cooldown reset."
        return 0
    fi

    for auth in "${AUTH_FILES[@]}"; do
        python3 - "$auth" << 'PYEOF'
import json, sys
path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

stats = data.setdefault("usageStats", {})
for _, entry in stats.items():
    entry["cooldownUntil"] = 0
    entry["errorCount"] = 0
    entry["failureCounts"] = {}
    entry.pop("lastFailureAt", None)

with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

print(f"Cooldown reset in {path}")
PYEOF
    done
}

any_openai_codex_cooldown() {
    if [ "${#AUTH_FILES[@]}" -eq 0 ]; then
        return 1
    fi

    local now_ms
    now_ms="$(python3 - << 'PYEOF'
import time
print(int(time.time() * 1000))
PYEOF
)"

    for auth in "${AUTH_FILES[@]}"; do
        if python3 - "$auth" "$now_ms" << 'PYEOF'
import json, sys
path, now_ms = sys.argv[1], int(sys.argv[2])
try:
    with open(path) as f:
        data = json.load(f)
except Exception:
    raise SystemExit(1)
for key, entry in (data.get("usageStats") or {}).items():
    if not isinstance(entry, dict):
        continue
    if "openai-codex" not in str(key):
        continue
    cooldown = int(entry.get("cooldownUntil") or 0)
    if cooldown > now_ms:
        raise SystemExit(0)
raise SystemExit(1)
PYEOF
        then
            return 0
        fi
    done
    return 1
}

status() {
    python3 - "$CONFIG" << 'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
m = data.get("agents", {}).get("defaults", {}).get("model", {})
print("Primary:", m.get("primary", "unknown"))
print("Fallbacks:", ", ".join(m.get("fallbacks", [])) or "none")
PYEOF
}

TARGET="${1:-status}"
case "$TARGET" in
    status)
        status
        ;;
    patch-codex53)
        patch_codex53
        ;;
    codex53|gpt|codex)
        any_openai_codex_cooldown && cooldown_bypass || true
        if ! is_model_available "openai-codex/gpt-5.3-codex"; then
            echo "codex53 missing in registry. Attempting patch..."
            patch_codex53 || true
        fi
        if is_model_available "openai-codex/gpt-5.3-codex"; then
            set_model "openai-codex/gpt-5.3-codex" "openai-codex/gpt-5.2-codex"
        else
            echo "codex53 still unavailable, falling back to codex52."
            set_model "openai-codex/gpt-5.2-codex" "openai-codex/gpt-5.3-codex"
        fi
        clawdbot gateway restart >/dev/null 2>&1 || true
        status
        ;;
    codex52|gpt52)
        set_model "openai-codex/gpt-5.2-codex" "openai-codex/gpt-5.3-codex"
        clawdbot gateway restart >/dev/null 2>&1 || true
        status
        ;;
    gemini|gemini3|gemini-flash)
        set_model "google/gemini-3-flash-preview" "anthropic/claude-sonnet-4-6"
        clawdbot gateway restart >/dev/null 2>&1 || true
        status
        ;;
    opus46|opus)
        set_model "anthropic/claude-opus-4-6" "anthropic/claude-opus-4-5"
        clawdbot gateway restart >/dev/null 2>&1 || true
        status
        ;;
    opus45)
        set_model "anthropic/claude-opus-4-5" "google/gemini-3-flash-preview"
        clawdbot gateway restart >/dev/null 2>&1 || true
        status
        ;;
    sonnet46|sonnet)
        set_model "anthropic/claude-sonnet-4-6" "google/gemini-3-flash-preview"
        clawdbot gateway restart >/dev/null 2>&1 || true
        status
        ;;
    cooldown-bypass|clear-cooldown)
        cooldown_bypass
        ;;
    *)
        echo "Unknown target: $TARGET"
        echo "Available: status, codex53, codex52, gemini, opus46, opus45, sonnet46, cooldown-bypass, patch-codex53"
        exit 1
        ;;
esac
