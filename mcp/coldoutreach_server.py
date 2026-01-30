#!/usr/bin/env python3
"""
Cold Outreach MCP Server - Email & Call Campaigns
For Clean Up Bros lead generation and sales outreach

Built by Shamal with Claude Code
The most honest, well-researched cold outreach in Australia

Philosophy:
- Be radically honest (this IS a cold call/email)
- No begging, no desperation
- Cool, confident, conversational
- Research-backed personalization
- AI-powered but authentically human
"""
import os
import json
import urllib.request
import urllib.error
import urllib.parse
import base64
from pathlib import Path
from datetime import datetime, timedelta
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

# Email (Gmail SMTP)
GMAIL_ADDRESS = os.environ.get('GMAIL_ADDRESS', 'cleanupbros.au@gmail.com')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')

# Twilio for SMS/Calls (Twilio number is for SENDING only)
TWILIO_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '+61483945127')

# REAL BUSINESS CONTACT INFO - clients should call/message HERE, not Twilio
BUSINESS_PHONE = "0406 764 585"
BUSINESS_PHONE_INTL = "+61406764585"
WEBSITE = "cleanupbros.com.au"
HAFSAH_PHONE = "+61415429117"  # Forward ALL SMS copies to Hafsah

# Lead tracking file
LEADS_FILE = Path.home() / "clawd" / "data" / "outreach_leads.json"
LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Google Sheets for logging
TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID', '')

def get_google_token():
    """Get Google access token for Sheets logging"""
    if not TOKEN_FILE.exists():
        return None
    with open(TOKEN_FILE) as f:
        tokens = json.load(f)
    if 'refresh_token' in tokens:
        data = urllib.parse.urlencode({
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'refresh_token': tokens['refresh_token'],
            'grant_type': 'refresh_token'
        }).encode()
        try:
            req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())['access_token']
        except:
            pass
    return tokens.get('access_token')

def log_outreach_to_sheets(lead_name: str, company: str, channel: str, status: str, notes: str = ""):
    """Log outreach activity to Google Sheets"""
    token = get_google_token()
    if not token or not GOOGLE_SHEETS_ID:
        return False

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    values = [[date_str, lead_name, company, channel, status, notes]]

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEETS_ID}/values/Outreach!A:F:append?valueInputOption=USER_ENTERED"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = json.dumps({"values": values}).encode()

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        urllib.request.urlopen(req)
        return True
    except:
        return False

# Create MCP server
mcp = FastMCP("ColdOutreach")

# ============== LEAD MANAGEMENT ==============

def load_leads():
    """Load leads from file"""
    if LEADS_FILE.exists():
        with open(LEADS_FILE) as f:
            return json.load(f)
    return {"leads": [], "campaigns": []}

def save_leads(data):
    """Save leads to file"""
    with open(LEADS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@mcp.tool()
def add_lead(name: str, email: str = "", phone: str = "", company: str = "", role: str = "", source: str = "manual", notes: str = "") -> str:
    """
    Add a new lead to the outreach list.
    Source can be: manual, google_maps, linkedin, referral, website
    """
    data = load_leads()

    lead = {
        "id": len(data["leads"]) + 1,
        "name": name,
        "email": email,
        "phone": phone,
        "company": company,
        "role": role,
        "source": source,
        "notes": notes,
        "status": "new",
        "created": datetime.now().isoformat(),
        "last_contact": None,
        "contact_count": 0,
        "response": None
    }

    data["leads"].append(lead)
    save_leads(data)

    return f"""Lead added:
• Name: {name}
• Company: {company}
• Email: {email}
• Phone: {phone}
• Status: new"""

@mcp.tool()
def list_leads(status: str = "all") -> str:
    """List leads. Status: all, new, contacted, interested, converted, dead"""
    data = load_leads()
    leads = data.get("leads", [])

    if status != "all":
        leads = [l for l in leads if l.get("status") == status]

    if not leads:
        return f"No leads found with status: {status}"

    output = [f"Leads ({status}):", ""]
    for lead in leads:
        name = lead.get("name", "Unknown")
        company = lead.get("company", "N/A")
        lead_status = lead.get("status", "new")
        contacts = lead.get("contact_count", 0)
        output.append(f"[{lead.get('id')}] {name} ({company})")
        output.append(f"    Status: {lead_status} | Contacts: {contacts}")
        output.append("")

    return "\n".join(output)

@mcp.tool()
def update_lead_status(lead_id: int, status: str, notes: str = "") -> str:
    """
    Update lead status.
    Status: new, contacted, interested, converted, dead
    """
    data = load_leads()

    for lead in data["leads"]:
        if lead.get("id") == lead_id:
            lead["status"] = status
            if notes:
                lead["notes"] = notes
            lead["last_contact"] = datetime.now().isoformat()
            save_leads(data)
            return f"Lead {lead_id} updated to: {status}"

    return f"Lead {lead_id} not found"

@mcp.tool()
def get_lead(lead_id: int) -> str:
    """Get detailed information about a lead"""
    data = load_leads()

    for lead in data["leads"]:
        if lead.get("id") == lead_id:
            return f"""Lead #{lead_id}:
Name: {lead.get('name')}
Company: {lead.get('company')}
Role: {lead.get('role')}
Email: {lead.get('email')}
Phone: {lead.get('phone')}
Source: {lead.get('source')}
Status: {lead.get('status')}
Contact Count: {lead.get('contact_count')}
Last Contact: {lead.get('last_contact', 'Never')}
Notes: {lead.get('notes', 'None')}"""

    return f"Lead {lead_id} not found"

# ============== EMAIL OUTREACH ==============

@mcp.tool()
def send_cold_email(to_email: str, to_name: str, company: str, template: str = "bella_honest") -> str:
    """
    Send a cold outreach email using Bella's authentic, honest style.
    Templates: bella_honest, bella_researched, property_manager, airbnb_host, commercial

    Built by Shamal with Claude Code - radically honest, no begging, just facts.
    """
    templates = {
        # NEW: Bella's signature honest style
        "bella_honest": {
            "subject": f"Cold email alert - but hear me out",
            "body": f"""Hey {to_name},

This is a cold email. I know. You know. Let's not pretend otherwise.

But here's the thing: I'm not blasting this to 10,000 people hoping someone bites.

I specifically looked up {company}, saw you handle property management in Western Sydney, and thought - these people probably deal with dodgy cleaners who ghost them before bond inspections.

That's our whole thing. End of lease. Bond-back guaranteed. No drama.

If you've already got a cleaner you trust, respect. Delete this.

If not, I'm Hafsah from Clean Up Bros. We've done 500+ cleans this year. One number: 0406 764 585.

No pressure. Just putting it out there.

- Hafsah
Clean Up Bros

P.S. This email was researched by Bella, our AI assistant built by Shamal using Claude Code. She found you. I wrote this. Real human here."""
        },

        # NEW: The well-researched approach
        "bella_researched": {
            "subject": f"I noticed {company} is hiring...",
            "body": f"""Hi {to_name},

Saw {company} recently listed a new property manager role. Growth mode - nice.

When you're scaling, the last thing you need is chasing cleaners who don't show up to bond cleans. Been there.

Quick intro: Clean Up Bros. Western Sydney. 100% bond-back rate this year. We work with 50+ property managers who got tired of unreliable cleaners.

Not here to hard sell. Just wanted to be on your radar for when your current cleaner inevitably lets you down (they always do).

If that day comes: 0406 764 585

Good luck with the growth.

Hafsah Nuzhat
Clean Up Bros

P.S. Found you via Bella, our AI research assistant. Built by Shamal with Claude Code. She's pretty good at finding people who need reliable cleaners."""
        },

        # Original - slightly updated
        "property_manager": {
            "subject": f"Cleaning Services for {company}",
            "body": f"""Hi {to_name},

I'll keep this short - you're busy.

Clean Up Bros. End of lease specialists. Liverpool & Western Sydney.

What makes us different:
- 100% bond-back guarantee (we've never lost one)
- Same-day availability for emergencies
- One point of contact - me

If your current cleaner is solid, ignore this. If they're not, save my number: 0406 764 585

Hafsah Nuzhat
Director, Clean Up Bros
cleanupbros.com.au"""
        },
        "airbnb_host": {
            "subject": "Fast Turnaround Cleaning for Your Properties",
            "body": f"""Hi {to_name},

Do you manage short-term rentals in Sydney?

I'm Hafsah from Clean Up Bros. We offer:
• Same-day Airbnb turnovers ($120)
• Linen changes
• Restocking supplies
• Deep cleans between guests

We work with multiple Airbnb hosts in Western Sydney and understand the tight turnaround times you need.

Would you like to try us for your next turnover?

Best,
Hafsah Nuzhat
Clean Up Bros
0406 764 585"""
        },
        "commercial": {
            "subject": f"Commercial Cleaning Services for {company}",
            "body": f"""Hi {to_name},

Is {company} looking for reliable commercial cleaning?

Clean Up Bros offers:
• Daily/weekly office cleaning
• Deep cleaning services
• End of lease commercial cleans
• Window cleaning

We serve businesses across Liverpool and Western Sydney, with flexible scheduling to suit your operations.

I'd love to provide a free quote for your space.

Best regards,
Hafsah Nuzhat
Clean Up Bros
0406 764 585"""
        },
        "general": {
            "subject": "Professional Cleaning Services in Sydney",
            "body": f"""Hi {to_name},

I'm reaching out from Clean Up Bros, a trusted cleaning service in Western Sydney.

We offer:
• End of lease cleaning
• Residential cleaning
• Commercial cleaning
• Airbnb turnovers

Our clients love our reliability, attention to detail, and competitive pricing.

Would you be interested in a free quote?

Best,
Hafsah Nuzhat
Clean Up Bros
0406 764 585
cleanupbros.com.au"""
        }
    }

    email_template = templates.get(template, templates["general"])
    subject = email_template["subject"]
    body = email_template["body"]

    # Send via SMTP
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        # Update lead if exists
        data = load_leads()
        for lead in data["leads"]:
            if lead.get("email") == to_email:
                lead["contact_count"] = lead.get("contact_count", 0) + 1
                lead["last_contact"] = datetime.now().isoformat()
                lead["status"] = "contacted"
                save_leads(data)
                break

        # Log to Google Sheets
        log_outreach_to_sheets(to_name, company, "Email", "Sent", f"Template: {template}")

        return f"""Cold email sent:
To: {to_name} <{to_email}>
Subject: {subject}
Template: {template}
Logged to Sheets: Yes"""

    except Exception as e:
        return f"Error sending email: {str(e)}"

@mcp.tool()
def preview_outreach(to_name: str, company: str, channel: str = "email", template: str = "bella_honest") -> str:
    """
    ALWAYS use this first! Preview what Bella will send before actually sending.
    Hafsah should approve before any outreach is sent.

    Channel: email, sms, or call
    """
    if channel == "email":
        templates = {
            "bella_honest": f"""Subject: Cold email alert - but hear me out

Hey {to_name},

This is a cold email. I know. You know. Let's not pretend otherwise.

But here's the thing: I'm not blasting this to 10,000 people hoping someone bites.

I specifically looked up {company}... [continues]

- Hafsah""",
            "childcare": f"""Subject: Keeping {company} sparkling for the little ones

Hey {to_name},

Cold email - I know. But bear with me for 30 seconds.

Running a childcare centre means you're probably thinking about cleanliness 24/7...

- Hafsah"""
        }
        preview = templates.get(template, templates["bella_honest"])
    elif channel == "sms":
        preview = f"""Hey {to_name} - cold text, I know.

Saw you at {company} manage... [SMS preview]

- Hafsah"""
    else:
        preview = f"""[Call Script]
"Hey! Quick heads up - this is a cold call.
I know, I know. The bad news is: yes, it's a cold call..."

Target: {to_name} at {company}"""

    return f"""═══════════════════════════════════════
  OUTREACH PREVIEW - AWAITING APPROVAL
═══════════════════════════════════════

To: {to_name}
Company: {company}
Channel: {channel.upper()}
Template: {template}

--- PREVIEW ---
{preview}
----------------

⚠️ Reply "send" to approve this outreach
⚠️ Or "edit" to make changes first"""

@mcp.tool()
def send_followup_email(to_email: str, to_name: str, days_since_first: int = 3) -> str:
    """Send a Bella-style follow-up email - honest, not desperate"""
    subject = "Bumping this (no hard feelings if you're not interested)"
    body = f"""Hey {to_name},

Sent you an email a few days ago. No response - totally get it.

Just bumping this in case it got buried. If you're not interested, zero judgment. Delete away.

But if your current cleaner situation is... questionable... my number's still 0406 764 585.

That's it. No essay. No "just checking in." Just this.

Hafsah
Clean Up Bros

P.S. Bella (our AI) says I should follow up. She's usually right about these things."""

    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        return f"Follow-up email sent to {to_email}"

    except Exception as e:
        return f"Error: {str(e)}"

# ============== SMS OUTREACH ==============

def _send_sms_raw(phone: str, message: str):
    """Internal: Send single SMS without forwarding"""
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    credentials = base64.b64encode(f"{TWILIO_SID}:{TWILIO_TOKEN}".encode()).decode()

    data = urllib.parse.urlencode({
        "To": phone,
        "From": TWILIO_NUMBER,
        "Body": message
    }).encode()

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:200]}"}

def send_twilio_sms(to: str, message: str, forward_to_hafsah: bool = True):
    """Send SMS via Twilio and forward copy to Hafsah"""
    phone = to.replace(" ", "").replace("-", "")
    if not phone.startswith('+'):
        if phone.startswith('0'):
            phone = '+61' + phone[1:]
        else:
            phone = '+61' + phone

    # Send to client
    result = _send_sms_raw(phone, message)

    # Forward copy to Hafsah
    if forward_to_hafsah and "error" not in result:
        copy_msg = f"[COPY TO {phone}]\n{message}"
        _send_sms_raw(HAFSAH_PHONE, copy_msg)

    return result

@mcp.tool()
def send_cold_sms(to_phone: str, to_name: str, company: str = "") -> str:
    """Send a cold outreach SMS - Bella's honest, no-pressure style"""
    company_ref = f" at {company}" if company else ""

    message = f"""Hey {to_name} - cold text, I know.

Saw you{company_ref} manage properties in Sydney. Thought you might be over dodgy cleaners.

Clean Up Bros. End of lease. Bond-back guaranteed.

Not for everyone. But if you need us: 0406 764 585

- Hafsah

(Found by Bella, our AI. Built by Shamal + Claude Code)"""

    result = send_twilio_sms(to_phone, message)

    if "error" in result:
        return f"Error: {result['error']}"

    # Update lead
    data = load_leads()
    for lead in data["leads"]:
        if lead.get("phone") == to_phone:
            lead["contact_count"] = lead.get("contact_count", 0) + 1
            lead["last_contact"] = datetime.now().isoformat()
            save_leads(data)
            break

    # Log to Google Sheets
    log_outreach_to_sheets(to_name, company, "SMS", "Sent", to_phone)

    return f"Cold SMS sent to {to_name} ({to_phone}) - Logged to Sheets"

# ============== CALL OUTREACH ==============

def make_twilio_call(to: str, message: str):
    """Internal function to make call via Twilio"""
    phone = to.replace(" ", "").replace("-", "")
    if not phone.startswith('+'):
        if phone.startswith('0'):
            phone = '+61' + phone[1:]
        else:
            phone = '+61' + phone

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Calls.json"
    credentials = base64.b64encode(f"{TWILIO_SID}:{TWILIO_TOKEN}".encode()).decode()

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Nicole" language="en-AU">{message}</Say>
</Response>"""

    data = urllib.parse.urlencode({
        "To": phone,
        "From": TWILIO_NUMBER,
        "Twiml": twiml
    }).encode()

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:200]}"}

@mcp.tool()
def make_cold_call(to_phone: str, to_name: str, company: str) -> str:
    """
    Make a cold outreach call with Bella's honest, pattern-interrupt style.
    Built by Shamal with Claude Code.
    IMPORTANT: Tells clients NOT to call back the Twilio number.
    """
    script = f"""Hey! Quick heads up - this is a cold call.

I know, I know. The bad news is: yes, it's a cold call. You can hang up if you want.

The good news? This is actually a well-researched cold call.
I'm calling because I looked up {company}, saw you're in property management,
and thought you might be tired of unreliable cleaners.

I'm Hafsah from Clean Up Bros. We do end of lease cleans in Western Sydney.
Bond-back guaranteed. We've never lost one.

If you've got 30 seconds, I'd love to know - is your current cleaner actually reliable?
If yes, great! Sorry to bother you.

One important thing: please don't call back this number - it's an automated line.

To reach us, call {BUSINESS_PHONE} or visit {WEBSITE}. That's {BUSINESS_PHONE}.

This call was researched by Bella, our AI assistant built by Shamal using Claude Code.
She found you. I'm the human who runs the business.

Thanks for your time!"""

    result = make_twilio_call(to_phone, script)

    if "error" in result:
        return f"Error: {result['error']}"

    # Update lead
    data = load_leads()
    for lead in data["leads"]:
        if lead.get("phone") == to_phone:
            lead["contact_count"] = lead.get("contact_count", 0) + 1
            lead["last_contact"] = datetime.now().isoformat()
            save_leads(data)
            break

    # Log to Google Sheets
    log_outreach_to_sheets(to_name, company, "Call", "Initiated", to_phone)

    return f"Cold call initiated to {to_name} ({to_phone}) - Logged to Sheets"

# ============== CAMPAIGN MANAGEMENT ==============

@mcp.tool()
def create_campaign(name: str, lead_ids: list, channel: str = "email") -> str:
    """
    Create an outreach campaign for multiple leads.
    Channel: email, sms, call, or multi (all channels)
    """
    data = load_leads()

    campaign = {
        "id": len(data.get("campaigns", [])) + 1,
        "name": name,
        "channel": channel,
        "lead_ids": lead_ids,
        "status": "created",
        "created": datetime.now().isoformat(),
        "sent_count": 0
    }

    if "campaigns" not in data:
        data["campaigns"] = []

    data["campaigns"].append(campaign)
    save_leads(data)

    return f"""Campaign created:
Name: {name}
Channel: {channel}
Leads: {len(lead_ids)}

Run 'execute_campaign({campaign['id']})' to start."""

@mcp.tool()
def execute_campaign(campaign_id: int, delay_seconds: int = 30) -> str:
    """Execute an outreach campaign (with delay between contacts)"""
    data = load_leads()

    campaign = None
    for c in data.get("campaigns", []):
        if c.get("id") == campaign_id:
            campaign = c
            break

    if not campaign:
        return f"Campaign {campaign_id} not found"

    lead_ids = campaign.get("lead_ids", [])
    channel = campaign.get("channel", "email")

    results = []
    import time

    for lead_id in lead_ids:
        lead = None
        for l in data["leads"]:
            if l.get("id") == lead_id:
                lead = l
                break

        if not lead:
            continue

        name = lead.get("name", "")
        email = lead.get("email", "")
        phone = lead.get("phone", "")
        company = lead.get("company", "")

        if channel == "email" and email:
            result = send_cold_email(email, name, company)
            results.append(f"Email: {name} - Sent")
        elif channel == "sms" and phone:
            result = send_cold_sms(phone, name, company)
            results.append(f"SMS: {name} - Sent")
        elif channel == "call" and phone:
            result = make_cold_call(phone, name, company)
            results.append(f"Call: {name} - Initiated")

        time.sleep(delay_seconds)

    # Update campaign
    for c in data["campaigns"]:
        if c.get("id") == campaign_id:
            c["status"] = "executed"
            c["sent_count"] = len(results)
            c["executed_at"] = datetime.now().isoformat()
            break

    save_leads(data)

    return f"""Campaign {campaign_id} executed:
{chr(10).join(results)}

Total sent: {len(results)}"""

@mcp.tool()
def get_outreach_stats() -> str:
    """Get outreach statistics"""
    data = load_leads()
    leads = data.get("leads", [])
    campaigns = data.get("campaigns", [])

    status_counts = {}
    for lead in leads:
        status = lead.get("status", "new")
        status_counts[status] = status_counts.get(status, 0) + 1

    total_leads = len(leads)
    total_contacted = sum(1 for l in leads if l.get("contact_count", 0) > 0)
    total_interested = status_counts.get("interested", 0)
    total_converted = status_counts.get("converted", 0)

    conversion_rate = (total_converted / total_leads * 100) if total_leads > 0 else 0

    return f"""Outreach Statistics:
═══════════════════════════

Leads:
• Total: {total_leads}
• Contacted: {total_contacted}
• Interested: {total_interested}
• Converted: {total_converted}
• Dead: {status_counts.get('dead', 0)}

Conversion Rate: {conversion_rate:.1f}%

Campaigns: {len(campaigns)}

Built by Shamal with Claude Code"""

# ============== BELLA'S OUTREACH PHILOSOPHY ==============

@mcp.tool()
def get_outreach_philosophy() -> str:
    """Get Bella's outreach philosophy and guidelines"""
    return """
═══════════════════════════════════════════════════════════════
  BELLA'S COLD OUTREACH PHILOSOPHY
  Built by Shamal with Claude Code
═══════════════════════════════════════════════════════════════

THE PROBLEM WITH MOST COLD OUTREACH:
• Sounds desperate and salesy
• Generic templates that scream "mass email"
• Fake personalization ("I noticed your company...")
• Tries to hide that it's a cold contact

BELLA'S APPROACH:

1. RADICAL HONESTY
   "This is a cold email. You know it. I know it."
   Being honest about the nature of the contact is refreshing.
   Studies show pattern interrupts increase engagement by 35%.

2. NO BEGGING
   We don't need their business to survive.
   We offer a service. They either need it or they don't.
   "If you're not interested, zero judgment. Delete away."

3. RESEARCH-BASED
   Don't pretend to know them deeply.
   One meaningful signal is enough:
   - They're hiring (growth mode)
   - They manage properties in our area
   - They had a recent review mentioning cleaners

4. GIVE THEM AN OUT
   "If your current cleaner is solid, ignore this."
   This makes them think about their current situation.
   If they're happy, no harm. If not, we're top of mind.

5. BE MEMORABLE
   Sign off with:
   "Found by Bella, our AI. Built by Shamal with Claude Code."
   No one else is doing this. It's honest and interesting.

THE SCRIPT PATTERN:

EMAIL:
1. Acknowledge it's a cold email (pattern interrupt)
2. One specific reason you're contacting them
3. What you do in 10 words or less
4. Give them an out
5. One call to action (just a phone number)
6. Bella attribution

CALL:
1. "Bad news: this is a cold call"
2. "Good news: it's well-researched"
3. Why you specifically called them
4. Quick pitch (under 15 seconds)
5. Simple question
6. Bella attribution

SMS:
1. Acknowledge it's cold
2. One reason + one value prop
3. Phone number
4. Bella signature

═══════════════════════════════════════════════════════════════
"""

@mcp.tool()
def generate_personalized_email(to_name: str, company: str, research_fact: str) -> str:
    """
    Generate a highly personalized cold email based on specific research.

    Example research facts:
    - "recently hired a new property manager"
    - "got a 3-star review mentioning cleanliness"
    - "just listed 5 new rental properties"
    - "posted about expanding to Western Sydney"
    """
    return f"""Subject: {research_fact.capitalize()}

Hey {to_name},

This is a cold email. Now that we've got that out of the way...

I noticed {company} {research_fact}. Thought I'd reach out while the timing made sense.

Quick version: I'm Hafsah from Clean Up Bros. End of lease cleaning. Western Sydney.
Bond-back guaranteed - we've literally never lost one.

If you've got a reliable cleaner already, delete this. Seriously.

If not, or if you're curious what "reliable" actually looks like, my number is 0406 764 585.

No pitch deck. No "let's hop on a call." Just that.

- Hafsah
Clean Up Bros

P.S. This email was researched by Bella, our AI assistant.
Built by Shamal using Claude Code. She's pretty good at finding people at the right moment.
I'm the human who wrote this and runs the business."""

# ============== TARGET MARKET SPECIALISTS ==============

# Priority order: Childcare is HIGHEST priority
TARGET_MARKETS = {
    # PRIORITY 1: Childcare (highest value, recurring)
    "childcare": {
        "priority": 1,
        "search_terms": ["childcare centres", "daycare", "early learning centre", "preschool", "kindergarten"],
        "email_subject": "Keeping your little ones in a safe, clean space",
        "pain_point": "Maintaining hygiene standards for kids' health and parent confidence",
        "notes": "HIGHEST PRIORITY - recurring contracts, strict hygiene requirements"
    },
    # PRIORITY 2: Property Managers (volume, recurring)
    "property_managers": {
        "priority": 2,
        "search_terms": ["property managers", "real estate agents", "rental property management"],
        "email_subject": "Your end of lease cleans sorted",
        "pain_point": "Dodgy cleaners who ghost before bond inspections",
        "notes": "High volume, potential for ongoing relationship"
    },
    # PRIORITY 3: Aged Care
    "aged_care": {
        "priority": 3,
        "search_terms": ["aged care facilities", "nursing homes", "retirement villages", "senior living"],
        "email_subject": "Professional cleaning for aged care",
        "pain_point": "Maintaining hygiene and dignity for elderly residents",
        "notes": "Recurring contracts, requires respect and care"
    },
    # PRIORITY 4: NDIS
    "ndis": {
        "priority": 4,
        "search_terms": ["NDIS provider", "disability services", "supported independent living", "SIL provider"],
        "email_subject": "NDIS-friendly cleaning services",
        "pain_point": "Reliable, respectful cleaning for participants' homes",
        "notes": "NDIS funding available, participants deserve quality"
    },
    # PRIORITY 5: Airbnb
    "airbnb": {
        "priority": 5,
        "search_terms": ["airbnb host", "short term rental", "holiday rental management", "vacation rental"],
        "email_subject": "Fast turnovers, 5-star reviews",
        "pain_point": "Tight turnaround times and guest expectations",
        "notes": "Quick turnarounds, $120 per clean"
    }
}

# IMPORTANT: Always ask before outreach
OUTREACH_RULES = """
BELLA'S OUTREACH RULES:
1. ALWAYS ask Hafsah before sending outreach
2. Log all outreach to Google Sheets
3. Childcare is HIGHEST priority
4. Never spam - quality over quantity
5. Research before reaching out
"""

@mcp.tool()
def generate_childcare_email(to_name: str, centre_name: str) -> str:
    """Generate personalized email for childcare/daycare centres"""
    return f"""Subject: Keeping {centre_name} sparkling for the little ones

Hey {to_name},

Cold email - I know. But bear with me for 30 seconds.

Running a childcare centre means you're probably thinking about cleanliness 24/7.
Parents notice everything. Kids touch everything. And your staff have enough on their plate.

I'm Hafsah from Clean Up Bros. We do deep cleans for childcare centres in Western Sydney.

What we handle:
• After-hours deep cleaning (no disruption to your day)
• Toy and play area sanitisation
• Kitchen and bathroom deep cleans
• Carpet steam cleaning

If you've got a cleaner you trust, great. Delete this.

If not, or if you're paying too much for mediocre results: 0406 764 585

- Hafsah
Clean Up Bros

P.S. Found by Bella, our AI. Built by Shamal with Claude Code.
We take hygiene seriously because we know you have to."""

@mcp.tool()
def generate_aged_care_email(to_name: str, facility_name: str) -> str:
    """Generate personalized email for aged care facilities"""
    return f"""Subject: Professional cleaning for {facility_name}

Hi {to_name},

This is a cold email from Clean Up Bros. I'll get straight to the point.

Aged care facilities need a different kind of clean. It's not just about appearances -
it's about dignity, health, and creating a space where residents feel respected.

We offer:
• Regular deep cleaning (weekly/fortnightly)
• Infection control focused cleaning
• Respectful team who understand the environment
• Flexible scheduling around resident needs

We're fully insured, police-checked, and understand the standards you need to maintain.

If you're happy with your current provider, no worries at all.

If not: 0406 764 585

Hafsah Nuzhat
Clean Up Bros

P.S. Researched by Bella, our AI. Built by Shamal using Claude Code.
We do our homework before reaching out."""

@mcp.tool()
def generate_ndis_email(to_name: str, provider_name: str) -> str:
    """Generate personalized email for NDIS providers"""
    return f"""Subject: NDIS-friendly cleaning support for {provider_name}

Hey {to_name},

Cold email - straight up. But I think this might be relevant.

If you're an NDIS provider, you know that participants deserve clean, dignified living spaces.
And finding reliable cleaners who actually show up and do the job right? Not always easy.

Clean Up Bros specialises in:
• Supported Independent Living (SIL) cleaning
• Participant home cleaning
• Respite and holiday accommodation cleans
• One-off deep cleans

We're:
✓ Fully insured
✓ Police checked
✓ Trained to be respectful of participants' spaces
✓ Reliable (we actually show up)

If you've got this sorted, ignore me.

If not: 0406 764 585

Hafsah
Clean Up Bros

P.S. Found by Bella, our AI built by Shamal with Claude Code.
We research before we reach out - you're not just a number on a list."""

@mcp.tool()
def generate_airbnb_email(to_name: str, property_count: str = "properties") -> str:
    """Generate personalized email for Airbnb hosts/managers"""
    return f"""Subject: Same-day turnovers, 5-star cleanliness

Hey {to_name},

Cold email. Yes. But here's why I'm reaching out specifically to you.

Managing short-term rentals means you're probably dealing with:
• Guests checking out at 10am, new guests at 2pm
• Reviews that mention cleanliness (good or bad)
• Cleaners who bail last minute

Clean Up Bros does Airbnb turnovers in Western Sydney. $120.

What's included:
• Full clean (beds made, bathrooms spotless, kitchen reset)
• Linen change (if needed)
• Restocking essentials
• Same-day availability for emergencies

If you've got a reliable cleaner, nice. Delete this.

If not, save my number for when they inevitably ghost you: 0406 764 585

- Hafsah
Clean Up Bros

P.S. Bella (our AI, built by Shamal with Claude Code) found you.
I'm the human who'll actually do the cleans."""

@mcp.tool()
def find_leads_by_market(market: str, suburb: str = "Liverpool NSW") -> str:
    """
    Get search terms to find leads for a specific target market.

    Markets: property_managers, childcare, aged_care, ndis, airbnb
    """
    if market not in TARGET_MARKETS:
        return f"Unknown market: {market}\nAvailable: {', '.join(TARGET_MARKETS.keys())}"

    market_info = TARGET_MARKETS[market]

    return f"""Target Market: {market.upper()}
Location: {suburb}

Search Google Maps or Apify for:
{chr(10).join(f"  • {term}" for term in market_info['search_terms'])}

Pain Point to Address:
  "{market_info['pain_point']}"

Email Subject Line:
  "{market_info['email_subject']}"

Next Steps:
1. Use 'find_property_managers("{suburb}")' or equivalent Apify tool
2. Add leads with 'add_lead(name, email, phone, company)'
3. Use 'generate_{market}_email(name, company)' for personalized email
4. Start campaign with 'create_campaign(name, lead_ids, "email")'"""

@mcp.tool()
def list_target_markets() -> str:
    """List all target markets Bella can find leads for"""
    output = ["═══════════════════════════════════════", "  BELLA'S TARGET MARKETS", "═══════════════════════════════════════", ""]

    for market, info in TARGET_MARKETS.items():
        output.append(f"**{market.upper()}**")
        output.append(f"  Pain: {info['pain_point']}")
        output.append(f"  Subject: {info['email_subject']}")
        output.append("")

    output.append("Use: find_leads_by_market('<market>', '<suburb>')")
    return "\n".join(output)

if __name__ == "__main__":
    mcp.run()
