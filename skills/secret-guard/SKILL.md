---
name: secret-guard
description: Mandatory security layer to scan for exposed secrets, API keys, and credentials before any git push or external deployment.
---

# Secret Guard Skill

This skill is a mandatory security gate. You must run this check before every `git push` or any operation that sends code/data to a public or external destination.

## Mandatory Workflow

### 1. Pre-Push Scan
Before executing any git push, you must scan the staged files for patterns that resemble:
- API Keys (e.g., `ghp_`, `AIza`, `sk-`, `sq0atp-`)
- Client Secrets
- Private Tokens
- Personal Identifiable Information (PII) not intended for the dashboard.

### 2. Implementation Logic
If you are about to push:
1. Run a grep-based scan on the workspace for common secret prefixes.
2. If a secret is found in a file that is not `.gitignore` or `secrets.json`:
   - **ABORT** the push.
   - Inform Hafsah immediately that a potential secret leak was detected.
   - Move the secret to an environment variable or a local-only file.

### 3. Verification
Only proceed with the push if the scan returns clean or if the secrets are properly obfuscated/stored in non-tracked files.

## Automation Script
When this skill is active, you are encouraged to use a local `pre-push-check.py` to automate this regex scanning.
