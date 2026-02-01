# Compact Instructions for Bella

> Used by Claude Code's auto-compaction feature
> Updated: 2026-02-02

When compacting this conversation:

## ALWAYS Preserve (High Priority)

1. **Outstanding payments and debts:**
   - Claudia Alz: $320 (OVERDUE)
   - Meshach Ephraim Care: $3,750 remaining
   - Any new overdue accounts

2. **Current tasks from working memory:**
   - Read from `memory/working/current-tasks.json`
   - Preserve ALL pending and in-progress tasks

3. **Today's schedule:**
   - Upcoming bookings (next 7 days)
   - Calendar appointments
   - Deadlines (BAS, invoices)

4. **Recent invoices created:**
   - Last 5 invoices with numbers and amounts
   - Payment status for each

5. **Pending follow-up actions:**
   - Client communication pending
   - Quotes waiting for response
   - Payment reminders needed

## Can Summarize (Medium Priority)

- **Tool outputs:** Keep only results, remove verbose logs
- **Successful operations:** "Created invoice INV-123" (don't need full API response)
- **Conversation history:** Keep decisions and outcomes, remove detailed back-and-forth
- **Event logs:** Summarize multiple similar events ("Sent 3 booking confirmations")

## Never Compact (Protected Content)

These are EXTERNAL to context (not loaded), so safe:

- `.claude/rules/` content (auto-loaded separately)
- `memory/entities/` client files (queried on demand)
- User profile (`USER.md`)
- Business rules and pricing

## Compaction Strategy

**If context is at 75% capacity:**

1. Keep last 10 conversation turns verbatim
2. Summarize turns 11-50 into key decisions
3. Archive turns 50+ to session file
4. Keep ALL items from "ALWAYS Preserve" list
5. Compress tool outputs to one-line summaries

**Expected reduction:** 60-70% context freed

## Example Compact

**Before (500 tokens):**
```
Created Square invoice for Sarah Chen
Invoice details: {"id": "inv_123", "amount": 380, "due_date": "2026-02-12", ...}
Square API response: {"invoice": {...}, "created_at": "2026-02-05T10:30:00Z", ...}
SMS sent to 0412345678: "Hi Sarah! Your booking is confirmed..."
Twilio response: {"sid": "SM123", "status": "sent", ...}
Calendar event created: {...}
```

**After (50 tokens):**
```
Booking confirmed for Sarah Chen:
- Invoice INV-123: $380 (due 12/02)
- SMS confirmation sent
- Calendar updated
```

---

*This file ensures critical information survives auto-compaction.*
