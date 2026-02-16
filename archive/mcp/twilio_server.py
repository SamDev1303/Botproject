#!/usr/bin/env python3
"""
Twilio MCP Server - SMS and Voice Calls
For Clean Up Bros communications and cold outreach
"""
import os
import json
import urllib.request
import urllib.error
import urllib.parse
import base64
from pathlib import Path
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from mcp.validation import validate_phone, sanitize_input
from mcp.logging_config import setup_logging

# Setup logging
logger = setup_logging(__name__)

# Load environment
def load_env():
    env_file = Path.home() / ".clawdbot" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))

load_env()

ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
FROM_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '+61483945127')  # Default AU number
BASE_URL = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}"

# Business contact details - NEVER use Twilio number for callbacks
BUSINESS_PHONE = os.environ.get('BUSINESS_PHONE', '')
BUSINESS_PHONE_INTL = os.environ.get('BUSINESS_PHONE_INTL', '')
WEBSITE = os.environ.get('BUSINESS_WEBSITE', 'cleanupbros.com.au')
HAFSAH_PHONE = os.environ.get('HAFSAH_PHONE', '')  # Forward ALL SMS copies to Hafsah

def api_request(endpoint, method="GET", data=None):
    """Make Twilio API request"""
    url = f"{BASE_URL}{endpoint}"

    # Basic auth
    credentials = base64.b64encode(f"{ACCOUNT_SID}:{AUTH_TOKEN}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    if data:
        data = urllib.parse.urlencode(data).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            logger.info(f"{method} {endpoint} - Success")
            return result
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:200]
        logger.error(f"{method} {endpoint} - {e.code}: {error_msg}")
        return {"error": f"{e.code}: {error_msg}"}

def format_au_number(phone):
    """Format phone number for Australian format"""
    phone = phone.replace(" ", "").replace("-", "")
    if not phone.startswith('+'):
        if phone.startswith('0'):
            phone = '+61' + phone[1:]
        elif phone.startswith('61'):
            phone = '+' + phone
        else:
            phone = '+61' + phone
    return phone

# Create MCP server
mcp = FastMCP("Twilio")

# ============== SMS ==============

def _send_sms_raw(to: str, message: str) -> dict:
    """Internal: Send SMS without forwarding (used for copies to Hafsah)"""
    data = {
        "To": to,
        "From": FROM_NUMBER,
        "Body": message
    }
    return api_request("/Messages.json", method="POST", data=data)

@mcp.tool()
def send_sms(to: str, message: str, forward_to_hafsah: bool = True) -> str:
    """
    Send an SMS message to a customer.
    Phone numbers: 0412345678 or +61412345678
    Automatically forwards a copy to Hafsah unless disabled.
    """
    # Validate and sanitize inputs
    try:
        validate_phone(to)
    except ValueError as e:
        logger.warning(f"Invalid phone number provided: {to}")
        return f"Error: {e}"

    message = sanitize_input(message, max_length=1600)  # SMS limit
    to = format_au_number(to)

    # Send to client
    result = _send_sms_raw(to, message)

    if "error" in result:
        logger.error(f"Failed to send SMS to {to}: {result['error']}")
        return f"Error: {result['error']}"

    logger.info(f"SMS sent to {to}, SID: {result.get('sid', 'unknown')}")
    output = f"""SMS sent to {to}
Message SID: {result.get('sid', 'unknown')}
Status: {result.get('status', 'unknown')}"""

    # Forward copy to Hafsah
    if forward_to_hafsah:
        copy_msg = f"[COPY TO {to}]\n{message}"
        copy_result = _send_sms_raw(HAFSAH_PHONE, copy_msg)
        if "error" not in copy_result:
            logger.info("SMS copy forwarded to Hafsah")
            output += "\n📋 Copy forwarded to Hafsah"

    return output

@mcp.tool()
def send_booking_confirmation(to: str, client_name: str, date: str, time: str, address: str, service: str) -> str:
    """Send a booking confirmation SMS"""
    to = format_au_number(to)

    message = f"""Hi {client_name}!

Your Clean Up Bros booking is confirmed:

Date: {date}
Time: {time}
Service: {service}
Address: {address}

Questions? Reply to this message or call 0406 764 585.

See you soon!
- Clean Up Bros"""

    return send_sms(to, message)

@mcp.tool()
def send_reminder(to: str, client_name: str, date: str, time: str) -> str:
    """Send a booking reminder SMS (24 hours before)"""
    to = format_au_number(to)

    message = f"""Hi {client_name}!

Just a reminder - your cleaning is tomorrow:

Date: {date}
Time: {time}

Please ensure access is available. See you soon!

- Clean Up Bros
0406 764 585"""

    return send_sms(to, message)

@mcp.tool()
def send_payment_reminder(to: str, client_name: str, amount: float, invoice_id: str = "") -> str:
    """Send a payment reminder SMS"""
    to = format_au_number(to)

    inv_ref = f" (Invoice #{invoice_id})" if invoice_id else ""

    bank_name = os.environ.get('BANK_NAME', '')
    bank_bsb = os.environ.get('BANK_BSB', '')
    bank_account = os.environ.get('BANK_ACCOUNT', '')

    message = f"""Hi {client_name},

Friendly reminder that payment of ${amount:.2f}{inv_ref} is due.

Pay online: https://square.link/cleanupbros
Bank: {bank_name}, BSB: {bank_bsb}, Acc: {bank_account}

Questions? Call {BUSINESS_PHONE}

Thanks!
- Clean Up Bros"""

    return send_sms(to, message)

@mcp.tool()
def send_quote(to: str, client_name: str, service: str, price: float) -> str:
    """Send a quote via SMS"""
    to = format_au_number(to)

    message = f"""Hi {client_name}!

Thanks for your enquiry. Here's your quote:

Service: {service}
Price: ${price:.2f} (incl. GST)

Ready to book? Reply YES or call 0406 764 585.

Valid for 7 days.
- Clean Up Bros"""

    return send_sms(to, message)

@mcp.tool()
def send_review_request(to: str, client_name: str) -> str:
    """Send a review request SMS after job completion"""
    to = format_au_number(to)

    message = f"""Hi {client_name}!

Thanks for choosing Clean Up Bros!

We'd love your feedback - it really helps:
https://g.page/r/cleanupbros/review

As a thank you, mention this text for 10% off your next clean!

- The Clean Up Bros Team"""

    return send_sms(to, message)

@mcp.tool()
def list_recent_sms(limit: int = 10) -> str:
    """List recent SMS messages"""
    result = api_request(f"/Messages.json?PageSize={limit}")

    if "error" in result:
        return f"Error: {result['error']}"

    messages = result.get('messages', [])
    if not messages:
        return "No messages found."

    output = ["Recent SMS messages:", ""]
    for msg in messages:
        direction = "SENT" if msg.get('direction') == 'outbound-api' else "RECEIVED"
        date = msg.get('date_sent', '')[:16]
        to_from = msg.get('to') if direction == "SENT" else msg.get('from')
        body = msg.get('body', '')[:40] + "..." if len(msg.get('body', '')) > 40 else msg.get('body', '')
        status = msg.get('status', 'unknown')

        output.append(f"{direction} | {date} | {to_from}")
        output.append(f"  {body}")
        output.append(f"  Status: {status}")
        output.append("")

    return "\n".join(output)

# ============== VOICE CALLS ==============

@mcp.tool()
def make_call(to: str, message: str) -> str:
    """
    Make a voice call with text-to-speech message.
    Use for important reminders or cold outreach.
    """
    to = format_au_number(to)

    # TwiML for text-to-speech with Australian accent
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Nicole" language="en-AU">{message}</Say>
</Response>"""

    data = {
        "To": to,
        "From": FROM_NUMBER,
        "Twiml": twiml
    }

    result = api_request("/Calls.json", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"""Call initiated to {to}
Call SID: {result.get('sid', 'unknown')}
Status: {result.get('status', 'unknown')}"""

@mcp.tool()
def call_with_recording(to: str, intro_message: str) -> str:
    """
    Make a call that records the conversation.
    Good for cold outreach where you want to review responses.
    """
    to = format_au_number(to)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Nicole" language="en-AU">{intro_message}</Say>
    <Record maxLength="120" playBeep="true" />
    <Say voice="Polly.Nicole" language="en-AU">Thank you for your time. Goodbye!</Say>
</Response>"""

    data = {
        "To": to,
        "From": FROM_NUMBER,
        "Twiml": twiml,
        "Record": "true"
    }

    result = api_request("/Calls.json", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"""Call with recording initiated to {to}
Call SID: {result.get('sid', 'unknown')}
Recording will be available after call ends."""

@mcp.tool()
def cold_outreach_call(to: str, business_name: str, contact_name: str = "") -> str:
    """
    Make a cold outreach call to a property manager or business.
    Professional script for Clean Up Bros.
    IMPORTANT: Tells clients NOT to call back Twilio number.

    NOTE: For GROK-STYLE calls with ElevenLabs, use:
    cold_outreach_call_grok() instead - it's faster and punchier.
    """
    to = format_au_number(to)

    name_part = f" May I speak with {contact_name}?" if contact_name else ""

    script = f"""Hello!{name_part} This is a quick call from Clean Up Bros, Sydney's trusted cleaning service.

We specialise in end of lease and commercial cleaning for {business_name}.
Many property managers in your area use us for reliable, bond-back guaranteed cleans.

Please note - this is an automated line, so don't call back this number.

To reach us, call {BUSINESS_PHONE} or visit {WEBSITE}.

Thank you for your time!"""

    return make_call(to, script)

@mcp.tool()
def cold_outreach_call_grok(to: str, business_name: str, contact_name: str = "") -> str:
    """
    Make a GROK-STYLE cold call - fast, punchy, witty, no fluff.
    This is what Hafsah wants - like Grok AI personality.

    Uses faster TTS settings and punchy script.
    IMPORTANT: Tells clients NOT to call back Twilio number.
    """
    to = format_au_number(to)

    name_part = f"Is this {contact_name}? Perfect. " if contact_name else ""

    # GROK STYLE: Fast, direct, no corporate fluff
    script = f"""{name_part}Cold call. I know. 15 seconds max.

You're at {business_name}. You deal with cleaners. Some good. Most aren't.

I'm Hafsah. Clean Up Bros. End of lease. Zero bond failures. Ever.

Quick note - don't call this number back. It's automated.

Real number: {BUSINESS_PHONE}. That's {BUSINESS_PHONE}.

Found by Bella, our AI. Built by Shamal. I'm the human.

Later."""

    # Use Polly.Matthew for faster, punchier delivery (instead of Nicole)
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Matthew" language="en-AU">{script}</Say>
</Response>"""

    data = {
        "To": to,
        "From": FROM_NUMBER,
        "Twiml": twiml
    }

    result = api_request("/Calls.json", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"""GROK-STYLE call initiated to {to}
Call SID: {result.get('sid', 'unknown')}
Status: {result.get('status', 'unknown')}
Style: Fast, punchy, Grok personality"""

@mcp.tool()
def list_recent_calls(limit: int = 10) -> str:
    """List recent voice calls"""
    result = api_request(f"/Calls.json?PageSize={limit}")

    if "error" in result:
        return f"Error: {result['error']}"

    calls = result.get('calls', [])
    if not calls:
        return "No calls found."

    output = ["Recent calls:", ""]
    for call in calls:
        direction = "OUTBOUND" if 'outbound' in call.get('direction', '') else "INBOUND"
        date = call.get('start_time', '')[:16]
        to_from = call.get('to') if direction == "OUTBOUND" else call.get('from')
        duration = call.get('duration', '0')
        status = call.get('status', 'unknown')

        output.append(f"{direction} | {date} | {to_from}")
        output.append(f"  Duration: {duration}s | Status: {status}")
        output.append("")

    return "\n".join(output)

# ============== ACCOUNT ==============

@mcp.tool()
def check_twilio_balance() -> str:
    """Check Twilio account balance"""
    result = api_request("/Balance.json")

    if "error" in result:
        return f"Error: {result['error']}"

    balance = result.get('balance', '0')
    currency = result.get('currency', 'USD')

    return f"Twilio Balance: {currency} {balance}"

@mcp.tool()
def lookup_phone(phone: str) -> str:
    """Look up information about a phone number (carrier, type)"""
    phone = format_au_number(phone)

    url = f"https://lookups.twilio.com/v1/PhoneNumbers/{urllib.parse.quote(phone)}?Type=carrier"
    credentials = base64.b64encode(f"{ACCOUNT_SID}:{AUTH_TOKEN}".encode()).decode()

    req = urllib.request.Request(url, headers={"Authorization": f"Basic {credentials}"})

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            carrier = result.get('carrier', {})
            return f"""Phone Lookup: {result.get('phone_number')}
Country: {result.get('country_code')}
Carrier: {carrier.get('name', 'Unknown')}
Type: {carrier.get('type', 'Unknown')}"""
    except urllib.error.HTTPError as e:
        return f"Error: {e.code}"

if __name__ == "__main__":
    mcp.run()
