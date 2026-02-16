#!/usr/bin/env python3
"""
Ref.tools MCP Server - Reference Data & Business Lookups
For Clean Up Bros business verification and competitor research

Uses Ref.tools API for Australian business data lookups.
Also provides quick-reference tools for common business queries.
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from mcp.shared_utils import load_env, api_get
from mcp.logging_config import setup_logging
from mcp.validation import validate_abn, sanitize_input

# Setup logging
logger = setup_logging(__name__)

# Load environment
load_env()

REF_API_URL = os.environ.get('REF_API_URL', 'https://api.ref.tools/mcp')

# Create server
mcp = FastMCP("RefTools")


@mcp.tool()
def lookup_abn(abn: str) -> str:
    """
    Look up an Australian Business Number (ABN) via ABR.

    Returns business name, status, entity type, GST registration, and location.
    Useful for verifying new clients or checking competitor details.
    """
    abn = sanitize_input(abn, max_length=20).strip()

    try:
        formatted_abn = validate_abn(abn)
    except ValueError as e:
        return f"Error: {e}"

    digits = formatted_abn.replace(" ", "")
    url = f"https://abr.business.gov.au/json/AbnDetails.aspx?abn={digits}&callback=_"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read().decode()
            # ABR returns JSONP, strip the callback wrapper
            json_str = raw.strip()
            if json_str.startswith("_"):
                json_str = json_str[2:-1]  # Remove _( and )
            data = json.loads(json_str)

            if "Message" in data and data["Message"]:
                return f"ABR Error: {data['Message']}"

            name = data.get("EntityName", "Unknown")
            status = data.get("AbnStatus", "Unknown")
            entity_type = data.get("EntityTypeCode", "Unknown")
            gst = data.get("Gst", "Unknown")
            state = data.get("AddressState", "Unknown")
            postcode = data.get("AddressPostcode", "Unknown")

            return f"""ABN Lookup: {formatted_abn}

Business Name: {name}
Status: {status}
Entity Type: {entity_type}
GST Registered: {gst}
State: {state}
Postcode: {postcode}"""

    except urllib.error.HTTPError as e:
        logger.error(f"ABR lookup failed: {e.code}")
        return f"Error looking up ABN: HTTP {e.code}"
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        logger.error(f"ABR lookup failed: {e}")
        return f"Error looking up ABN: {e}"


@mcp.tool()
def quick_gst_calc(total: float) -> str:
    """
    Quick GST calculator (Australian).

    Given a GST-inclusive total, returns the GST amount and ex-GST price.
    Formula: GST = Total / 11
    """
    if total <= 0:
        return "Error: Total must be a positive number"

    gst = total / 11
    ex_gst = total - gst

    return f"""GST Calculation:

Total (inc. GST): ${total:,.2f}
GST Amount: ${gst:,.2f}
Ex-GST Amount: ${ex_gst:,.2f}

Formula: GST = Total / 11"""


@mcp.tool()
def pricing_reference(service: str = "all") -> str:
    """
    Quick pricing reference for Clean Up Bros services.

    Service: all, general, eol_1br, eol_2br, eol_3br, airbnb
    """
    prices = {
        "general": ("General Cleaning", 180, "2-3 hours"),
        "eol_1br": ("End of Lease 1BR", 280, "3-4 hours"),
        "eol_2br": ("End of Lease 2BR", 380, "4-5 hours"),
        "eol_3br": ("End of Lease 3BR", 480, "5-6 hours"),
        "airbnb": ("Airbnb Turnover", 120, "1-2 hours"),
    }

    extras = {
        "Oven deep clean": 50,
        "Carpet steam (per room)": 60,
        "Wall washing": 80,
        "Garage/storage": 40,
    }

    if service != "all" and service in prices:
        name, price, duration = prices[service]
        gst = price / 11
        ex_gst = price - gst
        return f"""{name}:
  Price: ${price} (inc. GST)
  GST: ${gst:.2f}
  Ex-GST: ${ex_gst:.2f}
  Duration: {duration}"""

    output = ["Clean Up Bros Pricing:", ""]
    for key, (name, price, duration) in prices.items():
        gst = price / 11
        output.append(f"  {name}: ${price} (GST ${gst:.2f}) - {duration}")

    output.extend(["", "Extras:"])
    for name, price in extras.items():
        output.append(f"  {name}: +${price}")

    output.extend(["", "Payment: Due within 7 days | Late fee: $50 after 14 days"])

    return "\n".join(output)


@mcp.tool()
def bas_quarter_info() -> str:
    """
    Get current BAS quarter information and due dates.
    Useful for quick reference when preparing quarterly BAS.
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo

    now = datetime.now(ZoneInfo("Australia/Sydney"))
    month = now.month

    # Determine current quarter (Australian financial year: Jul-Jun)
    if month in (7, 8, 9):
        quarter = "Q1"
        period = "1 Jul - 30 Sep"
        due = "28 October"
    elif month in (10, 11, 12):
        quarter = "Q2"
        period = "1 Oct - 31 Dec"
        due = "28 January"
    elif month in (1, 2, 3):
        quarter = "Q3"
        period = "1 Jan - 31 Mar"
        due = "28 April"
    else:
        quarter = "Q4"
        period = "1 Apr - 30 Jun"
        due = "28 July"

    return f"""Current BAS Quarter: {quarter} ({now.year})

Period: {period}
Due Date: {due}
Today: {now.strftime('%d/%m/%Y')}

BAS Labels:
  G1: Total sales (GST inclusive)
  G10: Capital purchases
  G11: Non-capital purchases
  GST on Sales: G1 / 11
  GST Credits: (G10 + G11) / 11
  GST Owing: GST on Sales - GST Credits"""


if __name__ == "__main__":
    mcp.run()
