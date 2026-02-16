#!/usr/bin/env python3
"""
Brave Search MCP Server - Web Search
For Clean Up Bros research and information gathering
"""
import os
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from mcp.server.fastmcp import FastMCP
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

API_KEY = os.environ.get('BRAVE_API_KEY', '')
BASE_URL = "https://api.search.brave.com/res/v1"

def api_request(endpoint, params=None):
    """Make Brave Search API request"""
    url = f"{BASE_URL}{endpoint}"

    if params:
        param_str = urllib.parse.urlencode(params)
        url = f"{url}?{param_str}"

    headers = {
        "X-Subscription-Token": API_KEY,
        "Accept": "application/json"
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            logger.info(f"GET {endpoint} - Success")
            return result
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:200]
        logger.error(f"GET {endpoint} - {e.code}: {error_msg}")
        return {"error": f"{e.code}: {error_msg}"}

# Create MCP server
mcp = FastMCP("BraveSearch")

# ============== WEB SEARCH ==============

@mcp.tool()
def search(query: str, count: int = 10) -> str:
    """
    Search the web using Brave Search.
    Returns titles, URLs, and descriptions.
    """
    result = api_request("/web/search", params={
        "q": query,
        "count": count,
        "country": "AU",
        "search_lang": "en"
    })

    if "error" in result:
        return f"Error: {result['error']}"

    web_results = result.get('web', {}).get('results', [])

    if not web_results:
        return f"No results found for: {query}"

    output = [f"Search Results: '{query}'", ""]
    for r in web_results[:count]:
        title = r.get('title', 'No title')
        url = r.get('url', '')
        desc = r.get('description', '')[:150]

        output.append(f"**{title}**")
        output.append(f"  {url}")
        output.append(f"  {desc}...")
        output.append("")

    return "\n".join(output)

@mcp.tool()
def search_news(query: str, count: int = 10) -> str:
    """Search for news articles"""
    result = api_request("/news/search", params={
        "q": query,
        "count": count,
        "country": "AU"
    })

    if "error" in result:
        return f"Error: {result['error']}"

    news = result.get('results', [])

    if not news:
        return f"No news found for: {query}"

    output = [f"News: '{query}'", ""]
    for n in news[:count]:
        title = n.get('title', 'No title')
        source = n.get('source', 'Unknown')
        date = n.get('age', 'Unknown date')
        url = n.get('url', '')

        output.append(f"**{title}**")
        output.append(f"  {source} | {date}")
        output.append(f"  {url}")
        output.append("")

    return "\n".join(output)

@mcp.tool()
def search_local(query: str, location: str = "Sydney, Australia") -> str:
    """Search for local businesses/places"""
    full_query = f"{query} {location}"

    result = api_request("/web/search", params={
        "q": full_query,
        "count": 10,
        "country": "AU",
        "search_lang": "en"
    })

    if "error" in result:
        return f"Error: {result['error']}"

    # Check for local results
    locations = result.get('locations', {}).get('results', [])
    web_results = result.get('web', {}).get('results', [])

    output = [f"Local Search: '{query}' in {location}", ""]

    if locations:
        output.append("Local Results:")
        for loc in locations[:5]:
            name = loc.get('title', 'Unknown')
            address = loc.get('address', {}).get('streetAddress', 'N/A')
            output.append(f"• {name}")
            output.append(f"  {address}")
            output.append("")
    else:
        output.append("Web Results:")
        for r in web_results[:5]:
            title = r.get('title', 'No title')
            desc = r.get('description', '')[:100]
            output.append(f"• {title}")
            output.append(f"  {desc}...")
            output.append("")

    return "\n".join(output)

# ============== BUSINESS RESEARCH ==============

@mcp.tool()
def research_competitor(business_name: str) -> str:
    """Research a competitor cleaning business"""
    return search(f"{business_name} cleaning services Sydney reviews", 5)

@mcp.tool()
def find_cleaning_prices(suburb: str = "Sydney") -> str:
    """Research cleaning service prices in an area"""
    return search(f"cleaning services prices rates {suburb} Australia 2026", 10)

@mcp.tool()
def find_property_managers_online(suburb: str = "Liverpool") -> str:
    """Find property managers in an area via web search"""
    return search(f"property managers real estate agents {suburb} NSW contact", 10)

@mcp.tool()
def research_cleaning_tips() -> str:
    """Get latest cleaning tips and trends for content ideas"""
    return search("professional cleaning tips tricks 2026", 10)

# ============== QUESTION ANSWERING ==============

@mcp.tool()
def answer_question(question: str) -> str:
    """
    Search for an answer to a question.
    Good for customer questions or research.
    """
    result = api_request("/web/search", params={
        "q": question,
        "count": 5,
        "country": "AU"
    })

    if "error" in result:
        return f"Error: {result['error']}"

    # Check for FAQ or quick answers
    faq = result.get('faq', {}).get('results', [])
    infobox = result.get('infobox', {})
    web_results = result.get('web', {}).get('results', [])

    output = [f"Q: {question}", ""]

    if faq:
        output.append("Quick Answers:")
        for f in faq[:3]:
            q = f.get('question', '')
            a = f.get('answer', '')[:200]
            output.append(f"• {q}")
            output.append(f"  {a}")
            output.append("")
    elif infobox:
        desc = infobox.get('description', '')
        if desc:
            output.append(f"Answer: {desc}")
            output.append("")
    else:
        output.append("Related Results:")
        for r in web_results[:3]:
            title = r.get('title', '')
            desc = r.get('description', '')[:150]
            output.append(f"• {title}")
            output.append(f"  {desc}...")
            output.append("")

    return "\n".join(output)

# ============== AUSTRALIAN BUSINESS INFO ==============

@mcp.tool()
def lookup_abn(abn: str) -> str:
    """Look up an Australian Business Number"""
    return search(f"ABN {abn} Australia business lookup", 5)

@mcp.tool()
def ato_info(topic: str) -> str:
    """Search for ATO tax information"""
    return search(f"ATO {topic} Australia tax 2026 site:ato.gov.au", 5)

@mcp.tool()
def find_industry_news() -> str:
    """Find cleaning industry news in Australia"""
    return search_news("cleaning industry Australia", 10)

if __name__ == "__main__":
    mcp.run()
