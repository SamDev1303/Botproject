#!/usr/bin/env python3
"""
LinkedIn MCP Server - Professional Networking
For Clean Up Bros B2B marketing and professional presence

Features:
- Profile management
- Text, image, and article posts (v2 API)
- Connection request message generation
- Content templates for cleaning industry
- OAuth setup flow
- Company page management
"""
import os
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from mcp.shared_utils import load_env
from mcp.logging_config import setup_logging
from mcp.validation import sanitize_input, validate_url

# Setup logging
logger = setup_logging(__name__)

# Load environment
load_env()

CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET', '')
ACCESS_TOKEN = os.environ.get('LINKEDIN_ACCESS_TOKEN', '')
LINKEDIN_ORG_ID = os.environ.get('LINKEDIN_ORG_ID', '')  # Company page ID
BASE_URL = "https://api.linkedin.com/v2"


def api_request(endpoint, method="GET", data=None, extra_headers=None):
    """Make LinkedIn API request with proper error handling"""
    if not ACCESS_TOKEN:
        return {"error": "LINKEDIN_ACCESS_TOKEN not set. Run linkedin_oauth_url() to set up OAuth."}

    url = f"{BASE_URL}{endpoint}"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202401",
    }
    if extra_headers:
        headers.update(extra_headers)

    body = json.dumps(data).encode() if data else None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode()
            result = json.loads(raw) if raw else {}
            logger.info(f"LinkedIn {method} {endpoint[:60]} - Success")
            return result
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:300]
        logger.error(f"LinkedIn {method} {endpoint[:60]} - {e.code}: {error_msg}")
        return {"error": f"HTTP {e.code}: {error_msg}"}
    except urllib.error.URLError as e:
        logger.error(f"LinkedIn {method} {endpoint[:60]} - URL Error: {e.reason}")
        return {"error": f"Connection error: {e.reason}"}
    except TimeoutError:
        logger.error(f"LinkedIn {method} {endpoint[:60]} - Timeout")
        return {"error": "Request timed out"}


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
    user_id = result.get('id', 'unknown')

    return f"""LinkedIn Profile:

Name: {first} {last}
ID: {user_id}
URN: urn:li:person:{user_id}"""


# ============== POSTING ==============

@mcp.tool()
def linkedin_post(text: str) -> str:
    """
    Create a LinkedIn post (text only).
    Great for business updates, tips, and engagement.
    Max 3000 characters.
    """
    text = sanitize_input(text, max_length=3000)
    if not text:
        return "Error: Post text is required"

    # Get user URN
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

    post_id = result.get('id', 'unknown')
    logger.info(f"LinkedIn post created: {post_id}")
    return f"Posted to LinkedIn!\nPost ID: {post_id}"


@mcp.tool()
def linkedin_post_with_link(text: str, article_url: str, title: str = "", description: str = "") -> str:
    """
    Share a link/article on LinkedIn with commentary.
    Great for sharing blog posts, case studies, or news.
    """
    text = sanitize_input(text, max_length=3000)
    if not text:
        return "Error: Post text is required"

    try:
        validate_url(article_url)
    except ValueError as e:
        return f"Error: Invalid URL - {e}"

    title = sanitize_input(title, max_length=200)
    description = sanitize_input(description, max_length=500)

    me_result = api_request("/me")
    if "error" in me_result:
        return f"Error getting profile: {me_result['error']}"

    user_urn = f"urn:li:person:{me_result.get('id')}"

    media_entry = {
        "status": "READY",
        "originalUrl": article_url,
    }
    if title:
        media_entry["title"] = {"text": title}
    if description:
        media_entry["description"] = {"text": description}

    data = {
        "author": user_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "ARTICLE",
                "media": [media_entry]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    result = api_request("/ugcPosts", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    post_id = result.get('id', 'unknown')
    logger.info(f"LinkedIn article post created: {post_id}")
    return f"Article shared on LinkedIn!\nPost ID: {post_id}"


@mcp.tool()
def linkedin_post_with_image(text: str, image_url: str) -> str:
    """
    Create a LinkedIn post with an image.
    Perfect for before/after shots, team photos, etc.

    Note: Posts the image as a link preview. For native image uploads,
    use the LinkedIn web interface.
    """
    text = sanitize_input(text, max_length=3000)
    if not text:
        return "Error: Post text is required"

    try:
        validate_url(image_url)
    except ValueError as e:
        return f"Error: Invalid image URL - {e}"

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

    post_id = result.get('id', 'unknown')
    logger.info(f"LinkedIn image post created: {post_id}")
    return f"Posted to LinkedIn with image!\nPost ID: {post_id}"


# ============== CONTENT TEMPLATES ==============

@mcp.tool()
def generate_linkedin_post(topic: str = "cleaning_tips") -> str:
    """
    Generate a professional LinkedIn post for Clean Up Bros.

    Topics: cleaning_tips, property_managers, business_update, before_after,
            hiring, milestone, industry_insight
    """
    templates = {
        "cleaning_tips": """3 Signs Your Office Needs a Professional Deep Clean:

1. Dust building up on air vents and surfaces faster than usual
2. Staff complaining about allergies or stale air
3. High-traffic areas showing visible wear and grime

A professional commercial clean doesn't just improve appearances - it boosts employee health and productivity.

At Clean Up Bros, we specialise in commercial cleaning for Sydney businesses.

Get a free quote: 0406 764 585
cleanupbros.com.au

#CommercialCleaning #SydneyBusiness #WorkplaceHealth #CleanUpBros""",

        "property_managers": """Attention Property Managers!

End of lease cleaning shouldn't be a headache.

We offer:
- Bond-back guarantee
- Same-day availability
- Professional, insured team
- Competitive rates for bulk bookings

We work with 50+ property managers across Western Sydney.

Let's chat about how we can make your job easier.

0406 764 585
cleanupbros.com.au

#PropertyManagement #EndOfLeaseCleaning #Sydney #RealEstate #CleanUpBros""",

        "business_update": """Exciting news from Clean Up Bros!

We've just completed our 500th end-of-lease clean this year!

Thank you to all the property managers, real estate agents, and tenants who trust us with their properties.

Zero bond failures. That's not a marketing line - that's our actual record.

Here's to sparkling clean spaces and happy clients!

#Milestone #CleaningServices #Sydney #SmallBusiness #CleanUpBros""",

        "before_after": """Transformation Tuesday!

Swipe to see what 4 hours of professional cleaning can do.

This 3-bedroom end of lease clean included:
- Deep kitchen clean (oven, rangehood, cabinets)
- Bathroom sanitisation
- Floor scrubbing and mopping
- Window cleaning
- Wall spot cleaning

Result? Full bond returned!

Book your clean: 0406 764 585

#BeforeAndAfter #EndOfLeaseCleaning #CleaningTransformation #CleanUpBros""",

        "hiring": """We're growing!

Clean Up Bros is looking for reliable, detail-oriented cleaners to join our team in Western Sydney.

What we offer:
- Competitive pay
- Flexible schedule
- Great team culture
- Training provided
- Consistent work

If you take pride in doing a thorough job and show up when you say you will, we want to hear from you.

DM or call: 0406 764 585

#Hiring #SydneyJobs #CleaningJobs #WesternSydney #CleanUpBros""",

        "milestone": """Reflecting on 2 years of Clean Up Bros.

What started as one person with a mop and a dream has become:
- 500+ satisfied clients
- 50+ property manager partnerships
- 100% bond-back rate
- A team I'm proud of

Biggest lesson? Show up on time, do what you say, and never cut corners.

Thank you to everyone who's trusted us.

- Hafsah Nuzhat, Director
Clean Up Bros

#SmallBusiness #Entrepreneurship #CleaningBusiness #SydneyBusiness""",

        "industry_insight": """The cleaning industry is changing.

Here's what I'm seeing in 2026:
- Demand for eco-friendly products is up 40%
- Property managers want reliability over price
- AI is helping us run our business (yes, we use it)
- Standards are getting higher - and that's a good thing

For us at Clean Up Bros, the formula hasn't changed:
Show up. Do the work. Be honest.

Technology helps, but it doesn't replace elbow grease.

What changes are you seeing in your industry?

#CleaningIndustry #SmallBusiness #BusinessInsights #CleanUpBros""",
    }

    if topic not in templates:
        return f"Error: Unknown topic '{topic}'. Available: {', '.join(templates.keys())}"

    return f"Suggested LinkedIn Post ({topic}):\n\n{templates[topic]}"


@mcp.tool()
def generate_outreach_message(contact_name: str, company: str, role: str = "Property Manager") -> str:
    """
    Generate a LinkedIn connection request message for B2B outreach.
    Max 300 characters for connection requests.
    """
    contact_name = sanitize_input(contact_name, max_length=100)
    company = sanitize_input(company, max_length=200)
    role = sanitize_input(role, max_length=100)

    if not contact_name:
        return "Error: Contact name is required"
    if not company:
        return "Error: Company name is required"

    # Short version for connection request (300 char limit)
    short_msg = f"Hi {contact_name}, I'm Hafsah from Clean Up Bros. We work with {role}s across Western Sydney. Would love to connect and see if we can help {company}. - Hafsah"

    # Longer follow-up for after connection
    long_msg = f"""Hi {contact_name},

Thanks for connecting! I'm the director of Clean Up Bros, a cleaning service that works with property managers across Western Sydney.

We specialise in end of lease and commercial cleaning, with a 100% bond-back guarantee.

I'd love to see if there's an opportunity to work together with {company}.

Best regards,
Hafsah Nuzhat
Clean Up Bros
0406 764 585"""

    return f"""Connection Request (max 300 chars):

{short_msg}
({len(short_msg)} characters)

Follow-up Message (after they connect):

{long_msg}"""


# ============== OAUTH SETUP ==============

@mcp.tool()
def linkedin_oauth_url() -> str:
    """Get the LinkedIn OAuth authorization URL"""
    if not CLIENT_ID:
        return "Error: LINKEDIN_CLIENT_ID not set in .env"

    redirect_uri = "http://localhost:8080/callback"
    scope = "openid profile email w_member_social"

    url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&scope={urllib.parse.quote(scope)}"
    )

    return f"""LinkedIn OAuth Setup:

1. Visit this URL in your browser:
   {url}

2. Authorise the application

3. Copy the 'code' parameter from the redirect URL

4. Run: linkedin_exchange_code('<code>')

Scopes requested: openid, profile, email, w_member_social"""


@mcp.tool()
def linkedin_exchange_code(code: str) -> str:
    """Exchange OAuth code for access token"""
    if not CLIENT_ID or not CLIENT_SECRET:
        return "Error: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in .env"

    code = sanitize_input(code, max_length=500).strip()
    if not code:
        return "Error: OAuth code is required"

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
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            token = result.get('access_token', '')
            expires_in = result.get('expires_in', 'unknown')

            if token:
                logger.info("LinkedIn OAuth token obtained successfully")
                return f"""LinkedIn Access Token obtained!

Add this to your ~/.clawdbot/.env file:
LINKEDIN_ACCESS_TOKEN={token}

Token expires in: {expires_in} seconds (~{int(expires_in)//86400 if isinstance(expires_in, int) else '?'} days)

After adding to .env, restart the LinkedIn MCP server."""
            else:
                return f"Error: No token in response: {json.dumps(result)[:200]}"
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:300]
        logger.error(f"LinkedIn OAuth exchange failed: {e.code}")
        return f"Error: {e.code}: {error_msg}"
    except urllib.error.URLError as e:
        return f"Error: Connection failed: {e.reason}"


@mcp.tool()
def linkedin_check_token() -> str:
    """Check if the LinkedIn access token is valid"""
    if not ACCESS_TOKEN:
        return "No LinkedIn access token configured. Run linkedin_oauth_url() to set up."

    result = api_request("/me")

    if "error" in result:
        return f"Token appears invalid or expired.\nError: {result['error']}\n\nRun linkedin_oauth_url() to get a new token."

    first = result.get('localizedFirstName', '')
    last = result.get('localizedLastName', '')

    return f"Token is valid! Authenticated as: {first} {last}"


if __name__ == "__main__":
    mcp.run()
