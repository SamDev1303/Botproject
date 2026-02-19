#!/usr/bin/env python3
"""
Simple account-type classifier for financial descriptions.
"""

import argparse

BUSINESS_HINTS = [
    "clean", "client", "airbnb", "invoice", "square", "equipment", "supply",
    "bunnings", "officeworks", "fuel", "gst", "bas", "connecteam",
]
PERSONAL_HINTS = [
    "groceries", "rent", "baby", "family", "personal", "tuition", "school", "doctor",
]


def classify(text: str) -> str:
    low = text.lower()
    if any(k in low for k in PERSONAL_HINTS):
        return "personal"
    if any(k in low for k in BUSINESS_HINTS):
        return "business"
    return "business"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--text", required=True)
    args = p.parse_args()
    print(classify(args.text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
