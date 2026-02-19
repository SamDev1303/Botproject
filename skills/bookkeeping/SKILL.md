---
name: bookkeeping
description: Australian bookkeeping — GST calculations (÷11), BAS preparation, expense categorization (ATO-compliant), P&L generation, staff wages with 11.5% super. Use when the user asks about GST, BAS, expenses, profit & loss, payroll, superannuation, or any Australian tax/accounting task.
---

# Bookkeeping

Australian bookkeeping for Clean Up Bros, ATO-compliant.

## Prerequisites

- **Google Sheets access** via `google-workspace` skill
- **Master Ops Sheet**: `1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU` (Bookkeeping tab)
- **Square data** via `square-finance` or `square-sync` skills for revenue figures

## Core Formulas

### GST Calculation (Australian method)

```
GST Amount = Total Price ÷ 11
Net Amount = Total Price - GST Amount
```

Example: Invoice $550 → GST = $50, Net = $500

### Superannuation (2025-26 rate: 11.5%)

```
Super = Gross Wages × 0.115
Total Cost = Gross Wages + Super
```

Example: Staff paid $1,000 gross → Super = $115 → Total cost = $1,115

### Hourly Rate Calculation

```
Hourly Cost = Hourly Rate × (1 + 0.115)  # Including super
```

## Workflows

### 0. Instant Expense Capture (Receipts)

When Hafsah says "this is my expense" or sends a receipt, immediately log it with:

```bash
python3 scripts/add-expense-entry.py \
  --description "Receipt description" \
  --amount 55.00 \
  --category "Cleaning Supplies" \
  --payment-method "Card" \
  --supplier "Bunnings" \
  --notes "Receipt upload"
```

This writes to:
- `Expenses!A:J`
- `Bookkeeping!A:K`

in the canonical Master Ops sheet (`1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU`).

### 1. Categorize Expenses (ATO-Compliant)

Use these standard categories for Clean Up Bros:

| Category | ATO Code | Examples |
|----------|----------|---------|
| Cleaning Supplies | D5 | Chemicals, cloths, mops, bins |
| Equipment | D5 | Vacuum, pressure washer, carpet cleaner |
| Vehicle/Transport | D1 | Fuel, rego, insurance, tolls |
| Staff Wages | W1 | Hourly pay, overtime |
| Superannuation | W2 | 11.5% of gross wages |
| Insurance | D12 | Public liability, workers comp |
| Phone/Internet | D4 | Business phone, data plans |
| Marketing/Ads | D16 | Google Ads, Facebook Ads, flyers |
| Software/Subscriptions | D5 | Connecteam, Square fees |
| Uniforms | D5 | Staff shirts, PPE, gloves |
| Rent/Storage | D13 | Equipment storage |
| Bank Fees | D5 | Square processing fees (1.6%) |

### 2. BAS Preparation (Quarterly)

Collect for the quarter:

1. **Total Sales (G1)**: Sum all invoices (inc. GST)
2. **GST on Sales (1A)**: Total Sales ÷ 11
3. **Total Purchases (G11)**: Sum all business expenses (inc. GST)
4. **GST on Purchases (1B)**: Total Purchases ÷ 11
5. **GST Payable**: 1A − 1B (positive = owe ATO, negative = refund)
6. **Total Wages (W1)**: Gross wages paid in quarter
7. **PAYG Withheld (W2)**: Tax withheld from staff pay

```
BAS Quarter Dates:
Q1: Jul 1 – Sep 30  (due Oct 28)
Q2: Oct 1 – Dec 31  (due Feb 28)
Q3: Jan 1 – Mar 31  (due Apr 28)
Q4: Apr 1 – Jun 30  (due Jul 28)
```

### 3. Generate P&L

```
REVENUE
  Cleaning Services Income     $XX,XXX
  Less: GST Collected          ($X,XXX)
  Net Revenue                  $XX,XXX

EXPENSES
  Staff Wages                  $X,XXX
  Superannuation               $X,XXX
  Cleaning Supplies            $X,XXX
  Vehicle/Transport            $X,XXX
  Insurance                    $X,XXX
  Marketing                    $X,XXX
  Software/Subscriptions       $X,XXX
  Bank/Processing Fees         $X,XXX
  Other Expenses               $X,XXX
  Total Expenses               $XX,XXX

NET PROFIT (LOSS)              $X,XXX
```

### 4. Record to Master Ops Sheet

Append new entries to the Bookkeeping tab:

```
| Date | Description | Category | Amount (inc GST) | GST | Net | Type |
```

Use `google-workspace` skill to append rows:
```bash
gog sheets append 1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU "Bookkeeping!A:G" \
  --values-json '[["2026-02-10","Cleaning supplies - Bunnings","Cleaning Supplies","$55.00","$5.00","$50.00","Expense"]]' \
  --input USER_ENTERED
```

### 5. Staff Payroll Summary

For each staff member per pay period:

```
Name | Hours | Rate | Gross | Super (11.5%) | PAYG | Net Pay | Total Cost
```

## Square Fee Tracking

Square charges 1.6% per transaction. Track as Bank Fees:
```
Square Fee = Transaction Amount × 0.016
```

## Important Notes

- Australian financial year: July 1 – June 30
- All prices assumed GST-inclusive unless stated otherwise
- ABN required on all invoices
- Keep records for 5 years (ATO requirement)
- Lodge BAS quarterly via myGov or tax agent

## References

- ATO BAS guide: https://www.ato.gov.au/businesses-and-organisations/preparing-lodging-and-paying/business-activity-statements-bas
- Super guarantee rate: https://www.ato.gov.au/tax-rates-and-codes/super-guarantee-percentage
- Master Ops Sheet: `1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU`
