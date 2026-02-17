---
name: pre-flight-validator
description: Mandatory validation layer used before finalizing any response. Use this skill to cross-reference Square for financial data, check clinical templates for shift notes, and verify API status before answering Hafsah.
---

# Pre-Flight Validator Skill

This skill acts as a mandatory validation layer. Before confirming any deployment, external update, or critical data retrieval to Hafsah, you MUST perform a "Live Check."

## Mandatory Workflow

### 1. Verification Step
Before saying "It's done" or "The link is live," you must:
- **Web Fetch/Browse:** Actually visit the URL you just generated or updated.
- **Status Check:** Verify the HTTP status code (200 OK) and confirm the content matches the expected update.
- **Data Validation:** If referencing financial or clinical data, cross-reference the source of truth (Square/Templates) one last time.

### 2. Failure Handling
If the verification fails (404, 500, or data mismatch):
- Do NOT tell Hafsah it is done.
- Diagnose the issue (e.g., GitHub Pages build time, API rate limit).
- Fix the issue or provide a transparent progress update with a "Retrying" status.

### 3. Confirmation Style
Only after a successful live verification should you provide the confirmation and the link.

## Implementation Pattern
When Hafsah asks "Is the dashboard updated?", the internal thought process should be:
1. Update `dashboard-data.json`.
2. Git push.
3. `web_fetch` the URL.
4. If fetch successful -> Reply "Dashboard is updated. Verified at [URL]."
