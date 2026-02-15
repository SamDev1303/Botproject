# Bella — Tools & APIs

> **Primary LLM:** Anthropic Claude (claude-sonnet-4-20250514)
> **Fallback LLM:** Google Gemini 3 Flash Preview
> **Last Updated:** 14/02/2026

---

## MCP Servers (15 Total)

All MCP servers are in `~/Desktop/🦀/mcp/`

### 🔥 Daily Operations (Highest Priority)
| Server | File | Primary Tools |
|--------|------|---------------|
| Google | `google_server.py` | Gmail, Sheets, Calendar, Drive |
| Square | `square_server.py` | Invoices, payments, customers |
| Accounting | `accounting_server.py` | Income, expenses, GST, BAS prep |
| Twilio | `twilio_server.py` | SMS/voice calls, booking reminders |

### 📊 Business Growth (Weekly)
| Server | File | Primary Tools |
|--------|------|---------------|
| Meta | `meta_server.py` | Facebook/Instagram posting |
| WhatsApp | `whatsapp_server.py` | Business messaging |
| Brave | `brave_server.py` | Web search, lead research |
| OpenRouter | `openrouter_server.py` | Text chunking, summarisation (FREE) |

### 🔧 Marketing & Outreach (On-Demand)
| Server | File | Primary Tools |
|--------|------|---------------|
| LinkedIn | `linkedin_server.py` | Professional posts, B2B |
| ElevenLabs | `elevenlabs_server.py` | Voice generation |
| Apify | `apify_server.py` | Web scraping, lead gen |
| Cold Outreach | `coldoutreach_server.py` | Email/SMS campaigns |
| Kie | `kie_server.py` | AI video generation |

### ⚙️ Infrastructure
| Server | File | Primary Tools |
|--------|------|---------------|
| Convex | `convex_server.py` | Real-time database, persistent memory |
| Logging | `logging_config.py` | Centralized logging, monitoring |

### Shared Utilities
| File | Purpose |
|------|---------|
| `shared_utils.py` | Common utilities across servers |
| `validation.py` | Input validation helpers |
| `ref_server.py` | Reference data lookups |

---

## Utility Scripts

All scripts are in `~/Desktop/🦀/scripts/`

| Script | Purpose |
|--------|---------|
| `api_health_check.py` | Test all API connections |
| `test_google_services.py` | Google API connectivity test |
| `sync_memory_files.py` | Sync memory across sessions |
| `session_logoff.py` | Clean session shutdown |
| `delegate_to_claude.sh` | Delegate tasks to Claude Code |
| `setup-convex.sh` | Convex database setup |
| `check_ads.py` | Google Ads checker |
| `check_unpaid_invoices.py` | Square invoice scanner |
| `google-oauth-setup.py` | Google OAuth flow |
| `google_oauth_setup_ads.py` | Google Ads OAuth flow |
| `google_org_task.py` | Google organisation tasks |
| `reconcile_accounts.py` | Full account reconciliation |
| `reconcile_simple.py` | Quick reconciliation |
| `sync_to_sheets.py` | Sync data to Google Sheets |
| `create_sam_square.py` | Square customer creation |

---

## API Keys

All 82+ keys in `~/.clawdbot/.env` (secured, chmod 600)

| Service | Status |
|---------|--------|
| **Anthropic Claude** | ✅ Primary LLM |
| Google Gemini | ✅ Fallback LLM |
| Square | ✅ Production |
| Telegram | ✅ Active |
| Gmail / Calendar / Sheets | ✅ Configured |
| ElevenLabs | ✅ Active |
| Twilio | ✅ Active |
| n8n | ✅ 18 workflows |
| Meta (WhatsApp/IG) | ✅ Configured |
| Kie.AI | ✅ Active |
| Brave Search | ✅ Active |
| Apify | ✅ Active |
| OpenRouter | ✅ Active (FREE) |
| Convex | ✅ Ready to initialize |

---

## Paths

| Type | Location |
|------|----------|
| MCP Servers | `~/Desktop/🦀/mcp/` |
| Scripts | `~/Desktop/🦀/scripts/` |
| Skills | `~/Desktop/🦀/skills/` + `~/.claude/skills/` |
| Memory | `~/Desktop/🦀/memory/` |
| Docs | `~/Desktop/🦀/docs/` |
| API Keys | `~/.clawdbot/.env` |
| Config | `~/.clawdbot/clawdbot.json` |
| Logs | `~/.clawdbot/logs/mcp/` |
