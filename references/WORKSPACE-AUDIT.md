# 🦀 WORKSPACE AUDIT — Complete Map

> **Generated:** 2026-02-17 ~8:00 PM AEDT  
> **Workspace:** `/Users/hafsahnuzhat/Desktop/🦀`  
> **Git Remote:** `https://github.com/SamDev1303/Botproject.git`  
> **Owner:** Hafsah Nuzhat — Director, Clean Up Bros (ABN 26 443 426 374)

---

## Table of Contents

1. [Folder Structure](#1-folder-structure)
2. [Script Files](#2-script-files)
3. [Skills](#3-skills)
4. [Config Files](#4-config-files)
5. [API Integrations](#5-api-integrations)
6. [Memory Files](#6-memory-files)
7. [Google Sheets References](#7-google-sheets-references)
8. [Archive / MCP Folder](#8-archive--mcp-folder)
9. [References Folder](#9-references-folder)
10. [Claude Code Workspace](#10-claude-code-workspace-claudeking)
11. [.claude Rules & Skills](#11-claude-rules--skills)
12. [Docs Folder](#12-docs-folder)
13. [Work Folder](#13-work-folder)
14. [Marketing & Asset Files](#14-marketing--asset-files)
15. [Git & Security](#15-git--security)

---

## 1. Folder Structure

```
🦀/ (workspace root)
├── .claude/                    # Claude Code integration config
│   ├── agents/                 # (empty — agent definitions)
│   ├── rules/                  # Auto-loaded business rules
│   │   ├── automation/         # heartbeat-tasks.md
│   │   ├── business/           # pricing.md, tax-compliance.md, email-usage.md
│   │   ├── clients/            # communication.md, overdue-accounts.md
│   │   └── operations/         # booking-workflow.md
│   ├── skills/                 # Claude Code-specific skill stubs
│   │   ├── bas-preparation/    # (empty — BAS lodgement)
│   │   ├── cold-outreach/      # (empty — cold outreach stub)
│   │   ├── tax-calculator/     # (empty — tax calc stub)
│   │   ├── google-health-check.md
│   │   └── session-logoff.md
│   └── settings.local.json     # Claude Code permissions (allowed bash commands)
│
├── archive/                    # Deprecated / old code
│   ├── convex/                 # Old Convex real-time DB setup
│   │   ├── schema.ts, memory.ts, package.json, README.md
│   ├── mcp/                    # 18 archived MCP server scripts (Python)
│   ├── old-logs/               # Old clawdbot logs
│   ├── old-scripts/            # 12 deprecated Python/Bash scripts
│   └── .env.example            # Template showing ALL possible env vars
│
├── assets/                     # Static visual assets
│   ├── bella-banner.svg        # Bella branding banner
│   ├── bella-goddess-2026-02-14.png
│   └── bella-self-portrait-2026-02-14.png
│
├── config/                     # Configuration & repair scripts
│   ├── WORKFLOW.md             # Delegation rules (model routing)
│   └── fix_clawdbot.sh         # Clawdbot repair/reset script
│
├── data/                       # Business data exports
│   ├── square_customers.csv    # Square customer export
│   └── square_top_customers.csv
│
├── docs/                       # Documentation hub (23 files)
│   ├── bookings/               # Booking confirmation PDFs
│   ├── contracts/              # Client contracts (draft_contract_sam*.md)
│   ├── identity/               # (empty)
│   ├── legal/                  # (empty)
│   ├── ops/                    # (empty)
│   ├── quotes/                 # quote_lisa_tran.md
│   ├── AGENTS.md, BELLA.md, CLAUDE.md, DAILY_TASKS.md
│   ├── HEARTBEAT.md, IDENTITY.md, MEMORY.md, PROGRESS.md
│   ├── MEMORY_ARCHITECTURE.md, SECURITY-FIX-2026-02-02.md
│   ├── SOUL.md, TOOLS.md, USER.md
│   ├── api_keys_reference.md   # Comprehensive API key reference (33KB)
│   └── Bella vs Human Accountant.md
│
├── logs/                       # (empty — active log dir)
│
├── marketing-assets/           # Marketing creative files
│   ├── clean-up-bros-promo.png
│   ├── cleanup_bros_ad.png
│   ├── 2026-02-03-commercial-clean-ad.png
│   ├── 2026-02-03-commercial-clean-v2.png
│   └── cleanup_bros_viral.mp4
│
├── memory/                     # AI memory system (35+ files)
│   ├── backup/                 # 7-day rolling backup copies
│   ├── entities/               # Structured client/contractor records
│   │   ├── clients/            # claudia-alz.md, mckayla-vamarasi.md, meshach-ephraim-care.md
│   │   ├── contractors/        # (empty)
│   │   └── client-template.md
│   ├── sessions/               # Session archives
│   │   ├── 2026-02/SESSION-2026-02-02.md
│   │   └── archive/
│   ├── working/                # Live working state
│   │   ├── active-context.md
│   │   ├── current-tasks.json
│   │   ├── metrics.json
│   │   ├── staff-hours-feb-2026.md
│   │   └── staff_timetables_feb_2026.md
│   ├── heartbeat-state.json    # Heartbeat tracking state
│   ├── compact-instructions.md
│   ├── session-template.md
│   └── 2026-01-31 through 2026-02-17 daily logs (30+ files)
│
├── references/                 # Reference documents
│   ├── post-log.md             # Social media post log
│   └── WORKSPACE-AUDIT.md      # (this file)
│
├── scripts/                    # Active utility scripts
│   ├── api_health_check.py
│   ├── google-oauth-setup.py
│   ├── sync_memory_files.py
│   └── delegate_to_claude.sh
│
├── skills/                     # Modular skill packages (12 skills)
│   ├── bella-dashboard-manager/
│   ├── clean-up-bros-ops/
│   ├── client-onboarding/
│   ├── clinical-documentation/
│   ├── connecteam-overhaul/
│   ├── connecteam-roster/
│   ├── mcp-orchestrator/
│   ├── pre-flight-validator/
│   ├── secret-guard/
│   ├── skill-creator/
│   ├── social-content-poster/
│   ├── square-sync/
│   ├── viral-ads-creator/
│   └── *.skill (4 packaged .skill archives)
│
├── temp_vercel_check/          # Temporary Vercel project link
│   └── .vercel/project.json
│
├── work/                       # Active work-in-progress
│   ├── clients/                # LARISSA-MARKS.md, LISA-MARK.md
│   ├── social-media/           # TRENDING-CONTENT-FEB2026.md
│   ├── DOCUMENTATION-SYSTEM.md # Clinical documentation templates
│   ├── commercial-outreach-content.md
│   └── commercial-prospects.md
│
├── AGENTS.md                   # Operating instructions (loaded every session)
├── HEARTBEAT.md                # Heartbeat checklist (dashboard sync, checks)
├── IDENTITY.md                 # Business identity reference
├── MEMORY.md                   # Long-term curated memory (gitignored)
├── README.md                   # Repo README
├── SOUL.md                     # Bella's personality & rules
├── TOOLS.md                    # Local tool notes (cameras, SSH, TTS)
├── USER.md                     # Hafsah's profile (gitignored)
├── LICENSE                     # Repo license
├── .env                        # API keys (gitignored, Connecteam only currently)
├── .gitignore                  # Comprehensive gitignore
├── branding_specs.json         # Clean Up Bros branding colors/font
├── dashboard-data.json         # Live dashboard data (synced to Vercel)
├── dashboard.html              # Static dashboard page (legacy)
├── generate_logo.py            # Logo generation script
├── pre-push-check.py           # Secret scanning pre-push gate
├── update_dashboard.py         # Dashboard data update helper
└── 2026-02-17-*.png            # Generated images (logo, badges, transformation)
```

---

## 2. Script Files

### Root-Level Scripts

| File | Purpose |
|------|---------|
| `pre-push-check.py` | **Security gate** — scans workspace for exposed API keys (GitHub PATs, Google keys, Square tokens, OpenAI keys) before `git push`. Patterns: `ghp_`, `AIza`, `sk-`, `sq0atp-`, `sq0csp-` |
| `update_dashboard.py` | Updates `dashboard-data.json` with task statuses. Used to push live task data to the Bella Dashboard |
| `generate_logo.py` | Generates Clean Up Bros branding assets using AI image generation. Stores prompt for round badge logo |

### scripts/ Directory

| File | Purpose |
|------|---------|
| `scripts/api_health_check.py` | Tests all configured APIs (Square, Google, Twilio, etc.) without exposing credentials. Can save results to JSON |
| `scripts/google-oauth-setup.py` | One-time OAuth setup for Gmail, Sheets, Drive, Calendar. Runs localhost:8080 callback server |
| `scripts/sync_memory_files.py` | Syncs CLAUDE.md ↔ GEMINI.md memory files with timestamps and hashes |
| `scripts/delegate_to_claude.sh` | Delegates tasks from Bella's workspace to Claude Code CLI at `~/Desktop/claudeking` |

### config/ Scripts

| File | Purpose |
|------|---------|
| `config/fix_clawdbot.sh` | **Repair script** — stops Clawdbot, archives mixed sessions, resets gateway token. Contains recovery tokens for Telegram and ElevenLabs |

### Skill Scripts (Active)

| File | Purpose |
|------|---------|
| `skills/connecteam-roster/scripts/ct_api.py` | Connecteam API helper — thin wrapper for all roster API calls (auth, shifts, staff) |
| `skills/connecteam-roster/scripts/list_roster.py` | Lists current roster/shifts from Connecteam scheduler |
| `skills/connecteam-roster/scripts/list_staff.py` | Lists all staff members from Connecteam |
| `skills/connecteam-roster/scripts/list_jobs.py` | Lists job locations from Connecteam |
| `skills/connecteam-roster/scripts/create_shift.py` | Creates new shifts in Connecteam scheduler |
| `skills/connecteam-roster/scripts/update_shift.py` | Updates existing shifts |
| `skills/connecteam-roster/scripts/delete_shift.py` | Deletes shifts from roster |
| `skills/square-sync/scripts/check_unpaid_invoices.py` | Queries Square API for all unpaid invoices |
| `skills/square-sync/scripts/get_full_payment_data.py` | Gets complete payment data from Square |
| `skills/square-sync/scripts/inspect_meshach_invoice.py` | Inspects specific invoice for Meshach Ephraim Care |
| `skills/square-sync/scripts/sync_square_to_sheets.py` | Syncs Square invoice/payment data to Google Sheets |
| `skills/social-content-poster/scripts/post_to_meta.py` | Posts to Facebook Page + Instagram via Meta Graph API |
| `skills/viral-ads-creator/scripts/kie_gen.py` | Generates video via Kie.AI (Runway API wrapper) |
| `skills/viral-ads-creator/scripts/kie_img.py` | Generates images via Kie.AI |
| `skills/skill-creator/scripts/init_skill.py` | Scaffolds new skill directory structure |
| `skills/skill-creator/scripts/package_skill.py` | Packages a skill folder into a .skill archive |
| `skills/skill-creator/scripts/quick_validate.py` | Validates skill structure and metadata |

### Archive Scripts (Deprecated)

| File | Purpose |
|------|---------|
| `archive/old-scripts/sync_to_sheets.py` | Old Google Sheets sync |
| `archive/old-scripts/check_anthropic_models.py` | Check available Anthropic models |
| `archive/old-scripts/google_oauth_setup_ads.py` | Google Ads OAuth setup |
| `archive/old-scripts/reconcile_simple.py` | Simple account reconciliation |
| `archive/old-scripts/reconcile_accounts.py` | Full account reconciliation |
| `archive/old-scripts/test_google_services.py` | Google services connectivity test |
| `archive/old-scripts/session_logoff.py` | Old session logoff / state save |
| `archive/old-scripts/create_sam_square.py` | Create Square customer for Sam |
| `archive/old-scripts/google_org_task.py` | Google task organization |
| `archive/old-scripts/check_ads.py` | Check Google Ads status |
| `archive/old-scripts/setup-convex.sh` | Convex DB setup script |
| `archive/old-scripts/auto_refresh_3h.sh` | Auto-refresh token every 3 hours |

---

## 3. Skills

### Skill Directories (12 total)

| Skill | Description | Has Scripts | Has References |
|-------|-------------|:-----------:|:--------------:|
| **bella-dashboard-manager** | Controls Bella Dashboard v4.0 (React/Vite → Vercel → Telegram Mini App). Updates `dashboard-data.json`, pushes to GitHub for Vercel auto-deploy | ✅ (empty dir) | ✅ (empty dir) |
| **clean-up-bros-ops** | Core business operations — pricing ($180-$480 range), staff (Aminah), NDIS rates ($58.03/hr + $0.97/km), client schedules | ❌ | ✅ pricing.md, schedules.md |
| **client-onboarding** | Deep-dive research for new commercial cleaning leads. Searches reviews for hygiene issues, identifies decision makers, generates strategy docs and outreach drafts | ❌ | ❌ |
| **clinical-documentation** | Generates legally defensible shift notes, incident reports, and team updates for community mental health settings (clients: Larissa Marks, Lisa Mark) | ❌ | ✅ templates.md, client-profiles.md |
| **connecteam-overhaul** | Complete Connecteam app overhaul — branding, forms, staff bios, navigation cleanup, badge/ID creation. Critical: ONE TAB ONLY rule, navigate by URL hash not sidebar | ✅ (empty) | ✅ (empty) |
| **connecteam-roster** | Staff roster management via Connecteam API. Scheduler ID: `13218868`. Staff: Hafsah (11925732), Shamal (11925807), Teenay (13917939). Job locations: UNIT3, UNIT4, UNIT 2 NIGAL, HOME SITE | ✅ 7 scripts | ✅ 6 reference docs (training, checklists, API ref) |
| **mcp-orchestrator** | Coordinates MCP (Model Context Protocol) server operations via `mcporter` CLI at `/Users/hafsahnuzhat/.npm-global/bin/mcporter` | ❌ | ✅ (empty dir) |
| **pre-flight-validator** | **Mandatory** validation before confirming any deployment/update. Must web_fetch URLs, verify HTTP 200, cross-reference Square/templates before saying "done" | ✅ (empty) | ✅ (empty) |
| **secret-guard** | **Mandatory** security scan before every `git push`. Scans for API key patterns. Aborts push if secrets detected | ❌ | ❌ |
| **skill-creator** | Meta-skill for creating/packaging new skills. Provides scaffolding, validation, and .skill archive packaging | ✅ 3 scripts | ❌ |
| **social-content-poster** | Researches trending content, creates viral posts, publishes to Facebook + Instagram for Clean Up Bros. Includes hashtag library and caption templates | ✅ 1 script | ✅ caption-templates.md, hashtags.md, post-log.md |
| **square-sync** | Syncs Square payment/invoice data with Google Sheets backup. Sheet ID: `1pocJwoOO3emKfQf9mzFHuahZ5nA7KSrehF9fBqn-00Q` | ✅ 4 scripts | ❌ |
| **viral-ads-creator** | Identifies viral trends (TikTok/IG Reels) and adapts them to cleaning ads. Uses Nano Banana Pro (Gemini) for images, Kie.AI for video | ✅ 2 scripts | ✅ targeting.md |

### Packaged .skill Archives (4)

| File | Contents |
|------|----------|
| `bella-dashboard-manager.skill` | ZIP archive of bella-dashboard-manager/ |
| `clean-up-bros-ops.skill` | ZIP archive of clean-up-bros-ops/ + references |
| `clinical-documentation.skill` | ZIP archive of clinical-documentation/ + references |
| `pre-flight-validator.skill` | ZIP archive of pre-flight-validator/ |
| `square-sync.skill` | ZIP archive of square-sync/ + all scripts |

---

## 4. Config Files

| File | Purpose |
|------|---------|
| `.env` | Active environment variables (currently: Connecteam API credentials only) |
| `archive/.env.example` | **Complete template** of all possible env vars (70+ variables across 15 service categories) |
| `.claude/settings.local.json` | Claude Code permissions — extensive allowlist of bash commands, web fetch domains, and tool permissions |
| `.gitignore` | Comprehensive ignore rules: all `.env` files, OAuth tokens, memory/, MEMORY.md, USER.md, Python artifacts, IDE files, OS files |
| `branding_specs.json` | Clean Up Bros branding: primary `#333333`, accent `#00E5FF`, font Inter |
| `dashboard-data.json` | Live dashboard data pushed to Vercel. Contains stats, financial data, calendar, cron status, live tasks, patterns |
| `memory/heartbeat-state.json` | Tracks last heartbeat runs: morning brief, invoice check, evening summary, full business sync |
| `memory/working/current-tasks.json` | Active task tracking with priorities and statuses |
| `memory/working/metrics.json` | Business metrics: $14,214 revenue, $12,673 net profit, $3,351 outstanding, 5 overdue invoices |
| `temp_vercel_check/.vercel/project.json` | Vercel project link for dashboard deployment |
| `config/WORKFLOW.md` | Model routing rules — which tasks go to Opus, Gemini, Claude Code, sub-agents, or browser |

---

## 5. API Integrations

### Currently Active (in `.env`)

| Service | Env Vars | Purpose |
|---------|----------|---------|
| **Connecteam** | `CONNECTEAM_API_ID`, `CONNECTEAM_CLIENT_ID`, `CONNECTEAM_CLIENT_SECRET`, `CONNECTEAM_COMPANY_CODE`, `CONNECTEAM_COMPANY_ID` | Staff roster management, scheduling, job tracking |

### Configured in `~/.clawdbot/.env` (Full Stack)

Based on `archive/.env.example` and `docs/api_keys_reference.md`:

| Service | Key Prefix / Vars | Purpose | Status |
|---------|-------------------|---------|--------|
| **Google OAuth** | `GOOGLE_API_KEY`, `GOOGLE_CLIENT_ID/SECRET`, `GOOGLE_REFRESH_TOKEN`, `GOOGLE_PROJECT_ID` | Gmail, Calendar, Sheets, Drive | Configured |
| **Google Sheets** | `GOOGLE_SHEETS_ID` | Finance backup spreadsheet | Active |
| **Google Ads** | Developer token via OAuth | Advertising | Configured |
| **Gemini** | `GEMINI_API_KEY` | AI image/text generation | Configured |
| **Meta/Facebook** | `META_APP_ID/SECRET`, `META_BUSINESS_ID`, `META_SYSTEM_USER_TOKEN`, `FB_PAGE_ID`, `INSTAGRAM_ACCOUNT_ID` | Social media posting (FB + IG) | Working |
| **WhatsApp** | `WHATSAPP_BUSINESS_ACCOUNT_ID`, `WHATSAPP_PHONE_NUMBER_ID` | Business messaging | Working |
| **Twilio** | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` | SMS & voice calls | Working |
| **Square** | `SQUARE_ACCESS_TOKEN`, `SQUARE_APPLICATION_ID` | Payments, invoices (Production) | Working |
| **Telegram** | `TELEGRAM_BOT_TOKEN` | Bot operations (@CubsBookKeeperBot) | Working |
| **Anthropic** | `ANTHROPIC_API_KEY` | Claude API | Configured |
| **OpenAI** | `OPENAI_API_KEY` | GPT models | Configured |
| **OpenRouter** | `OPENROUTER_API_KEY` | Free LLM routing | Working |
| **ElevenLabs** | `ELEVENLABS_API_KEY` | Voice/TTS generation | Working |
| **Brave** | `BRAVE_API_KEY` | Web search | Working |
| **Apify** | `APIFY_API_KEY` | Web scraping | Working |
| **Kie.AI** | `KIE_API_KEY` | Video & image generation (Runway) | Configured |
| **LinkedIn** | `LINKEDIN_CLIENT_ID/SECRET`, `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_ORG_ID` | Company page posting | Configured |
| **Convex** | `CONVEX_DEPLOY_KEY`, `CONVEX_URL` | Real-time DB (archived, likely inactive) | Archived |
| **AWS** | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | Cloud services (optional) | Configured |
| **Gmail** | `GMAIL_APP_PASSWORD`, `GMAIL_ADDRESS` | Direct email sending | Configured |
| **N8N** | `N8N_URL`, `N8N_API_KEY` | Workflow automation | Configured |
| **GitHub** | `GITHUB_SSH_KEY_FINGERPRINT` | Git operations | Configured |
| **Clawdbot** | `CLAWDBOT_GATEWAY_TOKEN`, `CLAWDBOT_GATEWAY_URL` | Gateway daemon | Active |

### API Integration Points in Code

- **Square API** → `skills/square-sync/scripts/` (4 scripts), `archive/mcp/square_server.py`
- **Connecteam API** → `skills/connecteam-roster/scripts/` (7 scripts)
- **Meta Graph API** → `skills/social-content-poster/scripts/post_to_meta.py`
- **Kie.AI/Runway API** → `skills/viral-ads-creator/scripts/kie_gen.py`, `kie_img.py`
- **Google Sheets API** → `skills/square-sync/scripts/sync_square_to_sheets.py`
- **Google OAuth** → `scripts/google-oauth-setup.py`

---

## 6. Memory Files

### Memory Hierarchy

| Layer | Location | Count | Purpose |
|-------|----------|-------|---------|
| **Identity** | `SOUL.md` | 1 | Bella's personality, rules, sources of truth |
| **Long-term** | `MEMORY.md` | 1 | Curated facts, preferences, mandatory rules |
| **Daily logs** | `memory/2026-*.md` | ~35 | Raw journal entries — decisions, tasks, learnings |
| **Backups** | `memory/backup/` | ~16 | 7-day rolling backup copies of daily logs |
| **Entities** | `memory/entities/` | 4 | Structured client/contractor records |
| **Working** | `memory/working/` | 5 | Active context, tasks, metrics, staff hours |
| **Sessions** | `memory/sessions/` | 1 | Archived session summaries |

### Key Memory Files

| File | Purpose |
|------|---------|
| `MEMORY.md` | **Mandatory rules**: Square = only financial SOT, Google Calendar = only schedule SOT. Client info, validation rules, skill creation rules |
| `SOUL.md` | Bella's personality charter. "Don't be generic." Sharp, proactive, opinionated. Sources of truth table |
| `USER.md` | Hafsah's profile (gitignored for privacy) |
| `HEARTBEAT.md` | Dashboard sync protocol — update JSON, copy to dashboard, secret scan, git push both repos |
| `memory/heartbeat-state.json` | Last check timestamps: morning brief, invoice check, evening summary |
| `memory/working/metrics.json` | Revenue $14,214, profit $12,673, outstanding $3,351, 5 overdue |
| `memory/working/current-tasks.json` | Active tasks: Claudia Alz follow-up, Meshach payment plan monitoring |
| `memory/entities/clients/meshach-ephraim-care.md` | $3,750 total, $2,000 paid, payment plan active |
| `memory/entities/clients/claudia-alz.md` | $320 — paid Feb 2026 |
| `memory/entities/clients/mckayla-vamarasi.md` | Client record |
| `memory/entities/client-template.md` | Template for new client entity files |

### Daily Log Date Range

- **Earliest:** 2026-01-31
- **Latest:** 2026-02-17
- **Key entries:** session summaries, gemini API fix, codebase improvements, bella dashboard, kimi session, weekly cleans/schedule, heartbeat checks, payment updates, version check, first meeting, new session, bella intro

---

## 7. Google Sheets References

### Active Sheet

| Sheet Name | Sheet ID | Purpose | Referenced In |
|------------|----------|---------|---------------|
| **Clean Up Bros - Finance Backup** | `1pocJwoOO3emKfQf9mzFHuahZ5nA7KSrehF9fBqn-00Q` | Square data backup — invoices, payments, client balances | `skills/square-sync/SKILL.md`, `MEMORY.md`, `SOUL.md` |

### Sheet Operations

- **Sync script:** `skills/square-sync/scripts/sync_square_to_sheets.py`
- **CLI tool:** Uses `gog sheets update` command (Google CLI wrapper)
- **Flow:** Square API → Python script → Google Sheets API → Sheet update
- **Rule:** Sheet is BACKUP only. Square is always primary source of truth

### Historical References

Files mentioning Sheets: `archive/mcp/accounting_server.py`, `archive/mcp/google_server.py`, `archive/old-scripts/sync_to_sheets.py`, `archive/old-scripts/reconcile_simple.py`, `archive/old-scripts/reconcile_accounts.py`, `scripts/google-oauth-setup.py`, `.claude/skills/google-health-check.md`

---

## 8. Archive / MCP Folder

### `archive/mcp/` — 18 Archived MCP Server Scripts

These are Model Context Protocol servers that were previously used but moved to archive:

| Server | Purpose |
|--------|---------|
| `square_server.py` | Square payments/invoicing API operations |
| `google_server.py` | Gmail, Calendar, Sheets, Drive operations |
| `meta_server.py` | Facebook/Instagram Graph API posting |
| `whatsapp_server.py` | WhatsApp Business messaging |
| `twilio_server.py` | SMS & voice calls via Twilio |
| `elevenlabs_server.py` | Text-to-speech voice generation |
| `linkedin_server.py` | LinkedIn company page posting |
| `brave_server.py` | Brave web search |
| `apify_server.py` | Web scraping via Apify |
| `openrouter_server.py` | LLM routing through OpenRouter |
| `coldoutreach_server.py` | Cold email/SMS outreach campaigns |
| `accounting_server.py` | Bookkeeping, BAS prep, reconciliation |
| `convex_server.py` | Convex real-time database operations |
| `kie_server.py` | Kie.AI video/image generation |
| `ref_server.py` | Reference document management |
| `shared_utils.py` | Shared utility functions for MCP servers |
| `logging_config.py` | Centralized logging configuration |
| `validation.py` | Input validation utilities |

### `archive/convex/` — Deprecated Convex DB Setup

| File | Purpose |
|------|---------|
| `schema.ts` | Convex database schema (TypeScript) |
| `memory.ts` | Memory storage/retrieval functions |
| `package.json` | Node.js dependencies |
| `README.md` | Setup instructions |

### `archive/old-scripts/` — 12 Deprecated Scripts

See [Script Files](#2-script-files) → Archive Scripts section.

---

## 9. References Folder

| File | Purpose |
|------|---------|
| `references/post-log.md` | Social media post log. Tracks posts with platform, type, caption, post IDs, hashtags. Latest: 2026-02-17 Facebook+Instagram transformation post |
| `references/WORKSPACE-AUDIT.md` | This file |

**Note:** The references folder is relatively thin. Most reference material lives inside individual skill folders:
- `skills/connecteam-roster/references/` — 6 files (training, checklists, API docs)
- `skills/clean-up-bros-ops/references/` — pricing.md, schedules.md
- `skills/social-content-poster/references/` — captions, hashtags, post log
- `skills/viral-ads-creator/references/` — targeting.md
- `skills/clinical-documentation/references/` — templates.md, client-profiles.md

---

## 10. Claude Code Workspace (`~/Desktop/claudeking`)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | **Only file** in this directory. Defines Claude Code's role as the "execution layer" for Bella. Contains owner context, key locations, integration scripts, API service table, common tasks, rules, and security guidelines |

### Key Points from CLAUDE.md

- **Architecture:** `Hafsah → Bella (Telegram) → Claude Code (CLI/Tools)`
- **Role:** Execution layer — receives tasks from Bella, executes, reports results
- **Key locations:** Points to `~/Desktop/🦀` for Bella's workspace, `~/.clawdbot/` for config
- **API Status Table:** 12 services listed as configured/working
- **GitHub:** `https://github.com/SamDev1303/Botproject`
- **Dashboard:** `/Users/hafsahnuzhat/cleanupbros-dashboard/` (note: different from `bella-dashboard/`)
- **Outstanding work noted:** Claudia Alz $320 (since cleared), Meshach $1,750

---

## 11. .claude Rules & Skills

### Auto-Loaded Rules (6 files, always active)

| Rule File | Category | Summary |
|-----------|----------|---------|
| `automation/heartbeat-tasks.md` | Automation | Comprehensive heartbeat schedule: morning brief (8AM), continuous monitoring (invoices, payments, bookings), EOD summary (6PM), weekly (Monday 9AM), monthly (1st), quarterly BAS. Includes notification rules, quiet hours (11PM-7AM), error handling |
| `business/pricing.md` | Business | Service pricing table: General $180, EOL 1BR $280 → 3BR $480, Airbnb $120. GST formula, quoting rules, extras/add-ons, payment terms |
| `business/tax-compliance.md` | Business | Australian tax rules: GST 10%, BAS quarters, worksheet labels (G1/G10/G11), ATO expense categories, superannuation 11.5%, record keeping 5 years |
| `business/email-usage.md` | Business | **Critical:** Business email `cleanupbros.au@gmail.com`, personal `hafsahnuzhat1303@gmail.com`. NEVER use `hafsah@cleanupbros.com.au` (doesn't exist). Templates for business/personal |
| `clients/communication.md` | Clients | Complete communication playbook: response time targets (2hrs SMS, 4hrs email), email/SMS/WhatsApp/phone templates for quotes, bookings, payment reminders, review requests. Follow-up sequences. Escalation rules |
| `clients/overdue-accounts.md` | Clients | Overdue management procedures: Day 0-28 escalation timeline, payment plan terms, bad debt write-off rules, blacklist policy. Current: Meshach $2,500 on payment plan, Claudia cleared |
| `operations/booking-workflow.md` | Operations | 6-step booking SOP: enquiry → quote → booking → reminder → clean → follow-up. Checklist template |

### Claude Code Skills (2 files)

| Skill | Trigger |
|-------|---------|
| `google-health-check.md` | "check google health", "google status" — validates OAuth tokens, tests Gmail/Calendar/Sheets/Drive |
| `session-logoff.md` | "done for the day", "wrap up", "logoff" — saves state, commits to GitHub |

---

## 12. Docs Folder

| File | Size | Purpose |
|------|------|---------|
| `AGENTS.md` | 7.8KB | Operating instructions (copy of root AGENTS.md for docs reference) |
| `BELLA.md` | 2.2KB | Bella's description/capabilities |
| `CLAUDE.md` | 12.4KB | Claude integration documentation |
| `DAILY_TASKS.md` | 267B | Daily task list |
| `HEARTBEAT.md` | 3.2KB | Heartbeat configuration docs |
| `IDENTITY.md` | 1.3KB | Business identity details |
| `MEMORY.md` | 5.0KB | Memory system docs |
| `MEMORY_ARCHITECTURE.md` | 16.5KB | Detailed memory architecture design |
| `PROGRESS.md` | 7.8KB | Project progress tracking |
| `SECURITY-FIX-2026-02-02.md` | 3.5KB | Security fix documentation (credential leak remediation) |
| `SOUL.md` | 1.7KB | Personality charter docs |
| `TOOLS.md` | 3.7KB | Tool configuration docs |
| `USER.md` | 3.1KB | User profile docs |
| `api_keys_reference.md` | **33.3KB** | **Comprehensive** API key reference — 100+ env vars, OAuth flow explanation, all service configs |
| `Bella vs Human Accountant.md` | 8.5KB | Comparison document |
| `bookings/` | 1 PDF | Booking_Confirmation_Basem_Holsworthy.pdf |
| `contracts/` | 2 files | draft_contract_sam.md, draft_contract_sam_v2.md |
| `quotes/` | 1 file | quote_lisa_tran.md |

---

## 13. Work Folder

Active work-in-progress documents:

| File | Purpose |
|------|---------|
| `work/DOCUMENTATION-SYSTEM.md` | Clinical documentation system — shift note templates, incident report structure for mental health support work |
| `work/commercial-prospects.md` | Commercial cleaning prospects list. Target: 5 paying commercial clients. High-priority: childcare centers |
| `work/commercial-outreach-content.md` | Outreach email/SMS content for commercial leads |
| `work/clients/LARISSA-MARKS.md` | Clinical client profile — age 42, HIGH risk during dysregulated episodes, complex mental health |
| `work/clients/LISA-MARK.md` | Clinical client profile |
| `work/social-media/TRENDING-CONTENT-FEB2026.md` | Trending content research for Feb 2026: short vertical videos, transformation content, Reels strategies |

---

## 14. Marketing & Asset Files

### Root-Level Images

| File | Description |
|------|-------------|
| `2026-02-17-cleanupbros-logo.png` | Generated Clean Up Bros logo |
| `2026-02-17-staff-badge-template.png` | Staff badge template design |
| `2026-02-17-badge-arieta.png` | Staff badge for Arieta |
| `2026-02-17-badge-hafsah.png` | Staff badge for Hafsah |
| `2026-02-17-badge-shamal.png` | Staff badge for Shamal |
| `2026-02-17-cleanupbros-transformation-post.png` | Social media transformation post |
| `2026-02-17-kitchen-transformation.png` | Kitchen before/after |

### marketing-assets/

| File | Description |
|------|-------------|
| `clean-up-bros-promo.png` | Promotional image |
| `cleanup_bros_ad.png` | Ad creative |
| `2026-02-03-commercial-clean-ad.png` | Commercial cleaning ad v1 |
| `2026-02-03-commercial-clean-v2.png` | Commercial cleaning ad v2 |
| `cleanup_bros_viral.mp4` | Viral video content |

### assets/

| File | Description |
|------|-------------|
| `bella-banner.svg` | Bella AI branding banner |
| `bella-goddess-2026-02-14.png` | Bella portrait (6.4MB) |
| `bella-self-portrait-2026-02-14.png` | Bella self-portrait (5.6MB) |

---

## 15. Git & Security

### Repository

- **Remote:** `https://github.com/SamDev1303/Botproject.git`
- **Branch:** `main`
- **⚠️ WARNING:** Git remote URL contains a GitHub PAT token in plaintext (`ghp_IQ4p...`). This should be migrated to SSH or credential helper.

### Recent Commits (last 10)

All from 2026-02-17, frequent dashboard syncs (every 5 minutes):
```
92cb020 dashboard sync 7:05 PM AEDT
95ff2cc dashboard sync: 7:00 PM AEDT
4388a53 dashboard sync 6:55 PM AEDT
ab2710c dashboard sync: 6:50 PM AEDT
538fafb dashboard sync 6:45 PM AEDT
a2866d3 dashboard sync: 6:40 PM AEDT
1ebf34e Dashboard sync @ 6:35 PM AEDT
ce50073 dashboard sync 6:30 PM AEDT
349819c dashboard sync 6:25 PM AEDT
c643253 dashboard sync: 6:20 PM AEDT
```

### Security Notes

- `.env` is gitignored but currently only has Connecteam keys. Main secrets in `~/.clawdbot/.env`
- `MEMORY.md` and `USER.md` are gitignored (contain personal/client data)
- `pre-push-check.py` scans for common secret patterns before push
- `SECURITY-FIX-2026-02-02.md` documents a previous credential leak remediation
- `config/fix_clawdbot.sh` contains hardcoded Telegram and ElevenLabs tokens (security concern if committed)
- Git remote URL exposes GitHub PAT (should be fixed)

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Total directories** (excl. .git) | ~50 |
| **Total files** (excl. .git) | ~150+ |
| **Python scripts** | 30 (17 active, 13 archived) |
| **Shell scripts** | 4 (2 active, 2 archived) |
| **TypeScript files** | 2 (archived Convex) |
| **Skills (directory)** | 13 |
| **Skills (packaged .skill)** | 5 |
| **Memory daily logs** | ~35 |
| **Config/JSON files** | 10 |
| **Business rules (.claude/rules)** | 7 |
| **API integrations configured** | 20+ services |
| **Marketing images** | 12+ |
| **Documentation files** | 20+ |

---

*End of audit. Generated by workspace-audit subagent.*
