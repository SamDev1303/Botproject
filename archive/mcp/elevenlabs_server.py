#!/usr/bin/env python3
"""
ElevenLabs MCP Server - AI Voice Generation
For Clean Up Bros professional voice messages, voicemails, and content
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

API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')
BASE_URL = "https://api.elevenlabs.io/v1"
OUTPUT_DIR = Path.home() / "clawd" / "generated" / "voice"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Business contact - NEVER tell people to call Twilio number
BUSINESS_PHONE = "0406 764 585"
WEBSITE = "cleanupbros.com.au"

# Default voice IDs (ElevenLabs preset voices)
VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",  # Female, warm
    "bella": "EXAVITQu4vr4xnSDxMaL",    # Female, soft
    "antoni": "ErXwobaYiN019PkySvjV",   # Male, well-rounded
    "elli": "MF3mGyEYCl7XYWbV9V6O",     # Female, young
    "josh": "TxGEqnHWrfWFTfGW9XjX",     # Male, deep
    "arnold": "VR6AewLTigWG4xSOukaG",   # Male, crisp
    "adam": "pNInz6obpgDQGcFmaJgB",     # Male, deep
    "sam": "yoZ06aMxZJJ28mfd3POQ",      # Male, raspy
    # GROK-STYLE: Fast, punchy, confident
    "grok": "pNInz6obpgDQGcFmaJgB",     # Using Adam - deep, confident male
}

def api_request(endpoint, method="GET", data=None, is_audio=False):
    """Make ElevenLabs API request"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    if data:
        data = json.dumps(data).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            if is_audio:
                logger.info(f"{method} {endpoint[:60]}... - Success (audio)")
                return response.read()
            result = json.loads(response.read().decode())
            logger.info(f"{method} {endpoint[:60]}... - Success")
            return result
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:200]
        logger.error(f"{method} {endpoint[:60]}... - {e.code}: {error_msg}")
        return {"error": f"{e.code}: {error_msg}"}

# Create MCP server
mcp = FastMCP("ElevenLabs")

# ============== TEXT TO SPEECH ==============

@mcp.tool()
def generate_voice(text: str, voice: str = "rachel", filename: str = "") -> str:
    """
    Generate voice audio from text.
    Voices: rachel, bella, antoni, elli, josh, arnold, adam, sam
    Returns path to generated MP3 file.
    """
    voice_id = VOICES.get(voice.lower(), VOICES["rachel"])

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    audio = api_request(f"/text-to-speech/{voice_id}", method="POST", data=data, is_audio=True)

    if isinstance(audio, dict) and "error" in audio:
        logger.error(f"Voice generation failed: {audio['error']}")
        return f"Error: {audio['error']}"

    # Save file
    if not filename:
        filename = f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

    filepath = OUTPUT_DIR / filename
    with open(filepath, 'wb') as f:
        f.write(audio)

    logger.info(f"Voice generated: {voice}, {len(text)} chars, saved to {filename}")
    return f"""Voice generated successfully!
File: {filepath}
Voice: {voice}
Text length: {len(text)} characters"""

@mcp.tool()
def generate_voicemail_greeting(business_hours: str = "9am to 5pm, Monday to Friday") -> str:
    """Generate a professional voicemail greeting for Clean Up Bros"""
    text = f"""Hello, you've reached Clean Up Bros, Sydney's trusted cleaning service.

We're unable to take your call right now, but your call is important to us.

Our business hours are {business_hours}.

Please leave your name, number, and a brief message, and we'll get back to you as soon as possible.

For urgent enquiries, you can also reach us via WhatsApp or email at cleanupbros.au@gmail.com.

Thank you for calling Clean Up Bros!"""

    return generate_voice(text, voice="rachel", filename="voicemail_greeting.mp3")

@mcp.tool()
def generate_booking_confirmation_audio(client_name: str, date: str, time: str, service: str) -> str:
    """Generate a voice booking confirmation"""
    text = f"""Hi {client_name}!

This is Clean Up Bros confirming your booking.

Your {service} is scheduled for {date} at {time}.

Please ensure access is available at the property.

If you have any questions, feel free to call us back or reply to this message.

We look forward to seeing you!"""

    filename = f"booking_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.mp3"
    return generate_voice(text, voice="rachel", filename=filename)

@mcp.tool()
def generate_reminder_audio(client_name: str, time: str) -> str:
    """Generate a voice reminder for tomorrow's booking"""
    text = f"""Hi {client_name}!

Just a friendly reminder from Clean Up Bros.

Your cleaning is scheduled for tomorrow at {time}.

Please make sure access is available and let us know if you have any special instructions.

See you tomorrow!"""

    filename = f"reminder_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.mp3"
    return generate_voice(text, voice="rachel", filename=filename)

@mcp.tool()
def generate_marketing_audio(promo_text: str, voice: str = "rachel") -> str:
    """Generate marketing/promotional audio content"""
    filename = f"promo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    return generate_voice(promo_text, voice=voice, filename=filename)

@mcp.tool()
def generate_cold_call_intro() -> str:
    """Generate a professional cold call introduction (standard style)"""
    text = """Hello! My name is Sarah from Clean Up Bros, Sydney's trusted cleaning service.

I'm reaching out because we work with property managers in your area,
providing reliable end of lease and commercial cleaning services.

Our clients love our bond-back guarantee and our eco-friendly cleaning products.

I'd love to tell you more about how we can help your business.
Would you have a few minutes to chat?

If now isn't a good time, please feel free to call us back at 0406 764 585,
or visit our website at cleanupbros.com.au.

Thank you for your time!"""

    return generate_voice(text, voice="rachel", filename="cold_call_intro.mp3")

# ============== GROK-STYLE COLD CALLS ==============

@mcp.tool()
def generate_grok_cold_call(company: str, contact_name: str = "") -> str:
    """
    Generate a GROK-STYLE cold call - fast, punchy, witty, confident.
    No fluff. No corporate speak. Just direct and memorable.

    This is the personality Hafsah wants - like Grok AI.
    """
    name_part = f"Is this {contact_name}? Perfect." if contact_name else "Quick 20 seconds."

    # GROK STYLE: Fast, punchy, no filler words, confident, slightly edgy
    text = f"""{name_part}

Cold call. I know. Hate getting these too. But hear me out - 15 seconds.

You're at {company}. You deal with cleaners. Some are good. Most aren't.

I'm Hafsah. Clean Up Bros. We do end of lease. One stat: zero bond failures. Ever.

Not asking for anything. Just saying - when your current cleaner ghosts you mid-lease,
call 0406 764 585. That's 0406 764 585.

Oh - don't call THIS number back. It's automated. Call the real one.

Bella found you. She's our AI. Built by Shamal. I'm the human.

Later."""

    filename = f"grok_cold_{company.replace(' ', '_')[:20]}_{datetime.now().strftime('%H%M%S')}.mp3"
    return generate_voice(text, voice="grok", filename=filename)

@mcp.tool()
def generate_grok_childcare_call(centre_name: str, contact_name: str = "") -> str:
    """
    GROK-STYLE cold call for childcare centres.
    Fast, punchy, gets to the point.
    """
    name_part = f"{contact_name}?" if contact_name else "Hey."

    text = f"""{name_part}

15 seconds. Cold call. Apologies in advance.

{centre_name}, right? Childcare. You care about hygiene more than most.

I'm Hafsah. Clean Up Bros. We deep clean centres after hours.
Parents notice clean. Kids touch everything. You know this.

Not selling. Just - when you need someone reliable, call 0406 764 585.
Don't call back THIS number. It's a robot. Call the real one.

Found you via Bella - our AI.

Cheers."""

    filename = f"grok_childcare_{centre_name.replace(' ', '_')[:15]}_{datetime.now().strftime('%H%M%S')}.mp3"
    return generate_voice(text, voice="grok", filename=filename)

@mcp.tool()
def generate_grok_followup_call(company: str, days_since: int = 3) -> str:
    """
    GROK-STYLE follow-up call. Even shorter and punchier.
    """
    text = f"""Hey. Quick follow-up.

Called you {days_since} days ago about {company}. Clean Up Bros.

Not chasing. Just - if your cleaner situation hasn't improved,
we're still here. 0406 764 585.

That's it. Short and sweet.

Later."""

    filename = f"grok_followup_{company.replace(' ', '_')[:15]}_{datetime.now().strftime('%H%M%S')}.mp3"
    return generate_voice(text, voice="grok", filename=filename)

@mcp.tool()
def get_grok_voice_settings() -> dict:
    """
    Get optimized voice settings for Grok-style delivery.
    Faster pace, more confidence, less robotic.
    """
    return {
        "voice": "grok",
        "model_id": "eleven_turbo_v2",  # Faster model
        "voice_settings": {
            "stability": 0.3,           # Less stable = more dynamic
            "similarity_boost": 0.8,    # High similarity for consistency
            "style": 0.5,               # Add some style variation
            "use_speaker_boost": True   # Clearer articulation
        },
        "notes": "Use eleven_turbo_v2 for faster generation. Lower stability for more natural, dynamic delivery."
    }

# ============== VOICE MANAGEMENT ==============

@mcp.tool()
def list_voices() -> str:
    """List all available voices"""
    result = api_request("/voices")

    if "error" in result:
        return f"Error: {result['error']}"

    voices = result.get('voices', [])
    output = ["Available Voices:", "", "Preset Voices:"]

    for name, vid in VOICES.items():
        output.append(f"  • {name}")

    output.append("")
    output.append("Custom/Cloned Voices:")

    for v in voices:
        if v.get('category') == 'cloned':
            output.append(f"  • {v.get('name')} (ID: {v.get('voice_id')})")

    return "\n".join(output)

@mcp.tool()
def get_voice_settings(voice: str = "rachel") -> str:
    """Get settings for a voice"""
    voice_id = VOICES.get(voice.lower(), VOICES["rachel"])
    result = api_request(f"/voices/{voice_id}/settings")

    if "error" in result:
        return f"Error: {result['error']}"

    return f"""Voice Settings for {voice}:
Stability: {result.get('stability', 'N/A')}
Similarity Boost: {result.get('similarity_boost', 'N/A')}"""

@mcp.tool()
def check_quota() -> str:
    """Check remaining character quota"""
    result = api_request("/user/subscription")

    if "error" in result:
        return f"Error: {result['error']}"

    char_count = result.get('character_count', 0)
    char_limit = result.get('character_limit', 0)
    remaining = char_limit - char_count

    return f"""ElevenLabs Usage:
Characters Used: {char_count:,}
Character Limit: {char_limit:,}
Remaining: {remaining:,}
Usage: {(char_count/char_limit*100):.1f}%"""

@mcp.tool()
def list_generated_files() -> str:
    """List all generated voice files"""
    files = list(OUTPUT_DIR.glob("*.mp3"))

    if not files:
        return "No generated voice files found."

    output = ["Generated Voice Files:", ""]
    for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
        size_kb = f.stat().st_size / 1024
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        output.append(f"• {f.name} ({size_kb:.1f} KB) - {mtime}")

    return "\n".join(output)

if __name__ == "__main__":
    mcp.run()
