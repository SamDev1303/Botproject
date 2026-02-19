---
name: codex-opencli-update-watch
description: Track and apply latest Codex/OpenAI CLI and OpenClaw API/config updates using official documentation and release sources, then validate local compatibility.
---

# Codex OpenCLI Update Watch

Use when:
- User asks for latest Codex CLI/OpenClaw updates.
- Need to validate model IDs, config keys, and routing behavior after updates.
- Need to refresh local upgrade notes from official sources.

## Official Sources (required)

- OpenAI Codex docs (`developers.openai.com/codex/*`)
- OpenClaw official GitHub releases
- OpenClaw docs (`docs.clawd.bot`)

Read: `references/sources-2026-02-19.md`

## Local Compatibility Checks

```bash
clawdbot --version
clawdbot config --help
clawdbot models --help
bash ~/Desktop/🦀/scripts/openclaw-model-switcher-pack.sh status
```

## Update Workflow

1. Pull latest official release/doc notes.
2. Compare current local version and commands.
3. Patch local scripts/config only where required.
4. Re-run model + embedding checks.
5. Report exact version/date and what changed.

## Quick Script

- `scripts/check-local-opencli-compat.sh`
