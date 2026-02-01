# Bella's Convex Memory Database

Real-time database for persistent memory management using Convex.

## What is this?

Convex provides a real-time, serverless database that:
- **Automatically syncs** across all instances of Bella
- **Persists memory** beyond local file storage
- **Enables querying** of historical data (clients, invoices, sessions)
- **Free tier** is generous for small businesses
- **Real-time updates** - changes sync instantly

## Setup

### 1. Install Dependencies

```bash
cd ~/Desktop/🦀/convex
npm install
```

### 2. Initialize Convex Project

```bash
npx convex dev --once --configure=new
```

This will:
- Open browser to create/login to Convex account
- Create a new project (name it "bella-memory" or similar)
- Generate deployment keys

### 3. Get Your Deployment URL

After initialization, you'll see output like:

```
✓ Deployment URL: https://happy-animal-123.convex.cloud
```

### 4. Update Environment Variables

Add to `~/.clawdbot/.env`:

```bash
CONVEX_DEPLOY_KEY=eyJ2MiI6IjNmMTcyOTEzNTk5MzRmYzBhNGU4NzFlZWRhNjExODI0In0=
CONVEX_TEAM_ID=404082
CONVEX_URL=https://happy-animal-123.convex.cloud  # YOUR deployment URL
```

### 5. Start Convex Dev Server

```bash
cd ~/Desktop/🦀/convex
npx convex dev
```

Keep this running in a terminal. It watches for changes and syncs your schema/functions.

### 6. Deploy to Production (Optional)

```bash
npx convex deploy
```

## Schema

The database stores 5 entity types:

### 1. **Clients**
- Client profiles with payment history
- Searchable by status (active, overdue, blacklist)
- Tracks amount owed, payment rating, total spent

### 2. **Invoices**
- Invoice records linked to clients
- Status tracking (unpaid, paid, overdue)
- Indexed by due date for reminders

### 3. **Sessions**
- Daily session summaries
- Tasks completed, decisions made
- Financial summary and client interactions

### 4. **Tasks**
- Reminders and to-do items
- Priority and status tracking
- Linked to clients/invoices

### 5. **Memory Chunks**
- For large data that needs chunking
- Linked to parent entities
- Summaries for quick retrieval

## Usage Examples

### Store a Client

```python
# Via MCP
convex_sync_client('claudia-alz', {
    'name': 'Claudia Alz',
    'email': 'claudia@example.com',
    'amount_owed': 320.00,
    'days_overdue': 45,
    'status': 'overdue'
})
```

### Get Overdue Clients

```python
# Via MCP
convex_get_all_overdue_clients()
```

### Store Session Summary

```python
# Via MCP
convex_sync_session('2026-02-02', {
    'tasks_completed': [
        'Applied logging to MCP servers',
        'Created Convex database'
    ],
    'outstanding_items': [
        'Follow up with Claudia Alz - $320 overdue'
    ],
    'financial_summary': 'Total overdue: $2,070'
})
```

## Dashboard

View your data at: https://dashboard.convex.dev

- Browse all tables
- Run queries
- View real-time updates
- Check deployment logs

## Benefits for Bella

1. **Persistent Memory**: Data survives bot restarts, system crashes
2. **Cross-Device Sync**: Use Bella from multiple devices with shared memory
3. **Historical Queries**: "What clients were overdue last month?"
4. **Real-Time Updates**: Changes sync instantly across all sessions
5. **Backup**: Convex handles backups automatically
6. **Scalable**: Free tier handles thousands of records

## Cost

**Free Tier:**
- 1M function calls/month
- 1 GB storage
- Real-time subscriptions
- Automatic backups

**More than enough for Clean Up Bros!**

## Troubleshooting

### "Deployment URL not configured"

1. Check `~/.clawdbot/.env` has `CONVEX_URL=...`
2. Restart Bella after adding the variable

### "Authentication failed"

1. Check `CONVEX_DEPLOY_KEY` is correct
2. Run `npx convex dev` to re-authenticate

### "Schema mismatch"

1. Make sure Convex dev server is running
2. It automatically syncs schema changes

## Next Steps

1. **Integrate with OpenRouter** for automatic summarization of large data
2. **Auto-sync** client entities after Square payments
3. **Real-time dashboard** for Hafsah to view all data
4. **Automated backups** to Google Drive

---

**Created:** 2026-02-02
**Last Updated:** 2026-02-02
