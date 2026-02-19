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

ROOT="/Users/hafsahnuzhat/Desktop/🦀"
VAULT="$ROOT/media-vault"

usage() {
  echo "Usage: bash scripts/store-media-asset.sh <file_path> [category]"
  echo "Categories: images | videos | audio | documents | exports"
}

if [ "${1:-}" = "" ]; then
  usage
  exit 1
fi

SRC="$1"
CATEGORY="${2:-auto}"

if [ ! -f "$SRC" ]; then
  echo "File not found: $SRC"
  exit 1
fi

mkdir -p "$VAULT/images" "$VAULT/videos" "$VAULT/audio" "$VAULT/documents" "$VAULT/exports"

ext="$(echo "${SRC##*.}" | tr '[:upper:]' '[:lower:]')"
if [ "$CATEGORY" = "auto" ]; then
  case "$ext" in
    png|jpg|jpeg|webp|gif|heic) CATEGORY="images" ;;
    mp4|mov|mkv|avi|webm) CATEGORY="videos" ;;
    mp3|wav|m4a|aac|flac) CATEGORY="audio" ;;
    pdf|doc|docx|ppt|pptx|xls|xlsx) CATEGORY="documents" ;;
    *) CATEGORY="exports" ;;
  esac
fi

DEST="$VAULT/$CATEGORY/$(basename "$SRC")"
mv "$SRC" "$DEST"
echo "$DEST"
