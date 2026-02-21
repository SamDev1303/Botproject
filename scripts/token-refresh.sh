#!/usr/bin/env bash
# token-refresh.sh — Monitor and auto-refresh provider tokens
# Usage:
#   bash token-refresh.sh status    — Show all token health
#   bash token-refresh.sh check     — Check & warn if expiring soon
#   bash token-refresh.sh fix       — Attempt to refresh expired tokens
# Run via heartbeat every 30 minutes
set -euo pipefail

CLAW_HOME="${CLAW_HOME:-$HOME/.clawdbot}"
AUTH_FILE="$CLAW_HOME/agents/main/agent/auth-profiles.json"
CONFIG="$CLAW_HOME/clawdbot.json"
LOG_FILE="$CLAW_HOME/logs/token-refresh.log"
WARN_HOURS=24  # Warn when token expires within this many hours

mkdir -p "$(dirname "$LOG_FILE")"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] $1" | tee -a "$LOG_FILE"; }

ACTION="${1:-status}"

case "$ACTION" in
    status)
        echo "=== Token Health ==="
        python3 - "$AUTH_FILE" << 'PYEOF'
import json, time, sys
from datetime import datetime

with open(sys.argv[1]) as f:
    data = json.load(f)

now = int(time.time() * 1000)

for name, prof in data.get("profiles", {}).items():
    ptype = prof.get("type", "unknown")
    expires = prof.get("expires", 0)

    if ptype == "api_key":
        print(f"  ✅ {name}: API key (never expires)")
    elif expires:
        remaining_h = (expires - now) // 3600000
        remaining_d = remaining_h // 24
        expiry_date = datetime.fromtimestamp(expires / 1000).strftime("%Y-%m-%d %H:%M")

        if expires < now:
            print(f"  ❌ {name}: EXPIRED {abs(remaining_h)}h ago (expired {expiry_date})")
        elif remaining_h < 24:
            print(f"  ⚠️  {name}: EXPIRING SOON — {remaining_h}h left (expires {expiry_date})")
        else:
            print(f"  ✅ {name}: OK — {remaining_d}d {remaining_h % 24}h left (expires {expiry_date})")
    else:
        print(f"  ℹ️  {name}: {ptype} (no expiry tracked)")

# Check cooldown status
usage = data.get("usageStats", {})
for key, entry in usage.items():
    if not isinstance(entry, dict):
        continue
    cooldown = int(entry.get("cooldownUntil") or 0)
    errors = int(entry.get("errorCount") or 0)
    if cooldown > now:
        remaining = (cooldown - now) // 60000
        print(f"  🔴 {key}: IN COOLDOWN — {remaining} min remaining")
    elif errors > 0:
        print(f"  🟡 {key}: {errors} recent errors (no cooldown)")
PYEOF
        ;;

    check)
        log "Running token health check..."
        ISSUES=$(python3 - "$AUTH_FILE" "$WARN_HOURS" << 'PYEOF'
import json, time, sys

with open(sys.argv[1]) as f:
    data = json.load(f)

now = int(time.time() * 1000)
warn_ms = int(sys.argv[2]) * 3600 * 1000
issues = []

for name, prof in data.get("profiles", {}).items():
    ptype = prof.get("type", "unknown")
    expires = prof.get("expires", 0)

    if ptype == "api_key":
        continue

    if expires and expires < now:
        issues.append(f"EXPIRED:{name}")
    elif expires and (expires - now) < warn_ms:
        hours = (expires - now) // 3600000
        issues.append(f"EXPIRING:{name}:{hours}h")

print("\n".join(issues) if issues else "OK")
PYEOF
        )

        if [ "$ISSUES" = "OK" ]; then
            log "All tokens healthy"
            echo "✅ All tokens healthy"
        else
            log "Token issues detected: $ISSUES"
            echo "⚠️ Token issues:"

            while IFS= read -r issue; do
                TYPE=$(echo "$issue" | cut -d: -f1)
                NAME=$(echo "$issue" | cut -d: -f2)

                case "$TYPE" in
                    EXPIRED)
                        echo "  ❌ $NAME: EXPIRED — needs manual refresh"
                        if [[ "$NAME" == *"anthropic"* ]]; then
                            echo "     Fix: Run 'claude login' in terminal, then copy token"
                        elif [[ "$NAME" == *"codex"* ]] || [[ "$NAME" == *"openai"* ]]; then
                            echo "     Fix: Run 'codex login' or wait for rate limit reset"
                        fi
                        ;;
                    EXPIRING)
                        HOURS=$(echo "$issue" | cut -d: -f3)
                        echo "  ⚠️  $NAME: Expiring in $HOURS"
                        ;;
                esac
            done <<< "$ISSUES"

            # Auto-trigger failover if primary model token is expired
            CURRENT_PRIMARY=$(python3 -c "
import json
with open('$CONFIG') as f:
    data = json.load(f)
print(data.get('agents',{}).get('defaults',{}).get('model',{}).get('primary','unknown'))
" 2>/dev/null)

            IS_PRIMARY_EXPIRED=$(echo "$ISSUES" | grep -c "EXPIRED" || true)
            if [ "$IS_PRIMARY_EXPIRED" -gt 0 ]; then
                log "Primary model token may be expired — triggering auto-failover..."
                echo ""
                echo "🔄 Running auto-failover..."
                bash "$HOME/Desktop/🦀/scripts/auto-failover.sh"
            fi
        fi
        ;;

    fix)
        log "Attempting token fixes..."

        # 1. Clear all cooldowns
        log "Clearing cooldowns..."
        bash "$HOME/Desktop/🦀/scripts/openclaw-model-switcher-pack.sh" cooldown-bypass 2>/dev/null || true

        # 2. Try to copy fresh Claude Code token to clawdbot
        log "Checking for fresh Claude Code token..."
        python3 << 'PYEOF'
import json, subprocess, time

# Try to get Claude Code token from keychain
try:
    result = subprocess.run(
        ["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0 and result.stdout.strip():
        creds = json.loads(result.stdout.strip())
        oauth = creds.get("claudeAiOauth", {})
        access = oauth.get("accessToken", "")
        refresh = oauth.get("refreshToken", "")
        expires = oauth.get("expiresAt", 0)
        now = int(time.time() * 1000)

        if access and expires > now:
            # Token is valid — copy to clawdbot auth
            auth_path = "/Users/hafsahnuzhat/.clawdbot/agents/main/agent/auth-profiles.json"
            with open(auth_path) as f:
                auth_data = json.load(f)

            profile = auth_data["profiles"]["anthropic:claude-cli"]
            profile["access"] = access
            if refresh:
                profile["refresh"] = refresh
            profile["expires"] = expires

            # Clear usage stats for anthropic
            for key in list(auth_data.get("usageStats", {}).keys()):
                if "anthropic" in str(key).lower():
                    entry = auth_data["usageStats"][key]
                    if isinstance(entry, dict):
                        entry["cooldownUntil"] = 0
                        entry["errorCount"] = 0
                        entry["failureCounts"] = {}

            with open(auth_path, "w") as f:
                json.dump(auth_data, f, indent=2)
                f.write("\n")

            hours = (expires - now) // 3600000
            print(f"✅ Anthropic token synced from Claude Code ({hours}h remaining)")
        else:
            print("⚠️  Claude Code token also expired — run 'claude login' in terminal")
    else:
        print("⚠️  No Claude Code credentials in keychain")
except Exception as e:
    print(f"⚠️  Could not check Claude Code token: {e}")
PYEOF

        # 3. Restart gateway
        log "Restarting gateway..."
        clawdbot gateway restart >/dev/null 2>&1 || true

        log "Token fix complete"
        echo ""
        bash "$0" status
        ;;

    *)
        echo "Usage: bash token-refresh.sh <status|check|fix>"
        exit 1
        ;;
esac
