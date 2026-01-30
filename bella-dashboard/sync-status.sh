#!/bin/bash
# Bella Dashboard - Live Sync Script
# Fetches Telegram messages and pushes to cloud

DASHBOARD_DIR="/Users/hafsahnuzhat/Desktop/🦀/bella-dashboard"
PYTHON_VENV="/Users/hafsahnuzhat/clawd/.venv/bin/python3"

# Run the Python fetch script
"$PYTHON_VENV" "$DASHBOARD_DIR/fetch-messages.py" 2>/dev/null

echo "Sync completed at $(date +%H:%M:%S)"
