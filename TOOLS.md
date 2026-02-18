# TOOLS.md - Bella's Scripts & Tools Reference

> Auto-loaded every session. Reference whichever script you need — don't load separately.
> Last updated: 2026-02-18

---

## Scripts Directory: `~/Desktop/🦀/scripts/`

### Daily Operations

| Script | Purpose | Run |
|--------|---------|-----|
| `morning_brief.py` | Daily summary: unpaid invoices, payments, stats | `python3 scripts/morning_brief.py` |
| `check_inbox.py` | List unread Gmail messages | `python3 scripts/check_inbox.py [limit]` |
| `weekly_report.py` | Weekly P&L, revenue, outstanding | `python3 scripts/weekly_report.py` |

### Financial / Bookkeeping

| Script | Purpose | Run |
|--------|---------|-----|
| `gst_calc.py` | Quick GST calculator (Total / 11) | `python3 scripts/gst_calc.py 380 280 480` |
| `bas_prep.py` | BAS quarter preparation worksheet | `python3 scripts/bas_prep.py [Q1/Q2/Q3/Q4]` |
| `bookkeeping_helpers.py` | GST, super, expense categories, P&L | Library (import) |
| `square_sheets_sync.py` | Sync Square payments to Google Sheets | `python3 scripts/square_sheets_sync.py` |
| `sync_square_sheets.sh` | Shell wrapper with logging | `bash scripts/sync_square_sheets.sh` |

### Square API

| Script | Purpose | Run |
|--------|---------|-----|
| `square_api.py` | Square API wrapper (customers, invoices, payments) | Library (import SquareAPI) |
| `quick_invoice.py` | Create Square invoice from CLI | `python3 scripts/quick_invoice.py "Name" 380 "Description"` |
| `create_square_customer.py` | Create new Square customer | `python3 scripts/create_square_customer.py` |
| `check_debtors.py` | List all customers with unpaid invoices | `python3 scripts/check_debtors.py` |
| `check_meshach.py` | Check Meshach payment plan status | `python3 scripts/check_meshach.py` |

### Google Workspace

| Script | Purpose | Run |
|--------|---------|-----|
| `google_sheets_api.py` | Google Sheets API wrapper | Library (import GoogleSheetsAPI) |
| `google-oauth-setup.py` | One-time OAuth token setup | `python3 scripts/google-oauth-setup.py` |
| `create_master_sheet.py` | Create Master Operations Sheet (4 tabs) | `python3 scripts/create_master_sheet.py` |

### Social Media

| Script | Purpose | Run |
|--------|---------|-----|
| `social_post.py` | Quick post to Facebook page | `python3 scripts/social_post.py "Message"` |

### Model Management

| Script | Purpose | Run |
|--------|---------|-----|
| `switch-to-opus46.sh` | Reset model to Opus 4.6, clear cooldown | `bash scripts/switch-to-opus46.sh` |
| `check-model.sh` | Check active model, auto-fix if drifted | `bash scripts/check-model.sh` |
| `setup-sonnet46.sh` | Switch primary to Claude Sonnet 4.6 + Gemini fallback | `bash setup-sonnet46.sh` |

### System / DevOps

| Script | Purpose | Run |
|--------|---------|-----|
| `api_health_check.py` | Test all configured APIs | `python3 scripts/api_health_check.py` |
| `delegate_to_claude.sh` | Send task to Claude Code CLI | `bash scripts/delegate_to_claude.sh "task"` |
| `validation_helpers.py` | AU validators (phone, ABN, BSB, email) | Library |
| `sync_memory_files.py` | Sync CLAUDE.md and GEMINI.md files | `python3 scripts/sync_memory_files.py` |

---

## MCP Servers (15 servers, 160+ tools) — `~/Desktop/🦀/mcp/`

### accounting_server.py (12 tools)
`record_income` `get_income_summary` `record_expense` `get_expense_summary` `record_outstanding` `get_outstanding` `profit_loss` `calculate_bas` `calculate_gst` `record_wage` `list_expense_categories` `tax_deduction_check`

### apify_server.py (16 tools)
`google_search` `search_google_maps` `scrape_website` `extract_emails_from_website` `find_real_estate_agencies` `find_property_managers` `find_airbnb_hosts` `find_airbnb_managers` `research_competitors` `find_aged_care_facilities` `find_childcare_centres` `find_ndis_providers` `find_commercial_buildings` `find_all_targets` `list_my_runs` `check_apify_usage`

### brave_server.py (10 tools)
`search` `search_local` `search_news` `answer_question` `find_property_managers_online` `find_cleaning_prices` `find_industry_news` `research_competitor` `research_cleaning_tips` `lookup_abn` `ato_info`

### coldoutreach_server.py (19 tools)
`add_lead` `get_lead` `list_leads` `update_lead_status` `list_target_markets` `find_leads_by_market` `get_outreach_philosophy` `create_campaign` `send_cold_email` `execute_campaign` `send_cold_sms` `make_cold_call` `preview_outreach` `send_followup_email` `generate_personalized_email` `generate_airbnb_email` `generate_aged_care_email` `generate_childcare_email` `generate_ndis_email` `get_outreach_stats`

### convex_server.py (8 tools)
`convex_store_memory` `convex_get_memory` `convex_search_memories` `convex_sync_client` `convex_sync_invoice` `convex_sync_session` `convex_get_all_overdue_clients` `convex_delete_memory`

### elevenlabs_server.py (14 tools)
`generate_voice` `list_voices` `check_quota` `get_voice_settings` `generate_booking_confirmation_audio` `generate_reminder_audio` `generate_marketing_audio` `generate_voicemail_greeting` `generate_cold_call_intro` `generate_grok_cold_call` `generate_grok_followup_call` `generate_grok_childcare_call` `get_grok_voice_settings` `list_generated_files`

### google_server.py (13 tools)
`gmail_unread_count` `gmail_search` `gmail_read` `gmail_send` `gmail_mark_read` `calendar_list_events` `calendar_create_event` `calendar_check_availability` `sheets_read` `sheets_append` `sheets_list` `drive_list` `drive_search`

### kie_server.py (6 tools)
`generate_video` `generate_image` `check_generation_status` `list_models` `generate_cleaning_ad_video` `generate_cleaning_ad_image`

### linkedin_server.py (9 tools)
`linkedin_oauth_url` `linkedin_exchange_code` `linkedin_check_token` `get_profile` `linkedin_post` `linkedin_post_with_image` `linkedin_post_with_link` `generate_linkedin_post` `generate_outreach_message`

### meta_server.py (17 tools)
`fb_post` `fb_post_photo` `fb_get_posts` `fb_get_reviews` `fb_get_messages` `fb_reply_message` `fb_get_page_insights` `ig_post_photo` `ig_post_carousel` `ig_post_reel` `ig_publish_media` `ig_get_posts` `ig_get_comments` `ig_reply_comment` `ig_get_insights` `generate_cleaning_post` `generate_hashtags`

### openrouter_server.py (6 tools)
`summarize_text` `summarize_session` `extract_key_info` `compress_memory_file` `chunk_text` `openrouter_list_free_models`

### ref_server.py (4 tools)
`quick_gst_calc` `lookup_abn` `pricing_reference` `bas_quarter_info`

### square_server.py (6 tools)
`square_list_locations` `square_list_payments` `square_create_invoice` `square_list_invoices` `square_get_balance` `square_create_payment_link`

### twilio_server.py (14 tools)
`send_sms` `send_booking_confirmation` `send_reminder` `send_payment_reminder` `send_quote` `send_review_request` `make_call` `call_with_recording` `cold_outreach_call` `cold_outreach_call_grok` `list_recent_sms` `list_recent_calls` `check_twilio_balance` `lookup_phone`

### whatsapp_server.py (12 tools)
`send_whatsapp` `send_booking_confirmation_wa` `send_reminder_wa` `send_payment_reminder_wa` `send_quote_wa` `send_review_request_wa` `send_completion_wa` `send_image_wa` `send_document_wa` `send_template` `list_templates` `get_business_profile`

---

## Active Cron Jobs (Recurring)

| Job | Schedule | What it does |
|-----|----------|-------------|
| `weekly-airbnb-reminder` | Sun 9PM | Airbnb cleaning schedule for the week |
| `thursday-invoice-wages` | Thu 10PM | Process wages + send invoices |
| `Weekly Business Review` | Mon 9AM | Square reconciliation + weekly report |
| `Tuition Fee Reminder` | Thu 10AM | INT College payment reminder |
| `Karanjeet Aus Post` | Sat 10AM/Fri 8PM | Weekly Horsley Park clean ($65) |
| `Maryam Al Atar` | Tue 8AM/Mon 8PM | Weekly Kingswood clean |
| `social-morning-post` | Daily 7AM | FB+IG morning content |
| `social-lunch-post` | Daily 12PM | FB+IG lunch content |
| `social-evening-post` | Daily 7PM | FB+IG evening content |
| `social-weekly-research` | Sun 9AM | Research trending cleaning content |
| `commercial-outreach-daily` | Daily 10AM | Follow up commercial leads |
| `dashboard-live-sync-5min` | Every 5 min | Update dashboard-data.json + push |

---

## Quick Task Lookup

**Need to...** | **Use this**
---|---
Check unpaid invoices | `python3 scripts/check_debtors.py` or `square_list_invoices` MCP tool
Create an invoice | `python3 scripts/quick_invoice.py "Name" 380 "2BR EOL"` or `square_create_invoice`
Calculate GST | `python3 scripts/gst_calc.py 380` or `quick_gst_calc` MCP tool
Prepare BAS | `python3 scripts/bas_prep.py Q3`
Send SMS | `send_sms` MCP tool (twilio_server)
Send WhatsApp | `send_whatsapp` MCP tool (whatsapp_server)
Post to Facebook | `python3 scripts/social_post.py "msg"` or `fb_post` MCP tool
Post to Instagram | `ig_post_photo` / `ig_post_reel` MCP tools
Check Gmail | `python3 scripts/check_inbox.py` or `gmail_search` MCP tool
Send email | `gmail_send` MCP tool (google_server)
Check calendar | `calendar_list_events` MCP tool or `gog calendar events`
Create booking | `calendar_create_event` MCP tool then `send_booking_confirmation`
Find leads (Apify) | `find_real_estate_agencies` / `find_property_managers` MCP tools
Cold outreach | `send_cold_email` / `generate_personalized_email` MCP tools
Generate voice | `generate_voice` MCP tool (elevenlabs_server)
Generate video | `generate_video` / `generate_cleaning_ad_video` MCP tools
Look up ABN | `lookup_abn` MCP tool (ref_server or brave_server)
Weekly report | `python3 scripts/weekly_report.py`
Morning brief | `python3 scripts/morning_brief.py`
Fix model drift | `bash scripts/switch-to-opus46.sh`
Sync Square to Sheets | `bash scripts/sync_square_sheets.sh`
Record expense | `record_expense` MCP tool (accounting_server)
Check P&L | `profit_loss` MCP tool (accounting_server)

---

## Environment

| Item | Value |
|------|-------|
| TTS Voice | "Bella" (ElevenLabs) |
| Timezone | Australia/Sydney (AEDT) |
| Date Format | DD/MM/YYYY |
| Currency | AUD ($) |
| GST | Total / 11 |
| Secrets | `~/.clawdbot/.env` (never expose) |
| Logs | `~/.clawdbot/logs/mcp/` |
| Data | `~/.clawdbot/data/` |
| Media | `~/.clawdbot/media/` |

---

*This is your cheat sheet. Reference what you need, when you need it.*
