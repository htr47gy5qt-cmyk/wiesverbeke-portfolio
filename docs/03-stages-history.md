# 03 — Stages History

Everything we've built, in the order it happened. Useful for understanding *why* things are the way they are.

---

## Stage 1 — Initial scaffold

**Goal**: get from "I have zero coding experience" to a clickable homepage.

- Created `index.html`, `style.css`, `script.js`.
- Picked the design system: Cormorant Garamond + Jost, cream/black/gold palette.
- Built a simple nav, a single hero image, a basic 3-column gallery, and a lightbox.
- Used Unsplash placeholder images during build-out, replaced with the user's photos once they arrived.

## Stage 2 — Real photos and project pages

**Goal**: replace placeholders with the user's actual film photography.

- The user dropped ~140 photos into `photos/`.
- Built `project-street.html`, `project-hongkong.html`, `project-landscapes.html`.
- Each page was originally a hardcoded list of `<figure>` blocks, one per photo.
- Built `work.html` with three project cards linking out to the project pages.
- Built `about.html` with bio text and a portrait.

**Key bug fixed in this stage**: filenames with `+` (e.g. `FP4+OM4-T_24.jpg`) didn't load. Browsers interpret `+` in URLs as space. Fix: URL-encode as `%2B` in HTML/JSON. The file on disk keeps the literal `+`.

## Stage 3 — Lightbox polish + metadata

**Goal**: when you click a photo, the lightbox should show shooting info.

- Added `data-location`, `data-date`, `data-filmstock` attributes to every `<figure>`.
- `script.js` reads them and injects into a metadata bar at the bottom of the lightbox.
- Long location names (Hong Kong: "Tsim Sha Tsui Promenade") were breaking layout — fixed with `flex-wrap`, `max-width: 90vw`, `white-space: normal` on `.lightbox__metadata`.
- Added touch swipe support for mobile lightbox navigation.
- Added keyboard support (←, →, Esc).

## Stage 4 — Favicon

**Goal**: that little icon in the browser tab.

- User generated the favicon set via realfavicongenerator.net.
- Wrote a `sed` one-liner that injects the favicon `<head>` block before `</head>` in every HTML file.
- Favicon paths use absolute `/favicon.ico` style, which **only works once published** (not on `file://`).

## Stage 5 — Image resize pipeline

**Goal**: stop the user from uploading 12MB phone photos directly to the site.

- Wrote `resize-photos.sh` — uses macOS `sips`, max 2400px long edge at 85% quality.
- Backs up originals to `photos/originals/` before resizing.
- Made it idempotent: skips photos already ≤2400px, never overwrites existing backups.
- Wrote `check-photo-sizes.sh` — read-only scan, flags anything over 1.5MB.

## Stage 6 — The analog page (experimental)

**Goal**: a fun "moodboard" / mouse-trail page separate from the curated galleries.

- Built `analog.html` as a self-contained page with its own `<style>` and `<script>` blocks.
- Mouse moves 200px → a new photo spawns at cursor position, true aspect ratio, max 620px long edge.
- Only the newest photo is clickable (opens lightbox). Older photos are visually present but inert.
- Has a custom cursor and a "Clear" button bottom-left.
- Photos come from a hardcoded `PHOTOS` array inside the file. To edit content, edit the file.
- Originally desktop-only ("This experience is designed for desktop." message on mobile).

**Bug fixed**: race condition where slow-loading images would briefly remain clickable after a newer one had appeared. Fix: two-layer guard — CSS `pointer-events: none` on demoted cards, **and** a JS check in event listeners (`if (card !== clickableCard) return;`).

## Stage 7 — JSON refactor (the big one)

**Goal**: stop editing HTML to add/reorder photos. Move all photo data to JSON.

1. Wrote `extract_to_json.py` — parses each `project-*.html`, pulls every `<figure>`'s metadata, writes `data/<id>.json`.
2. Ran it once. Generated `data/street.json`, `data/hongkong.json`, `data/landscapes.json`.
3. Rewrote `project-*.html` as thin shells with an empty `<div id="gallery-grid"></div>` and `<body data-project="...">`.
4. Rewrote `script.js` to: detect the project from `data-project`, `fetch()` the JSON, build figures dynamically, then run the existing fade-in and lightbox code.
5. Wrote README.md documenting the new workflow.

**Killed by this change**: ability to use `file://` URLs to test locally. `fetch()` is blocked by browsers over `file://`. The user must now `python3 -m http.server 8000` for local dev.

## Stage 8 — SEO

**Goal**: make the site discoverable and shareable.

- Wrote `patch_seo.py` — injects meta description, Open Graph tags, Twitter Card, canonical URL into every HTML file based on a `PAGES` dict at the top of the script.
- Wrote `patch_seo_jsonld.py` — injects JSON-LD structured data: `Person` schema on every page, plus `ImageGallery` schema on project pages.
- Both scripts idempotent (sentinel-based: skip if their marker is already present).
- Added `sitemap.xml` and `robots.txt`.

## Stage 9 — Mobile navigation (hamburger)

**Goal**: usable nav on phones (the inline nav links broke under 480px).

- Added `.nav__toggle` (hamburger button) and `.nav__mobile` (full-screen overlay menu) classes to `style.css`.
- Wrote `nav.js` — tiny standalone script handling open/close, `aria-expanded`, body class toggle, close-on-link-tap.
- Wrote `patch_mobile_nav.py` — injects the hamburger button + mobile menu HTML + `<script src="nav.js">` into every page's `<nav>` block. Idempotent.
- Boosted z-index of `.nav__mobile` to 9000 and `.nav__toggle` to 9100 so they sit above the analog page's spawned photo cards.

**Bug 1 fixed**: hamburger placement script initially placed the menu in the wrong spot. Fixed with `fix_nav_placement.py` (one-time).
**Bug 2 fixed**: analog page didn't load `style.css`, so the injected hamburger + mobile menu rendered as unstyled text in the middle of the page. Fix: added `<link rel="stylesheet" href="style.css" />` at the top of `analog.html`.
**Bug 3 fixed**: tapping the hamburger on the analog page also spawned a photo card. Fix: in the analog page's tap handler, ignore taps on `.nav__toggle` and `.nav__mobile` and their children.

## Stage 10 — Analog page goes mobile

**Goal**: make the desktop-only experience work on touch devices.

- Removed the "Designed for desktop" mobile block.
- On touch devices, photos spawn on **tap** instead of cursor-move.
- Clamped card positioning so a tap near the edge of a 380px-wide viewport doesn't push the card half off-screen (`clampTopLeft()` helper inside `spawnCard()`).

## Stage 11 — WebP companions + dimension metadata

**Goal**: faster loading + no layout shift.

- Wrote `convert-to-webp.sh` — generates `.webp` companions for every `.jpg` in `photos/` (skips existing). Uses `cwebp` (install via `brew install webp`).
- Wrote `add_dimensions_to_json.py` — reads each photo's pixel dimensions and writes `width` / `height` into the corresponding JSON entry. Allows `script.js` to reserve aspect-ratio space and prevent layout shift.
- Created `deploy-photos.sh` — runs `resize-photos.sh`, `convert-to-webp.sh`, `add_dimensions_to_json.py`, `check-photo-sizes.sh` in sequence with `set -e`.

## Stage 12 — Email migration

**Goal**: privacy. User created a dedicated Proton inbox.

- Old: `wiesverbeke@icloud.com`. New: `wiesverbeke-photo@proton.me`.
- Wrote a one-time `update_email.py` (now deleted) that did a `sed`-style replace across HTML files and the JSON-LD patcher.
- Also updated existing already-patched HTML (the JSON-LD scripts are idempotent and won't re-inject, so direct file patching was needed).

## Stage 13 — Hosting migration (done)

**Goal**: deal with the Netlify free-tier bandwidth limit.

- The site hit Netlify's 100GB/month cap and went down until the cycle reset.
- Cloudflare Pages was researched and chosen as the migration target — **but that plan was never executed.**
- Instead the site moved to a **self-managed Hetzner VPS in Helsinki** (Ubuntu + nginx) with **Coolify** as the deploy interface.
- Deploy flow changed from drag-and-drop to **`git push` → Coolify auto-deploys**.
- Side effect: the `_headers` file (Netlify-specific) became inert. nginx ignores it. See `07-deployment.md`.

## Stage 14 — Dark mode

- Added `theme-toggle.js` and a "curtain" dark/light toggle that wipes across the page on switch.
- Dark mode initially broke in Safari (commit `f915ba9`); fixed the same day.

## Stage 15 — Film borders move to CSS

- Wrote `strip_film_borders.py` to remove the borders baked into the image files.
- Replaced them with **theme-aware CSS borders**, so the frame follows dark/light mode instead of being burnt into the pixels.
- Re-converted `50y_Jubileum_34` from its original JPG after the strip.

## Stage 16 — Nav and curation pass

- Nav now scrolls with the page on project and work pages instead of staying fixed.
- Several culling passes: 5 photos removed (May), 4 more (June), then a trim to **6 curated photos per project** (July), matching Portraits.
- `shanghai_005.webp` (Lucky Film 200) added as the Landscapes closer.

## Stage 17 — SEO round two

- Open Graph / Twitter / JSON-LD meta added to `analog.html` and `work.html` (they had been missed).
- Fixed the placeholder OG image on `project-portraits.html`.
- Replaced the bulky base64-embedded `favicon.svg` with a lighter version.

## Stage 18 — Film-strip galleries

**Goal**: show photos at their true proportions instead of cropping them into a masonry grid.

- Replaced the CSS-columns masonry with a **single horizontal film strip**: large fixed-height photos, true aspect ratios, no cropping.
- Free momentum scrolling, plus vertical-wheel-to-horizontal mapping and click-and-drag panning.
- Arrow keys glide and centre one photo at a time.
- Added a right-edge "Swipe →" hint.
- Hover zoom is suppressed while scrolling to avoid jank.
- Lives in `script.js` + `style.css` (commit `aae71b5`).

## Stage 19 — Vertical galleries (current)

**Goal**: drop the horizontal strip. Sideways scrolling is not a gesture people
expect on a web page — it needed a "Swipe →" hint and a wheel hijack to be usable
at all.

- Galleries are now a plain vertical column: **one photo per row**, centred, at its
  true aspect ratio, capped to `min(80vh, 900px)` tall. Nothing is cropped.
- Each photo carries a **caption** beneath it — location · date · film stock, empty
  fields skipped. Metadata used to be visible only inside the lightbox.
- New markup: `figure.gallery__item` › `div.gallery__frame` (the bordered box, and
  the lightbox click target) + `figcaption.gallery__caption`. The border hugs the
  photo; the caption sits outside it.
- Removed with the strip: the wheel-to-horizontal hijack, click-and-drag panning,
  arrow-key glide-and-centre, the `.is-scrolling` hover suppression, and the
  "Swipe →" hint (`initStrip()` is gone entirely — script.js dropped 404 → 272 lines).
- Photos after the first now use `loading="lazy"`. Safe because the fade observer
  watches the figure, not the image — see BUG-12.

## Open / not done

- Eight photos across the four galleries still have empty `location` / `date` / `filmstock`. Only the user knows these values — **never invent them**.
- The about-page portrait is still the placeholder (`photos/Trasher-cat-with-sunglasses.webp`).
- No custom `404.html`.
- No cache-control headers configured on nginx (see `07-deployment.md`).
