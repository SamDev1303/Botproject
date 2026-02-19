# HEARTBEAT.md

## Dashboard Sync (EVERY heartbeat)
1. Update `dashboard-data.json` with latest metrics from Square, Calendar, and cron status.
2. Update `memory/working/metrics.json` for persistent stats.
3. Sync local `memory/` entities with Master Sheets.
4. Run `python3 pre-push-check.py` — BLOCK push if secrets detected.
5. Git push workspace and pulse-dashboard repo.

## Model Health Check (EVERY heartbeat)
1. Run `bash ~/Desktop/🦀/scripts/check-model.sh`
2. If output is "FIXED: ..." — model drifted and was auto-repaired. Notify Hafsah on Telegram:
   "⚠️ Model drifted — auto-fixed back to GPT 5.3 Codex. Reason: [reason]"
3. If output is "CHANGED: ..." — notify Hafsah:
   "ℹ️ Model routing changed: [reason]"
4. If output is "OK" — no action needed, model is healthy.
5. Chain: openai-codex/gpt-5.3-codex (primary) → openai-codex/gpt-5.2-codex (fallback).

## Standard Checks
- Check Gmail for unread client messages.
- Review Google Calendar for upcoming bookings.
- Verify Square for new unpaid invoices.
- Rotate through: inbox, upcoming bookings, overdue invoices, social engagement.

4. Refresh startup chat memory file from last 4 chat logs:
   `python3 scripts/update-startup-last4-chatlogs.py`
