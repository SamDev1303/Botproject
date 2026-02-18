# OpenClaw Model Config Reference Pack

This pack is designed to be portable across OpenClaw/Clawdbot installs.

## Primary Model IDs

- Codex 5.3: `openai-codex/gpt-5.3-codex`
- Codex 5.2: `openai-codex/gpt-5.2-codex`
- Gemini 3 Flash Preview: `google/gemini-3-flash-preview`
- Claude Opus 4.6: `anthropic/claude-opus-4-6`
- Claude Opus 4.5: `anthropic/claude-opus-4-5`
- Claude Sonnet 4.6: `anthropic/claude-sonnet-4-6`

## Recommended Fallback Chains

- Codex 5.3 -> Gemini 3 Flash Preview
- Codex 5.2 -> Gemini 3 Flash Preview
- Gemini 3 Flash Preview -> Sonnet 4.6
- Opus 4.6 -> Opus 4.5
- Opus 4.5 -> Gemini 3 Flash Preview
- Sonnet 4.6 -> Gemini 3 Flash Preview

## Shareable Script

Use `scripts/openclaw-model-switcher-pack.sh`.

Examples:

```bash
bash scripts/openclaw-model-switcher-pack.sh status
bash scripts/openclaw-model-switcher-pack.sh codex53
bash scripts/openclaw-model-switcher-pack.sh codex52
bash scripts/openclaw-model-switcher-pack.sh gemini
bash scripts/openclaw-model-switcher-pack.sh opus46
bash scripts/openclaw-model-switcher-pack.sh opus45
bash scripts/openclaw-model-switcher-pack.sh sonnet46
bash scripts/openclaw-model-switcher-pack.sh cooldown-bypass
```

## Config JSON Reference

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openai-codex/gpt-5.3-codex",
        "fallbacks": ["google/gemini-3-flash-preview"]
      },
      "models": {
        "openai-codex/gpt-5.3-codex": { "alias": "codex53" },
        "openai-codex/gpt-5.2-codex": { "alias": "codex52" },
        "google/gemini-3-flash-preview": { "alias": "gemini" },
        "anthropic/claude-opus-4-6": { "alias": "opus46" },
        "anthropic/claude-opus-4-5": { "alias": "opus45" },
        "anthropic/claude-sonnet-4-6": { "alias": "sonnet46" }
      }
    }
  }
}
```

## Codex 5.3 Patch Behavior

If `codex53` is selected and registry support is missing, the script:

1. Attempts to patch `models.generated.js` to add `gpt-5.3-codex`.
2. Falls back to `openai-codex/gpt-5.2-codex` if patch is unavailable.

## Cooldown Bypass

`cooldown-bypass` resets `usageStats` in discovered `auth-profiles.json` files by:

- setting `cooldownUntil` to `0`
- setting `errorCount` to `0`
- clearing `failureCounts`
- removing `lastFailureAt`

This does not create provider credentials; it only clears local cooldown/error counters.

