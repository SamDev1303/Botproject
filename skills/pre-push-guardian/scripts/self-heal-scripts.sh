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

ROOT="/Users/hafsahnuzhat/Desktop/🦀"
cd "$ROOT"

UPDATED=0
SCANNED=0

while IFS= read -r -d '' file; do
  SCANNED=$((SCANNED + 1))
  changed=0

  if ! head -n 1 "$file" | grep -q '^#!/usr/bin/env bash'; then
    tmp="$(mktemp)"
    {
      echo '#!/usr/bin/env bash'
      cat "$file"
    } > "$tmp"
    mv "$tmp" "$file"
    changed=1
  fi

  if ! rg -n '^set -euo pipefail$' "$file" >/dev/null 2>&1; then
    tmp="$(mktemp)"
    awk 'NR==1 { print; print "set -euo pipefail"; next } { print }' "$file" > "$tmp"
    mv "$tmp" "$file"
    changed=1
  fi

  if ! test -x "$file"; then
    chmod +x "$file"
    changed=1
  fi

  if [ "$changed" -eq 1 ]; then
    UPDATED=$((UPDATED + 1))
    echo "Healed: $file"
  fi
done < <(find scripts skills -type f -name '*.sh' -print0)

echo "Self-heal complete. Scanned: $SCANNED, Updated: $UPDATED"
