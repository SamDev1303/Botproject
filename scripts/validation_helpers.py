#!/usr/bin/env python3
"""
Australian Validation Helpers
Standalone validators for phone, ABN, BSB, email, amounts.

Extracted from: archive/mcp/validation.py
No external dependencies — stdlib only.

Usage as module:
    from validation_helpers import validate_phone, validate_abn, validate_email

Usage standalone:
    python3 validation_helpers.py
"""

import re
import sys


# ─── Email ────────────────────────────────────────────────────────────────────

def validate_email(email: str) -> bool:
    """
    Validate email format (RFC 5322 simplified).

    >>> validate_email("test@example.com")
    True
    >>> validate_email("bad@@email")
    False
    >>> validate_email("")
    False
    """
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# ─── Australian Phone ────────────────────────────────────────────────────────

def validate_phone(phone: str) -> str:
    """
    Validate and normalise an Australian phone number to 10-digit local format.

    Accepts: 0412345678, +61412345678, 61412345678, 412345678
    Returns: '0412345678'
    Raises ValueError on invalid input.

    >>> validate_phone("0412 345 678")
    '0412345678'
    >>> validate_phone("+61412345678")
    '0412345678'
    >>> validate_phone("61412345678")
    '0412345678'
    """
    if not phone or not isinstance(phone, str):
        raise ValueError("Phone number is required")

    digits = re.sub(r'\D', '', phone)

    if len(digits) == 10 and digits.startswith('0'):
        return digits
    if len(digits) == 11 and digits.startswith('61'):
        return '0' + digits[2:]
    if len(digits) == 9 and digits.startswith('4'):
        return '0' + digits

    raise ValueError(f"Invalid Australian phone number: {phone}")


def to_international_phone(phone: str) -> str:
    """
    Convert any AU phone format to +61... international format.

    >>> to_international_phone("0412345678")
    '+61412345678'
    """
    local = validate_phone(phone)
    return '+61' + local[1:]


# ─── ABN ──────────────────────────────────────────────────────────────────────

# ABN weighting factors for checksum (ATO algorithm)
_ABN_WEIGHTS = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]


def validate_abn(abn: str) -> str:
    """
    Validate an Australian Business Number using the ATO checksum algorithm.

    Returns formatted ABN: 'XX XXX XXX XXX'
    Raises ValueError if invalid.

    >>> validate_abn("26 443 426 374")
    '26 443 426 374'
    >>> validate_abn("26443426374")
    '26 443 426 374'
    """
    if not abn:
        raise ValueError("ABN is required")

    digits = re.sub(r'\D', '', abn)

    if len(digits) != 11:
        raise ValueError(f"ABN must be 11 digits, got {len(digits)}")

    # ATO checksum: subtract 1 from first digit, then weighted sum mod 89 == 0
    nums = [int(d) for d in digits]
    nums[0] -= 1
    checksum = sum(w * n for w, n in zip(_ABN_WEIGHTS, nums))
    if checksum % 89 != 0:
        raise ValueError(f"ABN checksum failed — not a valid ABN: {abn}")

    return f"{digits[0:2]} {digits[2:5]} {digits[5:8]} {digits[8:11]}"


# ─── BSB ──────────────────────────────────────────────────────────────────────

def validate_bsb(bsb: str) -> str:
    """
    Validate an Australian BSB (Bank-State-Branch) number.

    Returns formatted BSB: 'XXX-XXX'

    >>> validate_bsb("062-000")
    '062-000'
    >>> validate_bsb("062000")
    '062-000'
    """
    if not bsb:
        raise ValueError("BSB is required")

    digits = re.sub(r'\D', '', bsb)

    if len(digits) != 6:
        raise ValueError(f"BSB must be 6 digits, got {len(digits)}")

    return f"{digits[0:3]}-{digits[3:6]}"


# ─── Monetary Amount ─────────────────────────────────────────────────────────

def validate_amount(amount) -> float:
    """
    Parse and validate a monetary amount. Strips $, commas, whitespace.

    >>> validate_amount("$1,234.56")
    1234.56
    >>> validate_amount(99.9)
    99.9
    """
    if amount is None or (isinstance(amount, str) and not amount.strip()):
        raise ValueError("Amount is required")

    clean = str(amount).replace('$', '').replace(',', '').strip()

    try:
        value = float(clean)
    except ValueError:
        raise ValueError(f"Invalid amount: {amount}")

    if value < 0:
        raise ValueError("Amount cannot be negative")

    return round(value, 2)


# ─── General Sanitiser ───────────────────────────────────────────────────────

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Remove control characters and limit length.

    >>> sanitize_input("Hello\\x00World")
    'HelloWorld'
    """
    if not text or not isinstance(text, str):
        return ""
    clean = ''.join(ch for ch in text if ch.isprintable() or ch in '\n\t')
    return clean[:max_length]


# ─── URL ──────────────────────────────────────────────────────────────────────

def validate_url(url: str, allowed_protocols: list = None) -> str:
    """
    Validate URL format and protocol.

    >>> validate_url("https://example.com")
    'https://example.com'
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL is required")
    if allowed_protocols is None:
        allowed_protocols = ['http', 'https']

    pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url, re.IGNORECASE):
        raise ValueError(f"Invalid URL format: {url}")

    protocol = url.split(':')[0].lower()
    if protocol not in allowed_protocols:
        raise ValueError(f"Protocol '{protocol}' not allowed. Allowed: {allowed_protocols}")

    return url


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _demo():
    """Run interactive demo of all validators."""
    print("=" * 50)
    print("  Australian Validation Helpers — Demo")
    print("=" * 50)

    tests = [
        ("Email", validate_email, "cleanupbros.au@gmail.com"),
        ("Phone (local)", validate_phone, "+61406764585"),
        ("Phone (intl)", to_international_phone, "0406764585"),
        ("ABN", validate_abn, "26 443 426 374"),
        ("BSB", validate_bsb, "062000"),
        ("Amount", validate_amount, "$1,234.56"),
    ]

    for label, fn, sample in tests:
        try:
            result = fn(sample)
            print(f"  ✅ {label:18s}  {sample!r:>25s}  →  {result}")
        except Exception as e:
            print(f"  ❌ {label:18s}  {sample!r:>25s}  →  {e}")


if __name__ == "__main__":
    if "--test" in sys.argv:
        import doctest
        results = doctest.testmod(verbose=True)
        sys.exit(0 if results.failed == 0 else 1)
    else:
        _demo()
