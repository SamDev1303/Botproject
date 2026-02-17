## 🗺️ WORKSPACE MAP

### 👥 NPCs & Entities
*   **Path:** `memory/entities/`
*   **Clients:** `memory/entities/clients/` (Individual .md files per client like `meshach-ephraim-care.md`)
*   **Staff:** `memory/entities/contractors/`
*   **Arieta (Privacy Rule):** Never listed as staff; documented only as **Donation** in bookkeeping.

### 🔑 APIs & Accounts
*   **Status/Log:** Master Ops Sheet → **Accounts** tab
*   **Secrets:** Managed via `~/.clawdbot/config.json` and `op` (1Password CLI)
*   **Reference:** `docs/api_keys_reference.md`

### 🐍 Python Scripts
*   **Global Utilities:** `scripts/` (Square API, Sheets API, OAuth, Memory sync)
*   **Skill-Specific:** `skills/<name>/scripts/` (Connecteam roster scripts, Meta Posting, Kie AI generation)

### 🎭 Skills Registry
*   **Location:** `skills/`
*   **Business:** `clean-up-bros-ops`, `square-sync`, `connecteam-roster`
*   **Marketing:** `social-content-poster`, `viral-ads-creator`
*   **Verification:** `pre-flight-validator`, `secret-guard`

### 🧠 Continuity & Memory
*   **Persona:** `SOUL.md` (Who I am and my hard rules)
*   **Long-term:** `MEMORY.md` (Stable business facts and preferences)
*   **Daily Experience:** `memory/YYYY-MM-DD.md` (Raw journal of what happened)
*   **Architecture:** `docs/MEMORY_ARCHITECTURE.md`
