# 04 — Scripts Reference

Every helper script in the project root. Sorted by frequency of use.

---

## 🔁 Run frequently (when adding photos)

### `deploy-photos.sh`

All-in-one wrapper. Runs the four photo-workflow scripts in sequence with `set -e` (stops on first failure).

```bash
./deploy-photos.sh
```

Sequence:
1. `resize-photos.sh` — downsize new big photos
2. `convert-to-webp.sh` — generate `.webp` companions
3. `add_dimensions_to_json.py` — fill width/height in JSON
4. `check-photo-sizes.sh` — final sanity scan

Must be run from project root (it checks for `photos/`).

### `resize-photos.sh`

Resizes every JPEG in `photos/` (NOT inside `photos/originals/`) to **max 2400px long edge at 85% quality** using macOS `sips`.

```bash
./resize-photos.sh
```

Behavior:
- **Skips** photos already ≤2400px on the long edge.
- **Backs up** originals to `photos/originals/` before resizing. **Never** overwrites an existing backup.
- Prints a summary: resized X, skipped Y, errors Z.
- Tunable constants at top: `MAX_EDGE=2400`, `QUALITY=85`.
- **macOS-only** (requires `sips`).

### `convert-to-webp.sh`

Generates a `.webp` companion next to every `.jpg` in `photos/`. Skips any that already have a companion.

```bash
./convert-to-webp.sh
```

- Requires `cwebp` from Google. Install: `brew install webp`.
- Used by `script.js` via `<picture>` tags with WebP source + JPG fallback (saves ~25-40% bandwidth in modern browsers).

### `add_dimensions_to_json.py`

Reads each photo's pixel dimensions (Pillow/PIL) and writes `width` + `height` into the corresponding entry in `data/*.json`.

```bash
python3 add_dimensions_to_json.py
```

- Skips entries that already have both fields.
- Walks all three JSON files: `data/street.json`, `data/hongkong.json`, `data/landscapes.json`.
- Requires the file to exist in `photos/`. If it doesn't, logs a warning and continues.
- Needs Pillow: `pip install Pillow` (or `python3 -m pip install Pillow --user`).

### `check-photo-sizes.sh`

Read-only scan. Flags any file in `photos/` over **1.5MB**. Doesn't change anything.

```bash
./check-photo-sizes.sh
```

- Tunable: `LIMIT_KB=1500` at top of script.
- Note: uses BSD `stat -f%z` (macOS). If ever run on Linux, swap to `stat -c%s`.

---

## 🛠️ Run rarely (one-shot patchers)

These are idempotent — safe to re-run. They detect "already patched" via sentinel strings in the HTML and skip those files.

### `patch_mobile_nav.py`

Adds the mobile hamburger button + full-screen mobile menu + `<script src="nav.js">` to every `*.html` file in the project root.

```bash
python3 patch_mobile_nav.py
```

- Sentinel: looks for `class="nav__toggle"` (won't double-inject).
- Runs once per new HTML file. If you add a new page, run this and it'll patch only the new one.

### `patch_seo.py`

Injects: meta description, Open Graph tags (og:title, og:description, og:image, og:url, og:type), Twitter Card, canonical URL.

```bash
python3 patch_seo.py
```

- Configured via a `PAGES` dict at the top of the file mapping HTML filename → metadata.
- Sentinel-based idempotent.
- **Adding a new page**: add an entry to the `PAGES` dict, run the script.

### `patch_seo_jsonld.py`

Injects JSON-LD structured data:
- `Person` schema on every page (uses the Proton email `wiesverbeke-photo@proton.me`).
- `ImageGallery` schema on project pages (lists photos from the corresponding JSON).

```bash
python3 patch_seo_jsonld.py
```

- Two top-of-file lists: `PAGES_PERSON` (every page) and `PROJECT_PAGES` (project pages with gallery data).
- Sentinel-based idempotent.

---

## 🪦 Deleted / historical (do not recreate unless needed)

These ran once, did their job, and were deleted. Their effects are baked into the current files. Listed here so you don't get confused finding them referenced in chat history.

- **`extract_to_json.py`** — Parsed old `<figure>`-heavy `project-*.html` files, extracted metadata, wrote initial `data/*.json`. **Done. Don't re-run** — it would overwrite hand-edited JSON.
- **`fix_nav_placement.py`** — Fixed a bug from the first `patch_mobile_nav.py` run where the hamburger ended up in the wrong place. Done.
- **`update_email.py`** — Replaced `wiesverbeke@icloud.com` with `wiesverbeke-photo@proton.me` everywhere. Done.

---

## Recurring script patterns to follow

Whenever writing a new Python patcher, copy this idiom:

```python
SENTINEL = '<some unique string that the patched HTML will contain>'

def patch(path):
    with open(path) as f: html = f.read()
    if SENTINEL in html:
        print(f"  ✓ {path} already patched, skipping")
        return
    # ... do the patch ...
    with open(path, 'w') as f: f.write(new_html)
    print(f"  ✓ patched {path}")
```

This is what makes every patcher safely re-runnable.

For shell scripts, follow these conventions seen in `resize-photos.sh`:
- `set -euo pipefail` at the top.
- Sanity-check the working directory (e.g. `if [ ! -d "photos" ]`).
- Use colored output for readability (`BOLD="\033[1m"`, `GREEN="\033[32m"`, etc.).
- Print a final summary (X done, Y skipped, Z errored).
