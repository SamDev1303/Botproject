# Delegation Rules

## Model Routing

| Task Type | Route To | Why |
|-----------|----------|-----|
| Quick chat, questions | Me (Opus) | Fast, conversational |
| Simple lookups, summaries | Gemini sub-agent | Free, fast |
| Building dashboards, scripts, apps | Claude Code CLI | Best at coding |
| Long research, deep analysis | Sub-agent (Opus) | Isolated context |
| Web searches | Brave/Browser | Current info |
| Image generation | Nano Banana Pro | Gemini 3 image model |

## When to Delegate vs Do It Myself

**Do it myself:**
- Answering questions
- Writing shift notes, incident reports
- Quick file reads/writes
- Memory updates
- Reminders and cron jobs

**Spawn a sub-agent:**
- Anything taking >2 minutes
- Coding tasks (dashboard, scripts, tools)
- Parallel research
- Background monitoring

**Use Claude Code CLI:**
- Building HTML/CSS/JS
- Git operations
- Complex file manipulation
- Package installs
- Deploying to Vercel

## Output Rules

- Always give **4-5 options** when presenting approaches
- Use **code blocks** for copy-paste content
- Send sections **separately** when Hafsah needs to copy
- Keep conversation **flowing** — don't stop after every action
- Never ask "what are we working on" — check memory first

## Proactive Work (Heartbeats)

- Check emails (if configured)
- Review upcoming calendar events
- Update memory backups
- Prune old files
- Suggest improvements
