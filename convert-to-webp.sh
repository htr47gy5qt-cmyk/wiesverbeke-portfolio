#!/bin/bash
# ─────────────────────────────────────────────────────────────────────
# convert-to-webp.sh
# Converts every JPEG in photos/ to a WebP companion file at 82% quality.
# Skips photos that already have a matching .webp newer than the source.
# Originals are left untouched — WebP just lives alongside them.
#
# Usage:  ./convert-to-webp.sh
#
# Requires: cwebp (install via `brew install webp` on macOS)
# ─────────────────────────────────────────────────────────────────────

set -euo pipefail

PHOTOS_DIR="photos"
QUALITY=82

if [ ! -d "$PHOTOS_DIR" ]; then
  echo "❌  Run this script from your project root (the folder that contains photos/)."
  exit 1
fi

if ! command -v cwebp >/dev/null 2>&1; then
  echo "❌  'cwebp' not found. Install it with: brew install webp"
  exit 1
fi

converted=0
skipped=0
errors=0

echo "──────────────────────────────────────────────────"
echo "  Converting JPEGs in $PHOTOS_DIR/ to WebP @ ${QUALITY}% quality"
echo "──────────────────────────────────────────────────"

shopt -s nullglob nocaseglob
for file in "$PHOTOS_DIR"/*.jpg "$PHOTOS_DIR"/*.jpeg; do
  shopt -u nocaseglob
  [ -f "$file" ] || continue

  filename=$(basename "$file")
  webp_path="${file%.*}.webp"

  # Skip if a fresh .webp already exists
  if [ -f "$webp_path" ] && [ "$webp_path" -nt "$file" ]; then
    skipped=$((skipped + 1))
    continue
  fi

  if cwebp -q "$QUALITY" -quiet "$file" -o "$webp_path"; then
    orig_size=$(du -k "$file"      | awk '{print $1}')
    new_size=$( du -k "$webp_path" | awk '{print $1}')
    saved=$(( orig_size - new_size ))
    pct=$(( saved * 100 / orig_size ))
    echo "  ✓  $filename → ${new_size}KB (saved ${pct}%)"
    converted=$((converted + 1))
  else
    echo "  ❌  $filename — conversion failed"
    errors=$((errors + 1))
  fi
done

echo "──────────────────────────────────────────────────"
echo "  Converted:  $converted"
echo "  Skipped:    $skipped (already up to date)"
echo "  Errors:     $errors"
echo "──────────────────────────────────────────────────"
