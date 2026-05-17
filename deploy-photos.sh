#!/bin/bash
# ─────────────────────────────────────────────────────────────────────
# deploy-photos.sh
# Runs the full "I added new photos" workflow in sequence:
#   1. Resize new full-size photos (resize-photos.sh)
#   2. Generate WebP companions       (convert-to-webp.sh)
#   3. Write width/height into JSON   (add_dimensions_to_json.py)
#   4. Final size sanity check        (check-photo-sizes.sh)
#
# Stops at the first failure so you can fix the problem before continuing.
# All four scripts are idempotent — re-running is safe.
#
# Usage from project root:
#     ./deploy-photos.sh
# ─────────────────────────────────────────────────────────────────────

set -e   # stop on any error

# ── Colors for readability ──
BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

# ── Sanity check: run from project root ──
if [ ! -d "photos" ] || [ ! -d "data" ]; then
  echo -e "${RED}❌  Run this script from your project root (folder containing photos/ and data/).${RESET}"
  exit 1
fi

# ── Helper: announce each step ──
step() {
  echo
  echo -e "${BOLD}── Step $1/4: $2 ──${RESET}"
}

# ── Helper: confirm a file exists and is runnable ──
require() {
  if [ ! -f "$1" ]; then
    echo -e "${RED}❌  Missing $1 — can't continue.${RESET}"
    exit 1
  fi
}

require "resize-photos.sh"
require "convert-to-webp.sh"
require "add_dimensions_to_json.py"
require "check-photo-sizes.sh"

# ── Step 1: Resize ──
step 1 "Resizing new photos to max 2400px @ 85%"
chmod +x resize-photos.sh
./resize-photos.sh

# ── Step 2: WebP conversion ──
step 2 "Generating WebP companions"
chmod +x convert-to-webp.sh
./convert-to-webp.sh

# ── Step 3: Dimensions into JSON ──
step 3 "Writing photo dimensions into JSON"
# Use the venv's python3 if a venv is active, otherwise the system python3
python3 add_dimensions_to_json.py

# ── Step 4: Size sanity check ──
step 4 "Final size check"
chmod +x check-photo-sizes.sh
./check-photo-sizes.sh

# ── Done ──
echo
echo -e "${GREEN}${BOLD}✓ All four steps finished successfully.${RESET}"
echo -e "${YELLOW}Next: drag the my-portfolio folder onto Netlify to deploy.${RESET}"
