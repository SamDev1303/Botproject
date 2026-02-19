---
name: api-health-and-quotas
description: Diagnose and recover API failures for OpenClaw/Clawdbot, including Gemini/OpenAI rate limits, key rotation, embedding health, and provider failover readiness.
---

# API Health And Quotas

Use when:
- API calls fail with `429`, `RESOURCE_EXHAUSTED`, or auth errors.
- Memory embeddings fail or drift from Gemini provider.
- User asks to verify API status after config changes.

## Core Checks

```bash
python3 ~/Desktop/🦀/scripts/api_health_check.py
bash ~/Desktop/🦀/scripts/check-embedding.sh
bash ~/Desktop/🦀/scripts/check-model.sh
```

## Fast Triage

1. Confirm model route first (`check-model.sh`).
2. Confirm embeddings provider (`check-embedding.sh`).
3. Run full API health check.
4. If `429`:
   - rotate or upgrade provider key/quota,
   - keep fallback chain enabled,
   - notify user that runtime remains limited by provider quota.

## Quick Scripts

- `scripts/run-full-health.sh`
- `scripts/read-last-rate-limit-errors.sh`
