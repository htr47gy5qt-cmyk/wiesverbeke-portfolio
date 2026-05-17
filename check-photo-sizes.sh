#!/bin/bash
# ─────────────────────────────────────────────────────────────────────
# check-photo-sizes.sh
# Quick sanity check before publishing — flags any photo in photos/
# that's larger than the soft limit (default 1.5 MB).
#
# Doesn't change anything. Just reports.
#
# Usage:  ./check-photo-sizes.sh
# ─────────────────────────────────────────────────────────────────────

set -euo pipefail

PHOTOS_DIR="photos"
LIMIT_KB=1500   # ~1.5 MB

if [ ! -d "$PHOTOS_DIR" ]; then
  echo "❌  Run this script from your project root (the folder that contains photos/)."
  exit 1
fi

echo "──────────────────────────────────────────────────"
echo "  Checking $PHOTOS_DIR/ for files larger than ${LIMIT_KB} KB"
echo "──────────────────────────────────────────────────"

oversized=0
total_count=0
total_bytes=0
oversized_bytes=0

shopt -s nullglob nocaseglob
for file in "$PHOTOS_DIR"/*.jpg "$PHOTOS_DIR"/*.jpeg "$PHOTOS_DIR"/*.png; do
  shopt -u nocaseglob
  [ -f "$file" ] || continue

  total_count=$((total_count + 1))
  size_bytes=$(stat -f%z "$file")
  total_bytes=$((total_bytes + size_bytes))
  size_kb=$(( size_bytes / 1024 ))

  if [ "$size_kb" -gt "$LIMIT_KB" ]; then
    oversized=$((oversized + 1))
    oversized_bytes=$((oversized_bytes + size_bytes))
    filename=$(basename "$file")
    size_human=$(du -h "$file" | awk '{print $1}')
    echo "  ⚠️  $filename — $size_human"
  fi
done

total_human=$(echo "$total_bytes" | awk '{printf "%.1f MB", $1/1024/1024}')

echo "──────────────────────────────────────────────────"
if [ "$oversized" -eq 0 ]; then
  echo "  ✓  All $total_count photos are under ${LIMIT_KB} KB."
  echo "  Total photos folder size: $total_human"
else
  over_human=$(echo "$oversized_bytes" | awk '{printf "%.1f MB", $1/1024/1024}')
  echo "  $oversized of $total_count photos are oversized ($over_human of $total_human total)."
  echo "  → Run ./resize-photos.sh to fix them."
fi
echo "──────────────────────────────────────────────────"
