#!/usr/bin/env python3
"""
Meta MCP Server - Facebook & Instagram Business
For Clean Up Bros social media marketing and customer engagement
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
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

ACCESS_TOKEN = os.environ.get('META_SYSTEM_USER_TOKEN', '')
PAGE_ID = os.environ.get('FB_PAGE_ID', '')
IG_ACCOUNT_ID = os.environ.get('INSTAGRAM_ACCOUNT_ID', '')
BASE_URL = "https://graph.facebook.com/v18.0"

def api_request(endpoint, method="GET", data=None, params=None):
    """Make Meta Graph API request"""
    url = f"{BASE_URL}{endpoint}"

    if params:
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{param_str}&access_token={ACCESS_TOKEN}"
    else:
        url = f"{url}?access_token={ACCESS_TOKEN}"

    headers = {"Content-Type": "application/json"}

    if data:
        data = json.dumps(data).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            logger.info(f"{method} {endpoint[:60]}... - Success")
            return result
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:200]
        logger.error(f"{method} {endpoint[:60]}... - {e.code}: {error_msg}")
        return {"error": f"{e.code}: {error_msg}"}

# Create MCP server
mcp = FastMCP("Meta")

# ============== FACEBOOK PAGE ==============

@mcp.tool()
def fb_post(message: str, link: str = "") -> str:
    """
    Post to the Clean Up Bros Facebook page.
    Can include a message and optional link.
    """
    data = {"message": message}
    if link:
        data["link"] = link

    result = api_request(f"/{PAGE_ID}/feed", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Posted to Facebook!\nPost ID: {result.get('id', 'unknown')}"

@mcp.tool()
def fb_post_photo(image_url: str, caption: str = "") -> str:
    """Post a photo to Facebook (before/after cleaning shots)"""
    data = {
        "url": image_url,
        "caption": caption
    }

    result = api_request(f"/{PAGE_ID}/photos", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Photo posted to Facebook!\nPost ID: {result.get('id', 'unknown')}"

@mcp.tool()
def fb_get_posts(limit: int = 10) -> str:
    """Get recent Facebook page posts"""
    result = api_request(f"/{PAGE_ID}/posts", params={"limit": str(limit), "fields": "message,created_time,likes.summary(true),comments.summary(true)"})

    if "error" in result:
        return f"Error: {result['error']}"

    posts = result.get('data', [])
    if not posts:
        return "No posts found"

    output = ["Recent Facebook Posts:", ""]
    for post in posts:
        date = post.get('created_time', '')[:10]
        message = post.get('message', 'No message')[:80]
        likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
        comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)

        output.append(f"• {date}: {message}...")
        output.append(f"  Likes: {likes} | Comments: {comments}")
        output.append("")

    return "\n".join(output)

@mcp.tool()
def fb_get_messages(limit: int = 10) -> str:
    """Get recent Facebook Messenger conversations"""
    result = api_request(f"/{PAGE_ID}/conversations", params={"limit": str(limit), "fields": "participants,messages.limit(1){message,from,created_time}"})

    if "error" in result:
        return f"Error: {result['error']}"

    convos = result.get('data', [])
    if not convos:
        return "No conversations found"

    output = ["Recent Messenger Conversations:", ""]
    for convo in convos:
        participants = convo.get('participants', {}).get('data', [])
        participant_names = [p.get('name', 'Unknown') for p in participants]
        messages = convo.get('messages', {}).get('data', [])

        if messages:
            last_msg = messages[0]
            msg_text = last_msg.get('message', '')[:50]
            msg_from = last_msg.get('from', {}).get('name', 'Unknown')
            msg_time = last_msg.get('created_time', '')[:16]

            output.append(f"• {', '.join(participant_names)}")
            output.append(f"  Last: {msg_from}: {msg_text}...")
            output.append(f"  Time: {msg_time}")
            output.append("")

    return "\n".join(output)

@mcp.tool()
def fb_reply_message(conversation_id: str, message: str) -> str:
    """Reply to a Facebook Messenger conversation"""
    data = {"message": message}

    result = api_request(f"/{conversation_id}/messages", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Reply sent!\nMessage ID: {result.get('id', 'unknown')}"

@mcp.tool()
def fb_get_reviews() -> str:
    """Get Facebook page reviews/recommendations"""
    result = api_request(f"/{PAGE_ID}/ratings", params={"fields": "reviewer,rating,review_text,created_time"})

    if "error" in result:
        return f"Error: {result['error']}"

    ratings = result.get('data', [])
    if not ratings:
        return "No reviews found"

    output = ["Facebook Reviews:", ""]
    for r in ratings[:10]:
        reviewer = r.get('reviewer', {}).get('name', 'Anonymous')
        rating = r.get('rating', 'N/A')
        text = r.get('review_text', 'No text')[:100]
        date = r.get('created_time', '')[:10]

        output.append(f"• {reviewer} - {rating}/5 ({date})")
        output.append(f"  {text}")
        output.append("")

    return "\n".join(output)

# ============== INSTAGRAM ==============

@mcp.tool()
def ig_post_photo(image_url: str, caption: str) -> str:
    """
    Post a photo to Instagram.
    Perfect for before/after cleaning transformations!
    """
    # First, create the media container
    create_data = {
        "image_url": image_url,
        "caption": caption
    }

    create_result = api_request(f"/{IG_ACCOUNT_ID}/media", method="POST", data=create_data)

    if "error" in create_result:
        return f"Error creating media: {create_result['error']}"

    container_id = create_result.get('id')
    if not container_id:
        return "Error: Could not create media container"

    # Then publish it
    publish_data = {"creation_id": container_id}
    publish_result = api_request(f"/{IG_ACCOUNT_ID}/media_publish", method="POST", data=publish_data)

    if "error" in publish_result:
        return f"Error publishing: {publish_result['error']}"

    return f"Posted to Instagram!\nMedia ID: {publish_result.get('id', 'unknown')}"

@mcp.tool()
def ig_post_carousel(image_urls: list, caption: str) -> str:
    """Post a carousel (multiple images) to Instagram"""
    # Create children containers
    children_ids = []
    for url in image_urls[:10]:  # Max 10 images
        child_data = {"image_url": url, "is_carousel_item": True}
        child_result = api_request(f"/{IG_ACCOUNT_ID}/media", method="POST", data=child_data)
        if child_result.get('id'):
            children_ids.append(child_result['id'])

    if not children_ids:
        return "Error: Could not create carousel items"

    # Create carousel container
    carousel_data = {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption
    }

    carousel_result = api_request(f"/{IG_ACCOUNT_ID}/media", method="POST", data=carousel_data)

    if "error" in carousel_result:
        return f"Error: {carousel_result['error']}"

    container_id = carousel_result.get('id')

    # Publish
    publish_result = api_request(f"/{IG_ACCOUNT_ID}/media_publish", method="POST", data={"creation_id": container_id})

    if "error" in publish_result:
        return f"Error publishing: {publish_result['error']}"

    return f"Carousel posted to Instagram!\nMedia ID: {publish_result.get('id', 'unknown')}"

@mcp.tool()
def ig_get_posts(limit: int = 10) -> str:
    """Get recent Instagram posts"""
    result = api_request(f"/{IG_ACCOUNT_ID}/media", params={"limit": str(limit), "fields": "caption,like_count,comments_count,timestamp,media_type"})

    if "error" in result:
        return f"Error: {result['error']}"

    posts = result.get('data', [])
    if not posts:
        return "No posts found"

    output = ["Recent Instagram Posts:", ""]
    for post in posts:
        date = post.get('timestamp', '')[:10]
        caption = post.get('caption', 'No caption')[:60]
        likes = post.get('like_count', 0)
        comments = post.get('comments_count', 0)
        media_type = post.get('media_type', 'IMAGE')

        output.append(f"• {date} [{media_type}]: {caption}...")
        output.append(f"  Likes: {likes} | Comments: {comments}")
        output.append("")

    return "\n".join(output)

@mcp.tool()
def ig_get_comments(media_id: str) -> str:
    """Get comments on an Instagram post"""
    result = api_request(f"/{media_id}/comments", params={"fields": "text,username,timestamp"})

    if "error" in result:
        return f"Error: {result['error']}"

    comments = result.get('data', [])
    if not comments:
        return "No comments found"

    output = [f"Comments on post {media_id}:", ""]
    for c in comments[:20]:
        user = c.get('username', 'unknown')
        text = c.get('text', '')[:80]
        date = c.get('timestamp', '')[:10]
        output.append(f"• @{user} ({date}): {text}")

    return "\n".join(output)

@mcp.tool()
def ig_reply_comment(comment_id: str, message: str) -> str:
    """Reply to an Instagram comment"""
    data = {"message": message}

    result = api_request(f"/{comment_id}/replies", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Reply posted!\nComment ID: {result.get('id', 'unknown')}"

@mcp.tool()
def ig_get_insights() -> str:
    """Get Instagram account insights"""
    result = api_request(f"/{IG_ACCOUNT_ID}/insights", params={
        "metric": "impressions,reach,profile_views,follower_count",
        "period": "day"
    })

    if "error" in result:
        return f"Error: {result['error']}"

    data = result.get('data', [])
    if not data:
        return "No insights available"

    output = ["Instagram Insights (Today):", ""]
    for metric in data:
        name = metric.get('name', 'unknown').replace('_', ' ').title()
        values = metric.get('values', [{}])
        value = values[0].get('value', 0) if values else 0
        output.append(f"• {name}: {value}")

    return "\n".join(output)

# ============== CONTENT TEMPLATES ==============

@mcp.tool()
def generate_cleaning_post(before_after: bool = True, service_type: str = "end of lease") -> str:
    """Generate a caption for a cleaning post"""
    if before_after:
        captions = [
            f"Another stunning {service_type} transformation! Swipe to see the before 👀\n\n✨ Bond back guaranteed\n📍 Liverpool & Western Sydney\n📞 0406 764 585\n\n#CleanUpBros #EndOfLeaseCleaning #SydneyCleaning #BondCleaning #BeforeAndAfter",
            f"When we say deep clean, we mean DEEP clean! 🧹✨\n\nThis {service_type} clean took our team 4 hours, but the results speak for themselves!\n\n📞 Book your clean: 0406 764 585\n🌐 cleanupbros.com.au\n\n#CleanUpBros #DeepCleaning #SydneyCleaning #PropertyCleaning",
        ]
    else:
        captions = [
            f"Ready for a sparkling clean home? 🏠✨\n\nWe offer:\n✅ End of Lease Cleaning\n✅ Airbnb Turnovers\n✅ Commercial Cleaning\n✅ Regular Home Cleans\n\n📞 0406 764 585\n🌐 cleanupbros.com.au\n\n#CleanUpBros #SydneyCleaning #CleaningServices",
            "Your local cleaning experts in Liverpool & Western Sydney! 🧹\n\nFrom one-off cleans to regular maintenance, we've got you covered.\n\n⭐ 5-star reviews\n✅ Fully insured\n💯 Satisfaction guaranteed\n\n📞 0406 764 585\n\n#CleanUpBros #LiverpoolCleaning #WesternSydney",
        ]

    import random
    return f"Suggested Caption:\n\n{random.choice(captions)}"

if __name__ == "__main__":
    mcp.run()
