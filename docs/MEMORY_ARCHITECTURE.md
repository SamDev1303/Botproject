# Bella's Memory Architecture

> **Based on:** AI Memory Research + Claude Code Best Practices
> **Implemented:** 2026-02-02
> **Architecture:** Hierarchical Multi-Tier Memory System

---

## Overview

Bella's memory system implements a **3-tier cognitive architecture** inspired by human memory systems and optimized for Claude Code's context management.

```
┌─────────────────────────────────────────────────────────────┐
│  WORKING MEMORY (Short-Term)                                │
│  • Current session context                                  │
│  • Active tasks and immediate decisions                     │
│  • Recent conversation (last 10-20 turns)                   │
│  Storage: In-context (Claude's active window)               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  EPISODIC MEMORY (Event-Based)                              │
│  • Session summaries (what happened when)                   │
│  • Task completion records                                  │
│  • Conversation history (timestamped)                       │
│  Storage: memory/ directory                                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  SEMANTIC MEMORY (Knowledge Base)                           │
│  • Business facts and rules                                 │
│  • Procedures and workflows                                 │
│  • Client data and preferences                              │
│  Storage: .claude/rules/ + CLAUDE.md                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
/Users/hafsahnuzhat/Desktop/🦀/
├── CLAUDE.md                      # Project memory (500 lines max)
├── CLAUDE.local.md                # Personal preferences (.gitignored)
├── .claude/
│   ├── rules/                     # Modular semantic memory
│   │   ├── business/
│   │   │   ├── pricing.md
│   │   │   ├── services.md
│   │   │   └── tax-compliance.md
│   │   ├── clients/
│   │   │   ├── communication.md
│   │   │   └── overdue-accounts.md
│   │   ├── operations/
│   │   │   ├── booking-workflow.md
│   │   │   ├── invoicing.md
│   │   │   └── payment-tracking.md
│   │   └── automation/
│   │       ├── heartbeat-tasks.md
│   │       └── daily-summaries.md
│   ├── skills/                    # On-demand knowledge
│   │   ├── tax-calculator/
│   │   │   └── SKILL.md
│   │   ├── cold-outreach/
│   │   │   └── SKILL.md
│   │   └── bas-preparation/
│   │       └── SKILL.md
│   └── agents/                    # Subagent templates
│       ├── invoice-processor.md
│       └── lead-generator.md
├── memory/                        # Episodic memory
│   ├── working/                   # Current session
│   │   ├── current-tasks.json
│   │   └── active-context.md
│   ├── sessions/                  # Historical sessions
│   │   ├── 2026-02/
│   │   │   ├── 02-morning.md
│   │   │   ├── 02-afternoon.md
│   │   │   └── 02-summary.md
│   │   └── archive/
│   │       └── 2026-01/
│   ├── entities/                  # Entity memory
│   │   ├── clients/
│   │   │   ├── sarah-chen.md
│   │   │   └── claudia-alz.md
│   │   └── contractors/
│   │       └── sam-contractor.md
│   └── compact-instructions.md    # Auto-compact guidance
├── IDENTITY.md                    # Personality (immutable)
├── USER.md                        # User profile (Hafsah)
└── HEARTBEAT.md                   # Scheduled tasks

~/.claude/CLAUDE.md                # User-level memory (cross-project)
~/.clawdbot/.env                   # Secrets (never in memory)
```

---

## Memory Types Explained

### 1. Working Memory (Short-Term)

**Purpose:** Active task tracking and immediate context

**Location:** `memory/working/`

**Files:**
- `current-tasks.json` - Active task list with status
- `active-context.md` - Current conversation summary

**Lifespan:** Cleared at session end or when `/clear` used

**Size limit:** ~5KB (to preserve context space)

**Example (`current-tasks.json`):**
```json
{
  "updated": "2026-02-02T10:30:00+11:00",
  "active_tasks": [
    {
      "id": "task-001",
      "description": "Follow up with Claudia Alz for $320 payment",
      "status": "pending",
      "priority": "high",
      "created": "2026-02-01"
    }
  ],
  "recent_actions": [
    "Created invoice #INV-123 for Sarah Chen",
    "Sent booking confirmation SMS to 0412345678"
  ]
}
```

---

### 2. Episodic Memory (Event-Based)

**Purpose:** Record of past interactions and decisions

**Location:** `memory/sessions/`

**Organization:** By date → By time period

**Structure:**
```
sessions/
├── 2026-02/
│   ├── 02-morning.md      # 6am-12pm session
│   ├── 02-afternoon.md    # 12pm-6pm session
│   ├── 02-evening.md      # 6pm-12am session
│   └── 02-summary.md      # Auto-generated daily summary
└── archive/
    └── 2026-01/           # Archived after 30 days
```

**Template (`session-template.md`):**
```markdown
# Session: [Date] [Period]

**Time:** [Start] - [End] AEST/AEDT
**Duration:** [X] minutes
**Type:** [Morning Brief | Client Work | Admin | Mixed]

## Context
- **Previous session:** [Link to previous]
- **Ongoing tasks:** [List from working memory]

## Events

### Event 1: [Event Name]
- **Time:** 10:15 AEDT
- **Type:** [Booking | Invoice | Communication | Task]
- **Details:** [What happened]
- **Outcome:** [Result]
- **Related:** [Client name, invoice #, etc.]

### Event 2: [Event Name]
...

## Decisions Made
1. [Decision 1]
2. [Decision 2]

## Actions Taken
- [ ] Created invoice for Sarah Chen ($380)
- [ ] Sent SMS confirmation to 0412345678
- [ ] Updated Google Sheets with income

## Follow-ups Required
- [ ] Chase Claudia Alz payment (due 2 days ago)
- [ ] Prepare BAS for Q2 (due April 28)

## Tools Used
- Square (invoice creation)
- Twilio (SMS sending)
- Google Sheets (bookkeeping)

## Notes
[Any important context for future sessions]

## Compact Priority
**If compacting:** Preserve follow-ups and outstanding tasks. Event details can be summarized.
```

---

### 3. Semantic Memory (Knowledge Base)

**Purpose:** Persistent facts, rules, and procedures

**Location:** `.claude/rules/`

**Loading:** Automatic via Claude Code's modular rules

**Organization:** By domain

#### Business Rules (`business/pricing.md`):
```markdown
# Clean Up Bros Pricing

> Auto-loaded on every session
> Last updated: 2026-02-02

## Service Pricing (GST Inclusive)

| Service | Price | GST | Duration |
|---------|-------|-----|----------|
| General Cleaning | $180 | $16.36 | 2-3 hours |
| End of Lease 1BR | $280 | $25.45 | 3-4 hours |
| End of Lease 2BR | $380 | $34.55 | 4-5 hours |
| End of Lease 3BR | $480 | $43.64 | 5-6 hours |
| Airbnb Turnover | $120 | $10.91 | 1-2 hours |

## GST Calculation
```
GST = Total ÷ 11
Ex-GST = Total - GST
```

## Quoting Rules
1. Ask for number of bedrooms
2. Ask if end of lease or general clean
3. Provide quote with GST breakdown
4. Mention bond-back guarantee for end of lease
```

#### Tax Compliance (`business/tax-compliance.md`):
```markdown
# Australian Tax Compliance

> Critical rules for bookkeeping and BAS preparation

## GST Rules
- **Rate:** 10% (calculate as Total ÷ 11)
- **BAS Quarters:**
  - Q1: Jul-Sep (due Oct 28)
  - Q2: Oct-Dec (due Jan 28)
  - Q3: Jan-Mar (due Apr 28)
  - Q4: Apr-Jun (due Jul 28)

## Expense Categories (ATO Compliant)
- Stock/Materials (cleaning supplies)
- Motor Vehicle (fuel, repairs)
- Marketing (ads, website)
- Office Supplies
- Repairs & Maintenance
- Professional Fees

## Tax-Free Threshold
$18,200/year (no tax below this)

## Superannuation
11.5% of employee wages (mandatory)
```

---

### 4. Entity Memory

**Purpose:** Track specific people/organizations

**Location:** `memory/entities/`

**Structure:**
```
entities/
├── clients/
│   ├── sarah-chen.md
│   ├── claudia-alz.md
│   └── meshach-ephraim-care.md
└── contractors/
    └── sam-contractor.md
```

**Template (`client-template.md`):**
```markdown
# Client: [Name]

## Basic Info
- **Full Name:** [First Last]
- **Phone:** [0412345678]
- **Email:** [email@example.com]
- **Address:** [Full address]
- **Source:** [How they found us]
- **First Contact:** [Date]

## Service History
| Date | Service | Amount | Status | Invoice |
|------|---------|--------|--------|---------|
| 15/01/2026 | 2BR End of Lease | $380 | Paid | INV-123 |

## Payment History
| Date | Amount | Method | Notes |
|------|--------|--------|-------|
| 18/01/2026 | $380 | Bank Transfer | On time |

## Communication Log
### 15/01/2026 - Initial Enquiry
- Channel: Email
- Request: Quote for 2BR Liverpool
- Response: $380 quote sent

### 16/01/2026 - Booking Confirmation
- Channel: SMS
- Details: Booked for 20/01/2026 at 10am

## Preferences
- Prefers SMS communication
- Pays within 3 days (reliable)
- Likely to rebook (end of lease tenants)

## Alerts
- [ ] None currently
```

---

## Memory Operations

### 1. Session Start

**Automatic loads (via Claude Code):**
1. `CLAUDE.md` (project memory)
2. All files in `.claude/rules/` (modular rules)
3. `IDENTITY.md` (personality)
4. `USER.md` (Hafsah's profile)

**Bella manually reads:**
1. `memory/working/current-tasks.json`
2. Latest session summary from `memory/sessions/`
3. `HEARTBEAT.md` for scheduled tasks

**Total context:** ~15-20KB

---

### 2. During Session

**Working memory updates:**
- Add tasks to `current-tasks.json`
- Track actions in `active-context.md`

**Episodic memory creation:**
- Log events as they happen
- Update session file in `memory/sessions/YYYY-MM/DD-period.md`

**Entity memory updates:**
- Create or update client files when interacting
- Log communication in entity files

---

### 3. Session End

**Auto-compact preparation:**
1. Summarize session events
2. Extract key decisions and follow-ups
3. Update `compact-instructions.md` with what to preserve

**Working memory:**
- Move completed tasks to session summary
- Keep pending tasks in `current-tasks.json`

**Daily summary generation:**
- Aggregate all sessions from the day
- Create `DD-summary.md` with highlights
- Clear working memory (optional)

---

### 4. Auto-Compaction (When Context Fills)

**Trigger:** Context window at 75% capacity

**Preserved (via `compact-instructions.md`):**
```markdown
# Compact Instructions for Bella

When compacting this conversation:

## ALWAYS Preserve
1. Outstanding client payments (Claudia Alz $320, etc.)
2. Current tasks from working memory
3. Today's booking schedule
4. Recent invoices created (last 5)
5. Any pending follow-up actions

## Can Summarize
- Tool outputs from successful operations
- Detailed event logs (keep just outcomes)
- Historical conversation turns (keep decisions only)

## Never Compact
- `.claude/rules/` content (not in context)
- Entity memory files (external)
- User profile and business rules
```

**Result:** Context reduced by 60-70% while preserving critical information

---

## Skills (On-Demand Loading)

Skills are loaded ONLY when explicitly invoked, saving context space.

**Example: Tax Calculator Skill**

**File:** `.claude/skills/tax-calculator/SKILL.md`

```markdown
# Skill: Tax Calculator

> Invoked with: "Calculate my BAS" or when preparing quarterly tax

## Capabilities
- GST calculations (G1, G10, G11)
- Superannuation calculations
- Tax bracket estimation
- FY profit/loss summaries

## Tools Required
- Google Sheets (read income/expenses)

## Process
1. Read all income for period from Sheets
2. Calculate GST collected (Total ÷ 11)
3. Read all expenses for period
4. Calculate GST credits
5. Generate BAS worksheet

## Output Format
```
📋 BAS Worksheet - Q[X] [Year]

G1 (Total Sales): $XX,XXX.XX
GST on Sales: $X,XXX.XX

G11 (Non-Capital Purchases): $X,XXX.XX
GST Credits: $XXX.XX

GST Owing: $X,XXX.XX

Due Date: [Date]
```
```

**Context cost:** 0KB until invoked, then ~2KB

---

## Integration with Claude Code

### Command Pattern

Bella can delegate complex tasks to Claude Code:

```
Bella: "I'll use Claude Code to generate the BAS report."

[Bella executes]:
cd /Users/hafsahnuzhat/Desktop/claudeking && \
claude "Generate BAS report for Q2 2026 using Clean Up Bros data" \
  --add-dir /Users/hafsahnuzhat/Desktop/🦀
```

Claude Code has its own memory (`/Users/hafsahnuzhat/Desktop/claudeking/CLAUDE.md`) and can access Bella's memory files.

---

## Memory Maintenance

### Daily (Automated via Heartbeat)
- [x] Create new session file for each period
- [x] Update working memory with today's tasks
- [x] Generate daily summary at 6pm

### Weekly (Manual Review)
- [ ] Review and archive old sessions (keep last 14 days)
- [ ] Update entity memory for frequent clients
- [ ] Check compact-instructions.md is current

### Monthly (End of Month)
- [ ] Archive previous month's sessions
- [ ] Generate monthly financial summary
- [ ] Update business rules if pricing changed

---

## Context Window Management

### Current Usage Estimate

| Component | Size | Frequency |
|-----------|------|-----------|
| CLAUDE.md | 10KB | Every request |
| .claude/rules/ | 15KB | Every request |
| IDENTITY.md + USER.md | 3KB | Every request |
| Working memory | 5KB | Every request |
| Session history (latest) | 10KB | Session start |
| **TOTAL BASE** | **43KB** | **~21% of 200K context** |

**Available for conversation:** 157KB (~79%)

### Optimization Strategies

1. **Use Skills:** Keep reference data external, load on-demand
2. **Modular Rules:** Split large rule files into smaller chunks
3. **Entity Files:** Store client data externally, query as needed
4. **Regular Compaction:** Use `/compact` at task boundaries
5. **Subagents:** Delegate high-volume tasks to isolated contexts

---

## Migration from Old Structure

### Mapping

| Old Location | New Location | Reason |
|--------------|--------------|--------|
| `memory/*.md` (flat) | `memory/sessions/YYYY-MM/` | Better organization |
| `GEMINI.md` | `CLAUDE.md` + `.claude/rules/` | Modular, auto-loading |
| `HEARTBEAT.md` | `.claude/rules/automation/` | Semantic memory |
| Single `MEMORY.md` | Multiple entity files | Scalability |

### Migration Script

```bash
# Run this to migrate old memory structure to new
cd /Users/hafsahnuzhat/Desktop/🦀
./scripts/migrate-memory.sh
```

---

## Sources & References

**AI Memory Research:**
- [Memoria: Agentic Memory Framework](https://www.arxiv.org/pdf/2512.12686)
- [AI Memory Systems: Cognitive Architecture](https://pub.towardsai.net/ai-memory-systems-a-deep-dive-into-cognitive-architecture-83190b3e1ac5)
- [Context Window Management Strategies](https://www.getmaxim.ai/articles/context-window-management-strategies-for-long-context-ai-agents-and-chatbots/)

**Claude Code Documentation:**
- [Memory Management](https://code.claude.com/docs/en/memory)
- [Auto-Compaction](https://claudelog.com/faqs/what-is-claude-code-auto-compact/)
- [Modular Rules](https://github.com/centminmod/my-claude-code-setup)

---

*This architecture is designed to scale with Bella's workload while staying within context limits.*
