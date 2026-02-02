#!/usr/bin/env python3
"""
Sync CLAUDE.md and GEMINI.md files
Keeps both files in sync with timestamps
Created: 2026-02-03
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import hashlib
import re

# Project directory
PROJECT_DIR = Path.home() / "Desktop" / "🦀"
CLAUDE_MD = PROJECT_DIR / "CLAUDE.md"
GEMINI_MD = PROJECT_DIR / "GEMINI.md"

def get_file_hash(filepath: Path) -> str:
    """Get MD5 hash of file content (excluding sync timestamp line)"""
    if not filepath.exists():
        return ""

    content = filepath.read_text()
    # Remove sync timestamp line for comparison
    content = re.sub(r'\n> \*\*Last Synced:\*\* .*\n', '\n', content)
    return hashlib.md5(content.encode()).hexdigest()

def get_mtime(filepath: Path) -> float:
    """Get file modification time"""
    if filepath.exists():
        return filepath.stat().st_mtime
    return 0

def add_sync_timestamp(content: str) -> str:
    """Add or update sync timestamp in file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S AEST')
    sync_line = f"> **Last Synced:** {timestamp}"

    # Check if sync timestamp already exists
    if "> **Last Synced:**" in content:
        content = re.sub(r'> \*\*Last Synced:\*\* .*', sync_line, content)
    else:
        # Add after the title block (first few lines)
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('> **') and 'Last Updated' in line:
                insert_idx = i + 1
                break
            elif line.startswith('---') and i > 0:
                insert_idx = i
                break

        if insert_idx > 0:
            lines.insert(insert_idx, sync_line)
            content = '\n'.join(lines)

    return content

def sync_files(source: Path, dest: Path, verbose: bool = True) -> bool:
    """Sync source file to destination with timestamp"""
    if not source.exists():
        if verbose:
            print(f"[!] Source file not found: {source}")
        return False

    try:
        content = source.read_text()
        content = add_sync_timestamp(content)
        dest.write_text(content)

        if verbose:
            print(f"[+] Synced: {source.name} -> {dest.name}")
        return True
    except Exception as e:
        if verbose:
            print(f"[-] Error syncing: {e}")
        return False

def auto_sync(verbose: bool = True) -> str:
    """
    Automatically determine which file is newer and sync
    Returns: 'claude_to_gemini', 'gemini_to_claude', 'in_sync', or 'error'
    """
    claude_exists = CLAUDE_MD.exists()
    gemini_exists = GEMINI_MD.exists()

    if not claude_exists and not gemini_exists:
        if verbose:
            print("[-] Neither CLAUDE.md nor GEMINI.md exists")
        return "error"

    if claude_exists and not gemini_exists:
        if verbose:
            print("[*] GEMINI.md missing, creating from CLAUDE.md")
        sync_files(CLAUDE_MD, GEMINI_MD, verbose)
        return "claude_to_gemini"

    if gemini_exists and not claude_exists:
        if verbose:
            print("[*] CLAUDE.md missing, creating from GEMINI.md")
        sync_files(GEMINI_MD, CLAUDE_MD, verbose)
        return "gemini_to_claude"

    # Both exist - check which is newer
    claude_hash = get_file_hash(CLAUDE_MD)
    gemini_hash = get_file_hash(GEMINI_MD)

    if claude_hash == gemini_hash:
        if verbose:
            print("[+] Files already in sync")
        return "in_sync"

    claude_mtime = get_mtime(CLAUDE_MD)
    gemini_mtime = get_mtime(GEMINI_MD)

    if claude_mtime > gemini_mtime:
        if verbose:
            print(f"[*] CLAUDE.md is newer ({datetime.fromtimestamp(claude_mtime).strftime('%H:%M:%S')})")
        sync_files(CLAUDE_MD, GEMINI_MD, verbose)
        return "claude_to_gemini"
    else:
        if verbose:
            print(f"[*] GEMINI.md is newer ({datetime.fromtimestamp(gemini_mtime).strftime('%H:%M:%S')})")
        sync_files(GEMINI_MD, CLAUDE_MD, verbose)
        return "gemini_to_claude"

def force_sync(direction: str, verbose: bool = True) -> bool:
    """Force sync in a specific direction"""
    if direction == "claude_to_gemini":
        return sync_files(CLAUDE_MD, GEMINI_MD, verbose)
    elif direction == "gemini_to_claude":
        return sync_files(GEMINI_MD, CLAUDE_MD, verbose)
    else:
        if verbose:
            print(f"[-] Unknown direction: {direction}")
        return False

def main():
    print("\n" + "="*50)
    print("  MEMORY FILE SYNC")
    print("  CLAUDE.md <-> GEMINI.md")
    print("="*50 + "\n")

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ["--claude-to-gemini", "-c"]:
            force_sync("claude_to_gemini")
        elif arg in ["--gemini-to-claude", "-g"]:
            force_sync("gemini_to_claude")
        elif arg in ["--status", "-s"]:
            claude_hash = get_file_hash(CLAUDE_MD)
            gemini_hash = get_file_hash(GEMINI_MD)
            print(f"CLAUDE.md: {CLAUDE_MD}")
            print(f"  Exists: {CLAUDE_MD.exists()}")
            print(f"  Hash: {claude_hash[:12]}...")
            print(f"\nGEMINI.md: {GEMINI_MD}")
            print(f"  Exists: {GEMINI_MD.exists()}")
            print(f"  Hash: {gemini_hash[:12]}...")
            print(f"\nIn sync: {claude_hash == gemini_hash}")
        elif arg in ["--help", "-h"]:
            print("Usage: sync_memory_files.py [OPTIONS]")
            print("\nOptions:")
            print("  (none)              Auto-sync based on modification time")
            print("  -c, --claude-to-gemini  Force CLAUDE.md -> GEMINI.md")
            print("  -g, --gemini-to-claude  Force GEMINI.md -> CLAUDE.md")
            print("  -s, --status        Show sync status")
            print("  -h, --help          Show this help")
        else:
            print(f"Unknown option: {arg}")
            print("Use --help for usage information")
            sys.exit(1)
    else:
        # Default: auto-sync
        result = auto_sync()
        if result == "error":
            sys.exit(1)

if __name__ == "__main__":
    main()
