---
name: bella-dashboard-manager
description: Control and update the Bella Dashboard v4.0 (React/Vite app at /Users/hafsahnuzhat/bella-dashboard/). Use when updating project status, business metrics, or financial alerts for Hafsah. Requires updating dashboard-data.json and pushing to Vercel via GitHub.
---

# Bella Dashboard Manager v4.0

Manage the live React dashboard deployed to Vercel as a Telegram Mini App.

## Mandatory Rule
**Dashboard-First**: Every major business decision or update must be reflected in the dashboard data before replying.

## Architecture
- **Dashboard App:** `/Users/hafsahnuzhat/bella-dashboard/` (React + Vite + TypeScript + Tailwind)
- **Data File:** `~/Desktop/🦀/dashboard-data.json` (workspace root)
- **Deploy Target:** Vercel (auto-deploys from GitHub push)
- **Mini App:** Telegram via @CubsBookKeeperBot

## Data Schema

```json
{
  "updatedAt": "ISO timestamp",
  "stats": {
    "revenueMTD": "$X,XXX",
    "outstandingBalance": "$X,XXX",
    "unpaidInvoices": "N",
    "leads": "N",
    "gstPayable": "$XXX"
  },
  "bella": {
    "model": "claude-opus-4-6",
    "contextUsage": "XX%",
    "sessions": 1,
    "memory": { "filesIndexed": N, "chunks": N, "cacheStatus": "warm|cold" },
    "lastHeartbeat": "HH:MM AM/PM AEDT"
  },
  "financial": {
    "recentTransactions": [{ "id", "client", "amount", "date", "type", "status" }],
    "monthlyData": [{ "month", "revenue", "expenses" }],
    "overdueAccounts": [{ "client", "amount", "daysOverdue", "lastContact", "status" }]
  },
  "calendar": {
    "today": [{ "title", "time", "location?", "type" }],
    "upcoming": [{ "title", "time", "location?", "type" }]
  },
  "crons": [{ "name", "enabled", "schedule": { "expr" }, "status" }],
  "liveTasks": [{ "label", "status" }],
  "patterns": [{ "description", "date" }],
  "activeSessions": { "main", "cronJobs", "lastActivity" },
  "social": { "lastPost?", "engagement?", "platform?" }
}
```

## Workflows

### 1. Update Dashboard Data (Every Heartbeat)
1. Gather latest metrics from Square API, Google Calendar, cron status
2. Update `~/Desktop/🦀/dashboard-data.json` with fresh data
3. Copy to `/Users/hafsahnuzhat/bella-dashboard/public/dashboard-data.json`
4. Run `python3 pre-push-check.py` to verify no secrets leaked
5. Git commit and push both repos

### 2. Key Leak Prevention
**CRITICAL:** dashboard-data.json must NEVER contain:
- API keys or tokens
- Passwords or secrets
- Full bank account numbers
- Personal phone numbers or emails
- Any value from ~/.clawdbot/.env

Only display-safe business metrics are allowed.

### 3. Deploy to Vercel
```bash
cd /Users/hafsahnuzhat/bella-dashboard
npm run build
# Push to GitHub — Vercel auto-deploys
git add -A && git commit -m "Dashboard sync" && git push
```

## Bundled Resources

### References
- `references/dashboard-layout.md`: Description of the v4 dashboard panels and components.
