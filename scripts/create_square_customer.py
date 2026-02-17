#!/usr/bin/env python3
"""
Create Square Customer — Generalised
Interactive or scripted customer creation via Square API.

Extracted from: archive/old-scripts/create_sam_square.py
No external dependencies — stdlib only.

Usage standalone (interactive):
    python3 create_square_customer.py

Usage standalone (scripted):
    python3 create_square_customer.py \\
        --name "Jane Smith" \\
        --email "jane@example.com" \\
        --phone "+61412345678" \\
        --address "10 High St" \\
        --suburb "Liverpool" \\
        --state "NSW" \\
        --postcode "2170" \\
        --note "Weekly clean $120"

Usage as module:
    from create_square_customer import create_customer
    result = create_customer(
        given_name="Jane", family_name="Smith",
        email="jane@example.com", phone="+61412345678",
    )
"""

import sys
from square_api import SquareAPI
from validation_helpers import validate_email, validate_phone, to_international_phone


def create_customer(given_name: str, family_name: str = "",
                    email: str = "", phone: str = "",
                    address_line: str = "", suburb: str = "",
                    state: str = "NSW", postcode: str = "",
                    note: str = "") -> dict:
    """
    Create a customer in Square with validation.
    Returns the customer dict from the API, or a dict with 'error' key.
    """
    sq = SquareAPI()

    # Validate email if provided
    if email and not validate_email(email):
        return {"error": f"Invalid email: {email}"}

    # Normalise phone to international format if provided
    if phone:
        try:
            phone = to_international_phone(phone)
        except ValueError as e:
            return {"error": str(e)}

    # Build address dict
    address = None
    if address_line or suburb:
        address = {"country": "AU"}
        if address_line:
            address["address_line_1"] = address_line
        if suburb:
            address["locality"] = suburb
        if state:
            address["administrative_district_level_1"] = state
        if postcode:
            address["postal_code"] = postcode

    return sq.create_customer(
        given_name=given_name,
        family_name=family_name,
        email=email,
        phone=phone,
        address=address,
        note=note,
    )


def _interactive():
    """Run interactive customer creation."""
    print("=" * 50)
    print("  Create Square Customer")
    print("=" * 50)
    print()

    given = input("First name: ").strip()
    if not given:
        print("First name is required.")
        sys.exit(1)

    family = input("Last name (optional): ").strip()
    email = input("Email (optional): ").strip()
    phone = input("Phone (optional, AU format): ").strip()
    address_line = input("Address line (optional): ").strip()
    suburb = input("Suburb (optional): ").strip()
    state = input("State [NSW]: ").strip() or "NSW"
    postcode = input("Postcode (optional): ").strip()
    note = input("Note (optional): ").strip()

    print()
    print("Creating customer...")
    result = create_customer(
        given_name=given, family_name=family,
        email=email, phone=phone,
        address_line=address_line, suburb=suburb,
        state=state, postcode=postcode, note=note,
    )

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)

    cid = result.get("id", "?")
    name = f"{result.get('given_name', '')} {result.get('family_name', '')}".strip()
    print(f"✅ Customer created!")
    print(f"   Name: {name}")
    print(f"   ID:   {cid}")
    if result.get("email_address"):
        print(f"   Email: {result['email_address']}")
    if result.get("phone_number"):
        print(f"   Phone: {result['phone_number']}")


def _scripted():
    """Parse command-line flags and create customer."""
    args = sys.argv[1:]

    # Quick flag parser (no argparse to stay stdlib-minimal)
    flags = {}
    i = 0
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            key = args[i][2:]
            flags[key] = args[i + 1]
            i += 2
        else:
            i += 1

    name_parts = flags.get("name", "").split(None, 1)
    given = name_parts[0] if name_parts else ""
    family = name_parts[1] if len(name_parts) > 1 else ""

    if not given:
        print("Usage: create_square_customer.py --name 'First Last' [--email ...] [--phone ...] ...")
        print("Or run without arguments for interactive mode.")
        sys.exit(1)

    result = create_customer(
        given_name=given,
        family_name=family,
        email=flags.get("email", ""),
        phone=flags.get("phone", ""),
        address_line=flags.get("address", ""),
        suburb=flags.get("suburb", ""),
        state=flags.get("state", "NSW"),
        postcode=flags.get("postcode", ""),
        note=flags.get("note", ""),
    )

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)

    cid = result.get("id", "?")
    name = f"{result.get('given_name', '')} {result.get('family_name', '')}".strip()
    print(f"✅ Customer created: {name} (ID: {cid})")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        _scripted()
    else:
        _interactive()
