---
name: model-switch-control
description: "Switch Bella's AI model. Triggered by /model command or when asked to switch models, fix fallback routing, clear cooldown, or recover from rate limits. Supports: sonnet, opus, gemini, codex."
user-invocable: true
argument-hint: "/model sonnet, /model opus, /model gemini, /model codex, /model status"
---

# Model Switch Control

## /model Command

When Hafsah says `/model <name>`, run:

```bash
bash ~/Desktop/🦀/scripts/model-switch.sh <name>
```

### Available Models

| Command | Primary Model | Fallback 1 | Fallback 2 |
|---------|--------------|------------|------------|
| `/model sonnet` | Claude Sonnet 4.6 | Gemini 3 Flash | Codex GPT-5.3 |
| `/model opus` | Claude Opus 4.6 | Sonnet 4.6 | Gemini 3 Flash |
| `/model gemini` | Gemini 3 Flash | Sonnet 4.6 | Codex GPT-5.3 |
| `/model codex` | Codex GPT-5.3 | Sonnet 4.6 | Gemini 3 Flash |
| `/model status` | Show current model + token health | | |

### Default Routing (Standard)

- Primary: `anthropic/claude-sonnet-4-6`
- Fallback 1: `google/gemini-3-flash-preview`
- Fallback 2: `openai-codex/gpt-5.3-codex`

### Gemini Budget Rule

Gemini runs on a FREE TIER key. Never use it as primary for heavy workloads. Conserve quota.

### Recovery Sequence (When All Models Fail)

1. `bash ~/Desktop/🦀/scripts/model-switch.sh status` — check what's broken
2. `bash ~/Desktop/🦀/scripts/openclaw-model-switcher-pack.sh cooldown-bypass` — clear cooldowns
3. `bash ~/Desktop/🦀/scripts/model-switch.sh sonnet` — reset to default
4. `bash ~/Desktop/🦀/scripts/auto-failover.sh` — test all models and pick first working one

### Auto-Failover

If the current model fails, run:

```bash
bash ~/Desktop/🦀/scripts/auto-failover.sh
```

This tests each model in order and switches to the first one that responds.

### Token Health Check

```bash
bash ~/Desktop/🦀/scripts/token-refresh.sh status
```

Shows expiry time for all provider tokens (Anthropic, OpenAI, Gemini).
