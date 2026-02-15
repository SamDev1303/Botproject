---
name: client-onboarding
description: Systematic process for commercial cleaning client research, lead enrichment, and outreach preparation. Use when starting work with a new commercial lead or when asked to research specific business targets for Clean Up Bros. Triggers on keywords like "deep dive", "research client", "prepare quote", or "outreach plan".
---

# Client Onboarding Skill

This skill automates the deep-dive research and professional outreach preparation for new commercial cleaning leads.

## Workflow

### 1. Deep-Dive Research
Use web search to identify:
- **Pain Points:** Search specifically for Google/Yelp/Uber Eats reviews mentioning "dirty", "cleanliness", "sticky", "dusty", or "understaffed".
- **Decision Makers:** Identify local owners, franchise partners, or practice managers.
- **Operating Context:** Operating hours (especially early starts or closed days), size of premises, and specific equipment (e.g., BBQ grills, medical OCT scanners).

### 2. Strategy Development
Categorize the lead based on urgency:
- **Priority 1 (Urgent):** Negative cleanliness reviews found. Focus on "Revenue Protection".
- **Priority 2 (Warm):** Previous contact made or referred. Focus on "Trust & Continuity".
- **Priority 3 (General):** Cold outreach. Focus on "Specialisation & Efficiency".

### 3. Output Generation
For every lead, generate the following in the `~/Desktop/"New commercial clients Quotes"` directory:
- **Sub-folder:** `[Client Name]`
- **Strategy Document:** `[Client]_Strategy.md` (Pain points, solution, pricing).
- **Outreach Drafts:** `[Client]_Outreach.md` (Customized email and SMS).

## Resources to Reference
- **Experience:** 4 years total, 2 years commercial.
- **Key Clients:** Kogarah Cancer Treatment Centre, Ramsgate Beach House, IGA Sutherland/Greenfield.
- **Standard Offer:** 25% off current cleaning invoice for new partners.

## Tool Integration
When performing a deep dive, use the following pattern:
1. `browser` action="open" targetUrl="https://www.google.com/search?q=[Client Name] [Location] reviews"
2. Use `browser` to navigate and scrape specific review sites or business directories for deep research.
3. Fallback to `web_search` only if browser access is restricted.
