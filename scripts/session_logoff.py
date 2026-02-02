#!/usr/bin/env python3
"""
Session Logoff Automation for Bella
Saves session state, creates summary, syncs memory files, commits to GitHub
Created: 2026-02-03
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_DIR = Path.home() / "Desktop" / "🦀"
MEMORY_DIR = PROJECT_DIR / "memory"
WORKING_DIR = MEMORY_DIR / "working"
SESSIONS_DIR = MEMORY_DIR / "sessions"

CURRENT_TASKS_FILE = WORKING_DIR / "current-tasks.json"
HEARTBEAT_STATE_FILE = MEMORY_DIR / "heartbeat-state.json"

def get_sydney_time() -> datetime:
    """Get current time in Sydney timezone"""
    # Simple offset for AEST/AEDT
    from datetime import timezone, timedelta
    # AEDT (summer) = UTC+11, AEST (winter) = UTC+10
    # For Feb, use AEDT
    sydney_offset = timezone(timedelta(hours=11))
    return datetime.now(sydney_offset)

def get_session_period(hour: int) -> str:
    """Determine session period based on hour"""
    if hour < 12:
        return "morning"
    elif hour < 18:
        return "afternoon"
    else:
        return "evening"

def ensure_directories():
    """Ensure all required directories exist"""
    WORKING_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

def load_current_tasks() -> dict:
    """Load current tasks from JSON file"""
    if CURRENT_TASKS_FILE.exists():
        try:
            with open(CURRENT_TASKS_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[!] Warning: Could not parse current-tasks.json")
    return {
        "updated": "",
        "schema_version": "1.0",
        "active_tasks": [],
        "completed_today": [],
        "recent_actions": [],
        "notes": ""
    }

def save_current_tasks(data: dict):
    """Save current tasks to JSON file"""
    now = get_sydney_time()
    data["updated"] = now.isoformat()

    with open(CURRENT_TASKS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def create_session_summary(completed_tasks: list = None, notes: str = None) -> Path:
    """Create session summary file"""
    now = get_sydney_time()
    period = get_session_period(now.hour)

    # Create year-month directory
    year_month = now.strftime("%Y-%m")
    session_subdir = SESSIONS_DIR / year_month
    session_subdir.mkdir(parents=True, exist_ok=True)

    # Session file name
    session_file = session_subdir / f"{now.strftime('%d')}-{period}.md"

    # Load current tasks for reference
    tasks_data = load_current_tasks()

    # Generate content
    content = f"""# Session Log - {now.strftime('%d/%m/%Y')} ({period.title()})

> **Time:** {now.strftime('%H:%M AEST')}
> **Owner:** Hafsah Nuzhat
> **Business:** Clean Up Bros

---

## Session Summary

**Duration:** Session logged off at {now.strftime('%H:%M')}

### Completed This Session

"""
    if completed_tasks:
        for task in completed_tasks:
            content += f"- {task}\n"
    elif tasks_data.get("completed_today"):
        for task in tasks_data["completed_today"]:
            content += f"- {task}\n"
    else:
        content += "- No completed tasks recorded\n"

    content += f"""
### Pending Tasks

"""
    if tasks_data.get("active_tasks"):
        for task in tasks_data["active_tasks"]:
            priority = task.get("priority", "medium")
            status = task.get("status", "pending")
            desc = task.get("description", "Unknown task")
            content += f"- [{priority.upper()}] {desc} (Status: {status})\n"
    else:
        content += "- No pending tasks\n"

    content += f"""
### Recent Actions

"""
    if tasks_data.get("recent_actions"):
        for action in tasks_data["recent_actions"][-5:]:  # Last 5 actions
            content += f"- {action}\n"
    else:
        content += "- No recent actions recorded\n"

    if notes or tasks_data.get("notes"):
        content += f"""
### Notes

{notes or tasks_data.get('notes', 'No notes.')}
"""

    content += f"""
---

## Outstanding Payments

| Client | Amount | Status |
|--------|--------|--------|
| Claudia Alz | $320 | OVERDUE (45+ days) |
| Meshach Ephraim Care | $1,750 remaining | Payment plan active |

---

*Session logged automatically by Bella*
*Timestamp: {now.isoformat()}*
"""

    # Write session file
    with open(session_file, 'w') as f:
        f.write(content)

    print(f"[+] Session summary created: {session_file}")
    return session_file

def update_heartbeat_state():
    """Update heartbeat state with last session time"""
    now = get_sydney_time()

    state = {}
    if HEARTBEAT_STATE_FILE.exists():
        try:
            with open(HEARTBEAT_STATE_FILE) as f:
                state = json.load(f)
        except json.JSONDecodeError:
            pass

    state["last_session_logoff"] = now.isoformat()
    state["last_session_date"] = now.strftime("%Y-%m-%d")

    with open(HEARTBEAT_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

    print(f"[+] Heartbeat state updated")

def sync_memory_files():
    """Run memory file sync"""
    sync_script = PROJECT_DIR / "scripts" / "sync_memory_files.py"
    if sync_script.exists():
        result = subprocess.run(
            ["python3", str(sync_script)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_DIR)
        )
        if result.returncode == 0:
            print("[+] Memory files synced (CLAUDE.md <-> GEMINI.md)")
        else:
            print(f"[!] Memory sync warning: {result.stderr}")
    else:
        print("[!] Sync script not found, skipping")

def commit_to_github(message: str = None):
    """Commit changes and push to GitHub"""
    now = get_sydney_time()
    if message is None:
        message = f"Session log: {now.strftime('%Y-%m-%d %H:%M')}"

    try:
        # Check for changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_DIR)
        )

        if not result.stdout.strip():
            print("[*] No changes to commit")
            return True

        # Stage relevant files
        files_to_stage = [
            "memory/",
            "CLAUDE.md",
            "GEMINI.md",
            "USER.md",
        ]

        for file_path in files_to_stage:
            full_path = PROJECT_DIR / file_path
            if full_path.exists():
                subprocess.run(
                    ["git", "add", file_path],
                    cwd=str(PROJECT_DIR),
                    capture_output=True
                )

        # Check if anything was staged
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_DIR)
        )

        if not result.stdout.strip():
            print("[*] No relevant changes to commit")
            return True

        # Commit
        commit_message = f"{message}\n\nCo-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_DIR)
        )

        if result.returncode != 0:
            print(f"[!] Commit warning: {result.stderr}")
            return False

        print(f"[+] Changes committed: {message}")

        # Push to GitHub
        result = subprocess.run(
            ["git", "push"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_DIR)
        )

        if result.returncode == 0:
            print("[+] Pushed to GitHub")
            return True
        else:
            print(f"[!] Push warning: {result.stderr}")
            return False

    except Exception as e:
        print(f"[-] Git error: {e}")
        return False

def run_logoff(commit: bool = True, notes: str = None, completed: list = None):
    """Run full logoff sequence"""
    print("\n" + "="*60)
    print("  BELLA SESSION LOGOFF")
    print("  Clean Up Bros - Sydney, Australia")
    now = get_sydney_time()
    print(f"  {now.strftime('%d/%m/%Y %H:%M:%S')} AEST")
    print("="*60 + "\n")

    ensure_directories()

    # Step 1: Create session summary
    print("[1/4] Creating session summary...")
    session_file = create_session_summary(completed_tasks=completed, notes=notes)

    # Step 2: Sync memory files
    print("\n[2/4] Syncing memory files...")
    sync_memory_files()

    # Step 3: Update heartbeat state
    print("\n[3/4] Updating heartbeat state...")
    update_heartbeat_state()

    # Step 4: Commit to GitHub (if enabled)
    if commit:
        print("\n[4/4] Committing to GitHub...")
        commit_to_github()
    else:
        print("\n[4/4] Skipping GitHub commit (--no-commit flag)")

    print("\n" + "="*60)
    print("  SESSION LOGGED OFF SUCCESSFULLY")
    print("="*60)
    print(f"\nSession file: {session_file}")
    print("Have a great day! - Bella")

def main():
    commit = True
    notes = None
    completed = None

    # Parse arguments
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--no-commit":
            commit = False
        elif arg == "--notes" and i + 1 < len(args):
            notes = args[i + 1]
            i += 1
        elif arg == "--completed" and i + 1 < len(args):
            completed = args[i + 1].split(",")
            i += 1
        elif arg in ["--help", "-h"]:
            print("Usage: session_logoff.py [OPTIONS]")
            print("\nOptions:")
            print("  --no-commit         Don't commit/push to GitHub")
            print("  --notes TEXT        Add session notes")
            print("  --completed TASKS   Comma-separated list of completed tasks")
            print("  -h, --help          Show this help")
            return
        i += 1

    run_logoff(commit=commit, notes=notes, completed=completed)

if __name__ == "__main__":
    main()
