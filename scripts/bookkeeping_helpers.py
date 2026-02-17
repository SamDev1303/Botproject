#!/usr/bin/env python3
"""
Australian Bookkeeping Helpers
GST calculations, BAS quarters, expense categories, P&L generation,
superannuation rates — all AU tax compliant.

Extracted from: archive/mcp/accounting_server.py
No external dependencies — stdlib only.

Usage as module:
    from bookkeeping_helpers import gst_inclusive, bas_quarter, EXPENSE_CATEGORIES

Usage standalone:
    python3 bookkeeping_helpers.py              # quick demo
    python3 bookkeeping_helpers.py --test       # run doctests
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import sys

# ─── Constants ────────────────────────────────────────────────────────────────

SYDNEY_TZ = ZoneInfo("Australia/Sydney")

GST_RATE = 0.10              # 10 % GST
GST_THRESHOLD = 75_000       # Must register for GST above this turnover
TAX_FREE_THRESHOLD = 18_200  # Personal income tax-free threshold
SUPER_RATE = 0.115           # 11.5 % superannuation (2024-25)
CENTS_PER_KM = 0.85          # ATO rate 2024-25
HOME_OFFICE_RATE = 0.67      # ATO fixed rate per hour 2024-25

# Australian Financial Year: 1 Jul → 30 Jun
BAS_QUARTERS = {
    1: {"name": "Q1 Jul-Sep", "months": [7, 8, 9],    "due": "28 Oct"},
    2: {"name": "Q2 Oct-Dec", "months": [10, 11, 12], "due": "28 Feb"},
    3: {"name": "Q3 Jan-Mar", "months": [1, 2, 3],    "due": "28 Apr"},
    4: {"name": "Q4 Apr-Jun", "months": [4, 5, 6],    "due": "28 Jul"},
}

# ATO-compliant expense categories
EXPENSE_CATEGORIES = {
    "cleaning_supplies": {"name": "Cleaning Supplies",          "gst_claimable": True},
    "equipment":         {"name": "Equipment & Tools",          "gst_claimable": True},
    "vehicle":           {"name": "Vehicle/Fuel",               "gst_claimable": True},
    "insurance":         {"name": "Insurance",                  "gst_claimable": False},
    "phone_internet":    {"name": "Phone & Internet",           "gst_claimable": True},
    "advertising":       {"name": "Advertising & Marketing",    "gst_claimable": True},
    "professional":      {"name": "Professional Services",      "gst_claimable": True},
    "uniforms":          {"name": "Work Uniforms",              "gst_claimable": True},
    "training":          {"name": "Training & Courses",         "gst_claimable": True},
    "office":            {"name": "Office Supplies",            "gst_claimable": True},
    "software":          {"name": "Software & Subscriptions",   "gst_claimable": True},
    "bank_fees":         {"name": "Bank Fees",                  "gst_claimable": False},
    "wages":             {"name": "Staff Wages",                "gst_claimable": False},
    "super":             {"name": "Superannuation",             "gst_claimable": False},
    "other":             {"name": "Other Business Expense",     "gst_claimable": True},
}

# Quick tax-deduction lookup for common cleaning-business expenses
TAX_DEDUCTIONS = {
    "cleaning supplies": {"deductible": True,  "notes": "Fully deductible. Keep receipts."},
    "equipment":         {"deductible": True,  "notes": "Items over $300 may need depreciation."},
    "vehicle":           {"deductible": True,  "notes": f"Business use only. Logbook or {CENTS_PER_KM*100:.0f}c/km."},
    "fuel":              {"deductible": True,  "notes": "Business portion. Keep fuel receipts."},
    "insurance":         {"deductible": True,  "notes": "Business insurance — no GST credit."},
    "phone":             {"deductible": True,  "notes": "Business portion. Itemised bill helps."},
    "internet":          {"deductible": True,  "notes": "Business portion only."},
    "uniforms":          {"deductible": True,  "notes": "Must have logo/branding; not everyday clothes."},
    "training":          {"deductible": True,  "notes": "Related to current income-earning activity."},
    "advertising":       {"deductible": True,  "notes": "Fully deductible — ads, flyers, etc."},
    "software":          {"deductible": True,  "notes": "Subscriptions fully deductible."},
    "home office":       {"deductible": True,  "notes": f"Fixed rate {HOME_OFFICE_RATE*100:.0f}c/hr or actual costs."},
    "meals":             {"deductible": False, "notes": "Generally NOT deductible unless overnight travel."},
    "clothing":          {"deductible": False, "notes": "Everyday clothing NOT deductible."},
    "personal":          {"deductible": False, "notes": "Personal expenses are never deductible."},
}


# ─── GST Calculations ────────────────────────────────────────────────────────

def gst_inclusive(total: float) -> dict:
    """
    Break a GST-inclusive amount into net + GST.

    Formula: GST = Total ÷ 11

    >>> gst_inclusive(110)
    {'total': 110.0, 'gst': 10.0, 'net': 100.0}
    >>> gst_inclusive(0)
    {'total': 0.0, 'gst': 0.0, 'net': 0.0}
    """
    total = float(total)
    gst = round(total / 11, 2)
    net = round(total - gst, 2)
    return {"total": total, "gst": gst, "net": net}


def gst_exclusive(net: float) -> dict:
    """
    Add GST to a net (ex-GST) amount.

    >>> gst_exclusive(100)
    {'total': 110.0, 'gst': 10.0, 'net': 100.0}
    """
    net = float(net)
    gst = round(net * GST_RATE, 2)
    total = round(net + gst, 2)
    return {"total": total, "gst": gst, "net": net}


def gst_claimable_for_category(category_key: str) -> bool:
    """
    Return whether GST can be claimed as an input credit for this category.

    >>> gst_claimable_for_category("cleaning_supplies")
    True
    >>> gst_claimable_for_category("wages")
    False
    """
    cat = EXPENSE_CATEGORIES.get(category_key, EXPENSE_CATEGORIES["other"])
    return cat["gst_claimable"]


# ─── BAS Quarter Helpers ─────────────────────────────────────────────────────

def current_bas_quarter(dt: datetime = None) -> int:
    """
    Return the BAS quarter number (1-4) for a given datetime.

    >>> current_bas_quarter(datetime(2025, 8, 15))
    1
    >>> current_bas_quarter(datetime(2025, 11, 1))
    2
    >>> current_bas_quarter(datetime(2026, 2, 28))
    3
    >>> current_bas_quarter(datetime(2026, 5, 1))
    4
    """
    if dt is None:
        dt = datetime.now(SYDNEY_TZ)
    month = dt.month
    for q, info in BAS_QUARTERS.items():
        if month in info["months"]:
            return q
    return 4  # fallback


def bas_quarter_dates(quarter: int, year: int = None) -> tuple:
    """
    Return (start_date, end_date) for a BAS quarter.

    If year is None, uses the current financial year.
    Year refers to the FY start year (e.g. 2025 means FY 2025-26).

    >>> s, e = bas_quarter_dates(1, 2025)
    >>> s.strftime('%Y-%m-%d'), e.strftime('%Y-%m-%d')
    ('2025-07-01', '2025-09-30')
    """
    if year is None:
        now = datetime.now(SYDNEY_TZ)
        year = now.year if now.month >= 7 else now.year - 1

    info = BAS_QUARTERS[quarter]
    months = info["months"]

    # Q1 & Q2 are in the first calendar year; Q3 & Q4 in the next
    cal_year = year if quarter <= 2 else year + 1
    start = datetime(cal_year, months[0], 1)

    if months[-1] == 12:
        end = datetime(cal_year + 1, 1, 1) - timedelta(days=1)
    else:
        end = datetime(cal_year, months[-1] + 1, 1) - timedelta(days=1)

    return start, end


def fy_date_range(fy_start_year: int = None) -> tuple:
    """
    Return (start, end) of an Australian financial year.

    >>> s, e = fy_date_range(2025)
    >>> s.strftime('%Y-%m-%d'), e.strftime('%Y-%m-%d')
    ('2025-07-01', '2026-06-30')
    """
    if fy_start_year is None:
        now = datetime.now(SYDNEY_TZ)
        fy_start_year = now.year if now.month >= 7 else now.year - 1
    return datetime(fy_start_year, 7, 1), datetime(fy_start_year + 1, 6, 30)


# ─── Superannuation ──────────────────────────────────────────────────────────

def calculate_super(gross_wages: float) -> dict:
    """
    Calculate superannuation on gross wages.

    >>> calculate_super(1000)
    {'gross': 1000.0, 'super_amount': 115.0, 'total_cost': 1115.0, 'rate': 0.115}
    """
    gross = float(gross_wages)
    super_amt = round(gross * SUPER_RATE, 2)
    return {
        "gross": gross,
        "super_amount": super_amt,
        "total_cost": round(gross + super_amt, 2),
        "rate": SUPER_RATE,
    }


def calculate_wage(hours: float, rate: float) -> dict:
    """
    Calculate wage including super.

    >>> w = calculate_wage(10, 30)
    >>> w['gross'], w['super_amount']
    (300.0, 34.5)
    """
    gross = round(hours * rate, 2)
    result = calculate_super(gross)
    result["hours"] = hours
    result["hourly_rate"] = rate
    return result


# ─── Profit & Loss Builder ──────────────────────────────────────────────────

def build_profit_loss(income_rows: list, expense_rows: list,
                      wage_rows: list = None,
                      period_label: str = "Period",
                      business_name: str = "Clean Up Bros",
                      abn: str = "26 443 426 374") -> str:
    """
    Generate a text P&L statement from raw data lists.

    Each income row:   [date_str, client, description, amount_str, ...]
    Each expense row:  [date_str, vendor, description, amount_str, category_name, ...]
    Each wage row:     [date_str, staff,  hours_str,   rate_str,   gross_str, super_str, ...]

    Returns a formatted multi-line string.
    """
    def parse_amount(s):
        try:
            return float(str(s).replace('$', '').replace(',', '').strip())
        except (ValueError, TypeError):
            return 0.0

    # Income
    income_total = sum(parse_amount(r[3]) for r in income_rows if len(r) > 3)
    income_gst = round(income_total / 11, 2)
    net_income = round(income_total - income_gst, 2)

    # Expenses by category
    expense_cats = {}
    expense_total = 0.0
    for row in expense_rows:
        if len(row) < 5:
            continue
        amt = parse_amount(row[3])
        cat = row[4]
        expense_cats[cat] = expense_cats.get(cat, 0.0) + amt
        expense_total += amt

    # Wages & super
    wages_total = 0.0
    super_total = 0.0
    if wage_rows:
        for row in wage_rows:
            if len(row) >= 5:
                wages_total += parse_amount(row[4])
            if len(row) >= 6:
                super_total += parse_amount(row[5])

    total_expenses = round(expense_total + wages_total + super_total, 2)
    profit = round(net_income - total_expenses, 2)

    lines = [
        "═" * 45,
        "  PROFIT & LOSS STATEMENT",
        f"  {business_name} — ABN {abn}",
        f"  {period_label}",
        "═" * 45,
        "",
        "INCOME",
        f"  Gross Income (incl GST): ${income_total:,.2f}",
        f"  Less GST Collected:      -${income_gst:,.2f}",
        "  " + "─" * 40,
        f"  Net Income:              ${net_income:,.2f}",
        "",
        "EXPENSES",
    ]

    for cat, amt in sorted(expense_cats.items(), key=lambda x: -x[1]):
        lines.append(f"  {cat}: ${amt:,.2f}")
    if wages_total:
        lines.append(f"  Staff Wages: ${wages_total:,.2f}")
    if super_total:
        lines.append(f"  Superannuation: ${super_total:,.2f}")

    lines += [
        "  " + "─" * 40,
        f"  Total Expenses:          ${total_expenses:,.2f}",
        "",
        "═" * 45,
        f"  NET PROFIT:              ${profit:,.2f}",
        "═" * 45,
    ]

    return "\n".join(lines)


# ─── BAS Calculator ─────────────────────────────────────────────────────────

def calculate_bas(income_total: float, claimable_expense_total: float,
                  quarter: int = 0) -> dict:
    """
    Calculate BAS amounts.

    income_total: GST-inclusive income for the quarter
    claimable_expense_total: GST-inclusive expenses where GST is claimable

    Returns dict with gst_collected, gst_credits, gst_payable, quarter_info.

    >>> r = calculate_bas(11000, 2200, quarter=1)
    >>> r['gst_collected'], r['gst_credits'], r['gst_payable']
    (1000.0, 200.0, 800.0)
    """
    if quarter == 0:
        quarter = current_bas_quarter()

    q_info = BAS_QUARTERS[quarter]
    gst_collected = round(income_total / 11, 2)
    gst_credits = round(claimable_expense_total / 11, 2)
    gst_payable = round(gst_collected - gst_credits, 2)

    return {
        "quarter": quarter,
        "quarter_name": q_info["name"],
        "due_date": q_info["due"],
        "income_total": income_total,
        "gst_collected": gst_collected,
        "gst_credits": gst_credits,
        "gst_payable": gst_payable,
        "owes_ato": gst_payable > 0,
    }


def format_bas(bas: dict) -> str:
    """Pretty-print a BAS result dict."""
    direction = "(You owe ATO)" if bas["owes_ato"] else "(ATO owes you)"
    return f"""📊 BAS Summary — {bas['quarter_name']}
Due: {bas['due_date']}

Income (GST-inclusive): ${bas['income_total']:,.2f}
├─ GST Collected (1A):  ${bas['gst_collected']:,.2f}

GST Credits (1B):       ${bas['gst_credits']:,.2f}

{'═' * 35}
GST Payable/Refund:     ${bas['gst_payable']:,.2f}
{direction}
{'═' * 35}

Lodge via ATO Business Portal or your BAS agent."""


# ─── Tax Deduction Check ────────────────────────────────────────────────────

def is_deductible(expense_type: str) -> dict:
    """
    Check if an expense type is tax deductible for a cleaning business.

    Returns dict with 'deductible' (bool) and 'notes' (str).
    Returns None if unknown.

    >>> is_deductible("cleaning supplies")['deductible']
    True
    >>> is_deductible("meals")['deductible']
    False
    """
    expense_lower = expense_type.lower()
    for key, info in TAX_DEDUCTIONS.items():
        if key in expense_lower or expense_lower in key:
            return info
    return None


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _demo():
    """Run a quick interactive demo."""
    print("=" * 50)
    print("  Australian Bookkeeping Helpers — Demo")
    print("=" * 50)

    print("\n── GST on $330 (inclusive) ──")
    r = gst_inclusive(330)
    print(f"  Total: ${r['total']:.2f}  |  GST: ${r['gst']:.2f}  |  Net: ${r['net']:.2f}")

    print("\n── GST on $300 (exclusive) ──")
    r = gst_exclusive(300)
    print(f"  Net: ${r['net']:.2f}  |  GST: ${r['gst']:.2f}  |  Total: ${r['total']:.2f}")

    print("\n── Super on $1,000 gross ──")
    s = calculate_super(1000)
    print(f"  Gross: ${s['gross']:.2f}  |  Super ({SUPER_RATE*100}%): ${s['super_amount']:.2f}  |  Total cost: ${s['total_cost']:.2f}")

    print("\n── Current BAS Quarter ──")
    now = datetime.now(SYDNEY_TZ)
    q = current_bas_quarter(now)
    info = BAS_QUARTERS[q]
    print(f"  {info['name']}  (due {info['due']})")

    start, end = bas_quarter_dates(q)
    print(f"  Period: {start.strftime('%d/%m/%Y')} – {end.strftime('%d/%m/%Y')}")

    print("\n── BAS Calc: $11,000 income, $2,200 claimable expenses ──")
    bas = calculate_bas(11000, 2200, quarter=q)
    print(format_bas(bas))

    print("\n── Tax Deduction Checks ──")
    for item in ["cleaning supplies", "fuel", "meals", "uniforms"]:
        result = is_deductible(item)
        if result:
            status = "✅" if result["deductible"] else "❌"
            print(f"  {status} {item:20s} — {result['notes']}")

    print("\n── Expense Categories ──")
    for key, info in EXPENSE_CATEGORIES.items():
        gst = "✅ GST" if info["gst_claimable"] else "❌ GST"
        print(f"  {key:20s}  {info['name']:30s}  {gst}")


if __name__ == "__main__":
    if "--test" in sys.argv:
        import doctest
        results = doctest.testmod(verbose=True)
        sys.exit(0 if results.failed == 0 else 1)
    else:
        _demo()
