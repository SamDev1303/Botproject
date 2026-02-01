#!/usr/bin/env python3
"""
WhatsApp MCP Server - Business Messaging
For Clean Up Bros customer communication via WhatsApp Business API
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from mcp.server.fastmcp import FastMCP

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

ACCESS_TOKEN = os.environ.get('META_SYSTEM_USER_TOKEN', '')
PHONE_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
BUSINESS_ID = os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
BASE_URL = "https://graph.facebook.com/v18.0"

def api_request(endpoint, method="GET", data=None):
    """Make WhatsApp Business API request"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    if data:
        data = json.dumps(data).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:200]}"}

def format_au_number(phone):
    """Format phone number for WhatsApp (no + prefix)"""
    phone = phone.replace(" ", "").replace("-", "").replace("+", "")
    if phone.startswith('0'):
        phone = '61' + phone[1:]
    elif not phone.startswith('61'):
        phone = '61' + phone
    return phone

# Create MCP server
mcp = FastMCP("WhatsApp")

# ============== MESSAGING ==============

@mcp.tool()
def send_whatsapp(to: str, message: str) -> str:
    """
    Send a WhatsApp text message.
    Phone: 0412345678 or +61412345678
    """
    to = format_au_number(to)

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    result = api_request(f"/{PHONE_ID}/messages", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    msg_id = result.get('messages', [{}])[0].get('id', 'unknown')
    return f"""WhatsApp message sent to {to}
Message ID: {msg_id}"""

@mcp.tool()
def send_booking_confirmation_wa(to: str, client_name: str, date: str, time: str, address: str, service: str, price: float) -> str:
    """Send a booking confirmation via WhatsApp"""
    to = format_au_number(to)

    message = f"""*Booking Confirmed* ✅

Hi {client_name}!

Your Clean Up Bros booking is confirmed:

*Service:* {service}
*Date:* {date}
*Time:* {time}
*Address:* {address}
*Price:* ${price:.2f} (incl. GST)

We'll send a reminder 24 hours before.

Questions? Just reply to this message!

— Clean Up Bros 🧹"""

    return send_whatsapp(to, message)

@mcp.tool()
def send_quote_wa(to: str, client_name: str, service: str, price: float, notes: str = "") -> str:
    """Send a quote via WhatsApp"""
    to = format_au_number(to)

    notes_section = f"\n*Notes:* {notes}" if notes else ""

    message = f"""*Quote from Clean Up Bros* 📋

Hi {client_name}!

Thanks for your enquiry. Here's your quote:

*Service:* {service}
*Price:* ${price:.2f} (incl. GST){notes_section}

✅ Bond-back guarantee (end of lease)
✅ Eco-friendly products
✅ Fully insured

*Ready to book?* Reply with your preferred date and time!

This quote is valid for 7 days.

— Clean Up Bros 🧹
0406 764 585"""

    return send_whatsapp(to, message)

@mcp.tool()
def send_payment_reminder_wa(to: str, client_name: str, amount: float, days_overdue: int = 0) -> str:
    """Send a payment reminder via WhatsApp"""
    to = format_au_number(to)

    if days_overdue > 0:
        urgency = f"This payment is now *{days_overdue} days overdue*."
    else:
        urgency = "Payment is due soon."

    bank_bsb = os.environ.get('BANK_BSB', '')
    bank_account = os.environ.get('BANK_ACCOUNT', '')

    message = f"""*Payment Reminder* 💳

Hi {client_name},

{urgency}

*Amount Due:* ${amount:.2f}

*Payment Options:*
• Bank Transfer: BSB {bank_bsb}, Acc {bank_account}
• Pay Online: square.link/cleanupbros

Please reply once paid or if you have any questions.

Thanks!
— Clean Up Bros"""

    return send_whatsapp(to, message)

@mcp.tool()
def send_reminder_wa(to: str, client_name: str, date: str, time: str) -> str:
    """Send a booking reminder via WhatsApp"""
    to = format_au_number(to)

    message = f"""*Reminder: Cleaning Tomorrow* ⏰

Hi {client_name}!

Just a friendly reminder about your cleaning:

*Date:* {date}
*Time:* {time}

Please ensure:
✅ Access is available
✅ Valuables are secured
✅ Any specific areas are noted

See you tomorrow!
— Clean Up Bros 🧹"""

    return send_whatsapp(to, message)

@mcp.tool()
def send_completion_wa(to: str, client_name: str, amount: float) -> str:
    """Send a job completion message via WhatsApp"""
    to = format_au_number(to)

    bank_bsb = os.environ.get('BANK_BSB', '')
    bank_account = os.environ.get('BANK_ACCOUNT', '')

    message = f"""*Cleaning Complete* ✨

Hi {client_name}!

Great news - your clean is finished!

*Amount Due:* ${amount:.2f}

*Payment Options:*
• Bank Transfer: BSB {bank_bsb}, Acc {bank_account}
• Pay Online: square.link/cleanupbros

We hope you love your sparkling clean space!

If you're happy with our service, we'd really appreciate a review:
⭐ g.page/r/cleanupbros/review

Thanks for choosing Clean Up Bros!
— The Team 🧹"""

    return send_whatsapp(to, message)

@mcp.tool()
def send_review_request_wa(to: str, client_name: str) -> str:
    """Send a review request via WhatsApp"""
    to = format_au_number(to)

    message = f"""Hi {client_name}! 👋

Thanks again for choosing Clean Up Bros!

We'd love to hear how we did. Your feedback helps us improve and helps other customers find quality cleaners.

⭐ Leave a Review: g.page/r/cleanupbros/review

As a thank you, mention this message for *10% off* your next clean!

— Clean Up Bros 🧹"""

    return send_whatsapp(to, message)

@mcp.tool()
def send_template(to: str, template_name: str, components: list = None) -> str:
    """
    Send a WhatsApp template message (for marketing/proactive messages).
    Templates must be pre-approved by WhatsApp.
    """
    to = format_au_number(to)

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en_AU"}
        }
    }

    if components:
        data["template"]["components"] = components

    result = api_request(f"/{PHONE_ID}/messages", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    msg_id = result.get('messages', [{}])[0].get('id', 'unknown')
    return f"""Template message sent to {to}
Template: {template_name}
Message ID: {msg_id}"""

# ============== MEDIA ==============

@mcp.tool()
def send_image_wa(to: str, image_url: str, caption: str = "") -> str:
    """Send an image via WhatsApp"""
    to = format_au_number(to)

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption
        }
    }

    result = api_request(f"/{PHONE_ID}/messages", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Image sent to {to}"

@mcp.tool()
def send_document_wa(to: str, document_url: str, filename: str, caption: str = "") -> str:
    """Send a document (PDF, invoice) via WhatsApp"""
    to = format_au_number(to)

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "document",
        "document": {
            "link": document_url,
            "filename": filename,
            "caption": caption
        }
    }

    result = api_request(f"/{PHONE_ID}/messages", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Document '{filename}' sent to {to}"

# ============== BUSINESS PROFILE ==============

@mcp.tool()
def get_business_profile() -> str:
    """Get WhatsApp Business profile information"""
    result = api_request(f"/{PHONE_ID}/whatsapp_business_profile?fields=about,address,description,email,profile_picture_url,websites,vertical")

    if "error" in result:
        return f"Error: {result['error']}"

    data = result.get('data', [{}])[0]
    return f"""WhatsApp Business Profile:
About: {data.get('about', 'N/A')}
Description: {data.get('description', 'N/A')}
Email: {data.get('email', 'N/A')}
Address: {data.get('address', 'N/A')}
Websites: {', '.join(data.get('websites', ['N/A']))}"""

@mcp.tool()
def list_templates() -> str:
    """List available WhatsApp message templates"""
    result = api_request(f"/{BUSINESS_ID}/message_templates")

    if "error" in result:
        return f"Error: {result['error']}"

    templates = result.get('data', [])
    if not templates:
        return "No templates found."

    output = ["Available WhatsApp Templates:", ""]
    for t in templates:
        status = t.get('status', 'unknown')
        output.append(f"• {t.get('name')} ({status})")
        output.append(f"  Category: {t.get('category', 'N/A')}")

    return "\n".join(output)

if __name__ == "__main__":
    mcp.run()
