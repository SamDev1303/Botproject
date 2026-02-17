#!/usr/bin/env python3
"""
Quick GST Calculator — Australian GST (10%)
Usage: python3 ~/Desktop/🦀/scripts/gst_calc.py 380
       python3 ~/Desktop/🦀/scripts/gst_calc.py 380 280 480
"""
import sys

def calc_gst(total):
    gst = total / 11
    ex_gst = total - gst
    return total, gst, ex_gst

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gst_calc.py <amount> [amount2] [amount3]...")
        sys.exit(1)

    amounts = [float(a) for a in sys.argv[1:]]
    grand_total = 0
    grand_gst = 0

    for amount in amounts:
        total, gst, ex_gst = calc_gst(amount)
        grand_total += total
        grand_gst += gst
        print(f"${total:>10,.2f}  →  GST: ${gst:>8,.2f}  |  Ex-GST: ${ex_gst:>10,.2f}")

    if len(amounts) > 1:
        print(f"{'─' * 50}")
        print(f"${grand_total:>10,.2f}  →  GST: ${grand_gst:>8,.2f}  |  Ex-GST: ${grand_total - grand_gst:>10,.2f}")
