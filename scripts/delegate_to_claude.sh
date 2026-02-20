#!/usr/bin/env bash
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
set -euo pipefail
#!/bin/bash
# Delegate tasks to Claude Code from Bella's workspace
# Usage: ./delegate_to_claude.sh "Task description here"
# Created: 2026-02-03

CLAUDE_WORKSPACE="/Users/hafsahnuzhat/Desktop/claudeking"
BELLA_WORKSPACE="/Users/hafsahnuzhat/Desktop/🦀"

if [ -z "$1" ]; then
    echo "Usage: $0 \"TASK_DESCRIPTION\""
    echo ""
    echo "Example:"
    echo "  $0 \"Run the health check script\""
    echo "  $0 \"Create a new invoice for John Smith, \$380\""
    echo "  $0 \"Check git status and push changes\""
    exit 1
fi

TASK="$1"

echo "======================================"
echo "  DELEGATING TO CLAUDE CODE"
echo "======================================"
echo ""
echo "Task: $TASK"
echo "Claude Workspace: $CLAUDE_WORKSPACE"
echo "Bella Workspace: $BELLA_WORKSPACE"
echo ""

# Change to Claude Code workspace and execute
cd "$CLAUDE_WORKSPACE" && claude "$TASK" --add-dir "$BELLA_WORKSPACE"
