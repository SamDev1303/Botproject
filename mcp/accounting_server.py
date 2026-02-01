#!/usr/bin/env python3
"""
Accounting MCP Server - Bookkeeping & Financial Management
For Clean Up Bros - Australian Tax Compliant

Handles:
- Income/Expense recording to Google Sheets
- GST calculations (Australian 10%)
- BAS preparation
- Outstanding invoice tracking
- Profit & Loss reporting
- Staff wages tracking
"""
import os
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

# Load environment
def load_env():
    env_file = Path.home() / ".clawdbot" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))

load_env()

# Config
TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID', '')

# Australian Tax Constants
GST_RATE = 0.10  # 10% GST
GST_THRESHOLD = 75000  # GST registration threshold
TAX_FREE_THRESHOLD = 18200  # Personal income tax-free threshold
SUPER_RATE = 0.115  # 11.5% superannuation (2024-25)

# BAS Quarters
BAS_QUARTERS = {
    1: {"name": "Q1 Jul-Sep", "months": [7, 8, 9], "due": "28 Oct"},
    2: {"name": "Q2 Oct-Dec", "months": [10, 11, 12], "due": "28 Feb"},
    3: {"name": "Q3 Jan-Mar", "months": [1, 2, 3], "due": "28 Apr"},
    4: {"name": "Q4 Apr-Jun", "months": [4, 5, 6], "due": "28 Jul"}
}

# Expense Categories (ATO Compliant)
EXPENSE_CATEGORIES = {
    "cleaning_supplies": {"name": "Cleaning Supplies", "gst_claimable": True},
    "equipment": {"name": "Equipment & Tools", "gst_claimable": True},
    "vehicle": {"name": "Vehicle/Fuel", "gst_claimable": True},
    "insurance": {"name": "Insurance", "gst_claimable": False},
    "phone_internet": {"name": "Phone & Internet", "gst_claimable": True},
    "advertising": {"name": "Advertising & Marketing", "gst_claimable": True},
    "professional": {"name": "Professional Services", "gst_claimable": True},
    "uniforms": {"name": "Work Uniforms", "gst_claimable": True},
    "training": {"name": "Training & Courses", "gst_claimable": True},
    "office": {"name": "Office Supplies", "gst_claimable": True},
    "software": {"name": "Software & Subscriptions", "gst_claimable": True},
    "bank_fees": {"name": "Bank Fees", "gst_claimable": False},
    "wages": {"name": "Staff Wages", "gst_claimable": False},
    "super": {"name": "Superannuation", "gst_claimable": False},
    "other": {"name": "Other Business Expense", "gst_claimable": True}
}

def get_access_token():
    """Get valid access token, refreshing if needed"""
    if not TOKEN_FILE.exists():
        return None

    with open(TOKEN_FILE) as f:
        tokens = json.load(f)

    if 'refresh_token' in tokens:
        data = urllib.parse.urlencode({
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': tokens['refresh_token'],
            'grant_type': 'refresh_token'
        }).encode()

        try:
            req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
            with urllib.request.urlopen(req) as response:
                new_tokens = json.loads(response.read().decode())
                tokens['access_token'] = new_tokens['access_token']
                with open(TOKEN_FILE, 'w') as f:
                    json.dump(tokens, f, indent=2)
                return new_tokens['access_token']
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            print(f"Token refresh failed: {e}")
            pass

    return tokens.get('access_token')

def sheets_request(endpoint, method="GET", data=None):
    """Make Google Sheets API request"""
    token = get_access_token()
    if not token:
        return {"error": "No access token. Run google-oauth-setup.py first."}

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEETS_ID}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}

    if data:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:200]}"}

def read_sheet(range_str):
    """Read data from a sheet range"""
    endpoint = f"/values/{urllib.parse.quote(range_str)}"
    return sheets_request(endpoint)

def append_sheet(range_str, values):
    """Append a row to a sheet"""
    endpoint = f"/values/{urllib.parse.quote(range_str)}:append?valueInputOption=USER_ENTERED"
    return sheets_request(endpoint, method="POST", data={"values": [values]})

# Create MCP server
mcp = FastMCP("Accounting")

# ============== INCOME ==============

@mcp.tool()
def record_income(date: str, client: str, description: str, amount: float, payment_method: str = "Bank Transfer", invoice_id: str = "") -> str:
    """
    Record income/payment received.
    Date format: YYYY-MM-DD or DD/MM/YYYY
    Amount should be the total received (GST-inclusive)
    """
    # Parse date
    try:
        if "/" in date:
            dt = datetime.strptime(date, "%d/%m/%Y")
        else:
            dt = datetime.strptime(date, "%Y-%m-%d")
        date_str = dt.strftime("%Y-%m-%d")
    except ValueError:
        return "Error: Date must be YYYY-MM-DD or DD/MM/YYYY format"

    # Calculate GST
    gst = amount / 11  # GST = Total ÷ 11
    net = amount - gst

    values = [date_str, client, description, f"${amount:.2f}", payment_method]
    if invoice_id:
        values.append(invoice_id)

    result = append_sheet("Income!A:F", values)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"""✅ Income recorded:
• Date: {date_str}
• Client: {client}
• Description: {description}
• Amount: ${amount:.2f} (incl. GST)
• GST component: ${gst:.2f}
• Net income: ${net:.2f}
• Payment: {payment_method}"""

@mcp.tool()
def get_income_summary(period: str = "month") -> str:
    """
    Get income summary for a period.
    Period: 'week', 'month', 'quarter', 'year', or 'all'
    """
    result = read_sheet("Income!A:F")

    if "error" in result:
        return f"Error: {result['error']}"

    values = result.get('values', [])
    if not values:
        return "No income records found."

    # Calculate date range
    today = datetime.now()
    if period == "week":
        start_date = today - timedelta(days=7)
    elif period == "month":
        start_date = today.replace(day=1)
    elif period == "quarter":
        quarter_start = ((today.month - 1) // 3) * 3 + 1
        start_date = today.replace(month=quarter_start, day=1)
    elif period == "year":
        # Australian financial year starts July 1
        if today.month >= 7:
            start_date = today.replace(month=7, day=1)
        else:
            start_date = today.replace(year=today.year - 1, month=7, day=1)
    else:
        start_date = datetime(2000, 1, 1)

    total = 0
    count = 0
    for row in values:
        try:
            row_date = datetime.strptime(row[0], "%Y-%m-%d")
            if row_date >= start_date:
                amount_str = row[3].replace("$", "").replace(",", "")
                total += float(amount_str)
                count += 1
        except (ValueError, IndexError, KeyError):
            # Skip malformed rows
            continue

    gst = total / 11
    net = total - gst

    return f"""📊 Income Summary ({period}):
• Total: ${total:.2f}
• GST collected: ${gst:.2f}
• Net income: ${net:.2f}
• Transactions: {count}
• Period: {start_date.strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')}"""

# ============== EXPENSES ==============

@mcp.tool()
def record_expense(date: str, vendor: str, description: str, amount: float, category: str = "other", payment_method: str = "Card", receipt: str = "") -> str:
    """
    Record a business expense.
    Categories: cleaning_supplies, equipment, vehicle, insurance, phone_internet,
    advertising, professional, uniforms, training, office, software, bank_fees, wages, super, other
    """
    # Parse date
    try:
        if "/" in date:
            dt = datetime.strptime(date, "%d/%m/%Y")
        else:
            dt = datetime.strptime(date, "%Y-%m-%d")
        date_str = dt.strftime("%Y-%m-%d")
    except ValueError:
        return "Error: Date must be YYYY-MM-DD or DD/MM/YYYY format"

    # Get category info
    cat_info = EXPENSE_CATEGORIES.get(category, EXPENSE_CATEGORIES["other"])
    cat_name = cat_info["name"]

    # Calculate GST (if claimable)
    if cat_info["gst_claimable"]:
        gst = amount / 11
        gst_note = f"GST credit: ${gst:.2f}"
    else:
        gst = 0
        gst_note = "No GST credit (exempt)"

    values = [date_str, vendor, description, f"${amount:.2f}", cat_name, payment_method]
    if receipt:
        values.append(receipt)

    result = append_sheet("Expenses!A:G", values)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"""✅ Expense recorded:
• Date: {date_str}
• Vendor: {vendor}
• Description: {description}
• Amount: ${amount:.2f}
• Category: {cat_name}
• {gst_note}
• Payment: {payment_method}"""

@mcp.tool()
def get_expense_summary(period: str = "month") -> str:
    """Get expense summary by category for a period."""
    result = read_sheet("Expenses!A:G")

    if "error" in result:
        return f"Error: {result['error']}"

    values = result.get('values', [])
    if not values:
        return "No expense records found."

    # Calculate date range
    today = datetime.now()
    if period == "month":
        start_date = today.replace(day=1)
    elif period == "quarter":
        quarter_start = ((today.month - 1) // 3) * 3 + 1
        start_date = today.replace(month=quarter_start, day=1)
    elif period == "year":
        if today.month >= 7:
            start_date = today.replace(month=7, day=1)
        else:
            start_date = today.replace(year=today.year - 1, month=7, day=1)
    else:
        start_date = datetime(2000, 1, 1)

    categories = {}
    total = 0
    gst_claimable = 0

    for row in values:
        try:
            row_date = datetime.strptime(row[0], "%Y-%m-%d")
            if row_date >= start_date:
                amount_str = row[3].replace("$", "").replace(",", "")
                amount = float(amount_str)
                category = row[4] if len(row) > 4 else "Other"

                categories[category] = categories.get(category, 0) + amount
                total += amount

                # Check if GST claimable
                for cat_key, cat_info in EXPENSE_CATEGORIES.items():
                    if cat_info["name"] == category and cat_info["gst_claimable"]:
                        gst_claimable += amount / 11
                        break
        except (ValueError, IndexError, KeyError):
            # Skip malformed rows
            continue

    output = [f"📊 Expense Summary ({period}):", f"• Total: ${total:.2f}", f"• GST credits: ${gst_claimable:.2f}", "", "By Category:"]
    for cat, amt in sorted(categories.items(), key=lambda x: -x[1]):
        output.append(f"  • {cat}: ${amt:.2f}")

    return "\n".join(output)

# ============== OUTSTANDING INVOICES ==============

@mcp.tool()
def record_outstanding(client: str, amount: float, description: str, due_date: str, invoice_id: str = "") -> str:
    """Record an outstanding invoice (money owed to you)"""
    try:
        if "/" in due_date:
            dt = datetime.strptime(due_date, "%d/%m/%Y")
        else:
            dt = datetime.strptime(due_date, "%Y-%m-%d")
        due_str = dt.strftime("%Y-%m-%d")
    except ValueError:
        return "Error: Date must be YYYY-MM-DD or DD/MM/YYYY format"

    today = datetime.now().strftime("%Y-%m-%d")
    values = [today, client, description, f"${amount:.2f}", due_str, "UNPAID"]
    if invoice_id:
        values.append(invoice_id)

    result = append_sheet("Outstanding!A:G", values)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"""📋 Outstanding invoice recorded:
• Client: {client}
• Amount: ${amount:.2f}
• Description: {description}
• Due: {due_str}"""

@mcp.tool()
def get_outstanding() -> str:
    """Get all outstanding invoices"""
    result = read_sheet("Outstanding!A:G")

    if "error" in result:
        return f"Error: {result['error']}"

    values = result.get('values', [])
    if not values:
        return "No outstanding invoices."

    today = datetime.now()
    total = 0
    overdue = 0
    output = ["📋 Outstanding Invoices:", ""]

    for row in values:
        try:
            if len(row) < 6 or row[5] == "PAID":
                continue

            client = row[1]
            amount_str = row[3].replace("$", "").replace(",", "")
            amount = float(amount_str)
            due_date = datetime.strptime(row[4], "%Y-%m-%d")

            total += amount

            if due_date < today:
                days_overdue = (today - due_date).days
                status = f"⚠️ OVERDUE ({days_overdue} days)"
                overdue += amount
            else:
                days_until = (due_date - today).days
                status = f"Due in {days_until} days"

            output.append(f"• {client}: ${amount:.2f} - {status}")
        except (ValueError, IndexError, KeyError):
            # Skip malformed rows
            continue

    output.append("")
    output.append(f"Total Outstanding: ${total:.2f}")
    if overdue > 0:
        output.append(f"⚠️ Total Overdue: ${overdue:.2f}")

    return "\n".join(output)

# ============== STAFF WAGES ==============

@mcp.tool()
def record_wage(date: str, staff_name: str, hours: float, rate: float, description: str = "") -> str:
    """Record staff wages paid"""
    try:
        if "/" in date:
            dt = datetime.strptime(date, "%d/%m/%Y")
        else:
            dt = datetime.strptime(date, "%Y-%m-%d")
        date_str = dt.strftime("%Y-%m-%d")
    except ValueError:
        return "Error: Date must be YYYY-MM-DD or DD/MM/YYYY format"

    gross = hours * rate
    super_amount = gross * SUPER_RATE

    values = [date_str, staff_name, f"{hours:.1f}", f"${rate:.2f}", f"${gross:.2f}", f"${super_amount:.2f}", description]

    result = append_sheet("Staff Wages!A:G", values)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"""✅ Wage recorded:
• Date: {date_str}
• Staff: {staff_name}
• Hours: {hours:.1f} @ ${rate:.2f}/hr
• Gross: ${gross:.2f}
• Super (11.5%): ${super_amount:.2f}
• Total cost: ${gross + super_amount:.2f}"""

# ============== BAS & TAX ==============

@mcp.tool()
def calculate_bas(quarter: int = 0) -> str:
    """
    Calculate BAS (Business Activity Statement) for a quarter.
    Quarter: 1 (Jul-Sep), 2 (Oct-Dec), 3 (Jan-Mar), 4 (Apr-Jun)
    If 0, uses current quarter.
    """
    today = datetime.now()

    if quarter == 0:
        # Determine current quarter
        month = today.month
        if month in [7, 8, 9]:
            quarter = 1
        elif month in [10, 11, 12]:
            quarter = 2
        elif month in [1, 2, 3]:
            quarter = 3
        else:
            quarter = 4

    q_info = BAS_QUARTERS[quarter]

    # Determine year
    if quarter == 1:
        year = today.year if today.month >= 7 else today.year - 1
    elif quarter in [2]:
        year = today.year if today.month >= 10 else today.year - 1
    else:
        year = today.year

    # Calculate date range
    months = q_info["months"]
    if quarter <= 2:
        start_date = datetime(year, months[0], 1)
    else:
        start_date = datetime(year, months[0], 1)

    if months[-1] == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year if months[-1] < 7 else year + 1, months[-1] + 1, 1) - timedelta(days=1)

    # Get income GST
    income_result = read_sheet("Income!A:F")
    income_total = 0
    if income_result.get('values'):
        for row in income_result['values']:
            try:
                row_date = datetime.strptime(row[0], "%Y-%m-%d")
                if start_date <= row_date <= end_date:
                    amount = float(row[3].replace("$", "").replace(",", ""))
                    income_total += amount
            except (ValueError, IndexError):
                # Skip invalid expense rows
                continue

    gst_collected = income_total / 11

    # Get expense GST credits
    expense_result = read_sheet("Expenses!A:G")
    gst_credits = 0
    if expense_result.get('values'):
        for row in expense_result['values']:
            try:
                row_date = datetime.strptime(row[0], "%Y-%m-%d")
                if start_date <= row_date <= end_date:
                    amount = float(row[3].replace("$", "").replace(",", ""))
                    category = row[4] if len(row) > 4 else "Other"
                    # Check if GST claimable
                    for cat_key, cat_info in EXPENSE_CATEGORIES.items():
                        if cat_info["name"] == category and cat_info["gst_claimable"]:
                            gst_credits += amount / 11
                            break
            except (ValueError, IndexError):
                # Skip invalid expense rows
                continue

    gst_payable = gst_collected - gst_credits

    return f"""📊 BAS Summary - {q_info['name']}
Period: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}
Due: {q_info['due']}

Income (GST-inclusive): ${income_total:.2f}
├─ GST Collected (1A): ${gst_collected:.2f}

GST Credits (1B): ${gst_credits:.2f}

═══════════════════════════
GST Payable/Refund: ${gst_payable:.2f}
{'(You owe ATO)' if gst_payable > 0 else '(ATO owes you)'}
═══════════════════════════

Note: Lodge via ATO Business Portal or through your BAS agent."""

@mcp.tool()
def profit_loss(period: str = "quarter") -> str:
    """Generate Profit & Loss statement for a period"""
    today = datetime.now()

    if period == "month":
        start_date = today.replace(day=1)
    elif period == "quarter":
        quarter_start = ((today.month - 1) // 3) * 3 + 1
        start_date = today.replace(month=quarter_start, day=1)
    elif period == "year":
        if today.month >= 7:
            start_date = today.replace(month=7, day=1)
        else:
            start_date = today.replace(year=today.year - 1, month=7, day=1)
    else:
        start_date = datetime(2000, 1, 1)

    # Get income
    income_result = read_sheet("Income!A:F")
    income_total = 0
    if income_result.get('values'):
        for row in income_result['values']:
            try:
                row_date = datetime.strptime(row[0], "%Y-%m-%d")
                if row_date >= start_date:
                    income_total += float(row[3].replace("$", "").replace(",", ""))
            except (ValueError, IndexError):
                # Skip invalid expense rows
                continue

    # Get expenses by category
    expense_result = read_sheet("Expenses!A:G")
    expenses = {}
    expense_total = 0
    if expense_result.get('values'):
        for row in expense_result['values']:
            try:
                row_date = datetime.strptime(row[0], "%Y-%m-%d")
                if row_date >= start_date:
                    amount = float(row[3].replace("$", "").replace(",", ""))
                    category = row[4] if len(row) > 4 else "Other"
                    expenses[category] = expenses.get(category, 0) + amount
                    expense_total += amount
            except (ValueError, IndexError):
                # Skip invalid expense rows
                continue

    # Get wages
    wages_result = read_sheet("Staff Wages!A:G")
    wages_total = 0
    super_total = 0
    if wages_result.get('values'):
        for row in wages_result['values']:
            try:
                row_date = datetime.strptime(row[0], "%Y-%m-%d")
                if row_date >= start_date:
                    wages_total += float(row[4].replace("$", "").replace(",", ""))
                    if len(row) > 5:
                        super_total += float(row[5].replace("$", "").replace(",", ""))
            except (ValueError, IndexError):
                # Skip invalid expense rows
                continue

    # Calculate net income (GST-exclusive)
    net_income = income_total - (income_total / 11)
    total_expenses = expense_total + wages_total + super_total
    profit = net_income - total_expenses

    output = [
        f"═══════════════════════════════════════",
        f"  PROFIT & LOSS STATEMENT",
        f"  Clean Up Bros - ABN 26 443 426 374",
        f"  Period: {start_date.strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')}",
        f"═══════════════════════════════════════",
        "",
        f"INCOME",
        f"  Gross Income (incl GST): ${income_total:.2f}",
        f"  Less GST Collected:      -${income_total/11:.2f}",
        f"  ─────────────────────────────────────",
        f"  Net Income:              ${net_income:.2f}",
        "",
        f"EXPENSES"
    ]

    for cat, amt in sorted(expenses.items(), key=lambda x: -x[1]):
        output.append(f"  {cat}: ${amt:.2f}")

    if wages_total > 0:
        output.append(f"  Staff Wages: ${wages_total:.2f}")
    if super_total > 0:
        output.append(f"  Superannuation: ${super_total:.2f}")

    output.extend([
        f"  ─────────────────────────────────────",
        f"  Total Expenses:          ${total_expenses:.2f}",
        "",
        f"═══════════════════════════════════════",
        f"  NET PROFIT:              ${profit:.2f}",
        f"═══════════════════════════════════════"
    ])

    return "\n".join(output)

@mcp.tool()
def list_expense_categories() -> str:
    """List all expense categories and their GST status"""
    output = ["📋 Expense Categories:", ""]
    for key, info in EXPENSE_CATEGORIES.items():
        gst = "✅ GST claimable" if info["gst_claimable"] else "❌ No GST credit"
        output.append(f"• {key}: {info['name']} ({gst})")
    return "\n".join(output)

@mcp.tool()
def calculate_gst(amount: float, inclusive: bool = True) -> str:
    """
    Calculate GST on an amount.
    inclusive=True: Amount includes GST, calculate GST component
    inclusive=False: Amount excludes GST, calculate GST to add
    """
    if inclusive:
        gst = amount / 11
        net = amount - gst
        return f"""GST Calculation (inclusive):
• Total: ${amount:.2f}
• GST: ${gst:.2f}
• Net: ${net:.2f}

Formula: GST = Total ÷ 11"""
    else:
        gst = amount * 0.10
        total = amount + gst
        return f"""GST Calculation (exclusive):
• Net: ${amount:.2f}
• GST (10%): ${gst:.2f}
• Total: ${total:.2f}

Formula: GST = Net × 0.10"""

@mcp.tool()
def tax_deduction_check(expense_type: str) -> str:
    """Check if an expense type is tax deductible for a cleaning business"""
    deductible_expenses = {
        "cleaning supplies": {"deductible": True, "notes": "Fully deductible. Keep receipts."},
        "equipment": {"deductible": True, "notes": "Deductible. Items over $300 may need to be depreciated."},
        "vehicle": {"deductible": True, "notes": "Business use portion only. Use logbook method or cents per km (85c/km 2024-25)."},
        "fuel": {"deductible": True, "notes": "Business use portion only. Keep fuel receipts."},
        "insurance": {"deductible": True, "notes": "Business insurance fully deductible. No GST credit."},
        "phone": {"deductible": True, "notes": "Business use portion. Keep itemised bills."},
        "internet": {"deductible": True, "notes": "Business use portion only."},
        "uniforms": {"deductible": True, "notes": "Work-specific clothing with logo/branding. Not everyday clothes."},
        "training": {"deductible": True, "notes": "Must be related to current income-earning activity."},
        "advertising": {"deductible": True, "notes": "Fully deductible. Facebook ads, Google ads, flyers, etc."},
        "software": {"deductible": True, "notes": "Business software subscriptions fully deductible."},
        "home office": {"deductible": True, "notes": "Fixed rate 67c/hour, or actual expenses method."},
        "meals": {"deductible": False, "notes": "Generally NOT deductible unless overnight travel."},
        "clothing": {"deductible": False, "notes": "Everyday clothing NOT deductible, even if worn for work."},
        "personal": {"deductible": False, "notes": "Personal expenses are never deductible."},
    }

    expense_lower = expense_type.lower()
    for key, info in deductible_expenses.items():
        if key in expense_lower or expense_lower in key:
            status = "✅ Deductible" if info["deductible"] else "❌ Not Deductible"
            return f"""{status}: {expense_type}

{info['notes']}

Remember:
• Keep receipts for 5 years
• Only claim business portion of mixed-use items
• Consult a tax agent for complex situations"""

    return f"""❓ Unsure about: {expense_type}

General rules:
• Must be directly related to earning income
• Must not be private or capital in nature
• Keep records for 5 years

Consult a registered tax agent for specific advice."""

if __name__ == "__main__":
    mcp.run()
