# 08 — TODO and Gotchas

## Open TODOs (things explicitly left undone)

*Last verified against the repo: 2026-09-20.*

### Content

- [ ] **Fill the remaining empty metadata in `data/*.json`.**
  Eight photos still have `"location": ""`, `"date": ""` or `"filmstock": ""` — two in each of hongkong, landscapes, portraits and street. Only the user knows the actual values. **Don't invent these — ask.**
  Current offenders: `IMG_3914`, `IMG_3922` (hongkong); `1758190419-55782500-4`, `1758190448-61499600` (landscapes); `IMG_2816`, `1758190492-61513300` (portraits); `1758190416-43194600_edited`, `1758190451-74825800-2` (street).
- [ ] **Replace the about-page portrait.**
  `about.html` line 52 still points at `photos/Trasher-cat-with-sunglasses.webp` — a placeholder. User said they'd swap it in eventually.

### Site

- [ ] **Custom 404 page** — currently the nginx default. To add: create `404.html` **and** point nginx at it (`error_page 404 /404.html;`). nginx does not pick it up automatically the way Netlify did. Low priority.
- [ ] **Cache-control headers** — the live site sends `etag`/`last-modified` but no `cache-control`, so photos revalidate on every visit. `_headers` is inert on nginx. Fix belongs in the nginx/Coolify config. See `07-deployment.md`. Low priority.

### Done — no longer open

- ~~`project-portraits.html` (Series IV)~~ — **built.** The page, `data/portraits.json` and the work.html card all exist.
- ~~Migrate off Netlify~~ — **done, but not to Cloudflare Pages.** The site now runs on a Hetzner VPS with Coolify. See `07-deployment.md`.

---

## Non-obvious gotchas — must read

### 1. JSON is the source of truth, HTML is the shell

The four project pages render their galleries from JSON via `script.js`. **Editing the HTML to add photos is a regression.** If you find yourself reaching for an `<img>` tag in `project-*.html`, stop and edit the JSON instead.

The only HTML on a project page is the nav, page header, the empty `#gallery-grid` div, and the lightbox markup.

### 2. The analog page is intentionally different

`analog.html` is fully self-contained: it has its own `<style>` block AND its own `<script>` block AND its own `PHOTOS` array. It does NOT use:
- `data/*.json`
- The shared gallery render code in `script.js`

It DOES load:
- `style.css` (purely for the shared mobile-nav classes — see BUG-8)
- `nav.js` (for hamburger toggle)

So if you're "fixing inconsistencies" between analog and the other pages, don't. The asymmetry is by design.

### 3. Don't refactor `script.js` lightly

`script.js` does three things in one file: gallery render, scroll fade-in (IntersectionObserver), lightbox (open/close/prev/next/keyboard/swipe). They share state. Splitting them seems clean but the lightbox needs to know the array of currently-visible photos that the renderer just produced. Keep it monolithic.

### 4. Idempotency is mandatory for patchers

Every Python patcher in the repo can be re-run safely. **Maintain this invariant.** If you write a new patcher and it's NOT idempotent, the user will eventually re-run it and break their site. The pattern:
```python
SENTINEL = "<unique string the patched file will contain>"
if SENTINEL in html: return  # skip
```

### 5. The user is on macOS

Several scripts use macOS-specific commands:
- `sips` (resize-photos.sh) — image manipulation.
- `stat -f%z` (check-photo-sizes.sh) — BSD stat syntax.
- `sed -i ''` — BSD sed needs empty string after -i, GNU sed doesn't.

If you ever need to run these on Linux, you'll need to adapt. Don't assume cross-platform.

### 6. Don't touch `photos/originals/`

That folder is the only place full-resolution backups live after resizing. Deleting it loses the originals permanently. The `resize-photos.sh` script will never overwrite a file already in `originals/`, but you can delete the folder by accident — which would be irreversible.

It is **gitignored**, so it is never deployed and never leaves this Mac. If disk space matters, move it to an external drive — but move it, don't delete it. As of 2026-09-20 it holds exactly two files: the source JPGs for `1758190356-50958100` and `50y_Jubileum_34`.

### 7. The `_2` and `_copy` filename suffixes mean something

- `IMG_3088_2.jpg` — variant of `IMG_3088.jpg` (e.g. different crop, different exposure). Both may be in `photos/`.
- `50y-Jubileum-34_copy.jpg` — film-strip-bordered version, used as project cover photos.

Don't "clean up duplicates" — they're intentional.

### 8. Filenames with `+` are real

`FP4+OM4-T_24.jpg` is a valid filename. The `+` is a film stock abbreviation. **Don't rename to remove the `+`.** Instead, encode as `%2B` in HTML and JSON paths. See BUG-1.

### 9. Hamburger menu needs all three: HTML + CSS + JS

If the hamburger seems broken on a specific page, check all three layers:
1. Does the HTML contain `<button class="nav__toggle">` and `<div class="nav__mobile">`? If not, run `python3 patch_mobile_nav.py`.
2. Does the page load `style.css`? Critical for analog.html — see BUG-8.
3. Does the page load `nav.js`? Check the `<script src="nav.js">` is there before `</body>`.

### 10. Output style

This doc was written when the project lived in claude.ai, where the workflow was "produce a file, user downloads it, user drags it into the folder." **In Claude Code you edit the files directly** — that older workflow no longer applies. What survives from it: when a change is small, show the user exactly what changed rather than dumping a whole file.

### 11. Don't run `extract_to_json.py` again

It's deleted, but if it ever comes back: don't run it. It reads the OLD `<figure>`-based HTML to produce JSON. The current HTML files have no `<figure>` elements (only the empty `#gallery-grid` div). Running it would produce empty JSON files and silently destroy the manually-curated metadata.

### 12. JSON-LD `Person` schema has the email baked in

If the user changes their email again, you need to update:
1. `about.html` (mailto link, visible text)
2. `patch_seo_jsonld.py` (the patcher source)
3. Every already-patched HTML file (in-place sed — the patcher won't re-inject)

See BUG-11.

### 13. The server is case-sensitive, macOS is not

The biggest source of "works locally, broken in production" issues. nginx on Linux distinguishes `Photo.webp` from `photo.webp`; your Mac does not. Always match filename casing exactly. When in doubt: `ls photos/ | grep -i <name>`.

### 14. `photos/` is webp-only

The repo went webp-only in May 2026. Source JPGs belong in `photos/originals/` (gitignored), not in `photos/`. A `.jpg` sitting loose in `photos/` is a mistake waiting to be committed — it will be served but nothing references it.

### 15. `_headers` does nothing

It is a Netlify-era file. nginx never reads it. Editing it to change caching will appear to work (the file changes, the deploy succeeds) and change nothing. See `07-deployment.md`.

---

## Things that look like bugs but aren't

- **Favicon doesn't show on `file://` or sometimes on localhost** — paths are root-relative (`/favicon.ico`). Works fine on the deployed site. Don't chase this locally.
- **`.webp` files with no `.jpg` beside them** — intentional since the webp-only migration. The JPGs live in `photos/originals/`, gitignored.
- **`photos/originals/` is huge** — intentional. It's the full-resolution backup folder. Gitignored, not served, never deployed. The user can move it to an external drive if disk space matters.
- **Docs live in `docs/` inside the deployed folder** — they get deployed along with everything else, but nobody finds them unless they navigate to `wiesverbeke.com/docs/...`. The user knows, and prefers the docs close to the code.

---

## When you're stuck

In rough order:
1. Check `05-bugs-and-solutions.md` — odds are good the symptom is already documented.
2. Check the browser console — many "broken page" issues are a single typo in a JSON file or a missing photo, and the console will say which.
3. Check the Network tab in DevTools — failed `fetch()` for `data/*.json` or a 404 on a photo will show here.
4. Ask the user. They know things about their photos and life that aren't in the code.
