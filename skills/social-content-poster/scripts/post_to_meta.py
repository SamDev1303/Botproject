#!/usr/bin/env python3
"""
Post to Facebook Page and Instagram via Meta Graph API
Uses credentials from ~/.clawdbot/.env
"""
import os
import json
import urllib.request
import urllib.parse
from pathlib import Path

# Load environment variables from ~/.clawdbot/.env
def load_env():
    env_file = Path.home() / ".clawdbot" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), value)

load_env()

# API credentials
TOKEN = os.environ.get('META_SYSTEM_USER_TOKEN', '')
BUSINESS_ID = os.environ.get('META_BUSINESS_ID', '')
API_VERSION = 'v18.0'
BASE_URL = f'https://graph.facebook.com/{API_VERSION}'

def meta_request(endpoint, method='GET', data=None, files=None):
    """Make a request to the Meta Graph API"""
    url = f"{BASE_URL}{endpoint}"
    
    # Add access token to params
    if '?' in url:
        url += f'&access_token={TOKEN}'
    else:
        url += f'?access_token={TOKEN}'
    
    headers = {}
    
    if data and not files:
        headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, headers=headers, method=method)
        req.data = json.dumps(data).encode()
    elif files:
        # For file uploads, use multipart/form-data
        import mimetypes
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
        
        body = b''
        for key, value in (data or {}).items():
            body += f'--{boundary}\r\n'.encode()
            body += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode()
            body += f'{value}\r\n'.encode()
        
        for key, filepath in files.items():
            filename = os.path.basename(filepath)
            mime_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
            body += f'--{boundary}\r\n'.encode()
            body += f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'.encode()
            body += f'Content-Type: {mime_type}\r\n\r\n'.encode()
            with open(filepath, 'rb') as f:
                body += f.read()
            body += b'\r\n'
        
        body += f'--{boundary}--\r\n'.encode()
        req = urllib.request.Request(url, headers=headers, method=method)
        req.data = body
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"API Error: {e.code} - {error_body}")
        return {'error': error_body}

def get_pages():
    """Get all Facebook Pages the user manages"""
    result = meta_request(f'/me/accounts')
    return result.get('data', [])

def get_instagram_accounts():
    """Get Instagram Business accounts linked to Pages"""
    pages = get_pages()
    ig_accounts = []
    
    for page in pages:
        page_id = page['id']
        result = meta_request(f'/{page_id}?fields=instagram_business_account')
        if 'instagram_business_account' in result:
            ig_accounts.append({
                'page_id': page_id,
                'page_name': page['name'],
                'instagram_id': result['instagram_business_account']['id']
            })
    
    return ig_accounts

def post_to_facebook(page_id, message, image_url=None, image_path=None):
    """
    Post to a Facebook Page
    
    Args:
        page_id: Facebook Page ID
        message: Post text/caption
        image_url: URL of image to post (optional)
        image_path: Local path to image (optional)
    
    Returns:
        Post ID if successful
    """
    if image_path:
        # Upload local image
        endpoint = f'/{page_id}/photos'
        result = meta_request(endpoint, 'POST', 
            data={'caption': message},
            files={'source': image_path})
    elif image_url:
        # Post with image URL
        endpoint = f'/{page_id}/photos'
        result = meta_request(endpoint, 'POST', data={
            'url': image_url,
            'caption': message
        })
    else:
        # Text-only post
        endpoint = f'/{page_id}/feed'
        result = meta_request(endpoint, 'POST', data={
            'message': message
        })
    
    if 'id' in result:
        print(f"✅ Posted to Facebook! Post ID: {result['id']}")
        return result['id']
    else:
        print(f"❌ Facebook post failed: {result}")
        return None

def post_to_instagram(instagram_id, caption, image_url):
    """
    Post to Instagram Business account
    
    Note: Instagram API requires image_url to be publicly accessible
    
    Args:
        instagram_id: Instagram Business Account ID
        caption: Post caption
        image_url: Public URL of image to post
    
    Returns:
        Media ID if successful
    """
    # Step 1: Create media container
    container = meta_request(f'/{instagram_id}/media', 'POST', data={
        'image_url': image_url,
        'caption': caption
    })
    
    if 'id' not in container:
        print(f"❌ Failed to create Instagram media container: {container}")
        return None
    
    container_id = container['id']
    
    # Step 2: Publish the container
    result = meta_request(f'/{instagram_id}/media_publish', 'POST', data={
        'creation_id': container_id
    })
    
    if 'id' in result:
        print(f"✅ Posted to Instagram! Media ID: {result['id']}")
        return result['id']
    else:
        print(f"❌ Instagram publish failed: {result}")
        return None

def post_reel_to_instagram(instagram_id, caption, video_url):
    """
    Post a Reel to Instagram Business account
    
    Args:
        instagram_id: Instagram Business Account ID
        caption: Reel caption
        video_url: Public URL of video file
    
    Returns:
        Media ID if successful
    """
    # Step 1: Create media container for Reel
    container = meta_request(f'/{instagram_id}/media', 'POST', data={
        'media_type': 'REELS',
        'video_url': video_url,
        'caption': caption
    })
    
    if 'id' not in container:
        print(f"❌ Failed to create Reel container: {container}")
        return None
    
    container_id = container['id']
    
    # Step 2: Check container status (video processing)
    import time
    for _ in range(30):  # Wait up to 5 minutes
        status = meta_request(f'/{container_id}?fields=status_code')
        if status.get('status_code') == 'FINISHED':
            break
        elif status.get('status_code') == 'ERROR':
            print(f"❌ Reel processing error: {status}")
            return None
        time.sleep(10)
    
    # Step 3: Publish the Reel
    result = meta_request(f'/{instagram_id}/media_publish', 'POST', data={
        'creation_id': container_id
    })
    
    if 'id' in result:
        print(f"✅ Posted Reel to Instagram! Media ID: {result['id']}")
        return result['id']
    else:
        print(f"❌ Reel publish failed: {result}")
        return None

def post_to_both(caption, image_url):
    """
    Post the same content to both Facebook and Instagram
    
    Args:
        caption: Post text
        image_url: Public URL of image
    
    Returns:
        Dict with facebook_id and instagram_id
    """
    results = {'facebook_id': None, 'instagram_id': None}
    
    # Get accounts
    pages = get_pages()
    ig_accounts = get_instagram_accounts()
    
    if not pages:
        print("❌ No Facebook Pages found")
        return results
    
    # Post to first Facebook Page
    page = pages[0]
    results['facebook_id'] = post_to_facebook(page['id'], caption, image_url=image_url)
    
    # Post to Instagram if available
    if ig_accounts:
        ig = ig_accounts[0]
        results['instagram_id'] = post_to_instagram(ig['instagram_id'], caption, image_url)
    else:
        print("⚠️ No Instagram Business account linked")
    
    return results

# CLI interface
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("""
Usage:
    python post_to_meta.py list              # List available accounts
    python post_to_meta.py post "Caption"    # Post text only to Facebook
    python post_to_meta.py post "Caption" --image URL  # Post with image to both
    python post_to_meta.py reel "Caption" --video URL  # Post Reel to Instagram
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        print("\n📘 Facebook Pages:")
        for page in get_pages():
            print(f"  - {page['name']} (ID: {page['id']})")
        
        print("\n📸 Instagram Accounts:")
        for ig in get_instagram_accounts():
            print(f"  - Linked to {ig['page_name']} (IG ID: {ig['instagram_id']})")
    
    elif command == 'post':
        if len(sys.argv) < 3:
            print("❌ Please provide a caption")
            sys.exit(1)
        
        caption = sys.argv[2]
        image_url = None
        
        if '--image' in sys.argv:
            idx = sys.argv.index('--image')
            if idx + 1 < len(sys.argv):
                image_url = sys.argv[idx + 1]
        
        if image_url:
            post_to_both(caption, image_url)
        else:
            pages = get_pages()
            if pages:
                post_to_facebook(pages[0]['id'], caption)
    
    elif command == 'reel':
        if len(sys.argv) < 3:
            print("❌ Please provide a caption")
            sys.exit(1)
        
        caption = sys.argv[2]
        video_url = None
        
        if '--video' in sys.argv:
            idx = sys.argv.index('--video')
            if idx + 1 < len(sys.argv):
                video_url = sys.argv[idx + 1]
        
        if not video_url:
            print("❌ Please provide --video URL")
            sys.exit(1)
        
        ig_accounts = get_instagram_accounts()
        if ig_accounts:
            post_reel_to_instagram(ig_accounts[0]['instagram_id'], caption, video_url)
        else:
            print("❌ No Instagram Business account found")
