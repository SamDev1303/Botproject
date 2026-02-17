#!/usr/bin/env python3
"""
Post video to Facebook Page + Instagram Reel via Meta Graph API.
Usage: python3 post_video_meta.py /path/to/video.mp4 "Caption text"
"""
import sys, os, json, time, urllib.request, urllib.parse
from pathlib import Path

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

TOKEN = os.environ.get('META_SYSTEM_USER_TOKEN', '')
PAGE_ID = os.environ.get('FB_PAGE_ID', '707617919097782')
IG_ID = os.environ.get('IG_BUSINESS_ID', '17841475542958087')
BASE = "https://graph.facebook.com/v21.0"

def api_call(url, data=None, method="POST"):
    if data:
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=body, method=method)
    else:
        req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())

def fb_post_video(video_path, caption):
    """Upload video to Facebook Page via resumable upload."""
    file_size = os.path.getsize(video_path)
    
    # Step 1: Start upload session
    start_data = {
        "upload_phase": "start",
        "file_size": str(file_size),
        "access_token": TOKEN
    }
    result = api_call(f"{BASE}/{PAGE_ID}/videos", start_data)
    upload_session_id = result.get("upload_session_id")
    video_id = result.get("video_id")
    print(f"  FB upload session: {upload_session_id}")
    
    # Step 2: Upload the video file
    with open(video_path, 'rb') as f:
        video_data = f.read()
    
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="upload_phase"\r\n\r\ntransfer\r\n'.encode()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="upload_session_id"\r\n\r\n{upload_session_id}\r\n'.encode()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="start_offset"\r\n\r\n0\r\n'.encode()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="access_token"\r\n\r\n{TOKEN}\r\n'.encode()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="video_file_chunk"; filename="video.mp4"\r\nContent-Type: video/mp4\r\n\r\n'.encode()
    body += video_data
    body += f"\r\n--{boundary}--\r\n".encode()
    
    req = urllib.request.Request(
        f"{BASE}/{PAGE_ID}/videos",
        data=body,
        method="POST"
    )
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    
    with urllib.request.urlopen(req, timeout=300) as r:
        transfer_result = json.loads(r.read().decode())
    print(f"  FB transfer: {transfer_result}")
    
    # Step 3: Finish upload
    finish_data = {
        "upload_phase": "finish",
        "upload_session_id": upload_session_id,
        "access_token": TOKEN,
        "description": caption
    }
    finish_result = api_call(f"{BASE}/{PAGE_ID}/videos", finish_data)
    print(f"  ✅ Facebook video posted! ID: {video_id}")
    return video_id

def fb_post_simple(video_path, caption):
    """Simple video upload to Facebook Page feed."""
    with open(video_path, 'rb') as f:
        video_data = f.read()
    
    boundary = "----FormBoundary7MA4YWxk"
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="description"\r\n\r\n{caption}\r\n'.encode()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="access_token"\r\n\r\n{TOKEN}\r\n'.encode()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="source"; filename="video.mp4"\r\nContent-Type: video/mp4\r\n\r\n'.encode()
    body += video_data
    body += f"\r\n--{boundary}--\r\n".encode()
    
    req = urllib.request.Request(
        f"{BASE}/{PAGE_ID}/videos",
        data=body,
        method="POST"
    )
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    
    with urllib.request.urlopen(req, timeout=300) as r:
        result = json.loads(r.read().decode())
    print(f"  ✅ Facebook video posted! Result: {result}")
    return result

def ig_post_reel(video_path, caption):
    """Post reel to Instagram. Requires public URL - upload to temp host first."""
    # For IG reels, we need a public video URL
    # Try using FB's video URL after upload, or skip if not possible
    print("  ⚠️ Instagram Reels require a public video URL.")
    print("  Posting as FB video only for now.")
    return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 post_video_meta.py /path/to/video.mp4 'Caption'")
        sys.exit(1)
    
    video_path = sys.argv[1]
    caption = sys.argv[2]
    
    if not os.path.exists(video_path):
        print(f"File not found: {video_path}")
        sys.exit(1)
    
    print(f"📹 Posting video: {video_path}")
    print(f"📝 Caption: {caption[:80]}...")
    print()
    
    print("--- FACEBOOK ---")
    try:
        fb_post_simple(video_path, caption)
    except Exception as e:
        print(f"  ❌ Facebook error: {e}")
    
    print("\n--- INSTAGRAM ---")
    ig_post_reel(video_path, caption)
