#!/usr/bin/env python3
"""List all staff from Connecteam."""

import sys, json

sys.path.insert(0, __import__("os").path.dirname(__file__))
from ct_api import list_users

def main():
    users = list_users()
    print(f"{'Name':<25} {'Role':<12} {'Phone':<16} {'Email':<35} {'UserID'}")
    print("-" * 100)
    for u in users:
        name = f"{u['firstName']} {u['lastName']}"
        print(f"{name:<25} {u['userType']:<12} {u.get('phoneNumber','—'):<16} {u.get('email','—'):<35} {u['userId']}")

if __name__ == "__main__":
    main()
