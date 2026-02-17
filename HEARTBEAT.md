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
   "⚠️ Model drifted — auto-fixed back to Opus 4.6. Reason: [reason]"
3. If output is "OK" — no action needed, model is healthy.
4. Chain: Opus 4.6 (primary) → Opus 4.5 (fallback only). Never use Gemini.

## Standard Checks
- Check Gmail for unread client messages.
- Review Google Calendar for upcoming bookings.
- Verify Square for new unpaid invoices.
- Rotate through: inbox, upcoming bookings, overdue invoices, social engagement.
