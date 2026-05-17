#!/bin/bash
# ─────────────────────────────────────────────────────────────────────
# resize-photos.sh
# Resizes every JPEG in photos/ to a max 2400px long edge at 85% quality.
# Skips photos that are already under 2400px on the long edge.
# Backs up originals to photos/originals/ (never overwrites an existing
# backup — so it's safe to run repeatedly).
#
# Usage:  ./resize-photos.sh
# ─────────────────────────────────────────────────────────────────────

set -euo pipefail

PHOTOS_DIR="photos"
BACKUP_DIR="photos/originals"
MAX_EDGE=2400
QUALITY=85

# Sanity check — must be run from project root
if [ ! -d "$PHOTOS_DIR" ]; then
  echo "❌  Run this script from your project root (the folder that contains photos/)."
  exit 1
fi

# Check sips exists (it should, on every Mac)
if ! command -v sips >/dev/null 2>&1; then
  echo "❌  'sips' not found. This script needs macOS."
  exit 1
fi

mkdir -p "$BACKUP_DIR"

resized=0
skipped=0
errors=0
already_backed=0

echo "──────────────────────────────────────────────────"
echo "  Resizing photos in $PHOTOS_DIR/"
echo "  Target: max ${MAX_EDGE}px long edge @ ${QUALITY}% quality"
echo "──────────────────────────────────────────────────"

# Loop over JPEGs in photos/ only — not subfolders like originals/
shopt -s nullglob nocaseglob
for file in "$PHOTOS_DIR"/*.jpg "$PHOTOS_DIR"/*.jpeg; do
  shopt -u nocaseglob
  [ -f "$file" ] || continue

  filename=$(basename "$file")

  # Read current dimensions
  if ! dims=$(sips -g pixelWidth -g pixelHeight "$file" 2>/dev/null); then
    echo "  ⚠️  $filename — could not read dimensions, skipping"
    errors=$((errors + 1))
    continue
  fi
  width=$(echo "$dims" | awk '/pixelWidth/ {print $2}')
  height=$(echo "$dims" | awk '/pixelHeight/ {print $2}')

  if [ -z "$width" ] || [ -z "$height" ]; then
    echo "  ⚠️  $filename — invalid dimensions, skipping"
    errors=$((errors + 1))
    continue
  fi

  long_edge=$(( width > height ? width : height ))

  # Already small enough? Skip.
  if [ "$long_edge" -le "$MAX_EDGE" ]; then
    echo "  ⏭  $filename — already ${long_edge}px, skipped"
    skipped=$((skipped + 1))
    continue
  fi

  # Back up original (only if no backup exists yet)
  backup_path="$BACKUP_DIR/$filename"
  if [ -e "$backup_path" ]; then
    # Already backed up — don't overwrite. Just resize the working copy.
    already_backed=$((already_backed + 1))
  else
    cp "$file" "$backup_path"
  fi

  # Resize in-place
  if sips --resampleHeightWidthMax "$MAX_EDGE" -s formatOptions "$QUALITY" "$file" >/dev/null 2>&1; then
    new_size=$(du -h "$file" | awk '{print $1}')
    echo "  ✓  $filename — resized to ${MAX_EDGE}px max (${new_size})"
    resized=$((resized + 1))
  else
    echo "  ❌  $filename — resize failed"
    errors=$((errors + 1))
  fi
done

echo "──────────────────────────────────────────────────"
echo "  Done."
echo "    Resized:        $resized"
echo "    Skipped:        $skipped  (already ≤${MAX_EDGE}px)"
echo "    Pre-backed-up:  $already_backed  (original kept from previous run)"
echo "    Errors:         $errors"
echo "  Originals safe in: $BACKUP_DIR/"
echo "──────────────────────────────────────────────────"
