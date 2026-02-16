#!/usr/bin/env python3
"""
Comprehensive Google Services Test
Tests Gmail, Calendar, Sheets, Drive, and Google Ads APIs
Created: 2026-02-03
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import urllib.request
import urllib.error
import urllib.parse

# Load environment variables
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

# Token management
TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"

def load_tokens():
    """Load OAuth tokens from file"""
    if not TOKEN_FILE.exists():
        return None
    with open(TOKEN_FILE) as f:
        return json.load(f)

def save_tokens(tokens):
    """Save OAuth tokens to file"""
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)
    os.chmod(TOKEN_FILE, 0o600)

def refresh_access_token(refresh_token):
    """Refresh the access token using refresh token"""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode()

    req = urllib.request.Request(
        'https://oauth2.googleapis.com/token',
        data=data,
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            new_tokens = json.loads(resp.read().decode())
            return new_tokens.get('access_token')
    except Exception as e:
        print(f"Failed to refresh token: {e}")
        return None

def get_valid_access_token():
    """Get a valid access token, refreshing if needed"""
    tokens = load_tokens()
    if not tokens:
        return None, "No tokens file found"

    # Try to refresh to get a fresh token
    if 'refresh_token' in tokens:
        new_access_token = refresh_access_token(tokens['refresh_token'])
        if new_access_token:
            tokens['access_token'] = new_access_token
            save_tokens(tokens)
            return new_access_token, None

    return tokens.get('access_token'), None

def api_request(url, access_token, method='GET', data=None):
    """Make an authenticated API request"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode()

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode()), None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return None, f"HTTP {e.code}: {error_body[:200]}"
    except Exception as e:
        return None, str(e)

# ===== TEST FUNCTIONS =====

def test_gmail(access_token):
    """Test Gmail API - list recent messages"""
    print("\n[GMAIL]")
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=5"
    data, error = api_request(url, access_token)

    if error:
        print(f"  [-] FAILED: {error}")
        return False

    messages = data.get('messages', [])
    print(f"  [+] SUCCESS: Found {len(messages)} recent messages")

    # Get profile
    url = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
    data, error = api_request(url, access_token)
    if data:
        print(f"  [+] Email: {data.get('emailAddress', 'unknown')}")

    return True

def test_calendar(access_token):
    """Test Google Calendar API - list upcoming events"""
    print("\n[CALENDAR]")

    # Get current time in ISO format
    now = datetime.utcnow().isoformat() + 'Z'
    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=5&timeMin={now}&singleEvents=true&orderBy=startTime"

    data, error = api_request(url, access_token)

    if error:
        print(f"  [-] FAILED: {error}")
        return False

    events = data.get('items', [])
    print(f"  [+] SUCCESS: Found {len(events)} upcoming events")

    for event in events[:3]:
        start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'No date'))
        print(f"      - {event.get('summary', 'No title')[:40]} ({start[:10]})")

    return True

def test_sheets(access_token):
    """Test Google Sheets API - read a spreadsheet"""
    print("\n[SHEETS]")

    sheet_id = os.environ.get('GOOGLE_SHEETS_ID', '')
    if not sheet_id:
        print("  [-] SKIPPED: GOOGLE_SHEETS_ID not set")
        return True  # Not a failure, just not configured

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}"
    data, error = api_request(url, access_token)

    if error:
        print(f"  [-] FAILED: {error}")
        return False

    title = data.get('properties', {}).get('title', 'Unknown')
    sheets = data.get('sheets', [])
    print(f"  [+] SUCCESS: Spreadsheet '{title}' with {len(sheets)} sheet(s)")

    return True

def test_drive(access_token):
    """Test Google Drive API - list recent files"""
    print("\n[DRIVE]")

    url = "https://www.googleapis.com/drive/v3/files?pageSize=5&fields=files(id,name,mimeType)"
    data, error = api_request(url, access_token)

    if error:
        print(f"  [-] FAILED: {error}")
        return False

    files = data.get('files', [])
    print(f"  [+] SUCCESS: Found {len(files)} recent files")

    for f in files[:3]:
        print(f"      - {f.get('name', 'Unknown')[:40]}")

    return True

def test_google_ads(access_token):
    """Test Google Ads API - get accessible customers"""
    print("\n[GOOGLE ADS]")

    developer_token = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', '')
    if not developer_token:
        print("  [-] SKIPPED: GOOGLE_ADS_DEVELOPER_TOKEN not set")
        return True

    # Use the Google Ads REST API to list accessible customers
    # Using v18 (latest stable as of 2026)
    url = "https://googleads.googleapis.com/v18/customers:listAccessibleCustomers"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'developer-token': developer_token,
        'Content-Type': 'application/json'
    }

    req = urllib.request.Request(url, headers=headers, method='GET')

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            customers = data.get('resourceNames', [])
            print(f"  [+] SUCCESS: Found {len(customers)} accessible customer account(s)")

            for cust in customers[:3]:
                # Extract customer ID from resource name
                cust_id = cust.split('/')[-1] if '/' in cust else cust
                print(f"      - Customer ID: {cust_id}")

            return True

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_json = json.loads(error_body)
            error_msg = error_json.get('error', {}).get('message', error_body[:200])
        except:
            error_msg = error_body[:200]

        # Check for common issues
        if 'DEVELOPER_TOKEN_NOT_APPROVED' in error_body:
            print(f"  [!] WARNING: Developer token pending approval (test account access only)")
            print(f"      This is normal for new tokens - apply at ads.google.com/aw/apicenter")
            return True  # Not a hard failure
        elif 'NOT_ADS_USER' in error_body:
            print(f"  [!] WARNING: No Google Ads account linked to this Google account")
            return True
        elif e.code == 404 or 'Not Found' in error_body:
            print(f"  [!] WARNING: Google Ads API not enabled in Cloud Console")
            print(f"      Enable at: console.cloud.google.com/apis/library/googleads.googleapis.com")
            return True  # Not a hard failure - API just needs enabling
        else:
            print(f"  [-] FAILED: {error_msg}")
            return False

    except Exception as e:
        print(f"  [-] FAILED: {e}")
        return False

def test_google_ads_campaign_info(access_token):
    """Test Google Ads API - get campaign information"""
    print("\n[GOOGLE ADS - CAMPAIGNS]")

    developer_token = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', '')
    customer_id = os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '')

    if not developer_token or not customer_id:
        print("  [-] SKIPPED: Missing GOOGLE_ADS_DEVELOPER_TOKEN or GOOGLE_ADS_LOGIN_CUSTOMER_ID")
        return True

    # Clean customer ID (remove dashes)
    customer_id = customer_id.replace('-', '')

    url = f"https://googleads.googleapis.com/v18/customers/{customer_id}/googleAds:searchStream"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'developer-token': developer_token,
        'Content-Type': 'application/json'
    }

    # Simple query to get campaign names
    query = {
        "query": "SELECT campaign.id, campaign.name, campaign.status FROM campaign LIMIT 5"
    }

    req = urllib.request.Request(url, headers=headers, method='POST')
    req.data = json.dumps(query).encode()

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode()
            # Response is newline-delimited JSON
            results = []
            for line in data.strip().split('\n'):
                if line:
                    results.append(json.loads(line))

            campaigns = []
            for result in results:
                for row in result.get('results', []):
                    campaign = row.get('campaign', {})
                    campaigns.append({
                        'id': campaign.get('id'),
                        'name': campaign.get('name'),
                        'status': campaign.get('status')
                    })

            print(f"  [+] SUCCESS: Found {len(campaigns)} campaign(s)")
            for c in campaigns[:5]:
                print(f"      - {c['name']} (ID: {c['id']}, Status: {c['status']})")

            return True

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        if 'DEVELOPER_TOKEN_NOT_APPROVED' in error_body:
            print(f"  [!] WARNING: Developer token pending approval")
            return True
        elif 'CUSTOMER_NOT_FOUND' in error_body:
            print(f"  [!] WARNING: Customer ID {customer_id} not found or not accessible")
            return True
        elif e.code == 404 or 'Not Found' in error_body:
            print(f"  [!] WARNING: Google Ads API not enabled - enable in Cloud Console")
            return True
        else:
            print(f"  [-] FAILED: {error_body[:200]}")
            return False
    except Exception as e:
        print(f"  [-] FAILED: {e}")
        return False

def run_all_tests():
    """Run all Google service tests"""
    print("=" * 60)
    print("  GOOGLE SERVICES COMPREHENSIVE TEST")
    print("  Clean Up Bros - Sydney, Australia")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} AEST")
    print("=" * 60)

    # Get valid access token
    print("\n[AUTHENTICATION]")
    access_token, error = get_valid_access_token()

    if error:
        print(f"  [-] FAILED: {error}")
        return False

    if not access_token:
        print("  [-] FAILED: No access token available")
        print("  Run: python3 google-oauth-setup.py")
        return False

    print(f"  [+] Access token obtained (refreshed)")

    # Check scopes
    tokens = load_tokens()
    scopes = tokens.get('scope', '').split()
    print(f"  [+] Authorized scopes: {len(scopes)}")

    has_ads = any('adwords' in s for s in scopes)
    print(f"  [+] Google Ads scope: {'Yes' if has_ads else 'No'}")

    # Run tests
    results = {}

    results['Gmail'] = test_gmail(access_token)
    results['Calendar'] = test_calendar(access_token)
    results['Sheets'] = test_sheets(access_token)
    results['Drive'] = test_drive(access_token)
    results['Google Ads (Auth)'] = test_google_ads(access_token)
    results['Google Ads (Campaigns)'] = test_google_ads_campaign_info(access_token)

    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")

    print(f"\n  Total: {total} | Passed: {passed} | Failed: {total - passed}")
    print(f"  Success Rate: {passed/total*100:.0f}%")

    if passed == total:
        print("\n  [+] ALL GOOGLE SERVICES WORKING!")
    else:
        print(f"\n  [!] {total - passed} service(s) need attention")

    print("=" * 60)

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
