# HEARTBEAT.md - Bella's Periodic Tasks

# These tasks run automatically based on the heartbeat interval (every 30m)

---

## Daily Morning Brief (Run once per day, around 8am Sydney time)

When it's the first heartbeat after 8am Sydney time:
1. Check Google Calendar for today's appointments
2. Check Square for any unpaid invoices
3. Report summary to Hafsah on Telegram

---

## Invoice Check

Every heartbeat, check:
- Are there any overdue invoices? (due_date < today)
- If yes, note them for Hafsah's attention

### Currently Overdue:
- Claudia Alz: $320 (OVERDUE - follow up required)
- Meshach Ephraim Care: $3,750 remaining

---

## Payment Monitoring

If a new payment comes in:
- Log it in the Google Sheet
- Notify Hafsah via Telegram

---

## End of Day Summary (Run once per day, around 6pm Sydney time)

When it's the first heartbeat after 6pm Sydney time:
1. Summarise today's completed tasks
2. List any pending follow-ups for tomorrow
3. Report to Hafsah

---

# Notes

- Heartbeat interval is set to 30 minutes in clawdbot.json
- These are guidelines - use judgement on when to notify
- Don't spam notifications - consolidate where possible
