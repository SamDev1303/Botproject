# Bella's Workspace - Claude Code Context

> **Workspace:** ~/Desktop/🦀 (Bella's home)
> **Owner:** Hafsah Nuzhat
> **Last Updated:** 2026-01-31

---

## What Is This Workspace?

This is **Bella's workspace** — the AI assistant for Clean Up Bros. Bella is a Telegram bot (@CubsBookKeeperBot) powered by Google Gemini 3 Flash that handles:

- Client enquiries, quotes, and bookings
- Invoice creation via Square
- Email replies and notifications
- Expense recording and bookkeeping
- Social media posting (Facebook/Instagram)
- Schedule management

---

## Key Files

| File | Purpose |
|------|---------|
| `MEMORY.md` | Long-term context (family, business, banking) |
| `GEMINI.md` | Instructions for Bella (Gemini model) |
| `IDENTITY.md` | Bella's personality and role |
| `BOOT.md` | Startup instructions (loads for all sessions) |
| `HEARTBEAT.md` | Daily health checks |
| `USER.md` | User profile (Hafsah) |
| `memory/*.md` | Session summaries and context |

---

## Business: Clean Up Bros

| Field | Value |
|-------|-------|
| Website | cleanupbros.com.au |
| ABN | 26 443 426 374 |
| Phone | 0406 764 585 |
| Email | cleanupbros.au@gmail.com |
| Location | Liverpool & Western Sydney |

### Pricing
- General: $180
- End of Lease 1BR: $280
- End of Lease 2BR: $380
- End of Lease 3BR: $480
- Airbnb: $120

---

## Current Status (2026-01-31)

### Financial
| Metric | Amount |
|--------|--------|
| Total Income | ~$14,214.42 |
| Total Expenses | ~$1,540.88 |
| Net Profit | ~$12,673.54 |

### Outstanding
| Client | Amount | Status |
|--------|--------|--------|
| Claudia Alz | $320.00 | OVERDUE |
| Meshach Ephraim Care | $3,750.00 | Partial balance |

### Recent Activity
- Square sync: 22 payments added ($8,103.97)
- Social post published (oven transformation)
- Sam's booking created (Feb 5, $160)

---

## MCP Servers (in `mcp/`)

| Server | Purpose |
|--------|---------|
| `square_server.py` | Square CRM/Payments API |
| `google_server.py` | Gmail, Sheets, Calendar, Drive |
| `social_server.py` | Facebook, Instagram posting |
| `telegram_server.py` | Telegram bot gateway |

---

## Integration with Claude Code

Bella (this workspace) works WITH Claude Code (at `/Users/hafsahnuzhat/Desktop/claudeking`).

**Bella** = Brain (handles tasks, context, decisions)
**Claude Code** = Tools (file ops, git, CLI commands)

When Bella needs CLI help:
```bash
cd /Users/hafsahnuzhat/Desktop/claudeking && claude "TASK_HERE"
```

---

## Environment

All API keys stored in: `~/.clawdbot/.env` (chmod 600)

Key services configured:
- Square Payments (Production)
- Google Workspace (Gmail, Sheets, Calendar, Drive)
- Telegram Bot
- Facebook/Instagram (Business Suite)
- ElevenLabs (Voice)
- Twilio (SMS/Calls)
- Brave Search

---

## GitHub Repository

| Field | Value |
|-------|-------|
| Repo | https://github.com/SamDev1303/Botproject |
| User | SamDev1303 |
| Branch | main |

All MCP servers, configs, and Bella's code live here.

---

## Session Summaries

Memory files in `memory/` contain session summaries:
- `2026-01-31-session-summary.md` — Today's comprehensive summary
- `2026-01-31-1108.md` — Square sync session
- `2026-01-31-1117.md` — New session marker

---

*This file helps Claude Code understand the Bella workspace context.*
