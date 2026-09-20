# 06 — Maintenance Workflow

The everyday tasks. Each workflow assumes you're starting from a fresh terminal in `~/my-portfolio/`.

---

## Local dev (always start here)

```bash
cd ~/my-portfolio
python3 -m http.server 8000
```

Leave that terminal open. In a browser, visit `http://localhost:8000/<page>.html`.

**Never** open the HTML files via `file://` — the gallery will be empty because `fetch()` is blocked. See BUG-4 in `05-bugs-and-solutions.md`.

To stop the server: focus the terminal, hit `Ctrl+C`.

---

## Adding new photos to an existing project

1. Drop new full-resolution JPEGs into `~/my-portfolio/photos/`.
2. Run the all-in-one workflow:
   ```bash
   cd ~/my-portfolio
   ./deploy-photos.sh
   ```
   This does: resize → webp → write dimensions → size check.
3. Open the right JSON file in `data/`:
   ```bash
   open data/street.json   # or hongkong.json / landscapes.json
   ```
4. Add a new entry. Copy the structure of an existing entry:
   ```json
   {
     "file": "photos/NEW_PHOTO.jpg",
     "alt": "Short description for screen readers",
     "location": "Antwerp",
     "date": "2025",
     "filmstock": "HP5+",
     "width": 0,
     "height": 0
   }
   ```
   Leave `width`/`height` as `0` — they'll be filled in next step.
5. Re-run dimensions (now safe with the new entry):
   ```bash
   python3 add_dimensions_to_json.py
   ```
6. Test locally: `python3 -m http.server 8000`, visit the project page.
7. Deploy (see `07-deployment.md`).

**Gotchas**:
- Filenames with `+` → write as `%2B` in the JSON `file` field. The file on disk keeps `+`.
- Casing must match exactly (the Linux server is case-sensitive).
- JSON is strict: no trailing commas, no comments, all strings double-quoted.

---

## Reordering photos in a gallery

Just rearrange the entries in the corresponding `data/*.json` file. Save. Refresh. Done.

---

## Removing a photo

1. Delete or comment-out the entry in `data/<project>.json`.
2. (Optional) Delete the physical file from `photos/` if you'll never want it back. **Don't** delete the corresponding entry in `photos/originals/` casually — that's the only full-res backup.

---

## Editing the analog page's photos

The analog page does NOT use the JSON system. It has its own `PHOTOS` array hardcoded inside `analog.html`. To change which photos appear:

1. Open `analog.html`.
2. Find the `const PHOTOS = [ ... ]` block (around line ~400).
3. Add/remove entries:
   ```js
   { file: "photos/IMG_1234.jpg", alt: "..." },
   ```
4. Save, refresh.

This is intentional — the analog page is meant to be a curated moodboard, not a full gallery.

---

## Adding a new HTML page

If you ever add e.g. `project-portraits.html`:

1. Copy an existing project page (e.g. `project-street.html`) as a template.
2. Update the `<body data-project="portraits">` attribute.
3. Update page header (title, eyebrow, back-link).
4. Create the JSON: `data/portraits.json` with the right schema (see `02-file-structure.md`).
5. Add the project to the `PROJECTS` array in `script.js` (matches `data-project` → JSON path).
6. Add the new page to:
   - `patch_seo.py` → `PAGES` dict
   - `patch_seo_jsonld.py` → `PAGES_PERSON` list AND `PROJECT_PAGES` dict
7. Run the patchers:
   ```bash
   python3 patch_mobile_nav.py
   python3 patch_seo.py
   python3 patch_seo_jsonld.py
   ```
8. Add a link to it in the `nav.html` of every page (or use the patcher pattern if it becomes a hassle).
9. Update `sitemap.xml`.
10. Add a project card to `work.html`.

**Status of `project-portraits.html`**: scaffolded in patcher scripts but not built. See `08-todo-and-gotchas.md`.

---

## Updating email or contact info

The email is referenced in **three places**:
1. `about.html` (visible mailto link + footer)
2. `patch_seo_jsonld.py` (in the Person schema email field)
3. Any already-injected JSON-LD blocks in HTML files (these are NOT re-run by the patcher because of the sentinel)

For a future email change, the safest approach is a quick one-shot `sed`:
```bash
cd ~/my-portfolio
sed -i '' 's/OLD@EMAIL\.COM/NEW@EMAIL.COM/g' *.html patch_seo_jsonld.py
```
(Note the empty `''` after `-i` — that's BSD sed syntax on macOS. On Linux it would be `sed -i 's/.../.../'`.)

---

## Regenerating sitemap.xml

Currently maintained by hand. If we ever automate this, the algorithm is: for each `*.html` in project root, write a `<url>` entry with `loc=https://wiesverbeke.com/<file>`, `lastmod=$(date +%Y-%m-%d)`.

---

## Clearing the cache / forcing an updated photo to show

If you replace a photo (same filename, new content) and the old one still shows, it is browser caching — note that `_headers` is inert on nginx (see `07-deployment.md`). Solutions in order of preference:

1. Bump the filename (`IMG_1234.jpg` → `IMG_1234_v2.jpg` and update JSON).
2. Hard refresh in the browser (Cmd+Shift+R on Mac).
3. Confirm the new file was actually committed and pushed (`git log -1 --stat`) — an uncommitted photo never reaches the server.

---

## Workflow summary card (pin this)

```
LOCAL DEV       cd ~/my-portfolio && python3 -m http.server 8000
ADD PHOTOS      drop into photos/ → ./deploy-photos.sh → edit data/<project>.json
ADD A PAGE      see "Adding a new HTML page" above
DEPLOY          git add -A && git commit -m "..." && git push  (Coolify auto-deploys)
EMERGENCY       check 05-bugs-and-solutions.md for the matching symptom
```
