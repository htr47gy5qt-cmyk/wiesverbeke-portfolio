#!/usr/bin/env python3
"""
strip_film_borders.py
---------------------
Removes dark film-rebate borders baked into scanned film photos.
Saves results back to the same .webp files in photos/.

Safeguards:
- Skips sides where the detected trim exceeds 12% of that dimension
  (flags the photo for manual review instead of silently cropping badly).
- Reports every change so you can verify before committing.

Run from project root:
    python3 strip_film_borders.py
"""

import os
import sys
from PIL import Image

# ── Settings ─────────────────────────────────────────────────────────
PHOTOS_DIR     = "photos"
DARK_THRESHOLD = 40     # pixels with all channels < this are "border"
BORDER_ROW_PCT = 0.75   # fraction of row/col that must be dark to count
MAX_TRIM_PCT   = 0.12   # skip trim on a side if it would remove >12% of dimension
WEBP_QUALITY   = 92     # output quality (0-100)
# ─────────────────────────────────────────────────────────────────────

def is_dark_pixel(r, g, b):
    return r < DARK_THRESHOLD and g < DARK_THRESHOLD and b < DARK_THRESHOLD

def find_trim_bounds(rgb_img):
    """Return (left, top, right, bottom) crop box."""
    w, h = rgb_img.size
    p = rgb_img.load()

    def row_is_border(y):
        dark = sum(1 for x in range(w) if is_dark_pixel(*p[x, y][:3]))
        return dark / w >= BORDER_ROW_PCT

    def col_is_border(x):
        dark = sum(1 for y in range(h) if is_dark_pixel(*p[x, y][:3]))
        return dark / h >= BORDER_ROW_PCT

    top = 0
    while top < h and row_is_border(top):
        top += 1

    bottom = h - 1
    while bottom > top and row_is_border(bottom):
        bottom -= 1

    left = 0
    while left < w and col_is_border(left):
        left += 1

    right = w - 1
    while right > left and col_is_border(right):
        right -= 1

    return (left, top, right + 1, bottom + 1)

def apply_safeguards(box, orig_w, orig_h):
    """
    Check each side: if the trim amount exceeds MAX_TRIM_PCT, reset that
    side to the original edge. Returns (safe_box, flagged_sides).
    """
    l, t, r, b = box
    flagged = []

    trim_left   = l
    trim_top    = t
    trim_right  = orig_w - r
    trim_bottom = orig_h - b

    if trim_left / orig_w > MAX_TRIM_PCT:
        flagged.append(f"left({trim_left}px={trim_left/orig_w:.0%})")
        l = 0
    if trim_right / orig_w > MAX_TRIM_PCT:
        flagged.append(f"right({trim_right}px={trim_right/orig_w:.0%})")
        r = orig_w
    if trim_top / orig_h > MAX_TRIM_PCT:
        flagged.append(f"top({trim_top}px={trim_top/orig_h:.0%})")
        t = 0
    if trim_bottom / orig_h > MAX_TRIM_PCT:
        flagged.append(f"bottom({trim_bottom}px={trim_bottom/orig_h:.0%})")
        b = orig_h

    return (l, t, r, b), flagged

def process_photo(path):
    """
    Returns one of:
      ("skipped",  None)          — no border detected
      ("cropped",  (new_w, new_h)) — border removed and file saved
      ("flagged",  list_of_sides)  — suspicious trim, saved conservatively
    """
    img = Image.open(path)
    orig_mode = img.mode
    orig_w, orig_h = img.size
    rgb = img.convert("RGB")

    box = find_trim_bounds(rgb)
    l, t, r, b = box

    if l == 0 and t == 0 and r == orig_w and b == orig_h:
        return ("skipped", None)

    safe_box, flagged = apply_safeguards(box, orig_w, orig_h)
    l, t, r, b = safe_box

    if l == 0 and t == 0 and r == orig_w and b == orig_h:
        return ("skipped", None)

    cropped = img.crop(safe_box)
    # Preserve original mode (e.g. RGBA) if possible
    if orig_mode != "RGB":
        cropped = cropped.convert(orig_mode)

    # Save back as webp
    cropped.save(path, format="WEBP", quality=WEBP_QUALITY, method=6)

    if flagged:
        return ("flagged", flagged)
    return ("cropped", (r - l, b - t))

def main():
    if not os.path.isdir(PHOTOS_DIR):
        print(f"ERROR: photos/ folder not found. Run from project root.")
        sys.exit(1)

    files = sorted(f for f in os.listdir(PHOTOS_DIR)
                   if f.lower().endswith(".webp"))

    cropped_count = 0
    skipped_count = 0
    flagged_list  = []
    errors        = []

    print(f"Processing {len(files)} .webp files in {PHOTOS_DIR}/...\n")

    for fname in files:
        path = os.path.join(PHOTOS_DIR, fname)
        try:
            status, data = process_photo(path)
        except Exception as e:
            errors.append((fname, str(e)))
            print(f"  ERROR {fname}: {e}")
            continue

        if status == "cropped":
            cropped_count += 1
            w, h = data
            print(f"  ✓ {fname} → {w}x{h}")
        elif status == "flagged":
            flagged_list.append((fname, data))
            print(f"  ⚠ {fname}: applied conservative crop (flagged sides: {', '.join(data)})")
        else:
            skipped_count += 1

    print(f"\n── Summary ──────────────────────────────")
    print(f"  Cropped:  {cropped_count}")
    print(f"  Flagged:  {len(flagged_list)}  (see below)")
    print(f"  Skipped:  {skipped_count}  (no border detected)")
    print(f"  Errors:   {len(errors)}")

    if flagged_list:
        print(f"\n── Photos that need manual review ───────")
        for fname, sides in flagged_list:
            print(f"  {fname}: {', '.join(sides)}")
        print("  For each flagged photo, check whether the crop looks correct.")
        print("  If not, manually crop and re-export from your scanning software.")

    if errors:
        print(f"\n── Errors ───────────────────────────────")
        for fname, msg in errors:
            print(f"  {fname}: {msg}")

    print("\nDone. Now run: python3 add_dimensions_to_json.py --force")

if __name__ == "__main__":
    main()
