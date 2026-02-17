# Google Sheets Consolidation Report

**Account:** cleanupbros.au@gmail.com  
**Date:** 2026-02-17  
**Total Sheets Found:** 14

---

## 📋 Complete Inventory

| # | Sheet Name | ID | Tabs | Rows (approx) | Category |
|---|-----------|-----|------|---------------|----------|
| 1 | **Clean Up Bros - Master Operations Log** | `1sZOaf57...BGCU` | Client Log, Bookkeeping, Task Log, Accounts | Headers only → now 8 rows in Client Log | ✅ KEEP (Master) |
| 2 | **Clean Up Bros - Finance Backup** | `1pocJwoO...n-00Q` | square | Square data backup | ✅ KEEP |
| 3 | **cleanupbros accounts** | `1Yd87dTo...ElYM` | 2026, Expenses, Staff Wages, Profit & Loss, Outstanding, Archive 2025 | ~10 rows across tabs | ⚠️ REVIEW — client data merged |
| 4 | **Untitled spreadsheet** | `1ysURF07...SJnHU` | Sheet1, Sheet2 | Competitor pricing research | 🗑️ DELETE or rename |
| 5 | **🇦🇺1616 MASTER APOLLO ✅** | `1RWhp2Gh...7QXQ` | URGENT 🔥 (82), HIGH 🚨 (616), MEDIUM ☎️ (636), LOW 😒 (256), MEH 😑 (29) | 1,619 total leads | ⚠️ KEEP as Lead DB |
| 6 | **CUBS-OUTBOUND AGENT LOG** | `1yb7s_Us...y2z0` | Sheet1 | Empty | 🗑️ DELETE |
| 7 | **OPBROS LOG SHEET** | `1CFjuhEj...s5RI` | SUCCESS, ERROR, DIRECTIVES, TOKEN USAGES | All empty | 🗑️ DELETE |
| 8 | **CUB Financial Tracker 2024–25** | `1L0wSzIa...jG9g` | 📄 INVOICES.csv, 💸 EXPENSES.csv, ✅ PAYMENTS_RECEIVED.csv, ❌ PAYMENTS_MISSED.csv, 📑 CONTRACTS.csv, 🧾 GST_SUMMARY.csv, 📊 TAX_DASHBOARD.csv | Headers only (all empty) | 🗑️ DELETE |
| 9 | **EXPENSES** | `1waU46cF...y190` | EXPENSES | Headers only (empty) | 🗑️ DELETE |
| 10 | **ugc_run** | `1poJ5hzV...ERBY` | ugc_runs | UGC automation logs, not client data | 🗑️ DELETE |
| 11 | **1616 master copy_md** | `1bICEfE9...n_cM` | 1616 MASTER 💵 | 1,615 rows — duplicate of #5 | 🗑️ DELETE (duplicate) |
| 12 | **TEST** | `1OyAW2Bt...BFew` | TEST DATA FOR APP | 13 rows — test lead data | 🗑️ DELETE |
| 13 | **68 TOP LEADS INSTANTLY 💯** | `1PdyK4_F...3Lw0` | 68 RAW LEADS (69), Sheet5 (13), Sheet4 (51), 37 VERIFIED EMAILS (37), 37 FULL ENRICHED PROFILES (1) | ~170 rows | ⚠️ KEEP as Lead DB |
| 14 | **400 STRATA AND CHILDCARE** | `1Oxv5agg...NCmI` | APPOLO SHEET RAW DATA | 401 rows | ⚠️ KEEP as Lead DB |

---

## ✅ Data Merged into Master Client Log

**7 rows appended** to `Client Log` tab of Master Operations Log:

| Client Name | Invoice # | Amount | Status | Source |
|------------|-----------|--------|--------|--------|
| Shayan Chand | #000004 | $160.00 | Paid | 2026 tab |
| Claudia Alz | #000011 | $160.00 | Overdue | Outstanding tab |
| Herdip Gill | #000010 | $290.00 | Overdue | Outstanding tab |
| Herdip Gill | #000009 | $145.00 | Overdue | Outstanding tab |
| Herdip Gill | #000008 | $435.00 | Overdue | Outstanding tab |
| Herdip Gill | #000007 | $290.00 | Overdue | Outstanding tab |
| Meshach Ephraim Care | #000005 | $5,000.00 | Partially Paid | Outstanding tab |

**Source sheet:** `cleanupbros accounts` (ID: `1Yd87dToNUGbyF7Olo1mXFOtwYxc375Ts7YFOOFXElYM`)

---

## 🗑️ Recommended for Deletion (8 sheets)

These sheets are either empty, duplicated, or no longer needed:

1. **CUBS-OUTBOUND AGENT LOG** — completely empty
2. **OPBROS LOG SHEET** — all tabs empty (was for bot logging)
3. **CUB Financial Tracker 2024–25** — all tabs have headers only, never populated
4. **EXPENSES** — headers only, never populated
5. **ugc_run** — UGC automation test data, not business-critical
6. **1616 master copy_md** — exact duplicate of "🇦🇺1616 MASTER APOLLO ✅" (same 1,615 leads)
7. **TEST** — 13 rows of test lead data, subset of other lead sheets
8. **Untitled spreadsheet** — competitor pricing research (2 rows), rename or archive

---

## ⚠️ Sheets to KEEP but NOT in Master Log

These contain **lead/prospect data** (not clients yet) and should stay separate:

### 🇦🇺1616 MASTER APOLLO ✅ (1,619 leads)
- Apollo-sourced B2B leads with priority scoring
- Columns: Priority, Name, Title, Email, Phone, Company, Industry, Revenue, Location, Scores
- **5 priority tiers:** URGENT (82), HIGH (616), MEDIUM (636), LOW (256), MEH (29)
- ❌ NOT merged — these are prospects, not clients. Different schema.

### 68 TOP LEADS INSTANTLY 💯 (~170 leads)
- Instantly-sourced leads with verification status
- Includes enriched profiles and verified emails
- ❌ NOT merged — prospect/outbound data, not client records

### 400 STRATA AND CHILDCARE (401 leads)
- Apollo-sourced strata managers and childcare contacts
- Columns: Name, Title, Email, Phone, Company, Industry, Location
- ❌ NOT merged — raw prospect list, not clients

### cleanupbros accounts
- Contains **financial records** (2026 income, expenses, wages, P&L)
- Outstanding invoices have been merged to Client Log
- **Recommend:** Keep as financial archive, reference from Master Sheet's Bookkeeping tab

---

## 📊 Summary

| Action | Count |
|--------|-------|
| Sheets found | 14 |
| Sheets to KEEP | 2 (Master + Finance Backup) |
| Sheets to KEEP (leads) | 3 (Apollo, 68 Top Leads, 400 Strata) |
| Sheets to KEEP (financial) | 1 (cleanupbros accounts) |
| Sheets to DELETE | 8 |
| Client rows merged | 7 |
| Total outstanding from merged data | $6,320.00 |

---

## 🔗 Quick Links

- **Master Sheet:** https://docs.google.com/spreadsheets/d/1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU
- **Finance Backup:** https://docs.google.com/spreadsheets/d/1pocJwoOO3emKfQf9mzFHuahZ5nA7KSrehF9fBqn-00Q
- **Lead DB (Apollo):** https://docs.google.com/spreadsheets/d/1RWhp2GhJgSDQ0LaM7R0uj0xBuxGu_UT_dbk43TM7QXQ
