#!/usr/bin/env python3
"""
Input validation utilities for Bella MCP servers
Validates and sanitizes user inputs to prevent security vulnerabilities
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
        
    Example:
        >>> validate_email("test@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    if not email or not isinstance(email, str):
        return False
    
    # RFC 5322 simplified pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> str:
    """
    Validate and format Australian phone number.
    
    Args:
        phone: Phone number in various formats
        
    Returns:
        Formatted phone number (10 digits starting with 0)
        
    Raises:
        ValueError: If phone number is invalid
        
    Example:
        >>> validate_phone("0412345678")
        '0412345678'
        >>> validate_phone("+61412345678")
        '0412345678'
        >>> validate_phone("61412345678")
        '0412345678'
    """
    if not phone or not isinstance(phone, str):
        raise ValueError("Phone number is required")
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Handle Australian formats
    if len(digits) == 10 and digits.startswith('0'):
        return digits
    elif len(digits) == 11 and digits.startswith('61'):
        return '0' + digits[2:]
    elif len(digits) == 9:
        # Mobile without leading 0
        if digits.startswith('4'):
            return '0' + digits
    
    raise ValueError(f"Invalid Australian phone number: {phone}")


def validate_international_phone(phone: str) -> str:
    """
    Validate and format phone number to international format.
    
    Args:
        phone: Phone number in various formats
        
    Returns:
        International format (+61...)
        
    Raises:
        ValueError: If phone number is invalid
        
    Example:
        >>> validate_international_phone("0412345678")
        '+61412345678'
    """
    # First validate as Australian number
    local = validate_phone(phone)
    # Convert to international format
    return '+61' + local[1:]


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Remove dangerous characters and limit length.
    
    Removes control characters (except newline/tab) that could
    cause issues in SMS, emails, or database fields.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length (default 1000)
        
    Returns:
        Sanitized text
        
    Example:
        >>> sanitize_input("Hello\\x00World")
        'HelloWorld'
        >>> sanitize_input("A" * 2000, max_length=100)
        'AAAA...' (100 chars)
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove control characters except newline and tab
    clean = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    
    # Limit length
    return clean[:max_length]


def validate_amount(amount: str) -> float:
    """
    Validate and parse monetary amount.
    
    Args:
        amount: Amount string (may include $ and commas)
        
    Returns:
        Validated amount as float
        
    Raises:
        ValueError: If amount is invalid or negative
        
    Example:
        >>> validate_amount("$123.45")
        123.45
        >>> validate_amount("1,234.56")
        1234.56
    """
    if not amount:
        raise ValueError("Amount is required")
    
    # Remove currency symbols and whitespace
    clean = str(amount).replace('$', '').replace(',', '').strip()
    
    try:
        value = float(clean)
    except ValueError:
        raise ValueError(f"Invalid amount: {amount}")
    
    if value < 0:
        raise ValueError("Amount cannot be negative")
    
    return value


def validate_abn(abn: str) -> str:
    """
    Validate Australian Business Number (ABN).
    
    Args:
        abn: ABN to validate (with or without spaces)
        
    Returns:
        Formatted ABN (11 digits with spaces: XX XXX XXX XXX)
        
    Raises:
        ValueError: If ABN is invalid
        
    Example:
        >>> validate_abn("26 443 426 374")
        '26 443 426 374'
        >>> validate_abn("26443426374")
        '26 443 426 374'
    """
    if not abn:
        raise ValueError("ABN is required")
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', abn)
    
    if len(digits) != 11:
        raise ValueError(f"ABN must be 11 digits, got {len(digits)}")
    
    # ABN checksum validation (simplified)
    # Full validation would use the ABN algorithm
    # For now, just check format
    
    # Format: XX XXX XXX XXX
    return f"{digits[0:2]} {digits[2:5]} {digits[5:8]} {digits[8:11]}"


def validate_bsb(bsb: str) -> str:
    """
    Validate Australian BSB (Bank-State-Branch) number.
    
    Args:
        bsb: BSB to validate (with or without hyphen)
        
    Returns:
        Formatted BSB (XXX-XXX)
        
    Raises:
        ValueError: If BSB is invalid
        
    Example:
        >>> validate_bsb("062-000")
        '062-000'
        >>> validate_bsb("062000")
        '062-000'
    """
    if not bsb:
        raise ValueError("BSB is required")
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', bsb)
    
    if len(digits) != 6:
        raise ValueError(f"BSB must be 6 digits, got {len(digits)}")
    
    # Format: XXX-XXX
    return f"{digits[0:3]}-{digits[3:6]}"


def validate_url(url: str, allowed_protocols: Optional[list] = None) -> str:
    """
    Validate URL format and protocol.
    
    Args:
        url: URL to validate
        allowed_protocols: List of allowed protocols (default: ['http', 'https'])
        
    Returns:
        Validated URL
        
    Raises:
        ValueError: If URL is invalid or uses disallowed protocol
        
    Example:
        >>> validate_url("https://example.com")
        'https://example.com'
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL is required")
    
    if allowed_protocols is None:
        allowed_protocols = ['http', 'https']
    
    # Simple URL pattern
    pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url, re.IGNORECASE):
        raise ValueError(f"Invalid URL format: {url}")
    
    # Check protocol
    protocol = url.split(':')[0].lower()
    if protocol not in allowed_protocols:
        raise ValueError(f"Protocol '{protocol}' not allowed. Allowed: {allowed_protocols}")
    
    return url


if __name__ == "__main__":
    # Run doctests
    import doctest
    doctest.testmod()
