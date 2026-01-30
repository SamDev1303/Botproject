# Bella — Tools & APIs

## How to Run Tools

**Always use:** `~/clawd/.venv/bin/python3 ~/clawd/tools/script.py`

---

## Available Tools

| Tool | Command | Purpose |
|------|---------|---------|
| Gmail | `gmail_api.py list/read/send` | Email |
| Sheets | `sheets_helper.py summary/read/outstanding` | Bookkeeping |
| Booking | `booking_system.py new/list/roster/confirm` | Jobs |
| Calendar | `calendar_helper.py today/add_booking` | Scheduling |
| Square | `square_api.py list_customers/list_payments/create_invoice` | Payments |
| n8n | `n8n_helper.py status/list_workflows/trigger` | Automations |
| Outreach | `outreach.py add_lead/list_leads/generate_email` | Sales |
| PDF | `create_pdf.py output.pdf "Title" "Content"` | Documents |
| Word | `create_word.py output.docx "Title" "Content"` | Documents |
| Excel | `create_excel.py output.xlsx "Sheet" "A1:Val"` | Documents |
| Voice | `elevenlabs_api.py` | Text-to-speech |
| Video | `kie_ai.py` | AI video |
| SMS | `twilio_api.py` | SMS/Calls |

---

## API Keys

All 82 keys in `~/.clawdbot/.env` (secured, chmod 600)

| Service | Status |
|---------|--------|
| Google Gemini | ✅ Active |
| Square | ✅ Production |
| Telegram | ✅ Active |
| Gmail | ✅ Configured |
| ElevenLabs | ✅ Active |
| Twilio | ✅ Active |
| n8n | ✅ 18 workflows |
| Meta (WhatsApp/IG) | ✅ Configured |
| Kie.AI | ✅ Active |
| Brave Search | ✅ Active |
| Apify | ✅ Active |

---

## n8n Workflows

URL: https://nioctibinu.online

- Booking Confirmation & Reminders
- Accounting Logger
- Review Request Automator
- Payment Link + Notifications
- Email Follow-Up Automator
- AI Chat Widget
- Outbound Sales Caller

---

## Paths

| Type | Location |
|------|----------|
| Skills | `~/clawd/skills/` |
| Tools | `~/clawd/tools/` |
| MCP | `~/clawd/mcp/` |
| API Keys | `~/.clawdbot/.env` |
| Config | `~/.clawdbot/clawdbot.json` |
