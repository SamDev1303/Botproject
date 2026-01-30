#!/usr/bin/env python3
"""
Fetch Telegram messages and update dashboard status
This runs on Mac and pushes updates to S3
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Load environment manually (no external dependencies)
def load_env_file(path):
    """Load env file without dotenv dependency"""
    env_vars = {}
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
    except:
        pass
    return env_vars

_env = load_env_file("~/.clawdbot/.env")
TELEGRAM_TOKEN = _env.get("TELEGRAM_BOT_TOKEN", "")
DASHBOARD_DIR = Path("/Users/hafsahnuzhat/Desktop/🦀/bella-dashboard")
STATUS_FILE = DASHBOARD_DIR / "status.json"
MESSAGES_FILE = DASHBOARD_DIR / "messages.json"
LAST_UPDATE_FILE = DASHBOARD_DIR / ".last_update_id"

def get_last_update_id():
    """Get the last processed update ID"""
    try:
        if LAST_UPDATE_FILE.exists():
            return int(LAST_UPDATE_FILE.read_text().strip())
    except:
        pass
    return 0

def save_last_update_id(update_id):
    """Save the last processed update ID"""
    LAST_UPDATE_FILE.write_text(str(update_id))

def fetch_telegram_updates():
    """Fetch new messages from Telegram"""
    import urllib.request
    import urllib.error

    last_id = get_last_update_id()
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={last_id + 1}&limit=10"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("ok"):
                return data.get("result", [])
    except Exception as e:
        print(f"Error fetching updates: {e}")
    return []

def check_gateway_health():
    """Check if gateway is running"""
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:18789/health", timeout=5) as r:
            return "1-UP" if r.status == 200 else "GAME OVER"
    except:
        return "GAME OVER"

def check_telegram_bot():
    """Check if Telegram bot process is running"""
    try:
        result = subprocess.run(["pgrep", "-f", "clawdbot|moltbot"], capture_output=True)
        return "LINKED" if result.returncode == 0 else "OFFLINE"
    except:
        return "OFFLINE"

def count_api_keys():
    """Count API keys in .env"""
    try:
        env_path = Path.home() / ".clawdbot" / ".env"
        if env_path.exists():
            count = sum(1 for line in env_path.read_text().splitlines()
                       if "=" in line and not line.strip().startswith("#"))
            return f"×{count}"
    except:
        pass
    return "×0"

def update_dashboard(updates):
    """Update the dashboard status and messages"""

    # Load existing status to preserve activities
    existing_status = {}
    if STATUS_FILE.exists():
        try:
            existing_status = json.loads(STATUS_FILE.read_text())
        except:
            existing_status = {}

    # Load existing activities
    existing_activities = existing_status.get("activities", [])
    existing_task_count = existing_status.get("taskCount", 0)
    last_message_time = existing_status.get("lastMessageTime", 0)

    status = {
        "status": "idle",
        "currentTask": "Princess Bella is ready for adventure!",
        "progress": 0,
        "taskCount": existing_task_count,
        "lastMessageTime": last_message_time,
        "health": {
            "gateway": check_gateway_health(),
            "telegram": check_telegram_bot(),
            "apis": count_api_keys()
        },
        "activities": existing_activities,  # Preserve existing activities
        "lastUpdated": datetime.utcnow().isoformat() + "Z"
    }

    # Load existing messages
    messages = []
    if MESSAGES_FILE.exists():
        try:
            data = json.loads(MESSAGES_FILE.read_text())
            messages = data.get("messages", []) if isinstance(data, dict) else data
        except:
            messages = []

    # Process new updates
    max_update_id = get_last_update_id()
    new_messages = []
    current_time = datetime.now().timestamp()

    for update in updates:
        update_id = update.get("update_id", 0)
        max_update_id = max(max_update_id, update_id)

        message = update.get("message", {})
        if message:
            text = message.get("text", "")
            sender = message.get("from", {})
            sender_name = sender.get("first_name", "Unknown")
            timestamp = message.get("date", 0)
            time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M")

            if text:
                new_messages.append({
                    "id": update_id,
                    "sender": sender_name,
                    "text": text[:200],  # Truncate long messages
                    "time": time_str,
                    "timestamp": timestamp
                })

                # Update status to working
                status["status"] = "working"
                status["currentTask"] = f"Processing: {text[:50]}..."
                status["progress"] = 50
                status["lastMessageTime"] = current_time
                status["taskCount"] = existing_task_count + 1

                # Add to activities (at the beginning)
                status["activities"].insert(0, {
                    "icon": "📨",
                    "time": time_str,
                    "text": f"Message from {sender_name}"
                })

    # Keep only last 10 messages
    messages = (new_messages + messages)[:10]

    # Keep only last 8 activities
    status["activities"] = status["activities"][:8]

    # If no new messages, check if we should go back to idle
    if not new_messages:
        # Only go idle after 10 seconds of no new messages
        time_since_last = current_time - status.get("lastMessageTime", 0)
        if time_since_last > 10:
            status["status"] = "idle"
            status["currentTask"] = "Princess Bella is ready for adventure!"
            status["progress"] = 0
        elif time_since_last > 5:
            # Transition: Bella finished the task, add completion activity
            status["status"] = "idle"
            status["currentTask"] = "Task complete! Waiting for next quest..."
            status["progress"] = 100
            # Add completion activity if the last one isn't already a completion
            if status["activities"] and "Completed" not in status["activities"][0].get("text", ""):
                now_str = datetime.now().strftime("%H:%M")
                status["activities"].insert(0, {
                    "icon": "✅",
                    "time": now_str,
                    "text": "Completed quest!"
                })
        else:
            # Still working - within 5 seconds
            status["status"] = "working"
            status["currentTask"] = existing_status.get("currentTask", "Processing...")
            status["progress"] = 75

    # Don't add default activities - show empty state instead
    # Real activities will be added when messages come in

    # Save files
    STATUS_FILE.write_text(json.dumps(status, indent=2))
    MESSAGES_FILE.write_text(json.dumps({"messages": messages}, indent=2))

    # Save last update ID
    if max_update_id > 0:
        save_last_update_id(max_update_id)

    return len(new_messages), status["status"]

def push_to_s3():
    """Push updated files to S3"""
    try:
        subprocess.run([
            "aws", "s3", "cp", str(STATUS_FILE),
            "s3://bella-dashboard-hafsah/status.json",
            "--quiet"
        ], check=True)

        subprocess.run([
            "aws", "s3", "cp", str(MESSAGES_FILE),
            "s3://bella-dashboard-hafsah/messages.json",
            "--quiet"
        ], check=True)

        return True
    except Exception as e:
        print(f"Error pushing to S3: {e}")
        return False

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching Telegram updates...")

    updates = fetch_telegram_updates()
    new_count, status = update_dashboard(updates)

    if new_count > 0:
        print(f"  📨 {new_count} new message(s) - Status: {status}")
    else:
        print(f"  ✓ No new messages - Status: {status}")

    if push_to_s3():
        print("  ☁️ Pushed to cloud")
    else:
        print("  ⚠️ Failed to push to cloud")

if __name__ == "__main__":
    main()
