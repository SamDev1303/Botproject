#!/usr/bin/env python3
"""
Morning Brief — Daily summary for Hafsah
Pulls: Calendar today, unpaid invoices, unread emails, overdue accounts
Usage: python3 ~/Desktop/🦀/scripts/morning_brief.py
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent))
from square_api import SquareAPI
from google_sheets_api import GoogleSheetsAPI

def morning_brief():
    now = datetime.now()
    print(f"\n🌅 Morning Brief — {now.strftime('%d/%m/%Y %A')}\n")

    # Square: unpaid invoices
    try:
        sq = SquareAPI()
        invoices = sq.list_invoices(status="UNPAID") or []
        total_unpaid = sum(float(inv.get('computed_amount_money', {}).get('amount', 0)) / 100 for inv in invoices)
        print(f"💰 Unpaid Invoices: {len(invoices)} (${total_unpaid:,.2f})")
        for inv in invoices[:5]:
            customer = inv.get('primary_recipient', {}).get('customer_id', 'Unknown')
            amount = float(inv.get('computed_amount_money', {}).get('amount', 0)) / 100
            due = inv.get('payment_requests', [{}])[0].get('due_date', 'No date')
            print(f"  • {customer}: ${amount:.2f} (due {due})")
    except Exception as e:
        print(f"  ⚠️ Square error: {e}")

    # Square: recent payments (last 7 days)
    try:
        payments = sq.list_payments(days=7) or []
        week_total = sum(float(p.get('amount_money', {}).get('amount', 0)) / 100 for p in payments)
        print(f"\n📊 Recent Payments (last 10): ${week_total:,.2f}")
    except Exception as e:
        print(f"  ⚠️ Payments error: {e}")

    # Dashboard data
    dash_file = Path.home() / "Desktop" / "🦀" / "dashboard-data.json"
    if dash_file.exists():
        try:
            data = json.loads(dash_file.read_text())
            stats = data.get('stats', {})
            print(f"\n📈 Dashboard Stats:")
            print(f"  • Revenue MTD: ${stats.get('revenueMTD', 0):,.2f}")
            print(f"  • Outstanding: ${stats.get('outstandingBalance', 0):,.2f}")
            print(f"  • GST Payable: ${stats.get('gstPayable', 0):,.2f}")
        except Exception:
            pass

    print(f"\n✅ Brief generated at {now.strftime('%H:%M AEDT')}")

if __name__ == "__main__":
    morning_brief()
