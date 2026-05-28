#!/usr/bin/env python3
"""
add_dimensions_to_json.py
-------------------------
For each photo in data/*.json, reads the corresponding image file from
photos/ and writes back its width + height into the JSON.

Run from the project root:
    python3 add_dimensions_to_json.py

Uses Pillow (PIL). Install with:
    pip3 install Pillow
"""

import json
import os
import sys
import argparse
from urllib.parse import unquote

try:
    from PIL import Image
except ImportError:
    print("❌  Pillow is not installed. Run: pip3 install Pillow")
    sys.exit(1)

DATA_DIR = "data"
PHOTOS_DIR = "photos"


def resolve_path(src):
    """Convert a JSON src like 'photos/FP4%2BOM4_T_24.jpg' to a real filesystem path."""
    return unquote(src)


def measure(path):
    """Return (width, height) for an image, or (None, None) on failure."""
    try:
        with Image.open(path) as im:
            return im.size  # (width, height)
    except Exception as e:
        print(f"    ⚠️  could not read {path}: {e}")
        return None, None


def process_json(json_path, force=False):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    missing = 0
    skipped = 0

    for photo in data.get("photos", []):
        # Skip if already has dimensions (unless --force)
        if not force and photo.get("width") and photo.get("height"):
            skipped += 1
            continue

        path = resolve_path(photo["src"])
        if not os.path.exists(path):
            print(f"    ❌  missing file: {path}")
            missing += 1
            continue

        w, h = measure(path)
        if w and h:
            photo["width"]  = w
            photo["height"] = h
            updated += 1

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return updated, missing, skipped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true",
                        help="Re-read dimensions even if they already exist in JSON")
    args = parser.parse_args()

    if not os.path.isdir(DATA_DIR):
        print(f"❌  No '{DATA_DIR}' folder. Run from project root.")
        sys.exit(1)
    if not os.path.isdir(PHOTOS_DIR):
        print(f"❌  No '{PHOTOS_DIR}' folder. Run from project root.")
        sys.exit(1)

    total_updated = 0
    for name in sorted(os.listdir(DATA_DIR)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(DATA_DIR, name)
        print(f"Processing {path} …")
        updated, missing, skipped = process_json(path, force=args.force)
        print(f"  ✓ updated: {updated}   skipped: {skipped}   missing: {missing}")
        total_updated += updated

    print(f"\nDone. Wrote dimensions for {total_updated} photos.")
    print("If any files were missing, check the filename matches photos/ exactly.")


if __name__ == "__main__":
    main()
