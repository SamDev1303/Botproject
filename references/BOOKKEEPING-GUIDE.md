# 📒 Cleaning Business Bookkeeping Guide — Australia

> Comprehensive reference for running the financial side of a small cleaning business in Australia.
> Covers GST, BAS, NDIS invoicing, receipt tracking, tax deductions, and a recommended Google Sheets structure.

---

## Table of Contents

1. [Australian Tax Obligations](#1-australian-tax-obligations)
2. [BAS Reporting Schedule](#2-bas-reporting-schedule)
3. [GST Tracking — Collected & Paid](#3-gst-tracking--collected--paid)
4. [NDIS Invoicing & Record-Keeping](#4-ndis-invoicing--record-keeping)
5. [Receipt Categories for Tax Deductions](#5-receipt-categories-for-tax-deductions)
6. [Client Logging (CRM-Style)](#6-client-logging-crm-style)
7. [Recommended Google Sheets Structure](#7-recommended-google-sheets-structure)
8. [Bank Reconciliation Process](#8-bank-reconciliation-process)
9. [Key ATO Record-Keeping Rules](#9-key-ato-record-keeping-rules)
10. [Useful Links & References](#10-useful-links--references)

---

## 1. Australian Tax Obligations

### ABN (Australian Business Number)
- **Required** for any business operating in Australia.
- Apply free at [abr.gov.au](https://www.abr.gov.au/).
- Must appear on every invoice you issue.
- Without a valid ABN, clients must withhold 47% of payments (no-ABN withholding).

### GST (Goods and Services Tax)
- **Mandatory registration** once annual turnover reaches **$75,000** (or $150,000 for not-for-profit).
- You can voluntarily register below $75K (useful if you want to claim GST credits on purchases).
- GST rate: **10%** on taxable supplies.
- You must:
  - Charge GST on taxable sales
  - Issue tax invoices for sales of $82.50+ (GST-inclusive)
  - Lodge BAS returns (quarterly or monthly)
  - Keep records for **5 years**

### Income Tax
- Sole traders report business income in their personal tax return.
- Companies/trusts lodge separate returns.
- Due date: **31 October** (self-lodgers) or later if using a registered tax agent.

### Superannuation
- If you have employees, you must pay **11.5% super** (2024–25 rate) on ordinary time earnings.
- Super is due **quarterly**, within 28 days after the quarter ends.
- Sole traders can make voluntary contributions for themselves.

### PAYG Withholding
- Required if you have employees — withhold tax from their wages.
- Report via BAS (W1 and W2 labels).

### Taxable Payments Annual Report (TPAR)
- Cleaning businesses **must** lodge a TPAR if they pay contractors for cleaning services.
- Due: **28 August** each year (for the previous financial year).
- Reports payments made to contractors, including their ABN, amounts paid, and GST.

---

## 2. BAS Reporting Schedule

### Quarterly BAS Due Dates

| Quarter | Period | Due Date |
|---------|--------|----------|
| Q1 | July – September | **28 October** |
| Q2 | October – December | **28 February** |
| Q3 | January – March | **28 April** |
| Q4 | April – June | **28 July** |

> **Online lodgement bonus:** If you lodge online (not via an agent), you may get an extra 2 weeks for Q1, Q3 and Q4. Q2 already includes a 1-month extension.

### Monthly BAS
- Due on the **21st of the following month** (e.g., July BAS due 21 August).
- Required if GST turnover is **$20M+**, or if the ATO directs you to monthly reporting.
- You can choose monthly reporting voluntarily for better cash flow management.

### Annual GST Reporting
- Available if **voluntarily registered** and turnover is under $75,000.
- Due: **31 October** (or 28 February if no income tax return required).

### What Goes on Your BAS
| Label | What It Reports |
|-------|----------------|
| **1A** | GST on sales |
| **1B** | GST on purchases |
| **W1** | Total salary/wages paid |
| **W2** | PAYG withheld from wages |
| **T1** | PAYG income tax instalment |

### Simpler BAS
Most small businesses use **Simpler BAS** (default since 2017):
- Only report **G1** (Total sales), **1A** (GST on sales), and **1B** (GST on purchases).
- No need to break down BAS-exempt, GST-free, and input-taxed sales separately.

---

## 3. GST Tracking — Collected & Paid

### How GST Works for a Cleaning Business

**GST Collected (on sales):**
- You charge 10% GST on your cleaning services (if GST-registered).
- Example: $100 service → $110 invoice ($10 GST collected).

**GST Paid (on purchases):**
- You pay GST on business purchases (supplies, fuel, equipment).
- You claim these back as **GST credits** (input tax credits).
- Example: $55 cleaning supplies → $5 GST paid (claimable).

**BAS Payment:**
- GST owed to ATO = GST Collected − GST Paid.
- If GST paid > GST collected, you receive a **refund**.

### Formulas for Extracting GST

```
GST Amount = GST-Inclusive Price ÷ 11
Price ex-GST = GST-Inclusive Price ÷ 1.1
GST-Inclusive Price = Price ex-GST × 1.1
```

### What's GST-Free?
- Most **NDIS supports** (see Section 4).
- Exports of services.
- Some health/medical services.
- **Important:** Keep GST-free sales separate from taxable sales in your records.

---

## 4. NDIS Invoicing & Record-Keeping

### Overview
Cleaning services for NDIS participants fall under:
- **Support Category:** Core — Assistance with Daily Life
- **Line Item:** `01_020_0120_1_1` — House Cleaning And Other Household Activities
- This is a **price-limited** support — you cannot charge above the NDIS price maximum.

### GST Treatment of NDIS Services
NDIS supplies are **GST-free** if ALL of the following are met:
1. The participant has an **NDIS plan in effect**
2. The supply is of **reasonable and necessary supports** specified in their plan
3. There is a **written agreement** (service agreement) between you and the participant
4. The supply is covered by the **NDIS Determination** (household tasks are included in Table 1)

> **Key point:** If the service is GST-free, you do NOT charge GST on the invoice. But you can still claim GST credits on your business purchases.

### Required Invoice Information

Every NDIS invoice **must** include:

| Field | Details |
|-------|---------|
| **Your business name** | Trading name or legal entity name |
| **Your ABN** | Mandatory — invoice rejected without it |
| **Your contact details** | Phone, email |
| **Participant's full name** | As registered with NDIS |
| **Participant's NDIS number** | Their unique NDIS identifier |
| **Invoice date** | Date the invoice was issued |
| **Unique invoice number** | Sequential, non-repeating |
| **NDIS line item number** | e.g., `01_020_0120_1_1` |
| **Date(s) of service** | When cleaning was performed |
| **Hours/quantity** | Number of hours worked |
| **Hourly rate** | Must not exceed NDIS price limit |
| **Total amount** | Hours × rate |
| **GST amount** | Usually $0.00 (GST-free) or separated if applicable |
| **Bank details** | BSB, account number, account name |

### NDIS-Specific Rules

- **Submit invoices within 90 days** of service delivery. Late invoices risk rejection.
- If the NDIS plan period has ended and 90+ days have passed, the invoice **may not be payable**.
- **No advance payments** — NDIS only pays after service delivery.
- **Consumables** (cleaning products) must be built into your hourly rate. You cannot bill them separately.
- **Travel costs** can be invoiced separately IF agreed with the participant:
  - Provider Travel Time (labour)
  - Provider Travel - non-labour cost per km

### Records You Must Keep
- Signed service agreement (schedule, cost, quantity, type, quality of supports, location, expected outcomes)
- Copies of all invoices
- Evidence of service delivery (timesheets, sign-off sheets)
- Communication records with participants
- **Retain for 5 years minimum**

### Registered vs Unregistered Provider
| | Registered | Unregistered |
|---|---|---|
| **Can service** | All NDIS participants | Plan-managed & self-managed only |
| **Requirements** | NDIS Commission registration, audit, compliance | ABN, bank account, worker screening (recommended) |
| **Cost** | Expensive registration process | Minimal |
| **Most cleaners** | ❌ | ✅ Unregistered |

---

## 5. Receipt Categories for Tax Deductions

### 🚗 Vehicle & Travel
| Expense | Deductible? | Notes |
|---------|-------------|-------|
| Fuel | ✅ | Business portion only |
| Registration | ✅ | Business portion (logbook method) |
| Insurance (vehicle) | ✅ | Business portion |
| Servicing & repairs | ✅ | Business portion |
| Depreciation (vehicle) | ✅ | Logbook method only |
| Tolls & parking | ✅ | Business travel only |
| Car wash | ✅ | If business vehicle |

**Two methods for car expenses:**
1. **Cents per km:** 88c/km (2024–25), max 5,000 km/year. Simple, no receipts needed for costs (but keep a diary of trips).
2. **Logbook method:** Keep a logbook for 12 consecutive weeks → determine business-use %. Apply that % to ALL car costs. Valid for 5 years. Often results in higher deductions.

> ⚠️ Travel from home → first job and last job → home is **private** (not claimable). Travel between jobs IS claimable.

### 🧹 Cleaning Supplies & Consumables
| Expense | Category |
|---------|----------|
| Cleaning solutions, sprays, chemicals | Supplies |
| Microfibre cloths, sponges, wipes | Supplies |
| Mops, brooms, buckets | Supplies |
| Rubbish bags, paper towels | Supplies |
| Gloves, masks, PPE | Protective clothing |
| Disinfectants, sanitisers | Supplies |

> Items under $300: **immediate full deduction**.

### 🔧 Equipment & Tools
| Expense | Treatment |
|---------|-----------|
| Vacuum cleaner (under $300) | Immediate deduction |
| Vacuum cleaner ($300+) | Depreciate over effective life |
| Steam cleaner | Depreciate if $300+ |
| Pressure washer | Depreciate if $300+ |
| Floor polisher | Depreciate if $300+ |
| Ladder | Immediate if under $300 |
| Trolley/caddy | Immediate if under $300 |

> **Instant Asset Write-Off:** Check current thresholds — small businesses may be able to immediately deduct assets up to $20,000 (2024–25 threshold, subject to legislation).

### 👕 Clothing & Protective Gear
| Expense | Deductible? |
|---------|-------------|
| Branded/logo uniforms | ✅ |
| Non-slip shoes (safety) | ✅ |
| Gloves | ✅ |
| Safety glasses | ✅ |
| Face masks | ✅ |
| Aprons | ✅ |
| Plain everyday clothing | ❌ Not deductible |

### 🏢 Insurance
| Type | Deductible? |
|------|-------------|
| Public liability insurance | ✅ |
| Professional indemnity | ✅ |
| Workers compensation | ✅ |
| Business vehicle insurance | ✅ (business portion) |
| Income protection insurance | ✅ |
| Tool/equipment insurance | ✅ |

### 📱 Phone, Internet & Office
| Expense | Treatment |
|---------|-----------|
| Mobile phone (business use %) | ✅ Deductible portion |
| Internet (business use %) | ✅ Deductible portion |
| Computer/tablet | Depreciate or instant write-off |
| Software subscriptions | ✅ |
| Stationery, printing | ✅ |
| Accounting software (Xero, MYOB) | ✅ |

### 📚 Training & Licences
| Expense | Deductible? |
|---------|-------------|
| Cleaning certifications | ✅ |
| First aid training | ✅ |
| NDIS worker screening | ✅ |
| Police check | ✅ |
| Working with children check | ✅ |
| Industry memberships | ✅ |

### 🏠 Home Office (if applicable)
| Expense | Treatment |
|---------|-----------|
| Dedicated home office | Actual expenses or fixed rate (67c/hr) |
| Furniture (desk, chair) | Depreciate or instant write-off |

### 💰 Other Business Expenses
| Expense | Category |
|---------|----------|
| Bank fees (business account) | Admin |
| Merchant/payment processing fees | Admin |
| Advertising (Gumtree, Facebook, flyers) | Marketing |
| Business cards, signage | Marketing |
| Subcontractor payments | Labour |
| Uniforms/embroidery | Clothing |

---

## 6. Client Logging (CRM-Style)

### Why Track Clients?
- Know who owes you money
- Track cleaning schedules and preferences
- Manage NDIS vs private clients differently
- Build repeat business
- Have records for disputes/insurance claims

### Recommended Client Log Fields

| Column | Purpose | Example |
|--------|---------|---------|
| Client ID | Unique identifier | C001 |
| Client Name | Full name | Sarah Johnson |
| Client Type | Category | Private / NDIS / Commercial |
| NDIS Number | If NDIS client | 431 234 567 |
| Plan Manager | Who manages their NDIS plan | Self / Plan-managed / Agency |
| Plan Manager Contact | Email/phone of plan manager | rosy@planmgr.com.au |
| Address | Service location | 42 Smith St, Parramatta NSW |
| Phone | Contact number | 0412 345 678 |
| Email | Contact email | sarah@email.com |
| Service Type | What you do | Regular clean / Deep clean / End of lease |
| Frequency | How often | Weekly / Fortnightly / One-off |
| Preferred Day/Time | Scheduling | Tuesday 9am |
| Hourly Rate | Agreed rate | $45/hr |
| Est. Hours | Per visit | 3 hrs |
| Service Agreement | Signed? Date? | Yes — 15/01/2025 |
| NDIS Line Item | If applicable | 01_020_0120_1_1 |
| Special Instructions | Notes | Has a dog, use back door, no bleach |
| Key/Access | Access method | Lockbox #4532 |
| Status | Active/Inactive | Active |
| Date Added | When they became a client | 01/03/2025 |
| Last Service Date | Auto-updated | 10/02/2026 |
| Notes | Running notes | Referred by Maria. Likes lavender scent. |

### Tips
- **Colour-code by client type:** Private = blue, NDIS = green, Commercial = orange.
- **Sort by day** for a weekly cleaning schedule view.
- **Track cancellations** — note if a client frequently cancels (affects revenue forecasting).
- **Flag expiring NDIS plans** — plans are reviewed annually; set reminders 2 months before expiry.

---

## 7. Recommended Google Sheets Structure

### Master Workbook: "Cleaning Business Finance Tracker"

Create one Google Sheets workbook with the following tabs:

---

### Tab 1: 📊 Dashboard

**Purpose:** At-a-glance business health overview.

| Cell | Content | Formula/Source |
|------|---------|---------------|
| B2 | Total Revenue MTD | `=SUMIFS(Income!E:E, Income!B:B, ">="&DATE(YEAR(TODAY()),MONTH(TODAY()),1))` |
| B3 | Total Expenses MTD | `=SUMIFS(Expenses!E:E, Expenses!B:B, ">="&DATE(YEAR(TODAY()),MONTH(TODAY()),1))` |
| B4 | Net Profit MTD | `=B2-B3` |
| B5 | GST Collected MTD | `=SUMIFS(Income!F:F, Income!B:B, ">="&DATE(YEAR(TODAY()),MONTH(TODAY()),1))` |
| B6 | GST Paid MTD | `=SUMIFS(Expenses!F:F, Expenses!B:B, ">="&DATE(YEAR(TODAY()),MONTH(TODAY()),1))` |
| B7 | GST Owed to ATO | `=B5-B6` |
| B8 | Outstanding Invoices | `=COUNTIF(Income!H:H, "Unpaid")` |
| B9 | Outstanding Amount | `=SUMIFS(Income!E:E, Income!H:H, "Unpaid")` |
| B10 | Total Revenue YTD | `=SUMIFS(Income!E:E, Income!B:B, ">="&DATE(YEAR(TODAY()),7,1))` |
| B11 | Total Expenses YTD | `=SUMIFS(Expenses!E:E, Expenses!B:B, ">="&DATE(YEAR(TODAY()),7,1))` |

**Additional dashboard elements:**
- Monthly revenue chart (bar chart from Monthly Summary tab)
- Expense breakdown pie chart
- BAS quarter countdown (days until next BAS due)

---

### Tab 2: 💰 Income

**Purpose:** Record every dollar earned.

| Column | Header | Format | Notes |
|--------|--------|--------|-------|
| A | Invoice # | Text | INV-001, INV-002, etc. |
| B | Date | Date | Service date |
| C | Client Name | Text | Link to Client Log |
| D | Client Type | Dropdown | Private / NDIS / Commercial |
| E | Amount (ex-GST) | Currency | Service fee before GST |
| F | GST | Currency | `=IF(D2="NDIS", 0, E2*0.1)` |
| G | Total (inc-GST) | Currency | `=E2+F2` |
| H | Payment Status | Dropdown | Paid / Unpaid / Overdue |
| I | Date Paid | Date | When payment received |
| J | Payment Method | Dropdown | Bank Transfer / Cash / Card |
| K | NDIS Line Item | Text | `01_020_0120_1_1` if NDIS |
| L | Hours Worked | Number | For rate calculation |
| M | Hourly Rate | Currency | Agreed rate |
| N | Notes | Text | Any special notes |

**Key formulas:**
```
GST (auto-calculate):     =IF(D2="NDIS", 0, E2*0.1)
Total:                     =E2+F2
Overdue flag:              =IF(AND(H2="Unpaid", TODAY()-B2>30), "⚠️ OVERDUE", "")
```

**Data validation:**
- Column D: Dropdown list → Private, NDIS, Commercial
- Column H: Dropdown list → Paid, Unpaid, Overdue
- Column J: Dropdown list → Bank Transfer, Cash, Card, PayPal

---

### Tab 3: 💸 Expenses

**Purpose:** Record every business expense.

| Column | Header | Format | Notes |
|--------|--------|--------|-------|
| A | Date | Date | Purchase date |
| B | Description | Text | What was purchased |
| C | Category | Dropdown | See category list below |
| D | Supplier | Text | Where purchased |
| E | Amount (ex-GST) | Currency | Cost before GST |
| F | GST Paid | Currency | `=E2/10` (if GST applies) |
| G | Total (inc-GST) | Currency | `=E2+F2` |
| H | Payment Method | Dropdown | Card / Cash / Bank Transfer |
| I | Receipt? | Checkbox | ☑ if receipt saved |
| J | Receipt Ref | Text | Photo filename or folder ref |
| K | Tax Deductible | Dropdown | Yes / No / Partial |
| L | BAS Quarter | Auto | `=CHOOSE(ROUNDUP(MONTH(A2)/3,0),"Q1","Q2","Q3","Q4")` |
| M | Notes | Text | Additional details |

**Expense categories (for dropdown in Column C):**
- Cleaning Supplies
- Equipment (under $300)
- Equipment (over $300 — asset)
- Vehicle — Fuel
- Vehicle — Maintenance
- Vehicle — Registration
- Vehicle — Insurance
- Vehicle — Tolls/Parking
- Phone & Internet
- Insurance — Public Liability
- Insurance — Other
- Clothing & PPE
- Marketing & Advertising
- Software & Subscriptions
- Training & Licences
- Subcontractor Payments
- Bank Fees
- Office Supplies
- Home Office
- Other

---

### Tab 4: 👥 Client Log

**Purpose:** CRM-style client database.

Use the columns from [Section 6](#6-client-logging-crm-style) above.

**Conditional formatting suggestions:**
- NDIS clients → green row highlight
- Inactive clients → grey text
- Clients with no service in 30+ days → yellow highlight

---

### Tab 5: 🧾 BAS Tracker

**Purpose:** Prepare quarterly BAS figures.

| Column | Header |
|--------|--------|
| A | Quarter |
| B | Period |
| C | Total Sales (G1) |
| D | GST on Sales (1A) |
| E | GST on Purchases (1B) |
| F | GST Payable/Refund |
| G | PAYG Withheld (W2) |
| H | PAYG Instalment (T1) |
| I | Total Payable |
| J | Due Date |
| K | Lodged? |
| L | Date Lodged |
| M | Amount Paid |
| N | Date Paid |

**Formulas:**
```
GST on Sales (1A):        =SUMIFS(Income!F:F, Income!B:B, ">="&[quarter_start], Income!B:B, "<="&[quarter_end])
GST on Purchases (1B):    =SUMIFS(Expenses!F:F, Expenses!A:A, ">="&[quarter_start], Expenses!A:A, "<="&[quarter_end])
GST Payable:              =D2-E2
Total Payable:            =F2+G2+H2
```

---

### Tab 6: 🏦 Bank Reconciliation

**Purpose:** Match bank transactions to your records.

| Column | Header |
|--------|--------|
| A | Date |
| B | Description (from bank) |
| C | Amount |
| D | Type (Income/Expense) |
| E | Matched to Invoice/Expense # |
| F | Reconciled? (Checkbox) |
| G | Difference |
| H | Notes |

**Process:**
1. Download CSV from your bank monthly
2. Paste into this tab
3. Match each transaction to an entry in Income or Expenses tabs
4. Check off as reconciled
5. Investigate any unmatched transactions

**Running balance formula:**
```
=SUMIFS(C:C, D:D, "Income") - SUMIFS(C:C, D:D, "Expense")
```

---

### Tab 7: 📅 Monthly Summary

**Purpose:** Month-by-month P&L overview for the financial year.

| Row | Jul | Aug | Sep | Oct | Nov | Dec | Jan | Feb | Mar | Apr | May | Jun | **FY Total** |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-------------|
| **Revenue** | | | | | | | | | | | | | |
| Private Income | =SUMIFS(...) | | | | | | | | | | | | |
| NDIS Income | =SUMIFS(...) | | | | | | | | | | | | |
| Commercial Income | =SUMIFS(...) | | | | | | | | | | | | |
| **Total Revenue** | | | | | | | | | | | | | |
| **Expenses** | | | | | | | | | | | | | |
| Cleaning Supplies | =SUMIFS(...) | | | | | | | | | | | | |
| Vehicle Costs | =SUMIFS(...) | | | | | | | | | | | | |
| Insurance | =SUMIFS(...) | | | | | | | | | | | | |
| Equipment | =SUMIFS(...) | | | | | | | | | | | | |
| Marketing | =SUMIFS(...) | | | | | | | | | | | | |
| Other | =SUMIFS(...) | | | | | | | | | | | | |
| **Total Expenses** | | | | | | | | | | | | | |
| **Net Profit** | | | | | | | | | | | | | |
| **GST Collected** | | | | | | | | | | | | | |
| **GST Paid** | | | | | | | | | | | | | |
| **GST Owed** | | | | | | | | | | | | | |

**SUMIFS formula pattern:**
```
=SUMIFS(Income!E:E, Income!B:B, ">="&DATE(2025,7,1), Income!B:B, "<"&DATE(2025,8,1), Income!D:D, "Private")
```

---

### Tab 8: 📋 Mileage Log

**Purpose:** Track vehicle use for tax deductions.

| Column | Header |
|--------|--------|
| A | Date |
| B | From (address) |
| C | To (address) |
| D | Purpose |
| E | Client Name |
| F | Kilometres |
| G | Business/Private |
| H | Running Total (Business km) |

**Formulas:**
```
Running Total:  =SUMIFS(F:F, G:G, "Business")
Annual Claim (cents/km): =MIN(H_total, 5000) * 0.88
```

---

### Tab 9: 📦 Asset Register

**Purpose:** Track equipment over $300 for depreciation.

| Column | Header |
|--------|--------|
| A | Asset Name |
| B | Date Purchased |
| C | Purchase Price |
| D | Effective Life (years) |
| E | Depreciation Method |
| F | Annual Depreciation |
| G | Written Down Value |
| H | Business Use % |
| I | Claimable Amount |

**Common effective lives for cleaning equipment:**
| Asset | Effective Life |
|-------|---------------|
| Vacuum cleaner (commercial) | 5 years |
| Pressure washer | 5 years |
| Floor polisher | 10 years |
| Steam cleaner | 5 years |
| Vehicle | 8 years |
| Computer/tablet | 4 years |
| Mobile phone | 3 years |

---

## 8. Bank Reconciliation Process

### Weekly Reconciliation Routine (15 mins)

1. **Download** bank transactions (or connect via API/bank feed).
2. **Match** each transaction to an entry in your Income or Expenses tab.
3. **Flag** unmatched transactions — investigate (forgotten receipt? personal expense?).
4. **Update** payment status on Income tab (mark as "Paid").
5. **File** any receipts for new expenses.

### Monthly Close Process (30 mins)

1. Complete weekly reconciliation for the month.
2. Check **bank balance** matches your calculated balance.
3. Review **outstanding invoices** — follow up on unpaid.
4. Update **Monthly Summary** tab.
5. Save/backup the file.

### Quarterly BAS Prep (1–2 hours)

1. Ensure all transactions for the quarter are entered and reconciled.
2. Pull figures into **BAS Tracker** tab.
3. Verify GST collected and GST paid totals.
4. Lodge BAS via myGov or through your BAS agent.
5. Pay amount owed by due date.
6. Mark as lodged in tracker.

---

## 9. Key ATO Record-Keeping Rules

| Rule | Detail |
|------|--------|
| **Retention period** | 5 years from lodgement date |
| **Language** | English (or easily translatable) |
| **Format** | Paper or digital — both acceptable |
| **Tax invoices** | Required for all sales over $82.50 (inc GST) |
| **Digital records** | Must be accessible, backed up, and printable |
| **Separate accounts** | Keep business and personal finances separate |
| **Receipt capture** | Photograph/scan receipts immediately — thermal paper fades |

### What Records to Keep
- ✅ All invoices issued
- ✅ All receipts for purchases
- ✅ Bank statements
- ✅ BAS lodgement confirmations
- ✅ Employee/contractor payment records
- ✅ Service agreements (especially NDIS)
- ✅ Vehicle logbook
- ✅ Asset purchase records
- ✅ Insurance policies
- ✅ Tax returns and assessments

### Receipt Storage Tips
- Use a free app like **Google Drive**, **Dropbox**, or **HubDoc** to photograph and organise receipts.
- Name files consistently: `YYYY-MM-DD_Supplier_Amount.jpg`
  - Example: `2025-09-15_Bunnings_42.50.jpg`
- Create folders by month: `2025-07_July/`, `2025-08_August/`, etc.
- Back up to cloud storage — thermal receipts fade within months.

---

## 10. Useful Links & References

### ATO Resources
- [Simpler BAS GST Bookkeeping Guide](https://www.ato.gov.au/businesses-and-organisations/preparing-lodging-and-paying/business-activity-statements-bas/goods-and-services-tax-gst/simpler-bas-gst-bookkeeping-guide)
- [BAS Due Dates](https://www.ato.gov.au/businesses-and-organisations/preparing-lodging-and-paying/business-activity-statements-bas/due-dates-for-lodging-and-paying-your-bas)
- [Business Deductions](https://www.ato.gov.au/businesses-and-organisations/income-deductions-and-concessions/income-and-deductions-for-business/deductions)
- [Cleaner Tax Deductions](https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/tradies-be-certain-about-what-you-can-claim)
- [GST and NDIS](https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst/in-detail/your-industry/gst-and-health/national-disability-insurance-scheme)
- [Taxable Payments Annual Report (TPAR)](https://www.ato.gov.au/businesses-and-organisations/preparing-lodging-and-paying/reports-and-returns/taxable-payments-annual-report)

### NDIS Resources
- [NDIS Invoicing and Record Keeping](https://www.ndis.gov.au/providers/working-provider/getting-paid/invoicing-and-record-keeping)
- [NDIS Pricing Arrangements and Price Limits](https://www.ndis.gov.au/providers/pricing-arrangements)
- [NDIS Provider Registration](https://www.ndiscommission.gov.au/providers/registered-ndis-providers)

### Tax Deduction Guides
- [Baron Accounting — 7 Unmissable Tax Deductions for Cleaners](https://www.baronaccounting.com/post/7-unmissable-tax-deductions-for-cleaners-in-2025)
- [North Advisory — Cleaners Tax Deduction Guide](https://northadvisory.com.au/cleaners-tax-deduction-guide/)
- [eTax — Cleaner Tax Deductions](https://www.etax.com.au/cleaner-tax-deductions/)

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│  🧹 CLEANING BUSINESS BOOKKEEPING CHEAT SHEET       │
├─────────────────────────────────────────────────────┤
│  GST threshold:        $75,000/year                 │
│  GST rate:             10%                          │
│  GST formula:          Total ÷ 11 = GST amount     │
│  BAS quarters:         Q1: Jul-Sep → due 28 Oct    │
│                        Q2: Oct-Dec → due 28 Feb    │
│                        Q3: Jan-Mar → due 28 Apr    │
│                        Q4: Apr-Jun → due 28 Jul    │
│  Record retention:     5 years                      │
│  Tax invoice needed:   Sales over $82.50 inc GST   │
│  TPAR due:             28 August yearly             │
│  Super rate:           11.5% (2024-25)              │
│  NDIS line item:       01_020_0120_1_1              │
│  NDIS invoice window:  Within 90 days of service   │
│  NDIS GST:             Usually GST-FREE             │
│  Car claim (simple):   88c/km, max 5,000 km        │
│  Instant asset limit:  $20,000 (check current)     │
│  Home office rate:     67c/hour                     │
└─────────────────────────────────────────────────────┘
```

---

*Last updated: February 2026*
*Disclaimer: This guide is for general reference only. Consult a registered tax agent or BAS agent for advice specific to your situation.*
