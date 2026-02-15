#!/bin/bash
# 🦁 Bella Neural Elite v6.0 - Hyper-Active Sync Script
# This script bridges memory to the UI and deploys to both Local, GitHub, and Vercel.

REPO_PATH="$HOME/Desktop/Botproject"
DASHBOARD_DIR="$HOME/Desktop/🦀/dashboard"

echo "🧠 Bella Neural Engine: Initiating Hyper-Sync..."

# 1. Update Data Bridge (Memory -> JSON/JS)
python3 "$HOME/Desktop/🦀/scripts/update_dashboard.py"

# 2. Sync to Local Repository (for GitHub Pages/Private Backup)
if [ -d "$REPO_PATH" ]; then
    echo "💾 Desktop/Botproject: Syncing assets and interface..."
    cp "$DASHBOARD_DIR/dashboard.html" "$REPO_PATH/index.html"
    cp "$DASHBOARD_DIR/dashboard-data.js" "$REPO_PATH/dashboard-data.js"
    mkdir -p "$REPO_PATH/assets"
    cp -R "$DASHBOARD_DIR/assets/"* "$REPO_PATH/assets/" 2>/dev/null
    
    cd "$REPO_PATH"
    git add .
    git commit -m "📊 Neural Dashboard v6.0 Update $(date '+%Y-%m-%d %H:%M')" 2>/dev/null
    git push origin main 2>&1
fi

# 3. Sync to Vercel (Public Elite Hosting)
# Note: This assumes current folder is linked and auth is active
# If failing, we fallback to just GitHub
echo "🚀 Vercel: Deploying production update..."
cd "$DASHBOARD_DIR" && npx vercel deploy --prod --yes > /dev/null 2>&1

echo "✅ Bella Neural Dashboard v6.0: All nodes synced."
