#!/bin/bash
# scripts/auto_refresh_3h.sh
# Runs every 3 hours to sync business data and update dashboard

WORKSPACE="$HOME/Desktop/🦀"
REPO="$HOME/Desktop/Botproject"

echo "Starting 3-hour business refresh: $(date)"

# 1. Sync Invoices from Square
python3 "$WORKSPACE/scripts/check_unpaid_invoices.py"

# 2. Sync Google (Gmail/Calendar) - Requires re-auth!
# gog gmail search 'newer_than:3h'
# gog calendar events primary --from "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# 3. Update Dashboard Logic here (Future: aggregate data)

# 4. Push to GitHub
cd "$REPO"
git add dashboard-data.json
git commit -m "📊 Automated 3h Business Sync"
git push origin main

echo "Refresh complete: $(date)"
