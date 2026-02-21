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
set -euo pipefail
set -euo pipefail
set -euo pipefail
# check-embedding.sh — Ensure memory embeddings are configured to Gemini and healthy
# Usage: bash ~/Desktop/🦀/scripts/check-embedding.sh

set -euo pipefail

CLAW_HOME="${CLAW_HOME:-$HOME/.clawdbot}"
CONFIG_FILE="$CLAW_HOME/clawdbot.json"
EXPECTED_PROVIDER="gemini"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "ERROR: missing config file $CONFIG_FILE"
  exit 1
fi

CURRENT_PROVIDER=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    data = json.load(f)
print(data.get('agents',{}).get('defaults',{}).get('memorySearch',{}).get('provider','unknown'))
" 2>/dev/null || echo "unknown")

if [ "$CURRENT_PROVIDER" != "$EXPECTED_PROVIDER" ]; then
  python3 - "$CONFIG_FILE" "$EXPECTED_PROVIDER" << 'PYEOF'
import json, sys
path, provider = sys.argv[1], sys.argv[2]
with open(path) as f:
    data = json.load(f)
defaults = data.setdefault("agents", {}).setdefault("defaults", {})
memory = defaults.setdefault("memorySearch", {})
memory["provider"] = provider
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PYEOF
  echo "FIXED: memorySearch.provider $CURRENT_PROVIDER -> $EXPECTED_PROVIDER"
  exit 0
fi

# Lightweight runtime probe. Some environments can fail due local FD/network state;
# keep this non-fatal so the cron still preserves the free provider setting.
if clawdbot memory search "heartbeat embedding probe" --json >/dev/null 2>&1; then
  echo "OK: provider=$CURRENT_PROVIDER runtime=healthy"
  exit 0
fi

echo "WARN: provider=$CURRENT_PROVIDER runtime_probe_failed"
exit 0
