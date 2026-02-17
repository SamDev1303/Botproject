#!/usr/bin/env python3
"""Delete a shift from Connecteam.

Usage:
  python3 delete_shift.py <shiftId>
"""

import sys, json

sys.path.insert(0, __import__("os").path.dirname(__file__))
from ct_api import delete_shift

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 delete_shift.py <shiftId>")
        sys.exit(1)

    shift_id = sys.argv[1]
    result = delete_shift(shift_id)
    print(json.dumps(result, indent=2))
    print(f"\n✅ Shift {shift_id} deleted")

if __name__ == "__main__":
    main()
