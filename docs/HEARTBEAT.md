# HEARTBEAT.md - Bella's Periodic Tasks

> **Primary LLM:** Anthropic Claude (claude-sonnet-4-20250514)
> **Heartbeat Interval:** Every 30 minutes (set in clawdbot.json)
> **Last Updated:** 14/02/2026

---

## 🚨 RULE #1: Dashboard First!
Before ANY reply to Hafsah, update the dashboard:
```bash
cd ~/Desktop/Botproject && git add -A && git commit -m "📊 Update" && git push origin main
```
Dashboard: https://samdev1303.github.io/Botproject/dashboard.html

---

## 🔄 3-Hour Business Sync
Every 3 hours, perform a full sync:
1. Check Square for invoice updates
2. Check Google Calendar for new bookings
3. Check Gmail for business enquiries
4. Update `dashboard-data.json` and push.
5. Track in `memory/heartbeat-state.json`.

---

## Tool Usage Priority (Most → Least Used)

### 🔥 Tier 1 — Daily Use
| Tool | Purpose | Heartbeat Tasks |
|------|---------|-----------------|
| **Google Calendar** | Check today's bookings | Morning brief, reminder checks |
| **Square** | Invoice/payment tracking | Payment monitoring, overdue checks |
| **Google Sheets** | Revenue tracking | Sync payments, daily totals |
| **Telegram** | Notifications to Hafsah | All heartbeat reports |
| **Twilio** | SMS reminders | Booking reminders (24hr/2hr) |

### 📊 Tier 2 — Weekly Use
| Tool | Purpose | Heartbeat Tasks |
|------|---------|-----------------|
| **Gmail** | Email follow-ups | Quote follow-ups, review requests |
| **Accounting** | GST/BAS tracking | Weekly financial summary |
| **OpenRouter** | Memory compression | Session summarisation (FREE) |
| **Brave Search** | Lead research | Weekly lead gen |

### 🔧 Tier 3 — On-Demand
| Tool | Purpose |
|------|---------|
| **Meta/Instagram** | Social media posts |
| **WhatsApp** | Client messaging |
| **LinkedIn** | B2B outreach |
| **ElevenLabs** | Voice messages |
| **Apify/Cold Outreach** | Campaign automation |
| **Convex** | Persistent memory |

---

## Daily Morning Brief (8:00 AM AEST/AEDT)

First heartbeat after 8am Sydney time:
1. Check Google Calendar for today's appointments
2. Check Square for any unpaid invoices
3. Review working memory for high-priority tasks
4. Report summary to Hafsah on Telegram

---

## Continuous Monitoring (Every 30 Minutes)

- **Overdue invoices:** Flag any unpaid invoices past due date
- **New payments:** Log in Google Sheets, notify Hafsah
- **Booking reminders:** 24-hour and 2-hour reminders via SMS

### Currently Overdue:
- Meshach Ephraim Care: $2,500 remaining

### Recently Cleared:
- ✅ Claudia Alz: $320 (Paid Feb 2026)

---

## End of Day Summary (6:00 PM AEST/AEDT)

First heartbeat after 6pm Sydney time:
1. Summarise today's completed tasks
2. List any pending follow-ups for tomorrow
3. Calculate daily revenue
4. Report to Hafsah

---

## Weekly (Monday 9:00 AM)

1. Generate weekly financial summary
2. Review all overdue accounts
3. Follow-up opportunities (recent cleans → review requests)
4. Sync Square payments to Google Sheets

---

## Notes

- **Detailed automation rules:** `.claude/rules/automation/heartbeat-tasks.md`
- **State tracking:** `memory/heartbeat-state.json`
- Don't spam notifications — consolidate where possible
- Quiet hours: before 7am and after 10pm Sydney time
