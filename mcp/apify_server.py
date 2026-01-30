#!/usr/bin/env python3
"""
Apify MCP Server - Web Scraping & Automation
For Clean Up Bros lead generation and market research
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
import time
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

API_KEY = os.environ.get('APIFY_API_KEY', '')
BASE_URL = "https://api.apify.com/v2"

# Common Apify actors for business use
ACTORS = {
    "google_maps": "nwua9Gu5YrADL7ZDj",  # Google Maps Scraper
    "google_search": "nFJndFXA5zjCTuudP",  # Google Search Results
    "instagram": "shu8hvrXbJbY3Eb9W",  # Instagram Scraper
    "facebook": "KoJrdxrcBVpVPpJHl",  # Facebook Pages Scraper
    "linkedin": "hMvNSpz3JnHgl5jkh",  # LinkedIn Profile Scraper
    "website_content": "aYG0l9s7dbB7j3gbS",  # Website Content Crawler
    "email_extractor": "emastra~email-extractor",  # Email Extractor
}

def api_request(endpoint, method="GET", data=None):
    """Make Apify API request"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    if data:
        data = json.dumps(data).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:200]}"}

# Create MCP server
mcp = FastMCP("Apify")

# ============== GOOGLE MAPS ==============

@mcp.tool()
def search_google_maps(query: str, location: str = "Sydney, Australia", max_results: int = 20) -> str:
    """
    Search Google Maps for businesses.
    Great for finding property managers, real estate agents, commercial buildings.
    Example: search_google_maps("property managers", "Liverpool NSW")
    """
    actor_id = ACTORS["google_maps"]

    input_data = {
        "searchStringsArray": [query],
        "locationQuery": location,
        "maxCrawledPlacesPerSearch": max_results,
        "language": "en",
        "includeWebResults": False
    }

    # Start the actor run
    result = api_request(f"/acts/{actor_id}/runs", method="POST", data=input_data)

    if "error" in result:
        return f"Error: {result['error']}"

    run_id = result.get('data', {}).get('id')
    if not run_id:
        return "Error: Could not start scraper"

    # Wait for completion (poll every 5 seconds, max 2 minutes)
    for _ in range(24):
        time.sleep(5)
        status = api_request(f"/actor-runs/{run_id}")
        if status.get('data', {}).get('status') in ['SUCCEEDED', 'FAILED', 'ABORTED']:
            break

    if status.get('data', {}).get('status') != 'SUCCEEDED':
        return f"Scraper failed: {status.get('data', {}).get('status')}"

    # Get results
    dataset_id = status.get('data', {}).get('defaultDatasetId')
    results = api_request(f"/datasets/{dataset_id}/items?limit={max_results}")

    if "error" in results:
        return f"Error getting results: {results['error']}"

    output = [f"Google Maps Results for '{query}' in {location}:", ""]
    for item in results[:max_results]:
        name = item.get('title', 'Unknown')
        phone = item.get('phone', 'N/A')
        website = item.get('website', 'N/A')
        address = item.get('address', 'N/A')
        rating = item.get('totalScore', 'N/A')

        output.append(f"**{name}**")
        output.append(f"  Phone: {phone}")
        output.append(f"  Website: {website}")
        output.append(f"  Address: {address}")
        output.append(f"  Rating: {rating}")
        output.append("")

    return "\n".join(output)

@mcp.tool()
def find_property_managers(suburb: str = "Liverpool NSW") -> str:
    """Find property managers in a specific suburb for cold outreach"""
    return search_google_maps("property managers real estate", f"{suburb}, Australia", 15)

@mcp.tool()
def find_airbnb_hosts(suburb: str = "Sydney") -> str:
    """Find Airbnb/short-term rental managers for cleaning services outreach"""
    return search_google_maps("airbnb property management short term rental", f"{suburb}, Australia", 15)

@mcp.tool()
def find_commercial_buildings(suburb: str = "Sydney CBD") -> str:
    """Find commercial buildings/offices for commercial cleaning outreach"""
    return search_google_maps("commercial building office complex", f"{suburb}, Australia", 15)

# ============== GOOGLE SEARCH ==============

@mcp.tool()
def google_search(query: str, max_results: int = 10) -> str:
    """
    Search Google for information.
    Returns titles, URLs, and snippets.
    """
    actor_id = ACTORS["google_search"]

    input_data = {
        "queries": query,
        "maxPagesPerQuery": 1,
        "resultsPerPage": max_results,
        "languageCode": "en",
        "countryCode": "au"
    }

    result = api_request(f"/acts/{actor_id}/runs", method="POST", data=input_data)

    if "error" in result:
        return f"Error: {result['error']}"

    run_id = result.get('data', {}).get('id')

    # Wait for completion
    for _ in range(12):
        time.sleep(5)
        status = api_request(f"/actor-runs/{run_id}")
        if status.get('data', {}).get('status') in ['SUCCEEDED', 'FAILED', 'ABORTED']:
            break

    if status.get('data', {}).get('status') != 'SUCCEEDED':
        return "Search failed"

    dataset_id = status.get('data', {}).get('defaultDatasetId')
    results = api_request(f"/datasets/{dataset_id}/items?limit={max_results}")

    if not results or "error" in results:
        return "No results found"

    output = [f"Google Search: '{query}'", ""]
    for item in results[:max_results]:
        organic = item.get('organicResults', [])
        for r in organic[:max_results]:
            title = r.get('title', 'No title')
            url = r.get('url', '')
            snippet = r.get('description', '')[:100]
            output.append(f"• {title}")
            output.append(f"  {url}")
            output.append(f"  {snippet}...")
            output.append("")

    return "\n".join(output)

# ============== EMAIL EXTRACTION ==============

@mcp.tool()
def extract_emails_from_website(url: str) -> str:
    """Extract email addresses from a website"""
    actor_id = ACTORS["email_extractor"]

    input_data = {
        "startUrls": [{"url": url}],
        "maxDepth": 2,
        "maxRequests": 50
    }

    result = api_request(f"/acts/{actor_id}/runs", method="POST", data=input_data)

    if "error" in result:
        return f"Error: {result['error']}"

    run_id = result.get('data', {}).get('id')

    for _ in range(24):
        time.sleep(5)
        status = api_request(f"/actor-runs/{run_id}")
        if status.get('data', {}).get('status') in ['SUCCEEDED', 'FAILED', 'ABORTED']:
            break

    if status.get('data', {}).get('status') != 'SUCCEEDED':
        return "Email extraction failed"

    dataset_id = status.get('data', {}).get('defaultDatasetId')
    results = api_request(f"/datasets/{dataset_id}/items")

    if not results:
        return "No emails found"

    emails = set()
    for item in results:
        if 'emails' in item:
            emails.update(item['emails'])

    if not emails:
        return f"No emails found on {url}"

    return f"Emails found on {url}:\n" + "\n".join(f"• {email}" for email in emails)

# ============== WEBSITE SCRAPING ==============

@mcp.tool()
def scrape_website(url: str) -> str:
    """Scrape content from a website"""
    actor_id = ACTORS["website_content"]

    input_data = {
        "startUrls": [{"url": url}],
        "maxCrawlDepth": 1,
        "maxCrawlPages": 5
    }

    result = api_request(f"/acts/{actor_id}/runs", method="POST", data=input_data)

    if "error" in result:
        return f"Error: {result['error']}"

    run_id = result.get('data', {}).get('id')

    for _ in range(24):
        time.sleep(5)
        status = api_request(f"/actor-runs/{run_id}")
        if status.get('data', {}).get('status') in ['SUCCEEDED', 'FAILED', 'ABORTED']:
            break

    dataset_id = status.get('data', {}).get('defaultDatasetId')
    results = api_request(f"/datasets/{dataset_id}/items?limit=5")

    if not results:
        return "No content scraped"

    output = [f"Content from {url}:", ""]
    for item in results[:3]:
        title = item.get('title', 'No title')
        text = item.get('text', '')[:500]
        output.append(f"**{title}**")
        output.append(text + "...")
        output.append("")

    return "\n".join(output)

# ============== COMPETITOR RESEARCH ==============

@mcp.tool()
def research_competitors(search_term: str = "cleaning services Sydney") -> str:
    """Research competitor cleaning businesses"""
    return search_google_maps(search_term, "Sydney, Australia", 10)

# ============== BELLA'S TARGET MARKET LEAD FINDERS ==============

@mcp.tool()
def find_childcare_centres(suburb: str = "Liverpool NSW", max_results: int = 15) -> str:
    """
    Find childcare centres, daycares, and early learning centres for outreach.
    These businesses need regular deep cleaning for hygiene standards.
    """
    return search_google_maps("childcare daycare early learning centre", f"{suburb}, Australia", max_results)

@mcp.tool()
def find_aged_care_facilities(suburb: str = "Liverpool NSW", max_results: int = 15) -> str:
    """
    Find aged care facilities, nursing homes, and retirement villages.
    These need professional cleaning with dignity and care.
    """
    return search_google_maps("aged care nursing home retirement village", f"{suburb}, Australia", max_results)

@mcp.tool()
def find_ndis_providers(suburb: str = "Sydney", max_results: int = 15) -> str:
    """
    Find NDIS service providers and supported independent living facilities.
    Participants deserve clean, dignified living spaces.
    """
    return search_google_maps("NDIS provider disability services SIL supported independent living", f"{suburb}, Australia", max_results)

@mcp.tool()
def find_airbnb_managers(suburb: str = "Sydney", max_results: int = 15) -> str:
    """
    Find Airbnb and short-term rental property managers.
    They need fast turnovers and reliable cleaners.
    """
    return search_google_maps("airbnb management short term rental property management", f"{suburb}, Australia", max_results)

@mcp.tool()
def find_real_estate_agencies(suburb: str = "Liverpool NSW", max_results: int = 15) -> str:
    """
    Find real estate agencies and property management companies.
    They need reliable end of lease cleaners for bond-back guarantees.
    """
    return search_google_maps("real estate agency property management", f"{suburb}, Australia", max_results)

@mcp.tool()
def find_all_targets(suburb: str = "Liverpool NSW") -> str:
    """
    Quick overview of all target markets in an area.
    Returns count of potential leads in each category.
    """
    markets = {
        "Property Managers": "real estate property management",
        "Childcare Centres": "childcare daycare",
        "Aged Care": "aged care nursing home",
        "NDIS Providers": "NDIS disability services",
        "Airbnb Managers": "airbnb short term rental"
    }

    output = [f"Target Market Overview: {suburb}", "=" * 40, ""]

    for market, search_term in markets.items():
        output.append(f"• {market}: Searching...")
        # Note: In practice, would run these searches

    output.append("")
    output.append("To find leads, use:")
    output.append("  find_childcare_centres('<suburb>')")
    output.append("  find_aged_care_facilities('<suburb>')")
    output.append("  find_ndis_providers('<suburb>')")
    output.append("  find_airbnb_managers('<suburb>')")
    output.append("  find_real_estate_agencies('<suburb>')")

    return "\n".join(output)

# ============== ACCOUNT ==============

@mcp.tool()
def check_apify_usage() -> str:
    """Check Apify account usage and limits"""
    result = api_request("/users/me/usage/monthly")

    if "error" in result:
        return f"Error: {result['error']}"

    data = result.get('data', {})
    return f"""Apify Usage (This Month):
Actor Compute Units: {data.get('actorComputeUnitsUsed', 0):.2f}
Dataset Reads: {data.get('datasetReads', 0)}
Dataset Writes: {data.get('datasetWrites', 0)}"""

@mcp.tool()
def list_my_runs(limit: int = 10) -> str:
    """List recent Apify actor runs"""
    result = api_request(f"/actor-runs?limit={limit}")

    if "error" in result:
        return f"Error: {result['error']}"

    runs = result.get('data', {}).get('items', [])
    if not runs:
        return "No recent runs found"

    output = ["Recent Apify Runs:", ""]
    for run in runs:
        status = run.get('status', 'unknown')
        started = run.get('startedAt', '')[:16]
        actor = run.get('actId', 'unknown')
        output.append(f"• {started} | {status} | {actor}")

    return "\n".join(output)

if __name__ == "__main__":
    mcp.run()
