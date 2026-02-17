# HEARTBEAT.md

## Dashboard Sync (EVERY heartbeat)
1. Update `dashboard-data.json` with latest metrics from Square, Calendar, and cron status.
2. Copy updated JSON to `/Users/hafsahnuzhat/bella-dashboard/public/dashboard-data.json`.
3. Run `python3 pre-push-check.py` — BLOCK push if secrets detected.
4. Git push both repos (workspace + bella-dashboard) to update live Telegram Mini App.
5. NEVER put API keys, tokens, or secrets in dashboard-data.json — only display-safe metrics.

## Standard Checks
- Check emails, calendar, and trending social content.
- Rotate through: inbox, upcoming bookings, overdue invoices, social engagement.
