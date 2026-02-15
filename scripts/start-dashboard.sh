#!/bin/bash
# Starts a local dashboard server on port 8001
PORT=8001

echo "🦁 Starting Bella Local Dashboard..."
echo "📂 Serving from: $HOME/Desktop/🦀/dashboard"

cd "$HOME/Desktop/🦀/dashboard"

# Kill anything on port 8001
lsof -ti :$PORT | xargs kill -9 2>/dev/null

# Try python3 then python
if command -v python3 &>/dev/null; then
    python3 -m http.server $PORT &
elif command -v python &>/dev/null; then
    python -m http.server $PORT &
else
    echo "❌ Error: Python not found. Please install Python."
    exit 1
fi

PID=$!
sleep 2

echo "🚀 Dashboard active at http://localhost:$PORT/dashboard.html"
echo "PRESS CTRL+C TO STOP (or close the terminal)"

# Open in default browser
open "http://localhost:$PORT/dashboard.html"

# Wait for user kill
wait $PID
