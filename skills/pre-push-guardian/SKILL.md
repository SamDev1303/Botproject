---
name: pre-push-guardian
description: Mandatory pre-push guardrail to run secret scans, hardcoded-key detection, target verification, and script self-healing before GitHub pushes or deploy-related commits.
---

# Pre Push Guardian

Use this skill when asked to prepare for `git push`, secure keys, or validate deployment safety.

## Workflow

1. Run:
```bash
bash scripts/bella-pre-push.sh
```
2. If it fails:
- Fix leaked/hardcoded credentials by moving them to env vars.
- Re-run `bash scripts/bella-pre-push.sh`.
3. For first-time setup (or if hook missing), install hook:
```bash
bash scripts/install-pre-push-hook.sh
```

## What It Enforces

- Secret scanning via `pre-push-check.py --staged`
- Hardcoded credential assignment detection
- Canonical repo/project validation via `scripts/verify-allowed-targets.sh`
- Self-healing for shell scripts via `skills/pre-push-guardian/scripts/self-heal-scripts.sh`

## Notes

- Never hardcode tokens in tracked files.
- Use environment variables for GitHub/Vercel credentials.
