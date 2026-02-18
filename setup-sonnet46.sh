#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# ClawdBot → Claude Sonnet 4.6 Setup Script
# Switches primary model to Claude Sonnet 4.6 with Gemini fallback
# Also installs the model-switcher skill for easy switching later
#
# Usage: bash setup-sonnet46.sh [/path/to/clawdbot/home]
# If no path given, auto-detects from clawdbot config
#
# What this does:
# 1. Patches models.generated.js to register claude-sonnet-4-6
# 2. Updates clawdbot.json (primary → Sonnet 4.6, fallback → Gemini)
# 3. Creates model-switcher skill for switching between models
# 4. Restarts the gateway
#
# Compatible with macOS bash 3.2+ and Linux
# ═══════════════════════════════════════════════════════════════════

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ClawdBot → Claude Sonnet 4.6 Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ═══════════════════════════════════════════════════════════
# STEP 0: Find ClawdBot installation
# ═══════════════════════════════════════════════════════════
BOT_HOME="${1:-}"

if [ -z "$BOT_HOME" ]; then
    # Try common locations
    for candidate in \
        "$HOME/.clawdbot" \
        "$HOME/Desktop/"*"CLAWD"*; do
        if [ -f "$candidate/config/clawdbot.json" ] || [ -f "$candidate/clawdbot.json" ]; then
            BOT_HOME="$candidate"
            break
        fi
    done
fi

if [ -z "$BOT_HOME" ] || { [ ! -f "$BOT_HOME/config/clawdbot.json" ] && [ ! -f "$BOT_HOME/clawdbot.json" ]; }; then
    echo "❌ Could not find ClawdBot installation."
    echo ""
    echo "Please run with your ClawdBot home path:"
    echo " bash setup-sonnet46.sh /path/to/your/clawdbot"
    echo ""
    echo "The directory should contain config/clawdbot.json or clawdbot.json"
    exit 1
fi

if [ -f "$BOT_HOME/config/clawdbot.json" ]; then
    CONFIG="$BOT_HOME/config/clawdbot.json"
else
    CONFIG="$BOT_HOME/clawdbot.json"
fi
echo "✅ Found ClawdBot at: $BOT_HOME"

# Find models.generated.js in npm
MODELS_FILE=""
for candidate in \
    "$HOME/.npm-global/lib/node_modules/clawdbot/node_modules/@mariozechner/pi-ai/dist/models.generated.js" \
    "/usr/local/lib/node_modules/clawdbot/node_modules/@mariozechner/pi-ai/dist/models.generated.js" \
    "/usr/lib/node_modules/clawdbot/node_modules/@mariozechner/pi-ai/dist/models.generated.js" \
    "$(npm root -g 2>/dev/null)/clawdbot/node_modules/@mariozechner/pi-ai/dist/models.generated.js"; do
    if [ -f "$candidate" ]; then
        MODELS_FILE="$candidate"
        break
    fi
done

if [ -z "$MODELS_FILE" ]; then
    echo "⚠️ Could not find models.generated.js — will skip patching."
    echo "   If Sonnet 4.6 doesn't work, find and patch it manually."
else
    echo "✅ Found models registry: $MODELS_FILE"
fi

# Find auth profiles
AUTH_PROFILES=""
for candidate in \
    "$BOT_HOME/state/agents/main/agent/auth-profiles.json" \
    "$BOT_HOME/auth-profiles.json"; do
    if [ -f "$candidate" ]; then
        AUTH_PROFILES="$candidate"
        break
    fi
done

echo ""

# ═══════════════════════════════════════════════════════════
# STEP 1: Patch models.generated.js
# ═══════════════════════════════════════════════════════════
if [ -n "$MODELS_FILE" ]; then
    # Check if already patched
    if grep -q '"claude-sonnet-4-6"' "$MODELS_FILE" 2>/dev/null; then
        echo "✅ models.generated.js already has claude-sonnet-4-6"
    else
        echo "🔧 Patching models.generated.js..."
        python3 - "$MODELS_FILE" << 'PYEOF'
import sys, re
models_path = sys.argv[1]
with open(models_path, 'r') as f:
    content = f.read()

# Find the claude-sonnet-4-5-20250929 entry and add claude-sonnet-4-6 after it
sonnet_45_entry = '''        "claude-sonnet-4-5-20250929": {
            id: "claude-sonnet-4-5-20250929",
            name: "Claude Sonnet 4.5",
            api: "anthropic-messages",
            provider: "anthropic",
            baseUrl: "https://api.anthropic.com",
            reasoning: true,
            input: ["text", "image"],
            cost: {
                input: 3,
                output: 15,
                cacheRead: 0.3,
                cacheWrite: 3.75,
            },
            contextWindow: 200000,
            maxTokens: 64000,
        },'''

sonnet_46_entry = '''        "claude-sonnet-4-5-20250929": {
            id: "claude-sonnet-4-5-20250929",
            name: "Claude Sonnet 4.5",
            api: "anthropic-messages",
            provider: "anthropic",
            baseUrl: "https://api.anthropic.com",
            reasoning: true,
            input: ["text", "image"],
            cost: {
                input: 3,
                output: 15,
                cacheRead: 0.3,
                cacheWrite: 3.75,
            },
            contextWindow: 200000,
            maxTokens: 64000,
        },
        "claude-sonnet-4-6": {
            id: "claude-sonnet-4-6",
            name: "Claude Sonnet 4.6",
            api: "anthropic-messages",
            provider: "anthropic",
            baseUrl: "https://api.anthropic.com",
            reasoning: true,
            input: ["text", "image"],
            cost: {
                input: 3,
                output: 15,
                cacheRead: 0.3,
                cacheWrite: 3.75,
            },
            contextWindow: 1000000,
            maxTokens: 64000,
        },'''

if sonnet_45_entry in content:
    content = content.replace(sonnet_45_entry, sonnet_46_entry)
    with open(models_path, 'w') as f:
        f.write(content)
    print("  ✅ Added claude-sonnet-4-6 to models registry")
else:
    # Fallback: try to find any anthropic provider section and append
    print("  ⚠️ Could not find exact insertion point.")
    print("     The claude-sonnet-4-5-20250929 entry format may differ.")
    print("     You may need to manually add claude-sonnet-4-6 to models.generated.js")
    sys.exit(1)
PYEOF
    fi

    # Also patch claude-opus-4-6 if missing
    if grep -q '"claude-opus-4-6"' "$MODELS_FILE" 2>/dev/null; then
        echo "✅ models.generated.js already has claude-opus-4-6"
    else
        echo "🔧 Patching claude-opus-4-6 into models.generated.js..."
        python3 - "$MODELS_FILE" << 'PYEOF'
import sys
models_path = sys.argv[1]
with open(models_path, 'r') as f:
    content = f.read()

opus_45_tail = '''            contextWindow: 200000,
            maxTokens: 64000,
        },
        "claude-sonnet-4-0":'''

opus_46_insert = '''            contextWindow: 200000,
            maxTokens: 64000,
        },
        "claude-opus-4-6": {
            id: "claude-opus-4-6",
            name: "Claude Opus 4.6",
            api: "anthropic-messages",
            provider: "anthropic",
            baseUrl: "https://api.anthropic.com",
            reasoning: true,
            input: ["text", "image"],
            cost: {
                input: 15,
                output: 75,
                cacheRead: 1.5,
                cacheWrite: 18.75,
            },
            contextWindow: 200000,
            maxTokens: 32000,
        },
        "claude-sonnet-4-0":'''

if opus_45_tail in content:
    content = content.replace(opus_45_tail, opus_46_insert, 1)
    with open(models_path, 'w') as f:
        f.write(content)
    print("  ✅ Added claude-opus-4-6 to models registry")
else:
    print("  ⚠️ Could not find opus insertion point — skipping (non-critical)")
PYEOF
    fi
fi

echo ""

# ═══════════════════════════════════════════════════════════
# STEP 2: Update clawdbot.json
# ═══════════════════════════════════════════════════════════
echo "🔧 Updating clawdbot.json..."
python3 - "$CONFIG" << 'PYEOF'
import json, sys
config_path = sys.argv[1]
with open(config_path) as f:
    config = json.load(f)

defaults = config.get("agents", {}).get("defaults", {})

# Update primary model and fallback
defaults.setdefault("model", {})
old_primary = defaults["model"].get("primary", "unknown")
defaults["model"]["primary"] = "anthropic/claude-sonnet-4-6"
defaults["model"]["fallbacks"] = ["google/gemini-3-flash-preview"]

# Update models aliases
defaults.setdefault("models", {})
# Add new entries
defaults["models"]["anthropic/claude-opus-4-6"] = {"alias": "opus"}
defaults["models"]["anthropic/claude-sonnet-4-6"] = {"alias": "sonnet"}

# Keep existing entries
if "google/gemini-3-flash-preview" not in defaults["models"]:
    defaults["models"]["google/gemini-3-flash-preview"] = {"alias": "gemini-flash"}

with open(config_path, "w") as f:
    json.dump(config, f, indent=2)
    f.write("\n")

print(f"  ✅ Primary: {old_primary} → anthropic/claude-sonnet-4-6")
print(f"  ✅ Fallback: google/gemini-3-flash-preview")
PYEOF

echo ""

# ═══════════════════════════════════════════════════════════
# STEP 3: Create model-switcher skill
# ═══════════════════════════════════════════════════════════
echo "🔧 Creating model-switcher skill..."

# Determine skill directory — try workspace first, then config sandbox
SKILL_DIR=""
for candidate in \
    "$BOT_HOME/workspace/skills/model-switcher" \
    "$BOT_HOME/skills/model-switcher"; do
    parent="$(dirname "$candidate")"
    if [ -d "$parent" ]; then
        SKILL_DIR="$candidate"
        break
    fi
done

# Fallback: find any skills directory
if [ -z "$SKILL_DIR" ]; then
    SKILLS_PARENT=$(find "$BOT_HOME" -maxdepth 3 -type d -name "skills" 2>/dev/null | head -1)
    if [ -n "$SKILLS_PARENT" ]; then
        SKILL_DIR="$SKILLS_PARENT/model-switcher"
    else
        SKILL_DIR="$BOT_HOME/skills/model-switcher"
    fi
fi

mkdir -p "$SKILL_DIR/scripts"

# Write SKILL.md
cat > "$SKILL_DIR/SKILL.md" << 'SKILLEOF'
---
name: model-switcher
description: Universal model switcher for Clawdbot. Use when told to switch model, use gemini, use opus, use sonnet, change model, swap model, rate limited, or switch to [any model name].
---

# Universal Model Switcher

Switch Clawdbot's primary model between any configured provider without breaking config.

## Model Registry

| Alias | Full Model ID | Provider | Use Case |
|-------|---------------|----------|----------|
| opus | anthropic/claude-opus-4-6 | anthropic | Max intelligence, expensive |
| sonnet | anthropic/claude-sonnet-4-6 | anthropic | Default — coding, complex tasks |
| gemini | google/gemini-3-flash-preview | google | Fast, free tier |
| deepseek | deepseek/deepseek-chat | deepseek | Budget, decent quality |
| openrouter | openrouter/auto | openrouter | Universal fallback |

## How to Switch

```bash
bash <SKILL_DIR>/scripts/switch-model.sh opus
bash <SKILL_DIR>/scripts/switch-model.sh sonnet
bash <SKILL_DIR>/scripts/switch-model.sh gemini
bash <SKILL_DIR>/scripts/switch-model.sh status
```

## Fallback Chain

- opus → sonnet (cheaper)
- sonnet → gemini (free tier)
- gemini → sonnet (paid reliable)
SKILLEOF

# Replace placeholder with actual path
sed -i.bak "s|<SKILL_DIR>|$SKILL_DIR|g" "$SKILL_DIR/SKILL.md" 2>/dev/null || \
sed -i '' "s|<SKILL_DIR>|$SKILL_DIR|g" "$SKILL_DIR/SKILL.md" 2>/dev/null
rm -f "$SKILL_DIR/SKILL.md.bak"

# Write switch-model.sh
cat > "$SKILL_DIR/scripts/switch-model.sh" << 'SCRIPTEOF'
#!/bin/bash
# Universal Model Switcher for Clawdbot
# Usage: switch-model.sh [opus|sonnet|gemini|deepseek|openrouter|status]

set -e

# Find bot home
BOT_HOME=""
for candidate in \
    "$HOME/.clawdbot" \
    "$HOME/Desktop/"*"CLAWD"*; do
    if [ -f "$candidate/config/clawdbot.json" ]; then
        BOT_HOME="$candidate"
        break
    fi
done

if [ -z "$BOT_HOME" ]; then
    echo "❌ Could not find ClawdBot installation."
    exit 1
fi

CONFIG="$BOT_HOME/config/clawdbot.json"

get_model_info() {
    local alias="$1"
    case "$alias" in
        opus) MODEL_ID="anthropic/claude-opus-4-6"; FALLBACK="anthropic/claude-sonnet-4-6" ;;
        sonnet) MODEL_ID="anthropic/claude-sonnet-4-6"; FALLBACK="google/gemini-3-flash-preview" ;;
        gemini) MODEL_ID="google/gemini-3-flash-preview"; FALLBACK="anthropic/claude-sonnet-4-6" ;;
        deepseek) MODEL_ID="deepseek/deepseek-chat"; FALLBACK="google/gemini-3-flash-preview" ;;
        openrouter) MODEL_ID="openrouter/auto"; FALLBACK="google/gemini-3-flash-preview" ;;
        *) return 1 ;;
    esac
    return 0
}

TARGET="${1:-}"

if [ -z "$TARGET" ] || [ "$TARGET" = "status" ]; then
    python3 - "$CONFIG" << 'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    config = json.load(f)
model = config["agents"]["defaults"]["model"]
print(f"Current Primary: {model['primary']}")
print(f"Current Fallbacks: {', '.join(model.get('fallbacks', []))}")
PYEOF
    [ "$TARGET" = "status" ] && exit 0
    echo "Usage: switch-model.sh [opus|sonnet|gemini|deepseek|openrouter|status]"
    exit 1
fi

if ! get_model_info "$TARGET"; then
    echo "Unknown model: $TARGET"
    exit 1
fi

echo "Switching to: $TARGET ($MODEL_ID)"

python3 - "$CONFIG" "$MODEL_ID" "$FALLBACK" << 'PYEOF'
import json, sys
config_path = sys.argv[1]
primary = sys.argv[2]
fallback = sys.argv[3]
with open(config_path) as f:
    config = json.load(f)
config["agents"]["defaults"]["model"]["primary"] = primary
config["agents"]["defaults"]["model"]["fallbacks"] = [fallback]
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)
    f.write("\n")
PYEOF

echo "Restarting gateway..."
clawdbot gateway restart 2>&1 || echo "Restart failed — run manually."
echo "DONE! Switched to $TARGET."
SCRIPTEOF

chmod +x "$SKILL_DIR/scripts/switch-model.sh"

echo "  ✅ Created: $SKILL_DIR/SKILL.md"
echo "  ✅ Created: $SKILL_DIR/scripts/switch-model.sh"
echo ""

# ═══════════════════════════════════════════════════════════
# STEP 4: Restart gateway
# ═══════════════════════════════════════════════════════════
echo "🔄 Restarting gateway..."
clawdbot gateway restart 2>&1 || echo "⚠️ Gateway restart failed — run manually: clawdbot gateway restart"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " DONE! Your bot is now running Claude Sonnet 4.6"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo " Primary: anthropic/claude-sonnet-4-6"
echo " Fallback: google/gemini-3-flash-preview"
echo ""
