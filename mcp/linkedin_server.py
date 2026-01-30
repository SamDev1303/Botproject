#!/usr/bin/env python3
"""
LinkedIn MCP Server - Professional Networking
For Clean Up Bros B2B marketing and professional presence
"""
import os
import json
import urllib.request
import urllib.error
import urllib.parse
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

CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET', '')
ACCESS_TOKEN = os.environ.get('LINKEDIN_ACCESS_TOKEN', '')  # Need to set up OAuth
BASE_URL = "https://api.linkedin.com/v2"

def api_request(endpoint, method="GET", data=None):
    """Make LinkedIn API request"""
    url = f"{BASE_URL}{endpoint}"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    if data:
        data = json.dumps(data).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:200]}"}

# Create MCP server
mcp = FastMCP("LinkedIn")

# ============== PROFILE ==============

@mcp.tool()
def get_profile() -> str:
    """Get LinkedIn profile information"""
    result = api_request("/me")

    if "error" in result:
        return f"Error: {result['error']}"

    first = result.get('localizedFirstName', '')
    last = result.get('localizedLastName', '')

    return f"LinkedIn Profile: {first} {last}"

# ============== POSTING ==============

@mcp.tool()
def linkedin_post(text: str) -> str:
    """
    Create a LinkedIn post (text only).
    Great for business updates, tips, and engagement.
    """
    # First get the user URN
    me_result = api_request("/me")
    if "error" in me_result:
        return f"Error getting profile: {me_result['error']}"

    user_urn = f"urn:li:person:{me_result.get('id')}"

    data = {
        "author": user_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    result = api_request("/ugcPosts", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Posted to LinkedIn!\nPost ID: {result.get('id', 'unknown')}"

@mcp.tool()
def linkedin_post_with_image(text: str, image_url: str) -> str:
    """
    Create a LinkedIn post with an image.
    Perfect for before/after shots, team photos, etc.
    """
    me_result = api_request("/me")
    if "error" in me_result:
        return f"Error getting profile: {me_result['error']}"

    user_urn = f"urn:li:person:{me_result.get('id')}"

    # Register the image
    register_data = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": user_urn,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }

    register_result = api_request("/assets?action=registerUpload", method="POST", data=register_data)

    if "error" in register_result:
        return f"Error registering image: {register_result['error']}"

    # For simplicity, we'll use a link post with the image URL
    data = {
        "author": user_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "ARTICLE",
                "media": [{
                    "status": "READY",
                    "originalUrl": image_url
                }]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    result = api_request("/ugcPosts", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Posted to LinkedIn with image!\nPost ID: {result.get('id', 'unknown')}"

@mcp.tool()
def linkedin_post_article_link(text: str, article_url: str, title: str = "") -> str:
    """Share an article/link on LinkedIn"""
    me_result = api_request("/me")
    if "error" in me_result:
        return f"Error getting profile: {me_result['error']}"

    user_urn = f"urn:li:person:{me_result.get('id')}"

    data = {
        "author": user_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "ARTICLE",
                "media": [{
                    "status": "READY",
                    "originalUrl": article_url,
                    "title": {"text": title} if title else {}
                }]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    result = api_request("/ugcPosts", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Article shared on LinkedIn!\nPost ID: {result.get('id', 'unknown')}"

# ============== CONTENT TEMPLATES ==============

@mcp.tool()
def generate_linkedin_post(topic: str = "cleaning tips") -> str:
    """Generate a professional LinkedIn post for Clean Up Bros"""
    templates = {
        "cleaning tips": """3 Signs Your Office Needs a Professional Deep Clean:

1️⃣ Dust building up on air vents and surfaces faster than usual
2️⃣ Staff complaining about allergies or stale air
3️⃣ High-traffic areas showing visible wear and grime

A professional commercial clean doesn't just improve appearances—it boosts employee health and productivity.

At Clean Up Bros, we specialise in commercial cleaning for Sydney businesses.

📞 Get a free quote: 0406 764 585
🌐 cleanupbros.com.au

#CommercialCleaning #SydneyBusiness #WorkplaceHealth #CleanOffice #CleanUpBros""",

        "property managers": """Attention Property Managers! 🏢

End of lease cleaning shouldn't be a headache.

We offer:
✅ Bond-back guarantee
✅ Same-day availability
✅ Professional, insured team
✅ Competitive rates for bulk bookings

We work with 50+ property managers across Western Sydney.

Let's chat about how we can make your job easier.

📞 0406 764 585
🌐 cleanupbros.com.au

#PropertyManagement #EndOfLeaseCleaning #Sydney #RealEstate #CleanUpBros""",

        "business update": """Exciting news from Clean Up Bros! 🎉

We've just completed our 500th end-of-lease clean this year!

Thank you to all the property managers, real estate agents, and tenants who trust us with their properties.

Here's to sparkling clean spaces and happy clients!

#Milestone #CleaningServices #Sydney #SmallBusiness #Grateful""",

        "before after": """Transformation Tuesday! ✨

Swipe to see what 4 hours of professional cleaning can do.

This 3-bedroom end of lease clean included:
- Deep kitchen clean (oven, rangehood, cabinets)
- Bathroom sanitisation
- Floor scrubbing and mopping
- Window cleaning
- Wall spot cleaning

Result? Full bond returned! 💯

📞 Book your clean: 0406 764 585

#BeforeAndAfter #EndOfLeaseCleaning #Sydney #CleaningTransformation #CleanUpBros"""
    }

    if topic in templates:
        return f"Suggested LinkedIn Post:\n\n{templates[topic]}"
    else:
        return f"Suggested LinkedIn Post:\n\n{templates['cleaning tips']}"

@mcp.tool()
def generate_outreach_message(contact_name: str, company: str, role: str = "Property Manager") -> str:
    """Generate a LinkedIn connection request message for B2B outreach"""
    message = f"""Hi {contact_name},

I noticed you're a {role} at {company}. I'm the director of Clean Up Bros, a cleaning service that works with property managers across Western Sydney.

We specialise in end of lease and commercial cleaning, with a 100% bond-back guarantee.

I'd love to connect and see if there's an opportunity to work together.

Best regards,
Hafsah Nuzhat
Clean Up Bros
0406 764 585"""

    return f"Suggested Connection Message:\n\n{message}"

# ============== OAUTH SETUP ==============

@mcp.tool()
def linkedin_oauth_url() -> str:
    """Get the LinkedIn OAuth authorization URL"""
    redirect_uri = "http://localhost:8080/callback"
    scope = "r_liteprofile w_member_social"

    url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(redirect_uri)}&scope={urllib.parse.quote(scope)}"

    return f"""LinkedIn OAuth Setup:

1. Visit this URL in your browser:
   {url}

2. Authorize the application

3. Copy the 'code' parameter from the redirect URL

4. Run: linkedin_exchange_code('<code>')"""

@mcp.tool()
def linkedin_exchange_code(code: str) -> str:
    """Exchange OAuth code for access token"""
    redirect_uri = "http://localhost:8080/callback"

    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }).encode()

    req = urllib.request.Request(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            token = result.get('access_token', '')

            if token:
                return f"""LinkedIn Access Token obtained!

Add this to your .env file:
LINKEDIN_ACCESS_TOKEN={token}

Token expires in: {result.get('expires_in', 'unknown')} seconds"""
            else:
                return f"Error: {result}"
    except urllib.error.HTTPError as e:
        return f"Error: {e.code}: {e.read().decode()}"

if __name__ == "__main__":
    mcp.run()
