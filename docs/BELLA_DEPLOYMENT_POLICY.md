# Bella Deployment Policy

Last updated: 2026-02-19

## Canonical Ownership

- Human owner: Hafsah Nuzhat
- Bot operator: Bella Bot
- Shared project access: enabled

## Canonical Repositories

- `SamDev1303/Botproject` (workspace and automation core)
- `SamDev1303/pulse-dashboard` (only Bella dashboard repo)
- `SamDev1303/Claudeking.org` (website)

## Canonical Vercel Target

- Team: `opbrosautomations-projects`
- Bella dashboard project ID: `prj_pAWJfT0ZshiJUxggFSR5pd3gqwhD`

## Hard Rules

- Never hardcode API keys or tokens in tracked files.
- Keep deployment secrets in environment variables only.
- Verify targets before deploy with `scripts/verify-allowed-targets.sh`.
- Run secret scan before push with `python3 pre-push-check.py`.
- Every project update must include README notes with:
  - what changed,
  - who owns the project,
  - which repo and Vercel project are linked.

## Required Environment Variables (local only)

- `GITHUB_TOKEN`
- `VERCEL_TOKEN`
- `VERCEL_PROJECT_ID`
- `VERCEL_TEAM_ID` (team slug/ID)
