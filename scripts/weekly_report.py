#!/usr/bin/env python3
"""
Weekly Business Report — P&L, invoices, bookings summary
Usage: python3 ~/Desktop/🦀/scripts/weekly_report.py
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from square_api import SquareAPI

def weekly_report():
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    print(f"\n📊 Weekly Business Report — {week_ago.strftime('%d/%m')} to {now.strftime('%d/%m/%Y')}\n")

    sq = SquareAPI()

    # Payments this week
    try:
        payments = sq.list_payments(limit=50) or []
        week_payments = []
        for p in payments:
            created = p.get('created_at', '')
            if created:
                try:
                    dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    if dt.replace(tzinfo=None) >= week_ago:
                        week_payments.append(p)
                except Exception:
                    pass

        total_revenue = sum(float(p.get('amount_money', {}).get('amount', 0)) / 100 for p in week_payments)
        gst = total_revenue / 11
        print(f"💰 Revenue This Week: ${total_revenue:,.2f}")
        print(f"   GST Collected: ${gst:,.2f}")
        print(f"   Net Revenue: ${total_revenue - gst:,.2f}")
        print(f"   Payments: {len(week_payments)}")
    except Exception as e:
        print(f"  ⚠️ Payments error: {e}")

    # Unpaid invoices
    try:
        invoices = sq.list_invoices(status="UNPAID") or []
        total_unpaid = sum(float(inv.get('computed_amount_money', {}).get('amount', 0)) / 100 for inv in invoices)
        print(f"\n⚠️ Outstanding: ${total_unpaid:,.2f} ({len(invoices)} invoices)")
    except Exception as e:
        print(f"  ⚠️ Invoice error: {e}")

    print(f"\n✅ Report generated at {now.strftime('%H:%M AEDT %d/%m/%Y')}")

if __name__ == "__main__":
    weekly_report()
