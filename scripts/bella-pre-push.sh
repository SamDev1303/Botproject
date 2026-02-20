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

ROOT="/Users/hafsahnuzhat/Desktop/🦀"
cd "$ROOT"

echo "[1/4] Self-healing shell scripts..."
bash "$ROOT/skills/pre-push-guardian/scripts/self-heal-scripts.sh"

echo "[2/4] Scanning staged files for secrets and hardcoded keys..."
python3 "$ROOT/pre-push-check.py" --staged

echo "[3/4] Validating canonical GitHub/Vercel targets..."
bash "$ROOT/scripts/verify-allowed-targets.sh"

echo "[4/4] Guardrail check complete."
echo "Pre-push checks passed."
