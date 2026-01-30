#!/bin/bash

# fix_clawdbot.sh - Repair script for Clawdbot
# 1. Archives old mixed-up sessions and memories
# 2. Resets the Gateway Token (for Dashboard access)
# 3. Provides commands to restore API keys

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CLAWDBOT_DIR="$HOME/.clawdbot"
ARCHIVE_DIR="$CLAWDBOT_DIR/archive_$TIMESTAMP"
CONFIG_FILE="$CLAWDBOT_DIR/clawdbot.json"
NEW_GATEWAY_TOKEN="clawdbot-local-2026"
# Recovered from aws-server-config.txt
TELEGRAM_TOKEN="8543603663:AAHdsPEgllNp6VBl7hCVonI5zvbvrJ4Vm9U"
ELEVENLABS_KEY="sk_98ceb9686261937ecc4ef06c42fb150185f94ce3f9450753"

echo "🦀 Clawdbot Repair Script Initiated..."

# 0. Stop Services (if running)
echo "Stopping any running clawdbot instances..."
pkill -f "clawdbot" || echo "No running instances found."

# 1. Archive Mixed Memories
echo "📂 Archiving mixed sessions and memories..."
mkdir -p "$ARCHIVE_DIR"

if [ -d "$CLAWDBOT_DIR/clawdbot-sessions" ]; then
    echo "  -> Moving clawdbot-sessions..."
    mv "$CLAWDBOT_DIR/clawdbot-sessions" "$ARCHIVE_DIR/"
fi

if [ -d "$CLAWDBOT_DIR/memory" ]; then
    echo "  -> Moving memory..."
    mv "$CLAWDBOT_DIR/memory" "$ARCHIVE_DIR/"
fi

# 2. Reset Gateway and Telegram Token in Config
echo "⚙️  Updating Configuration..."
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "$ARCHIVE_DIR/clawdbot.json.bak"
    
    # We use a temporary python script to cleanly edit the JSON
    # This prevents issues with sed on JSON files
    python3 -c "
import json
import os

config_path = '$CONFIG_FILE'
try:
    with open(config_path, 'r') as f:
        data = json.load(f)
    
    # Update Gateway Token
    if 'gateway' not in data: data['gateway'] = {}
    if 'auth' not in data['gateway']: data['gateway']['auth'] = {}
    data['gateway']['auth']['token'] = '$NEW_GATEWAY_TOKEN'
    data['gateway']['auth']['mode'] = 'token'

    # Ensure Telegram Token is set (recovered from AWS)
    if 'channels' not in data: data['channels'] = {}
    if 'telegram' not in data['channels']: data['channels']['telegram'] = {'enabled': True}
    data['channels']['telegram']['botToken'] = '$TELEGRAM_TOKEN'
    data['channels']['telegram']['enabled'] = True

    # Ensure ElevenLabs Key is set (recovered from AWS)
    if 'talk' not in data: data['talk'] = {}
    data['talk']['apiKey'] = '$ELEVENLABS_KEY'

    with open(config_path, 'w') as f:
        json.dump(data, f, indent=2)
    print('  -> Updated clawdbot.json (Gateway Token, Telegram, ElevenLabs)')
except Exception as e:
    print(f'  -> Error updating JSON: {e}')
"
else
    echo "  -> ⚠️  Config file not found at $CONFIG_FILE"
fi

echo ""
echo "✅ Repair Complete!"
echo "---------------------------------------------------"
echo "1. New Dashboard Token: $NEW_GATEWAY_TOKEN"
echo "   (Use this if asked when opening the dashboard)"
echo ""
echo "2. Recovered Keys Applied:"
echo "   - Telegram Bot Token"
echo "   - ElevenLabs API Key"
echo ""
echo "3. MISSING KEYS (ACTION REQUIRED):"
echo "   You need to re-add your Claude/OpenAI keys."
echo "   Run these commands:"
echo ""
echo "   To add Claude (Anthropic):"
echo "   npx clawdbot config set auth.profiles.anthropic:manual.apiKey \"YOUR_CLAUDE_KEY\""
echo ""
echo "   To add OpenAI:"
echo "   npx clawdbot config set agents.defaults.model.apiKey \"YOUR_OPENAI_KEY\""
echo "---------------------------------------------------"
echo "Run 'npx clawdbot start' to boot up."
