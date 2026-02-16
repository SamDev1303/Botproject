#!/bin/bash
# Setup Convex project for Bella's memory database

set -e

echo "=== Convex Setup for Bella AI ===="
echo ""

# Check if Convex CLI is installed
if ! command -v npx &> /dev/null; then
    echo "❌ Error: Node.js/npx not found"
    echo "Install Node.js first: https://nodejs.org/"
    exit 1
fi

# Create Convex directory if it doesn't exist
CONVEX_DIR="$HOME/Desktop/🦀/convex"
mkdir -p "$CONVEX_DIR"
cd "$CONVEX_DIR"

echo "📦 Installing Convex..."
npm install convex

echo ""
echo "🔧 Initializing Convex project..."
npx convex dev --once --configure=new

echo ""
echo "✅ Convex project created!"
echo ""
echo "Next steps:"
echo "1. Go to https://dashboard.convex.dev"
echo "2. Find your project's deployment URL"
echo "3. Add to ~/.clawdbot/.env:"
echo "   CONVEX_URL=https://your-project.convex.cloud"
echo ""
echo "4. Start Convex dev server:"
echo "   cd $CONVEX_DIR && npx convex dev"
echo ""
