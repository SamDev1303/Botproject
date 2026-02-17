# SKILL: Connecteam Overhaul for Clean Up Bros

## Purpose
Complete overhaul of the Connecteam app for Clean Up Bros cleaning business. Covers branding, forms, staff bios, navigation cleanup, and badge/ID creation.

## Critical Rules

### 1. ONE TAB ONLY
- Close ALL redundant Connecteam tabs immediately on start.
- Work in a single `clawd` profile tab throughout.
- Never open a second tab to the same domain.

### 2. Navigation via URL (NOT sidebar clicks)
Connecteam's sidebar elements are inside a complex SPA that breaks ref-based clicking.
**ALWAYS navigate by URL hash** instead of trying to click sidebar items:

| Section | URL |
|---------|-----|
| Dashboard | `https://app.connecteam.com/#/index/dashboard/dashboard` |
| Forms | `https://app.connecteam.com/#/index/forms` |
| Schedule | `https://app.connecteam.com/#/index/scheduler` |
| Time Clock | `https://app.connecteam.com/#/index/timeclock` |
| Users | `https://app.connecteam.com/#/index/users` |
| Directory | `https://app.connecteam.com/#/index/directory` |
| Chat | `https://app.connecteam.com/#/index/chat` |
| Updates | `https://app.connecteam.com/#/index/updates` |
| Knowledge Base | `https://app.connecteam.com/#/index/knowledgebase` |
| Courses | `https://app.connecteam.com/#/index/courses` |
| Documents | `https://app.connecteam.com/#/index/documents` |
| Quick Tasks | `https://app.connecteam.com/#/index/quicktasks` |
| Settings | `https://app.connecteam.com/#/index/settings` |

**Use `browser navigate` action** to move between sections. Example:
```
browser action=navigate targetId=<id> profile=clawd url="https://app.connecteam.com/#/index/forms"
```

### 3. Dismiss Tooltips/Walkthrough First
Before interacting with any page, dismiss any walkthrough tooltip by clicking "Skip" buttons. These overlays block other elements.

### 4. Snapshot Before Every Action
Always take a fresh snapshot immediately before clicking. Refs go stale fast in this SPA.

## Task Checklist

### Phase 1: Navigation Cleanup (Delete unnecessary sidebar features)
**KEEP** (essential for cleaning business):
- Dashboard/Overview
- Time Clock
- Forms (checklists)
- Schedule
- Chat
- Users
- Directory
- Documents
- Quick Tasks

**REMOVE** (not needed):
- Events
- Knowledge Base
- Help Desk
- Text Messages
- Surveys
- Updates
- Rewards
- Recognitions
- Celebrations
- Time Off
- Courses

To remove: Go to each feature's settings or use the sidebar "..." menu to hide/delete.

### Phase 2: Forms Review & Finalize
Four forms to review and finalize:
1. **End of Lease Checklist** — Comprehensive bond-back cleaning
2. **Deep Clean Checklist** — Intensive deep cleaning
3. **General Clean Checklist** — Standard weekly/fortnightly
4. **Airbnb Turnover Checklist** — Quick turnaround for short-stay

For each form:
- Navigate to Forms section via URL
- Open each form
- Review all fields/sections
- Ensure consistent branding (Clean Up Bros header)
- Ensure photo upload fields exist for before/after
- Ensure client signature field exists
- Ensure time tracking fields exist
- Publish if in draft

### Phase 3: Staff Bios
- Navigate to Users/Directory
- Update each staff member's profile:
  - Professional bio (2-3 sentences)
  - Consistent job title format
  - Profile photo if missing
- Staff: Hafsah Nuzhat (Owner), Shamal Krishna, Arieta Cinavilakeba, others

### Phase 4: Logo/Badge Creation
- Use Nano Banana or similar tool to create Clean Up Bros logo
- Style reference: cleanupbros.com.au
- Create staff ID badges with:
  - New logo
  - Staff name
  - Role/title
  - Employee ID number
  - Clean Up Bros branding colors

### Phase 5: Dashboard Data Update
After each phase, update `dashboard-data.json` with:
- Task completion status
- Timestamp
- Any issues encountered

## Troubleshooting

### Element not found/not visible
→ The SPA re-renders aggressively. Always re-snapshot.
→ Use URL navigation instead of clicking sidebar.

### Tooltip blocking
→ Look for "Skip" or "×" buttons in the snapshot.
→ Click those first before proceeding.

### Walkthrough popup
→ Dismiss immediately — it overlays the entire sidebar.
