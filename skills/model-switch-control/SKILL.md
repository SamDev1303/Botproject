---
name: model-switch-control
description: Switch OpenClaw/Clawdbot models safely with Codex GPT-5.3 as primary, Gemini 3 Flash Preview fallback, cooldown bypass, and model-change notifications. Use when asked to switch models, fix fallback routing, clear cooldown, or recover from rate limits.
---

# Model Switch Control

Use this skill for model routing operations only.

Use when:
- User asks to switch to Codex/Gemini/Opus/Sonnet.
- Primary/fallback chain drifted.
- OpenAI Codex profile is in cooldown.
- `All models failed` shows rate-limit or cooldown errors.

Do not use for:
- Generic coding tasks unrelated to model routing.

## Standard Routing

- Primary: `openai-codex/gpt-5.3-codex`
- Fallback: `google/gemini-3-flash-preview`
- Thinking target for maintenance jobs: `low`

## Commands

```bash
bash ~/Desktop/🦀/scripts/openclaw-model-switcher-pack.sh status
bash ~/Desktop/🦀/scripts/openclaw-model-switcher-pack.sh codex53
bash ~/Desktop/🦀/scripts/openclaw-model-switcher-pack.sh cooldown-bypass
bash ~/Desktop/🦀/scripts/check-model.sh
```

## Recovery Sequence

1. Run status command.
2. Run cooldown bypass.
3. Force `codex53`.
4. Run `check-model.sh`.
5. If output is `FIXED:` or `CHANGED:`, notify user with reason.

## Quick Scripts

- `scripts/set-codex53-primary.sh`
- `scripts/model-smoke-test.sh`
