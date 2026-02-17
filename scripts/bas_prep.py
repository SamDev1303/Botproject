#!/usr/bin/env python3
"""
BAS Preparation — Calculate GST for the current quarter
Usage: python3 ~/Desktop/🦀/scripts/bas_prep.py
       python3 ~/Desktop/🦀/scripts/bas_prep.py Q3  (specific quarter)
"""
import sys
from datetime import datetime

BAS_QUARTERS = {
    "Q1": {"months": [7, 8, 9], "period": "Jul-Sep", "due": "28 October"},
    "Q2": {"months": [10, 11, 12], "period": "Oct-Dec", "due": "28 February"},
    "Q3": {"months": [1, 2, 3], "period": "Jan-Mar", "due": "28 April"},
    "Q4": {"months": [4, 5, 6], "period": "Apr-Jun", "due": "28 July"},
}

def get_current_quarter():
    month = datetime.now().month
    if month in [7, 8, 9]: return "Q1"
    if month in [10, 11, 12]: return "Q2"
    if month in [1, 2, 3]: return "Q3"
    return "Q4"

def bas_prep(quarter=None):
    if not quarter:
        quarter = get_current_quarter()
    quarter = quarter.upper()

    if quarter not in BAS_QUARTERS:
        print(f"❌ Invalid quarter: {quarter}. Use Q1, Q2, Q3, or Q4.")
        return

    q = BAS_QUARTERS[quarter]
    year = datetime.now().year

    print(f"\n📋 BAS Preparation — {quarter} {q['period']} {year}")
    print(f"   Due Date: {q['due']} {year}\n")

    print("Enter your totals (or 0 to skip):\n")

    try:
        g1 = float(input("  G1  Total Sales (GST-inclusive):        $") or 0)
        g10 = float(input("  G10 Capital Purchases (GST-inclusive):   $") or 0)
        g11 = float(input("  G11 Non-Capital Purchases (GST-inc):     $") or 0)
    except (ValueError, EOFError):
        print("\n❌ Invalid input.")
        return

    gst_on_sales = g1 / 11
    gst_credits = (g10 + g11) / 11
    gst_owing = gst_on_sales - gst_credits

    print(f"\n{'─' * 50}")
    print(f"  G1  Total Sales:           ${g1:>12,.2f}")
    print(f"  GST on Sales:              ${gst_on_sales:>12,.2f}")
    print(f"")
    print(f"  G10 Capital Purchases:     ${g10:>12,.2f}")
    print(f"  G11 Non-Capital Purchases: ${g11:>12,.2f}")
    print(f"  GST Credits:               ${gst_credits:>12,.2f}")
    print(f"{'─' * 50}")
    if gst_owing >= 0:
        print(f"  GST OWING TO ATO:          ${gst_owing:>12,.2f}")
    else:
        print(f"  GST REFUND FROM ATO:       ${abs(gst_owing):>12,.2f}")
    print(f"\n  ⚠️ Lodge by {q['due']} {year}")

if __name__ == "__main__":
    quarter = sys.argv[1] if len(sys.argv) > 1 else None
    bas_prep(quarter)
