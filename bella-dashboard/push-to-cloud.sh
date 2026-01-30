#!/bin/bash
# Bella Dashboard - Push to AWS S3
# Run this to sync local status to cloud dashboard

DASHBOARD_DIR="/Users/hafsahnuzhat/Desktop/🦀/bella-dashboard"

# First update local status
"$DASHBOARD_DIR/sync-status.sh"

# Then push to S3
aws s3 cp "$DASHBOARD_DIR/status.json" s3://bella-dashboard-hafsah/status.json --quiet

echo "✨ Dashboard synced to cloud at $(date +%H:%M:%S)"
