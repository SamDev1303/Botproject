#!/usr/bin/env python3
"""
Kie.AI MCP Server - Video & Image Generation
For Clean Up Bros viral marketing content

Supports models: Sora, Veo, Kling, Flux, Grok Image
Uses Kie.AI API (https://kie.ai) for generation
"""
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from mcp.shared_utils import load_env, api_get, api_post
from mcp.logging_config import setup_logging
from mcp.validation import sanitize_input, validate_url

# Setup logging
logger = setup_logging(__name__)

# Load environment
load_env()

KIE_API_KEY = os.environ.get('KIE_API_KEY', '')
KIE_BASE_URL = os.environ.get('KIE_BASE_URL', 'https://api.kie.ai/v1')
OUTPUT_DIR = Path.home() / ".clawdbot" / "media" / "kie"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Supported models
VIDEO_MODELS = {
    "sora2": "OpenAI Sora 2 - Cinematic quality, best for storytelling",
    "veo2": "Google Veo 2 - Natural motion, good for product demos",
    "kling1.6": "Kling 1.6 - Fast generation, good for social media",
    "minimax": "MiniMax - Cost-effective, quick turnaround",
}

IMAGE_MODELS = {
    "flux2": "Flux 2 - High quality, photorealistic",
    "grok-image": "Grok Image - Creative, artistic style",
    "ideogram": "Ideogram - Great for text in images",
}

# Create server
mcp = FastMCP("KieAI")


def _kie_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Make authenticated Kie.AI API request"""
    if not KIE_API_KEY:
        return {"error": "KIE_API_KEY not set in environment"}

    url = f"{KIE_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Kie.AI {method} {endpoint} - Success")
            return result
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:300]
        logger.error(f"Kie.AI {method} {endpoint} - {e.code}: {error_msg}")
        return {"error": f"HTTP {e.code}: {error_msg}"}
    except urllib.error.URLError as e:
        logger.error(f"Kie.AI {method} {endpoint} - URL Error: {e.reason}")
        return {"error": f"Connection error: {e.reason}"}
    except TimeoutError:
        logger.error(f"Kie.AI {method} {endpoint} - Timeout")
        return {"error": "Request timed out"}


def _poll_for_result(task_id: str, max_wait: int = 300, interval: int = 10) -> dict:
    """Poll Kie.AI for task completion"""
    elapsed = 0
    while elapsed < max_wait:
        result = _kie_request(f"/tasks/{task_id}")
        if "error" in result:
            return result

        status = result.get("status", "unknown")
        if status == "completed":
            return result
        elif status == "failed":
            return {"error": f"Task failed: {result.get('error', 'Unknown error')}"}

        time.sleep(interval)
        elapsed += interval

    return {"error": f"Task timed out after {max_wait}s (task_id: {task_id})"}


@mcp.tool()
def generate_video(prompt: str, model: str = "kling1.6", duration: int = 5, aspect_ratio: str = "16:9") -> str:
    """
    Generate a video using Kie.AI.

    Models: sora2, veo2, kling1.6, minimax
    Duration: 5-30 seconds (depends on model)
    Aspect ratio: 16:9, 9:16, 1:1

    Perfect for:
    - Before/after cleaning transformations
    - Social media ads (9:16 for Reels/TikTok)
    - Website hero videos
    - Customer testimonial intros
    """
    prompt = sanitize_input(prompt, max_length=2000)

    if not prompt:
        return "Error: Prompt is required"

    if model not in VIDEO_MODELS:
        return f"Error: Unknown model '{model}'. Available: {', '.join(VIDEO_MODELS.keys())}"

    if duration < 3 or duration > 30:
        return "Error: Duration must be between 3 and 30 seconds"

    if aspect_ratio not in ("16:9", "9:16", "1:1"):
        return "Error: Aspect ratio must be 16:9, 9:16, or 1:1"

    data = {
        "prompt": prompt,
        "model": model,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
    }

    result = _kie_request("/generations/video", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    task_id = result.get("task_id") or result.get("id")
    if not task_id:
        # Some models return the URL directly
        video_url = result.get("url") or result.get("output", {}).get("url")
        if video_url:
            logger.info(f"Video generated directly: {model}, {duration}s")
            return f"""Video generated!

Model: {model} ({VIDEO_MODELS[model]})
Duration: {duration}s
Aspect Ratio: {aspect_ratio}
URL: {video_url}

Download or share this URL for your marketing content."""

        return f"Error: Unexpected response from Kie.AI: {json.dumps(result)[:200]}"

    logger.info(f"Video generation started: task {task_id}, model={model}, {duration}s")
    return f"""Video generation started!

Model: {model} ({VIDEO_MODELS[model]})
Duration: {duration}s
Aspect Ratio: {aspect_ratio}
Task ID: {task_id}

Use check_generation_status('{task_id}') to check progress.
Video generation typically takes 1-5 minutes depending on the model."""


@mcp.tool()
def generate_image(prompt: str, model: str = "flux2", aspect_ratio: str = "1:1", count: int = 1) -> str:
    """
    Generate images using Kie.AI.

    Models: flux2, grok-image, ideogram
    Aspect ratio: 16:9, 9:16, 1:1, 4:3, 3:4
    Count: 1-4 images per request

    Perfect for:
    - Before/after cleaning photos
    - Social media post images
    - Ad creatives
    - Logo variations
    """
    prompt = sanitize_input(prompt, max_length=2000)

    if not prompt:
        return "Error: Prompt is required"

    if model not in IMAGE_MODELS:
        return f"Error: Unknown model '{model}'. Available: {', '.join(IMAGE_MODELS.keys())}"

    if count < 1 or count > 4:
        return "Error: Count must be between 1 and 4"

    data = {
        "prompt": prompt,
        "model": model,
        "aspect_ratio": aspect_ratio,
        "count": count,
    }

    result = _kie_request("/generations/image", method="POST", data=data)

    if "error" in result:
        return f"Error: {result['error']}"

    # Handle direct URL response
    images = result.get("images") or result.get("output", {}).get("images", [])
    if images:
        logger.info(f"Image(s) generated: {model}, {len(images)} images")
        output = [f"Image(s) generated!\n", f"Model: {model} ({IMAGE_MODELS[model]})", f"Count: {len(images)}", ""]
        for i, img in enumerate(images, 1):
            url = img if isinstance(img, str) else img.get("url", "unknown")
            output.append(f"Image {i}: {url}")
        return "\n".join(output)

    task_id = result.get("task_id") or result.get("id")
    if task_id:
        logger.info(f"Image generation started: task {task_id}, model={model}")
        return f"""Image generation started!

Model: {model} ({IMAGE_MODELS[model]})
Count: {count}
Task ID: {task_id}

Use check_generation_status('{task_id}') to check progress."""

    return f"Error: Unexpected response: {json.dumps(result)[:200]}"


@mcp.tool()
def check_generation_status(task_id: str) -> str:
    """Check the status of a video or image generation task"""
    task_id = sanitize_input(task_id, max_length=100).strip()

    if not task_id:
        return "Error: Task ID is required"

    result = _kie_request(f"/tasks/{task_id}")

    if "error" in result:
        return f"Error: {result['error']}"

    status = result.get("status", "unknown")
    progress = result.get("progress", 0)

    output = [f"Task: {task_id}", f"Status: {status}", f"Progress: {progress}%"]

    if status == "completed":
        url = result.get("url") or result.get("output", {}).get("url")
        images = result.get("images") or result.get("output", {}).get("images", [])

        if url:
            output.append(f"\nResult URL: {url}")
        if images:
            for i, img in enumerate(images, 1):
                img_url = img if isinstance(img, str) else img.get("url", "unknown")
                output.append(f"Image {i}: {img_url}")

    elif status == "failed":
        output.append(f"\nError: {result.get('error', 'Unknown error')}")

    return "\n".join(output)


@mcp.tool()
def list_models() -> str:
    """List all available Kie.AI models for video and image generation"""
    output = ["Available Kie.AI Models:", "", "VIDEO MODELS:", ""]

    for model, desc in VIDEO_MODELS.items():
        output.append(f"  {model}: {desc}")

    output.extend(["", "IMAGE MODELS:", ""])

    for model, desc in IMAGE_MODELS.items():
        output.append(f"  {model}: {desc}")

    output.extend([
        "",
        "USAGE TIPS:",
        "  - Social media ads: 9:16 aspect ratio, kling1.6 (fast + cheap)",
        "  - Website hero: 16:9 aspect ratio, sora2 (cinematic quality)",
        "  - Instagram posts: 1:1, flux2 (photorealistic)",
        "  - Before/after: 1:1 or 4:3, flux2",
    ])

    return "\n".join(output)


@mcp.tool()
def generate_cleaning_ad_video(ad_type: str = "before_after", style: str = "energetic") -> str:
    """
    Generate a pre-written cleaning ad video prompt.

    ad_type: before_after, testimonial, team_intro, seasonal
    style: energetic, professional, cinematic, fun

    Returns a ready-to-use prompt for generate_video().
    """
    prompts = {
        "before_after": {
            "energetic": "Fast-paced before and after cleaning transformation of a modern Sydney apartment. Dirty kitchen transforms to sparkling clean. Energetic motion, bright lighting, satisfying reveal. Text overlay: Clean Up Bros.",
            "professional": "Smooth cinematic before and after cleaning transformation. A messy end-of-lease apartment becomes immaculate. Professional lighting, slow revealing pan. Clean modern aesthetic.",
            "cinematic": "Dramatic time-lapse of a complete apartment cleaning transformation. Morning light streams through windows. Every surface goes from dusty to gleaming. Cinematic shallow depth of field.",
            "fun": "Playful stop-motion style cleaning transformation. Mops and sponges dance across surfaces. Dirt magically disappears. Colourful, upbeat energy. Fun and shareable.",
        },
        "testimonial": {
            "energetic": "Happy property manager in a bright Sydney office, speaking to camera with enthusiasm about their cleaning service experience. Modern office background, warm lighting.",
            "professional": "Professional testimonial setup. Well-dressed property manager in a clean, modern office. Speaking confidently to camera about reliable cleaning services. Warm corporate lighting.",
            "cinematic": "Documentary-style testimonial. Property manager walking through a spotless apartment, gesturing at the clean spaces. Natural light, cinematic framing.",
            "fun": "Casual, relatable testimonial. Property manager giving a thumbs up in front of a freshly cleaned apartment. Bright, cheerful atmosphere. Before/after shown on phone screen.",
        },
        "team_intro": {
            "energetic": "Energetic team introduction video. Professional cleaning crew arrives at a Sydney apartment with equipment. Quick cuts showing teamwork, cleaning in action, smiling faces. Dynamic camera movement.",
            "professional": "Professional team introduction. Cleaning crew in branded uniforms, arriving at a property. Organised, efficient, friendly. Clean corporate style.",
            "cinematic": "Cinematic team arrival sequence. Cleaning van pulls up to a Sydney house at sunrise. Team exits with equipment. Slow motion, golden hour lighting. Premium feel.",
            "fun": "Fun team introduction. Cleaning crew doing a group pose, then breaking into action. Speed ramping effects. Music video style cuts. Personality-driven.",
        },
        "seasonal": {
            "energetic": "Spring cleaning promotional video. Flowers blooming outside, sunlight streaming into a home. Energetic cleaning montage. Fresh, bright, new season energy. Sydney suburb backdrop.",
            "professional": "End of financial year cleaning special. Professional office and home cleaning montage. Clean, organised spaces. Text: Start fresh this new financial year.",
            "cinematic": "New year, fresh start. Cinematic montage of homes being deep cleaned. Dramatic before/after reveals. Sydney skyline in background. Aspirational lifestyle feel.",
            "fun": "Holiday season cleaning chaos turned calm. Family home goes from party mess to sparkling clean. Fast-forward cleaning magic. Fun holiday music vibe.",
        },
    }

    if ad_type not in prompts:
        return f"Error: Unknown ad type '{ad_type}'. Available: {', '.join(prompts.keys())}"

    style_prompts = prompts[ad_type]
    if style not in style_prompts:
        return f"Error: Unknown style '{style}'. Available: {', '.join(style_prompts.keys())}"

    prompt = style_prompts[style]

    return f"""Ready-to-use video prompt:

Type: {ad_type}
Style: {style}

Prompt:
{prompt}

Recommended settings:
  Model: kling1.6 (fast) or sora2 (premium)
  Duration: 5s (social media) or 10s (website)
  Aspect: 9:16 (Reels/TikTok) or 16:9 (YouTube/website)

To generate, run:
  generate_video("{prompt[:80]}...", model="kling1.6", duration=5, aspect_ratio="9:16")"""


@mcp.tool()
def generate_cleaning_ad_image(ad_type: str = "before_after") -> str:
    """
    Generate a pre-written cleaning ad image prompt.

    ad_type: before_after, promotional, social_post, google_ad
    """
    prompts = {
        "before_after": "Split image showing before and after of an end-of-lease apartment clean. Left side dirty and messy, right side sparkling clean. Modern Sydney apartment. Professional photography style. High contrast. Satisfying transformation.",
        "promotional": "Professional cleaning service promotional image. Sparkling clean modern kitchen with gleaming benchtops. Fresh flowers on counter. Bright natural light. Text space at top for overlay. Premium feel. Sydney style apartment.",
        "social_post": "Eye-catching social media image for a cleaning business. Bright, clean apartment interior. Professional cleaning equipment artfully arranged. Instagram-worthy composition. Warm inviting lighting. Modern minimalist style.",
        "google_ad": "Clean, professional banner image for a cleaning service Google Ad. Simple composition: gleaming clean surface with cleaning supplies. White and blue colour scheme. Space for text overlay. High quality, commercial photography style.",
    }

    if ad_type not in prompts:
        return f"Error: Unknown ad type '{ad_type}'. Available: {', '.join(prompts.keys())}"

    prompt = prompts[ad_type]

    return f"""Ready-to-use image prompt:

Type: {ad_type}

Prompt:
{prompt}

Recommended settings:
  Model: flux2 (photorealistic) or ideogram (with text)
  Aspect: 1:1 (Instagram) or 16:9 (banner/cover)

To generate, run:
  generate_image("{prompt[:80]}...", model="flux2", aspect_ratio="1:1")"""


if __name__ == "__main__":
    mcp.run()
