#!/usr/bin/env python3
"""
Meta MCP Server - Facebook & Instagram Business
For Clean Up Bros social media marketing and customer engagement

Features:
- Facebook page posting (text, photo, link)
- Facebook Messenger conversations
- Facebook page reviews/recommendations
- Instagram posting (photo, carousel, reels)
- Instagram comments and replies
- Instagram insights and analytics
- Content template generation
- Hashtag management
"""
import os
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from mcp.shared_utils import load_env, format_date_au
from mcp.logging_config import setup_logging
from mcp.validation import sanitize_input, validate_url

# Setup logging
logger = setup_logging(__name__)

# Load environment
load_env()

ACCESS_TOKEN = os.environ.get('META_SYSTEM_USER_TOKEN', '')
PAGE_ID = os.environ.get('FB_PAGE_ID', '')
IG_ACCOUNT_ID = os.environ.get('INSTAGRAM_ACCOUNT_ID', '')
BASE_URL = "https://graph.facebook.com/v21.0"

# Rate limiting: Meta allows ~200 calls per hour
_call_count = 0
_call_window_start = None


def api_request(endpoint, method="GET", data=None, params=None):
    """Make Meta Graph API request with proper error handling"""
    if not ACCESS_TOKEN:
        return {"error": "META_SYSTEM_USER_TOKEN not set in environment. See .env.example"}

    url = f"{BASE_URL}{endpoint}"

    # Build query string
    query_parts = [f"access_token={ACCESS_TOKEN}"]
    if params:
        for k, v in params.items():
            query_parts.append(f"{k}={urllib.parse.quote(str(v))}")
    url = f"{url}?{'&'.join(query_parts)}"

    headers = {"Content-Type": "application/json"}

    body = json.dumps(data).encode() if data else None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Meta {method} {endpoint[:60]} - Success")
            return result
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:300]
        logger.error(f"Meta {method} {endpoint[:60]} - {e.code}: {error_msg}")
        # Parse Meta's error format for better messages
        try:
            error_data = json.loads(error_msg)
            meta_error = error_data.get("error", {})
            return {"error": f"{meta_error.get('type', 'Error')}: {meta_error.get('message', error_msg)}"}
        except json.JSONDecodeError:
            return {"error": f"HTTP {e.code}: {error_msg}"}
    except urllib.error.URLError as e:
        logger.error(f"Meta {method} {endpoint[:60]} - URL Error: {e.reason}")
        return {"error": f"Connection error: {e.reason}"}
    except TimeoutError:
        logger.error(f"Meta {method} {endpoint[:60]} - Timeout")
        return {"error": "Request timed out"}


# Create MCP server
mcp = FastMCP("Meta")

# ============== FACEBOOK PAGE ==============

@mcp.tool()
def fb_post(message: str, link: str = "") -> str:
    """
    Post to the Clean Up Bros Facebook page.
    Can include a message and optional link.
    """
    if not PAGE_ID:
        return "Error: FB_PAGE_ID not set in environment"

    message = sanitize_input(message, max_length=5000)
    if not message:
        return "Error: Message is required"

    data = {"message": message}
    if link:
        try:
            validate_url(link)
            data["link"] = link
        except ValueError as e:
            return f"Error: Invalid link URL - {e}"

    result = api_request(f"/{PAGE_ID}/feed", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    post_id = result.get('id', 'unknown')
    logger.info(f"Facebook post created: {post_id}")
    return f"Posted to Facebook!\nPost ID: {post_id}"


@mcp.tool()
def fb_post_photo(image_url: str, caption: str = "") -> str:
    """Post a photo to Facebook (before/after cleaning shots)"""
    if not PAGE_ID:
        return "Error: FB_PAGE_ID not set in environment"

    try:
        validate_url(image_url)
    except ValueError as e:
        return f"Error: Invalid image URL - {e}"

    caption = sanitize_input(caption, max_length=5000)

    data = {"url": image_url}
    if caption:
        data["caption"] = caption

    result = api_request(f"/{PAGE_ID}/photos", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Photo posted to Facebook!\nPost ID: {result.get('id', 'unknown')}"


@mcp.tool()
def fb_get_posts(limit: int = 10) -> str:
    """Get recent Facebook page posts"""
    if not PAGE_ID:
        return "Error: FB_PAGE_ID not set in environment"

    limit = min(max(1, limit), 50)

    result = api_request(
        f"/{PAGE_ID}/posts",
        params={
            "limit": str(limit),
            "fields": "message,created_time,likes.summary(true),comments.summary(true),shares"
        }
    )

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
        shares = post.get('shares', {}).get('count', 0)

        output.append(f"  {date}: {message}...")
        output.append(f"    Likes: {likes} | Comments: {comments} | Shares: {shares}")
        output.append("")

    return "\n".join(output)


@mcp.tool()
def fb_get_messages(limit: int = 10) -> str:
    """Get recent Facebook Messenger conversations"""
    if not PAGE_ID:
        return "Error: FB_PAGE_ID not set in environment"

    limit = min(max(1, limit), 25)

    result = api_request(
        f"/{PAGE_ID}/conversations",
        params={
            "limit": str(limit),
            "fields": "participants,messages.limit(1){message,from,created_time}"
        }
    )

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

            output.append(f"  {', '.join(participant_names)}")
            output.append(f"    Last: {msg_from}: {msg_text}...")
            output.append(f"    Time: {msg_time}")
            output.append(f"    ID: {convo.get('id', 'unknown')}")
            output.append("")

    return "\n".join(output)


@mcp.tool()
def fb_reply_message(conversation_id: str, message: str) -> str:
    """Reply to a Facebook Messenger conversation"""
    conversation_id = sanitize_input(conversation_id, max_length=100).strip()
    message = sanitize_input(message, max_length=2000)

    if not conversation_id:
        return "Error: Conversation ID is required"
    if not message:
        return "Error: Message is required"

    data = {"message": message}

    result = api_request(f"/{conversation_id}/messages", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Reply sent!\nMessage ID: {result.get('id', 'unknown')}"


@mcp.tool()
def fb_get_reviews() -> str:
    """Get Facebook page reviews/recommendations"""
    if not PAGE_ID:
        return "Error: FB_PAGE_ID not set in environment"

    result = api_request(
        f"/{PAGE_ID}/ratings",
        params={"fields": "reviewer,rating,review_text,created_time"}
    )

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

        output.append(f"  {reviewer} - {rating}/5 ({date})")
        output.append(f"    {text}")
        output.append("")

    return "\n".join(output)


@mcp.tool()
def fb_get_page_insights(period: str = "day") -> str:
    """
    Get Facebook page insights/analytics.

    Period: day, week, days_28
    """
    if not PAGE_ID:
        return "Error: FB_PAGE_ID not set in environment"

    if period not in ("day", "week", "days_28"):
        return "Error: Period must be day, week, or days_28"

    result = api_request(
        f"/{PAGE_ID}/insights",
        params={
            "metric": "page_impressions,page_engaged_users,page_fan_adds,page_views_total",
            "period": period
        }
    )

    if "error" in result:
        return f"Error: {result['error']}"

    data = result.get('data', [])
    if not data:
        return "No insights available"

    output = [f"Facebook Page Insights ({period}):", ""]
    for metric in data:
        name = metric.get('name', 'unknown').replace('_', ' ').title()
        values = metric.get('values', [{}])
        value = values[-1].get('value', 0) if values else 0
        output.append(f"  {name}: {value}")

    return "\n".join(output)


# ============== INSTAGRAM ==============

@mcp.tool()
def ig_post_photo(image_url: str, caption: str) -> str:
    """
    Post a photo to Instagram.
    Perfect for before/after cleaning transformations!
    """
    if not IG_ACCOUNT_ID:
        return "Error: INSTAGRAM_ACCOUNT_ID not set in environment"

    try:
        validate_url(image_url)
    except ValueError as e:
        return f"Error: Invalid image URL - {e}"

    caption = sanitize_input(caption, max_length=2200)  # Instagram caption limit
    if not caption:
        return "Error: Caption is required for Instagram posts"

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

    logger.info(f"Instagram photo posted: {publish_result.get('id', 'unknown')}")
    return f"Posted to Instagram!\nMedia ID: {publish_result.get('id', 'unknown')}"


@mcp.tool()
def ig_post_carousel(image_urls: list, caption: str) -> str:
    """Post a carousel (multiple images) to Instagram - max 10 images"""
    if not IG_ACCOUNT_ID:
        return "Error: INSTAGRAM_ACCOUNT_ID not set in environment"

    caption = sanitize_input(caption, max_length=2200)
    if not caption:
        return "Error: Caption is required"

    if not image_urls or len(image_urls) < 2:
        return "Error: Carousel requires at least 2 images"

    # Create children containers
    children_ids = []
    for url in image_urls[:10]:
        try:
            validate_url(url)
        except ValueError:
            logger.warning(f"Skipping invalid URL in carousel: {url[:50]}")
            continue

        child_data = {"image_url": url, "is_carousel_item": True}
        child_result = api_request(f"/{IG_ACCOUNT_ID}/media", method="POST", data=child_data)
        if child_result.get('id'):
            children_ids.append(child_result['id'])

    if len(children_ids) < 2:
        return "Error: Need at least 2 valid images for a carousel"

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
    publish_result = api_request(
        f"/{IG_ACCOUNT_ID}/media_publish",
        method="POST",
        data={"creation_id": container_id}
    )

    if "error" in publish_result:
        return f"Error publishing: {publish_result['error']}"

    logger.info(f"Instagram carousel posted: {publish_result.get('id', 'unknown')}, {len(children_ids)} images")
    return f"Carousel posted to Instagram!\nMedia ID: {publish_result.get('id', 'unknown')}\nImages: {len(children_ids)}"


@mcp.tool()
def ig_post_reel(video_url: str, caption: str) -> str:
    """
    Post a Reel to Instagram.
    Video must be between 3-90 seconds, max 1GB.
    Aspect ratio: 9:16 recommended.
    """
    if not IG_ACCOUNT_ID:
        return "Error: INSTAGRAM_ACCOUNT_ID not set in environment"

    try:
        validate_url(video_url)
    except ValueError as e:
        return f"Error: Invalid video URL - {e}"

    caption = sanitize_input(caption, max_length=2200)

    create_data = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption or ""
    }

    create_result = api_request(f"/{IG_ACCOUNT_ID}/media", method="POST", data=create_data)

    if "error" in create_result:
        return f"Error creating reel: {create_result['error']}"

    container_id = create_result.get('id')
    if not container_id:
        return "Error: Could not create reel container"

    # Reels need time to process - return the container ID for later publishing
    logger.info(f"Instagram reel container created: {container_id}")
    return f"""Reel container created!

Container ID: {container_id}

The video is being processed by Instagram. Wait 30-60 seconds, then publish with:
  ig_publish_media('{container_id}')

Note: If publishing fails, the video may still be processing. Wait and try again."""


@mcp.tool()
def ig_publish_media(container_id: str) -> str:
    """Publish a previously created Instagram media container (used for Reels)"""
    if not IG_ACCOUNT_ID:
        return "Error: INSTAGRAM_ACCOUNT_ID not set in environment"

    container_id = sanitize_input(container_id, max_length=100).strip()
    if not container_id:
        return "Error: Container ID is required"

    publish_result = api_request(
        f"/{IG_ACCOUNT_ID}/media_publish",
        method="POST",
        data={"creation_id": container_id}
    )

    if "error" in publish_result:
        return f"Error publishing: {publish_result['error']}"

    logger.info(f"Instagram media published: {publish_result.get('id', 'unknown')}")
    return f"Published to Instagram!\nMedia ID: {publish_result.get('id', 'unknown')}"


@mcp.tool()
def ig_get_posts(limit: int = 10) -> str:
    """Get recent Instagram posts with engagement metrics"""
    if not IG_ACCOUNT_ID:
        return "Error: INSTAGRAM_ACCOUNT_ID not set in environment"

    limit = min(max(1, limit), 50)

    result = api_request(
        f"/{IG_ACCOUNT_ID}/media",
        params={
            "limit": str(limit),
            "fields": "caption,like_count,comments_count,timestamp,media_type,permalink"
        }
    )

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
        permalink = post.get('permalink', '')

        output.append(f"  {date} [{media_type}]: {caption}...")
        output.append(f"    Likes: {likes} | Comments: {comments}")
        if permalink:
            output.append(f"    Link: {permalink}")
        output.append("")

    return "\n".join(output)


@mcp.tool()
def ig_get_comments(media_id: str) -> str:
    """Get comments on an Instagram post"""
    media_id = sanitize_input(media_id, max_length=100).strip()
    if not media_id:
        return "Error: Media ID is required"

    result = api_request(
        f"/{media_id}/comments",
        params={"fields": "text,username,timestamp,like_count"}
    )

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
        likes = c.get('like_count', 0)
        output.append(f"  @{user} ({date}): {text}")
        if likes > 0:
            output.append(f"    Likes: {likes}")

    return "\n".join(output)


@mcp.tool()
def ig_reply_comment(comment_id: str, message: str) -> str:
    """Reply to an Instagram comment"""
    comment_id = sanitize_input(comment_id, max_length=100).strip()
    message = sanitize_input(message, max_length=500)

    if not comment_id:
        return "Error: Comment ID is required"
    if not message:
        return "Error: Reply message is required"

    data = {"message": message}

    result = api_request(f"/{comment_id}/replies", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Reply posted!\nComment ID: {result.get('id', 'unknown')}"


@mcp.tool()
def ig_get_insights(period: str = "day") -> str:
    """
    Get Instagram account insights.

    Period: day, week, days_28, lifetime
    """
    if not IG_ACCOUNT_ID:
        return "Error: INSTAGRAM_ACCOUNT_ID not set in environment"

    if period not in ("day", "week", "days_28", "lifetime"):
        return "Error: Period must be day, week, days_28, or lifetime"

    result = api_request(
        f"/{IG_ACCOUNT_ID}/insights",
        params={
            "metric": "impressions,reach,profile_views,follower_count,accounts_engaged",
            "period": period
        }
    )

    if "error" in result:
        return f"Error: {result['error']}"

    data = result.get('data', [])
    if not data:
        return "No insights available"

    output = [f"Instagram Insights ({period}):", ""]
    for metric in data:
        name = metric.get('name', 'unknown').replace('_', ' ').title()
        values = metric.get('values', [{}])
        value = values[-1].get('value', 0) if values else 0
        output.append(f"  {name}: {value}")

    return "\n".join(output)


# ============== CONTENT TEMPLATES ==============

@mcp.tool()
def generate_cleaning_post(post_type: str = "before_after", platform: str = "both") -> str:
    """
    Generate a caption for a cleaning post.

    post_type: before_after, promotion, tip, testimonial, seasonal
    platform: facebook, instagram, both
    """
    hashtags_ig = "\n\n#CleanUpBros #SydneyCleaning #EndOfLeaseCleaning #BondCleaning #WesternSydney #CleaningServices #BeforeAndAfter #LiverpoolNSW"
    cta = "\n\n0406 764 585 | cleanupbros.com.au"

    templates = {
        "before_after": f"""Another stunning transformation! Swipe to see the before.

This 2BR end of lease clean included:
- Deep kitchen clean (oven, rangehood, splashback)
- Bathroom sanitisation
- Floor scrubbing and mopping
- Window tracks and sills
- Wall spot cleaning

Result? Full bond returned!{cta}""",

        "promotion": f"""Your local cleaning experts in Liverpool & Western Sydney!

We offer:
- End of Lease Cleaning (bond-back guaranteed)
- Airbnb Turnovers ($120)
- Commercial Cleaning
- Regular Home Cleans

Fully insured. Eco-friendly products. One call away.{cta}""",

        "tip": f"""3 cleaning hacks from the pros:

1. Microfibre cloths > paper towels (always)
2. Clean top to bottom, left to right - gravity is your friend
3. Let cleaning products sit for 5 mins before scrubbing

Save this for later!{cta}""",

        "testimonial": f"""Another happy client!

"Clean Up Bros made my end of lease stress-free. The apartment looked better than when I moved in. Got my full bond back within a week." - Sarah, Liverpool

We love hearing from our clients. Your clean space is our reward.{cta}""",

        "seasonal": f"""New season, fresh start!

Book your deep clean this month and get a free oven clean (worth $50).

Perfect timing for:
- Spring refresh
- Pre-inspection cleans
- Moving in or out
- Getting your space guest-ready

Limited spots available.{cta}""",
    }

    if post_type not in templates:
        return f"Error: Unknown post type '{post_type}'. Available: {', '.join(templates.keys())}"

    caption = templates[post_type]

    if platform in ("instagram", "both"):
        caption += hashtags_ig

    return f"Suggested {post_type.replace('_', ' ').title()} Post:\n\n{caption}"


@mcp.tool()
def generate_hashtags(category: str = "general") -> str:
    """
    Generate relevant hashtags for Instagram posts.

    Category: general, end_of_lease, airbnb, commercial, before_after
    """
    base = "#CleanUpBros #SydneyCleaning #CleaningServices #WesternSydney #LiverpoolNSW"

    categories = {
        "general": f"{base} #ProfessionalCleaning #CleanHome #SydneyBusiness #SmallBusinessAustralia",
        "end_of_lease": f"{base} #EndOfLeaseCleaning #BondCleaning #BondBackGuarantee #MovingOut #RealEstateSydney #PropertyManagement",
        "airbnb": f"{base} #AirbnbCleaning #ShortTermRental #AirbnbHost #TurnoverCleaning #HospitalityCleaning",
        "commercial": f"{base} #CommercialCleaning #OfficeCleaning #WorkplaceCleaning #SydneyOffice #CleanWorkspace",
        "before_after": f"{base} #BeforeAndAfter #CleaningTransformation #SatisfyingCleaning #DeepClean #TransformationTuesday",
    }

    if category not in categories:
        return f"Error: Unknown category '{category}'. Available: {', '.join(categories.keys())}"

    return f"Hashtags ({category}):\n\n{categories[category]}"


if __name__ == "__main__":
    mcp.run()
