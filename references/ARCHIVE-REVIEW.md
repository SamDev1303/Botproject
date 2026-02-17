# Archive Review — Complete File Audit

> **Reviewed:** 2025-07-18
> **Reviewer:** Bella (subagent: archive-review)
> **Scope:** `archive/mcp/`, `archive/old-scripts/`, `archive/old-skills/`
> **Note:** `archive/old-skills/` directory does not exist — nothing to review there.

---

## Summary

| Category | Files | Useful | Partial | Obsolete |
|----------|-------|--------|---------|----------|
| MCP Servers | 16 .py files | 0 (deprecated) | 5 (logic extractable) | 11 |
| Old Scripts | 10 files | 3 | 2 | 5 |
| Old Skills | 0 | — | — | — |
| **Total** | **26** | **3** | **7** | **16** |

---

## Full File Table

### archive/mcp/ — MCP Servers (All Deprecated as MCP Servers)

| File | What It Does | Still Useful? | Restore? | Notes |
|------|-------------|---------------|----------|-------|
| `square_server.py` | Square API: create invoices, list payments, payment links, get balance. AUD-native with Sydney TZ. | PARTIAL | **Extract logic** | Core Square API functions (invoice creation, payment listing, payment links) are **gold** for the Master Ops Sheet. Don't restore as MCP — extract as standalone functions. |
| `accounting_server.py` | Full bookkeeping: record income/expenses to Google Sheets, GST calcs, BAS prep, P&L reports, staff wages, expense categories (ATO-compliant). | PARTIAL | **Extract logic** | **Highest value file in the archive.** Contains complete Australian bookkeeping logic: GST ÷ 11, BAS quarters, expense categories, P&L generation, super rate (11.5%). Extract into standalone `bookkeeping.py` for Master Ops Sheet Bookkeeping tab. |
| `google_server.py` | Google APIs: Gmail (search, read, send), Sheets (read, append, list), Drive (list, search), Calendar (events, create, availability). | PARTIAL | **Extract logic** | Google Sheets read/append functions are directly needed for Master Ops Sheet sync. Calendar functions useful for Client Log tab. Extract Sheets + Calendar helpers. |
| `whatsapp_server.py` | WhatsApp Business API: send messages, booking confirmations, quotes, payment reminders, review requests. | PARTIAL | No | Good templates but WhatsApp is handled via Clawdbot channels now. Templates (booking confirmation, payment reminder) could inform Master Sheet automation. |
| `coldoutreach_server.py` | Cold email/SMS/call campaigns: lead management, email templates (Bella's honest style), Twilio SMS, cold call scripts, campaign execution, target market specialists. | PARTIAL | No | Huge file (~600 lines). Lead management + campaign tracking logic is useful. Email templates are well-written. But outreach is handled differently now. Keep as **reference** for email templates. |
| `convex_server.py` | Convex real-time DB for memory storage: CRUD operations for clients, invoices, sessions. | NO | No | Convex was abandoned. Memory is file-based now. |
| `elevenlabs_server.py` | ElevenLabs TTS: generate voice, voicemail greetings, booking confirmations, marketing audio, Grok-style cold calls. | NO | No | TTS is handled via Clawdbot `tts` tool now. Voice presets could be referenced but not restored. |
| `openrouter_server.py` | Free LLM access via OpenRouter: text chunking, summarization, session summaries, key info extraction, memory compression. | NO | No | Clawdbot has native LLM access. These utilities are redundant. |
| `meta_server.py` | Facebook + Instagram: page posts, Messenger, reviews, Instagram photos/carousels/reels, insights, content templates, hashtags. | NO | No | Social media is managed via browser/manual now. Templates are decent but not actionable as scripts. |
| `twilio_server.py` | Twilio SMS + voice calls: send SMS, booking confirmations/reminders, payment reminders, cold calls (normal + Grok-style), phone lookup. | NO | No | Twilio is handled via Clawdbot. SMS templates are similar to WhatsApp server. |
| `apify_server.py` | Apify web scraping: Google Maps search, find property managers/childcare/aged care/NDIS/Airbnb leads, email extraction, competitor research. | NO | No | Lead finding is done via web_search now. Apify actors may have changed IDs. |
| `kie_server.py` | Kie.AI video/image generation: Sora, Veo, Kling, Flux models. Video ad prompts for cleaning business. | NO | No | Niche tool. API likely changed. |
| `linkedin_server.py` | LinkedIn: profile, posts (text/image/article), content templates, B2B outreach messages, OAuth setup. | NO | No | LinkedIn posting is manual. Content templates are decent but not scripts. |
| `ref_server.py` | Reference tools: ABN lookup, GST calculator, pricing reference, BAS quarter info. | NO | No | Simple utility functions. The GST calc and pricing reference are trivially reimplementable. |
| `brave_server.py` | Brave Search API: web search, news, local, competitor research, ATO info. | NO | No | Clawdbot has native `web_search` tool. Completely redundant. |
| `logging_config.py` | Logging setup: rotating file handlers, console output. | NO | No | MCP infrastructure, not needed. |
| `shared_utils.py` | Shared utilities: env loading, HTTP helpers, rate limiter, date formatting, safe JSON I/O. | NO | No | MCP infrastructure. Some patterns are useful but trivial to rewrite. |
| `validation.py` | Input validation: email, phone (AU), ABN, BSB, URL, amount, sanitization. | PARTIAL | No | Well-written validation functions. Could be useful in standalone scripts but easy to rewrite. Keep as reference. |

### archive/old-scripts/ — Standalone Scripts

| File | What It Does | Still Useful? | Restore? | Notes |
|------|-------------|---------------|----------|-------|
| `sync_to_sheets.py` | **Syncs Square payments → Google Sheets Income tab.** Fetches Square payments, reads Sheet, finds missing entries, appends them. | **YES** | **✅ RESTORE** | **Directly needed** for Master Ops Sheet. Core logic: fetch Square payments, compare with Sheets, add missing. Needs updating (old tool paths `~/clawd/`) but the reconciliation algorithm is solid. |
| `reconcile_accounts.py` | **Reconciles Square payments vs Google Sheets.** Uses direct API calls (urllib). Identifies payments in Square missing from Sheet. | **YES** | **✅ RESTORE** | **Directly needed** for Bookkeeping tab. Better implementation than `reconcile_simple.py` — uses direct API calls instead of subprocess. Modernize and merge with sync_to_sheets. |
| `reconcile_simple.py` | Simpler version of reconcile_accounts. Uses subprocess to call old tools. | PARTIAL | No | Superseded by `reconcile_accounts.py`. Same logic, worse implementation. |
| `create_sam_square.py` | Creates a specific customer (Sam) in Square with address and notes. | **YES** | **✅ RESTORE** | **Template for client creation automation.** The Square customer creation pattern is exactly what's needed for the Client Log tab → Square sync. Generalize into `create_square_customer.py`. |
| `google_org_task.py` | Organizes Gmail (archives marketing emails, marks promos read), Drive (creates folders, moves files), Sheets (adds headers, archives 2025 data to new tab). | PARTIAL | No | Gmail/Drive org is one-time maintenance. Sheets org logic (archiving old data, creating year tabs) could inform Master Sheet setup. **Contains hardcoded client secrets — security risk.** |
| `session_logoff.py` | Session automation: creates session summary, syncs memory, updates heartbeat, commits to GitHub. | NO | No | Superseded by Clawdbot's built-in session hooks (`session-memory`). The session summary template format could be referenced. |
| `check_anthropic_models.py` | Lists available Anthropic models via API. | NO | No | One-time debug script. Uses `requests` (not stdlib). Trivially replaceable. |
| `google_oauth_setup_ads.py` | OAuth flow for Google services including Ads. Starts local server, handles callback, exchanges code for tokens. | NO | No | OAuth is already set up. **Contains hardcoded client secrets — security risk if shared.** |
| `test_google_services.py` | Comprehensive test of Gmail, Calendar, Sheets, Drive, Google Ads APIs. | PARTIAL | No | Good diagnostic tool but the tests are simple enough to recreate. Could be useful when debugging Google API issues. |
| `check_ads.py` | Checks Google Ads campaigns via API. | NO | No | One-time debug script. **Contains hardcoded developer token and customer ID.** |
| `setup-convex.sh` | Shell script to initialize Convex project. | NO | No | Convex was abandoned. |
| `auto_refresh_3h.sh` | Cron job: syncs invoices, updates dashboard, pushes to GitHub every 3 hours. | PARTIAL | No | The orchestration pattern (sync → aggregate → push) is useful for designing cron jobs. References `check_unpaid_invoices.py` which may not exist. |

---

## 🔄 RESTORE — Files Worth Bringing Back

These files should be extracted, modernized, and placed in `scripts/`:

### 1. `sync_to_sheets.py` → `scripts/square_sheets_sync.py`
**Priority: HIGH**
- **What:** Syncs Square payments to Google Sheets Income tab
- **Why:** Core automation for Master Ops Sheet Bookkeeping tab
- **Changes needed:**
  - Replace `~/clawd/` paths with current workspace/API structure
  - Use direct API calls (like `reconcile_accounts.py`) instead of subprocess
  - Add Sydney timezone handling
  - Support the new Master Ops Sheet's column structure
  - Add GST calculation on sync (amount ÷ 11)

### 2. `reconcile_accounts.py` → `scripts/reconcile_square_sheets.py`
**Priority: HIGH**
- **What:** Identifies Square payments missing from Google Sheets
- **Why:** Essential for bookkeeping accuracy — finds discrepancies
- **Changes needed:**
  - Update token paths from `~/clawd/credentials/` to `~/.clawdbot/`
  - Add option to auto-add missing entries (merge with sync logic)
  - Add date-range filtering
  - Output summary suitable for Task Log tab

### 3. `create_sam_square.py` → `scripts/create_square_customer.py`
**Priority: MEDIUM**
- **What:** Creates customers in Square API
- **Why:** Template for Client Log tab → Square sync automation
- **Changes needed:**
  - Generalize (remove hardcoded Sam data)
  - Accept parameters: name, email, phone, address, notes
  - Add validation (use patterns from `validation.py`)
  - Return customer ID for linking in Master Sheet

### 4. Extract from `accounting_server.py` → `scripts/bookkeeping_helpers.py`
**Priority: HIGH**
- **What:** Australian bookkeeping logic: GST calc, BAS quarters, expense categories, P&L generation
- **Why:** Core logic for Bookkeeping tab and BAS reporting
- **Extract:**
  - `GST_RATE`, `SUPER_RATE`, `BAS_QUARTERS`, `EXPENSE_CATEGORIES` constants
  - `calculate_bas()` → standalone function
  - `profit_loss()` → standalone function
  - `record_income()` / `record_expense()` → Sheets append helpers
  - GST calculator functions

### 5. Extract from `google_server.py` → `scripts/google_sheets_helpers.py`
**Priority: MEDIUM**
- **What:** Google Sheets read/append/list, Calendar event listing
- **Why:** Shared helpers for all Master Ops Sheet tabs
- **Extract:**
  - `get_access_token()` with refresh logic
  - `sheets_read()`, `sheets_append()`
  - `calendar_list_events()`, `calendar_create_event()`

---

## 🗑️ DELETE — Obsolete Files

These files are safe to delete (or keep archived but never restore):

### MCP Servers (All)
All 16 MCP `.py` files are deprecated. The MCP server framework is no longer used. Key logic has been flagged for extraction above. The remaining servers (`convex_server.py`, `elevenlabs_server.py`, `openrouter_server.py`, `meta_server.py`, `twilio_server.py`, `apify_server.py`, `kie_server.py`, `linkedin_server.py`, `ref_server.py`, `brave_server.py`, `logging_config.py`, `shared_utils.py`, `validation.py`) can remain in archive but should not be restored.

### Old Scripts
| File | Reason to Delete |
|------|-----------------|
| `reconcile_simple.py` | Superseded by `reconcile_accounts.py` |
| `session_logoff.py` | Superseded by Clawdbot session hooks |
| `check_anthropic_models.py` | One-time debug, trivially replaceable |
| `google_oauth_setup_ads.py` | OAuth already set up; **contains hardcoded secrets** |
| `check_ads.py` | One-time debug; **contains hardcoded tokens** |
| `setup-convex.sh` | Convex abandoned |
| `auto_refresh_3h.sh` | References non-existent scripts; cron design is now different |

### Security Warnings ⚠️
These files contain **hardcoded secrets** that should NOT be pushed to any public repo:
- `google_oauth_setup_ads.py` — Google OAuth client ID + client secret
- `check_ads.py` — Google Ads developer token + customer ID
- `google_org_task.py` — Google OAuth client ID + client secret

---

## Master Ops Sheet Automation Map

How restored scripts map to the 4-tab Master Sheet:

| Master Sheet Tab | Restored Script | What It Automates |
|-----------------|----------------|-------------------|
| **Client Log** | `create_square_customer.py` | New client → Square sync |
| **Bookkeeping** | `square_sheets_sync.py` + `bookkeeping_helpers.py` | Income recording, GST calc, expense tracking |
| **Bookkeeping** | `reconcile_square_sheets.py` | Payment verification, discrepancy detection |
| **Task Log** | (new script needed) | Reconciliation results → task entries |
| **Accounts** | `bookkeeping_helpers.py` (P&L, BAS) | BAS preparation, profit/loss reporting |

---

*Review complete. 3 scripts recommended for restoration, 2 MCP servers recommended for logic extraction.*
