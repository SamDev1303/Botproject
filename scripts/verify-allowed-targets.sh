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
set -euo pipefail
set -euo pipefail

ROOT="/Users/hafsahnuzhat/Desktop/🦀"
TARGETS="$ROOT/config/deployment-targets.json"
WORKSPACE_REPO="$ROOT"
DASHBOARD_REPO="/Users/hafsahnuzhat/bella-dashboard"

if [ ! -f "$TARGETS" ]; then
  echo "Missing $TARGETS"
  exit 1
fi

PARSED="$(python3 - <<'PY'
import json
from pathlib import Path
t = json.loads(Path("/Users/hafsahnuzhat/Desktop/🦀/config/deployment-targets.json").read_text())
owner = t["github"]["owner"]
dashboard_url = t["github"]["dashboardRepoUrl"]
project_id = t["vercel"]["dashboardProjectId"]
team_slug = t["vercel"]["teamSlug"]
allowed = ",".join(t["github"]["allowedRepos"])
print(owner)
print(dashboard_url)
print(project_id)
print(team_slug)
print(allowed)
PY
)"

OWNER="$(printf "%s\n" "$PARSED" | sed -n '1p')"
DASHBOARD_URL="$(printf "%s\n" "$PARSED" | sed -n '2p')"
VERCEL_PROJECT_ID="$(printf "%s\n" "$PARSED" | sed -n '3p')"
VERCEL_TEAM_SLUG="$(printf "%s\n" "$PARSED" | sed -n '4p')"
ALLOWED_REPOS_CSV="$(printf "%s\n" "$PARSED" | sed -n '5p')"

echo "Allowed owner: $OWNER"
echo "Allowed repos: $ALLOWED_REPOS_CSV"
echo "Allowed dashboard repo: $DASHBOARD_URL"
echo "Expected Vercel project: $VERCEL_PROJECT_ID"
echo "Expected Vercel team: $VERCEL_TEAM_SLUG"

if [ -d "$WORKSPACE_REPO/.git" ]; then
  ROOT_REMOTE="$(git -C "$WORKSPACE_REPO" remote get-url origin 2>/dev/null || true)"
  case "$ROOT_REMOTE" in
    *SamDev1303/Botproject*) ;;
    *)
      echo "Blocked: workspace origin remote is not SamDev1303/Botproject"
      echo "Found: $ROOT_REMOTE"
      exit 1
      ;;
  esac
fi

if [ -d "$DASHBOARD_REPO/.git" ]; then
  DASH_REMOTE="$(git -C "$DASHBOARD_REPO" remote get-url origin 2>/dev/null || true)"
  case "$DASH_REMOTE" in
    *SamDev1303/pulse-dashboard*) ;;
    *)
      echo "Blocked: bella-dashboard origin remote is not pulse-dashboard"
      echo "Found: $DASH_REMOTE"
      exit 1
      ;;
  esac
fi

if [ -n "${GITHUB_TOKEN:-}" ] && command -v gh >/dev/null 2>&1; then
  echo "GitHub token detected; optional duplicate repo audit:"
  echo "gh repo list \"$OWNER\" --json name --limit 500"
fi

if [ -n "${VERCEL_TOKEN:-}" ]; then
  echo "Vercel token detected in env."
else
  echo "Warning: VERCEL_TOKEN not set in env."
fi

echo "Target verification passed."
