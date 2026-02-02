#!/usr/bin/env python3
"""
API Health Check for Clean Up Bros / Bella
Tests all configured APIs and services without exposing credentials
Created: 2026-02-03
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.error
import ssl

# Sydney timezone for timestamps
TIMEZONE = "Australia/Sydney"

def load_env():
    """Load environment variables from ~/.clawdbot/.env"""
    env_file = Path.home() / ".clawdbot" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))

def check_env_var(var_name: str) -> tuple[bool, str]:
    """Check if an environment variable is set and non-empty"""
    value = os.environ.get(var_name, '')
    if value:
        # Mask the value for security
        masked = value[:4] + '***' + value[-4:] if len(value) > 12 else '***'
        return True, f"Set ({masked})"
    return False, "NOT SET"

def test_google_oauth() -> tuple[bool, str]:
    """Test Google OAuth token file exists and is valid"""
    token_file = Path.home() / ".clawdbot" / "google-oauth-tokens.json"
    if not token_file.exists():
        return False, "Token file missing - run google-oauth-setup.py"

    try:
        with open(token_file) as f:
            tokens = json.load(f)

        if 'refresh_token' in tokens:
            return True, "OAuth tokens present"
        elif 'access_token' in tokens:
            return True, "Access token only (may expire)"
        else:
            return False, "Invalid token file format"
    except json.JSONDecodeError:
        return False, "Token file corrupted"
    except Exception as e:
        return False, f"Error reading tokens: {type(e).__name__}"

def test_square_api() -> tuple[bool, str]:
    """Test Square API connectivity"""
    token = os.environ.get('SQUARE_ACCESS_TOKEN', '')
    if not token:
        return False, "SQUARE_ACCESS_TOKEN not set"

    env = os.environ.get('SQUARE_ENVIRONMENT', 'production')
    base_url = "https://connect.squareup.com" if env == "production" else "https://connect.squareupsandbox.com"

    try:
        req = urllib.request.Request(
            f"{base_url}/v2/locations",
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            locations = data.get('locations', [])
            return True, f"Connected ({len(locations)} location(s))"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection failed: {e.reason}"
    except Exception as e:
        return False, f"Error: {type(e).__name__}"

def test_twilio_api() -> tuple[bool, str]:
    """Test Twilio API connectivity"""
    sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
    token = os.environ.get('TWILIO_AUTH_TOKEN', '')

    if not sid or not token:
        return False, "TWILIO credentials not set"

    try:
        # Create a password manager for Basic Auth
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}.json"

        # Use basic auth
        import base64
        credentials = base64.b64encode(f"{sid}:{token}".encode()).decode()

        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Basic {credentials}"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            status = data.get('status', 'unknown')
            return True, f"Connected (status: {status})"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection failed: {e.reason}"
    except Exception as e:
        return False, f"Error: {type(e).__name__}"

def test_whatsapp_api() -> tuple[bool, str]:
    """Test WhatsApp Business API connectivity"""
    token = os.environ.get('META_SYSTEM_USER_TOKEN', '')
    phone_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')

    if not token or not phone_id:
        return False, "WhatsApp credentials not set"

    try:
        url = f"https://graph.facebook.com/v18.0/{phone_id}"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            display = data.get('display_phone_number', 'unknown')
            return True, f"Connected ({display})"
    except urllib.error.HTTPError as e:
        if e.code == 400:
            return False, "Invalid phone number ID"
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection failed: {e.reason}"
    except Exception as e:
        return False, f"Error: {type(e).__name__}"

def test_brave_search() -> tuple[bool, str]:
    """Test Brave Search API"""
    key = os.environ.get('BRAVE_API_KEY', '')
    if not key:
        return False, "BRAVE_API_KEY not set"

    try:
        url = "https://api.search.brave.com/res/v1/web/search?q=test&count=1"
        req = urllib.request.Request(
            url,
            headers={"X-Subscription-Token": key}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return True, "Connected"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection failed: {e.reason}"
    except Exception as e:
        return False, f"Error: {type(e).__name__}"

def test_elevenlabs() -> tuple[bool, str]:
    """Test ElevenLabs Voice API"""
    key = os.environ.get('ELEVENLABS_API_KEY', '')
    if not key:
        return False, "ELEVENLABS_API_KEY not set"

    try:
        url = "https://api.elevenlabs.io/v1/user"
        req = urllib.request.Request(
            url,
            headers={"xi-api-key": key}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            tier = data.get('subscription', {}).get('tier', 'unknown')
            return True, f"Connected (tier: {tier})"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection failed: {e.reason}"
    except Exception as e:
        return False, f"Error: {type(e).__name__}"

def test_openrouter() -> tuple[bool, str]:
    """Test OpenRouter API"""
    key = os.environ.get('OPENROUTER_API_KEY', '')
    if not key:
        return False, "OPENROUTER_API_KEY not set"

    try:
        url = "https://openrouter.ai/api/v1/auth/key"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {key}"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return True, "Connected"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection failed: {e.reason}"
    except Exception as e:
        return False, f"Error: {type(e).__name__}"

def test_telegram_bot() -> tuple[bool, str]:
    """Test Telegram Bot API"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    if not token:
        return False, "TELEGRAM_BOT_TOKEN not set"

    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get('ok'):
                username = data.get('result', {}).get('username', 'unknown')
                return True, f"Connected (@{username})"
            return False, "API returned error"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection failed: {e.reason}"
    except Exception as e:
        return False, f"Error: {type(e).__name__}"

def test_apify() -> tuple[bool, str]:
    """Test Apify API"""
    key = os.environ.get('APIFY_API_KEY', '')
    if not key:
        return False, "APIFY_API_KEY not set"

    try:
        url = f"https://api.apify.com/v2/users/me?token={key}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            username = data.get('data', {}).get('username', 'unknown')
            return True, f"Connected ({username})"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection failed: {e.reason}"
    except Exception as e:
        return False, f"Error: {type(e).__name__}"

def run_health_check() -> dict:
    """Run all health checks and return results"""
    load_env()

    results = {
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }

    # Google Services
    print("\n" + "="*60)
    print("GOOGLE SERVICES")
    print("="*60)

    google_tests = {
        "OAuth Tokens": test_google_oauth,
        "Client ID": lambda: check_env_var("GOOGLE_CLIENT_ID"),
        "Client Secret": lambda: check_env_var("GOOGLE_CLIENT_SECRET"),
        "Ads Developer Token": lambda: check_env_var("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "Ads Customer ID": lambda: check_env_var("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "Sheets ID": lambda: check_env_var("GOOGLE_SHEETS_ID"),
    }

    for name, test_func in google_tests.items():
        ok, msg = test_func()
        status = "OK" if ok else "FAIL"
        symbol = "[+]" if ok else "[-]"
        print(f"{symbol} {name}: {msg}")
        results["services"][f"Google_{name.replace(' ', '_')}"] = {"ok": ok, "message": msg}

    # Square
    print("\n" + "="*60)
    print("SQUARE PAYMENTS")
    print("="*60)

    ok, msg = test_square_api()
    status = "OK" if ok else "FAIL"
    symbol = "[+]" if ok else "[-]"
    print(f"{symbol} Square API: {msg}")
    results["services"]["Square_API"] = {"ok": ok, "message": msg}

    # Twilio
    print("\n" + "="*60)
    print("TWILIO (SMS/VOICE)")
    print("="*60)

    ok, msg = test_twilio_api()
    symbol = "[+]" if ok else "[-]"
    print(f"{symbol} Twilio API: {msg}")
    results["services"]["Twilio_API"] = {"ok": ok, "message": msg}

    # WhatsApp/Meta
    print("\n" + "="*60)
    print("META (WHATSAPP/FACEBOOK/INSTAGRAM)")
    print("="*60)

    ok, msg = test_whatsapp_api()
    symbol = "[+]" if ok else "[-]"
    print(f"{symbol} WhatsApp API: {msg}")
    results["services"]["WhatsApp_API"] = {"ok": ok, "message": msg}

    meta_vars = ["META_APP_ID", "META_SYSTEM_USER_TOKEN", "WHATSAPP_BUSINESS_ACCOUNT_ID"]
    for var in meta_vars:
        ok, msg = check_env_var(var)
        symbol = "[+]" if ok else "[-]"
        print(f"{symbol} {var}: {msg}")
        results["services"][f"Meta_{var}"] = {"ok": ok, "message": msg}

    # Other Services
    print("\n" + "="*60)
    print("OTHER SERVICES")
    print("="*60)

    other_tests = {
        "Brave Search": test_brave_search,
        "ElevenLabs Voice": test_elevenlabs,
        "OpenRouter AI": test_openrouter,
        "Telegram Bot": test_telegram_bot,
        "Apify Scraping": test_apify,
    }

    for name, test_func in other_tests.items():
        ok, msg = test_func()
        symbol = "[+]" if ok else "[-]"
        print(f"{symbol} {name}: {msg}")
        results["services"][name.replace(' ', '_')] = {"ok": ok, "message": msg}

    # Summary
    total = len(results["services"])
    passed = sum(1 for s in results["services"].values() if s["ok"])
    failed = total - passed

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"Health: {passed/total*100:.0f}%")

    results["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "health_percent": round(passed/total*100, 1)
    }

    return results

def save_results(results: dict, output_file: str = None):
    """Save results to JSON file"""
    if output_file is None:
        output_dir = Path.home() / "Desktop" / "🦀" / "logs"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    return output_file

def main():
    print("\n" + "="*60)
    print("  BELLA API HEALTH CHECK")
    print("  Clean Up Bros - Sydney, Australia")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} AEST")
    print("="*60)

    results = run_health_check()

    # Save if requested
    if "--save" in sys.argv or "-s" in sys.argv:
        save_results(results)

    # Return exit code based on health
    if results["summary"]["failed"] > 0:
        print(f"\n[!] {results['summary']['failed']} service(s) require attention")
        sys.exit(1)
    else:
        print("\n[+] All services healthy!")
        sys.exit(0)

if __name__ == "__main__":
    main()
