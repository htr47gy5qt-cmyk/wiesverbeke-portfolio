# 05 — Bugs and Solutions

Every non-trivial bug we've hit, with root cause and fix. **Read this fully** — most of these are subtle and several will recur if you don't know about them.

---

## 🔴 BUG-1 — Photos with `+` in filename don't load

**Symptom**: Some street photos showed broken image icons (specifically anything from the `FP4+OM4` series).

**Root cause**: The `+` character in URLs is interpreted as space by browsers (legacy form-encoding semantics). The file on disk is `FP4+OM4-T_24.jpg` but the browser was looking for `FP4 OM4-T_24.jpg`.

**Fix**: URL-encode `+` as `%2B` **in HTML and JSON paths only**. Don't rename the file on disk.

```html
<!-- WRONG -->
<img src="photos/FP4+OM4-T_24.jpg">
<!-- RIGHT -->
<img src="photos/FP4%2BOM4-T_24.jpg">
```

**Where to watch**: any time you write a path that references a photo, check if the filename contains `+` and encode it.

---

## 🔴 BUG-2 — Filename typo: hyphen vs underscore

**Symptom**: One Hong Kong photo wouldn't load.

**Root cause**: HTML referenced `28042026_02_fuji400-59.jpg` (hyphen) but the real file was `28042026_02_fuji400_59.jpg` (underscore). On macOS local dev with case-insensitive filesystem you may also get this for case mismatches and never see the error locally.

**Fix**: Match the filename exactly. **The server is case-sensitive**, so casing mismatches that pass locally will fail in production.

**Where to watch**: when typing paths by hand, always grab the exact filename via `ls photos/ | grep <pattern>` rather than guessing.

---

## 🔴 BUG-3 — `localhost` refused to connect

**Symptom**: User opened `http://localhost:8000/...` and browser said connection refused.

**Root causes** (in order of likelihood):
1. User closed the terminal window where `python3 -m http.server` was running. Closing the terminal kills the server.
2. User opened the browser before starting the server.
3. Port 8000 already in use. Python prints `OSError: [Errno 48] Address already in use` and refuses to start.

**Fix / instructions to give**:
```bash
cd ~/my-portfolio
python3 -m http.server 8000
# leave THIS terminal open, untouched
# in a NEW browser tab visit http://localhost:8000/project-street.html
```

If "Address already in use": `lsof -i :8000` to find the rogue process, `kill <PID>`, then restart. Or use a different port (`python3 -m http.server 8001`).

---

## 🔴 BUG-4 — Galleries empty when opening files via `file://`

**Symptom**: Double-clicking `project-street.html` opened the page but the gallery was empty.

**Root cause**: Browsers block `fetch()` over `file://` URLs (CORS / same-origin restriction). After the JSON refactor (Stage 7), `script.js` uses `fetch('data/street.json')` to load the gallery, which fails silently on `file://`.

**Fix**: Always run `python3 -m http.server 8000` for local dev. Never test by double-clicking the HTML.

**Documented in**: `README.md`, `06-maintenance-workflow.md`.

---

## 🔴 BUG-5 — Lightbox layout shift on long location names

**Symptom**: On the Hong Kong project page, opening the lightbox for a photo with a long location (`"Tsim Sha Tsui Promenade"`) shifted the bottom metadata bar horizontally and broke alignment.

**Root cause**: Default flex layout pushed the long string onto one line, blew past the viewport, and dragged the dot separators with it.

**Fix** (in `style.css` `.lightbox__metadata`):
```css
flex-wrap: wrap;
max-width: 90vw;
white-space: normal;
justify-content: center;
gap: 0.5rem 1rem;
```

Also, `script.js` hides the `●` separators if the adjacent field is empty (e.g. landscapes photos with no filmstock specified).

---

## 🔴 BUG-6 — Analog page: old photos remained clickable after newer ones spawned

**Symptom**: On the analog page, after spawning several photos, clicking what looked like an older (lower-z) card opened the lightbox to that photo — but the design says only the newest card should be clickable.

**Root cause**: A race condition. The "demote all other cards" loop happened *after* `stage.appendChild()`, and only re-set `pointer-events`. If a slow-loading image's `probe.onload` finished after newer cards had been spawned, that card's `onload` callback would re-promote itself as newest.

**Fix**: Two-layer guard.
1. **CSS layer**: Maintain a `clickableCard` reference. After every spawn, set `pointer-events: auto` only on `clickableCard`, `pointer-events: none` on every other card.
2. **JS guard layer**: In the click and mouseenter event listeners, check `if (card !== clickableCard) return;`. This guarantees that even if `pointer-events` race-conditions out, the click handler still refuses to act on the wrong card.

The combined approach means either layer alone is enough.

---

## 🔴 BUG-7 — Analog page mobile: cards pushed off-screen

**Symptom**: After making analog work on mobile, tapping near the edge of the viewport spawned a card that was half off-screen.

**Root cause**: Cards spawn centered on tap. On a 380px-wide phone, a 380px card centered on a tap at x=350 extends 175px off the right edge.

**Fix**: Added a `clampTopLeft(left, top, w, h)` helper inside `spawnCard()` that clamps the card's `left`/`top` to keep it on-screen with an 8px margin. Used in both the synchronous initial position and the async re-position after the image's true aspect ratio is known.

---

## 🔴 BUG-8 — Analog page nav looked broken after mobile-nav patch

**Symptom**: After running `patch_mobile_nav.py`, the analog page's nav rendered as plain unstyled text in the middle of the page: a bare "Open menu" button and the three nav links as stray block-level elements.

**Root cause**: The mobile hamburger classes (`.nav__toggle`, `.nav__mobile`) are styled in `style.css`. The analog page had been built as a fully self-contained page with its own inline `<style>` block — it didn't load `style.css`. So when the patcher injected those classes, there was no CSS to style them.

**Fix**: Added `<link rel="stylesheet" href="style.css" />` at the top of `analog.html`, **before** the page's inline `<style>` block. The inline block's later position in source order means it still wins on any conflicts (e.g. `body { background }`).

**Important**: This is the only page that loads `style.css` for cross-cutting concerns despite having its own styles. Don't refactor it without understanding this.

---

## 🔴 BUG-9 — Tap on hamburger also spawned a card on analog page

**Symptom**: After making the analog page work on mobile, tapping the hamburger icon spawned a new photo card behind the menu.

**Root cause**: The analog page's tap handler is on `document` and fires on every tap including ones meant for the nav.

**Fix**: At the top of the analog tap handler, return early if the tap target is inside `.nav__toggle`, `.nav__mobile`, or the regular nav:
```js
if (e.target.closest('.nav, .nav__toggle, .nav__mobile')) return;
```

Also bail out if the mobile menu is currently open (`document.body.classList.contains('nav-open')`).

---

## 🔴 BUG-10 — Mobile menu sat below the analog photo cards

**Symptom**: Open the hamburger on the analog page → menu appears, but cards spawned after a while overlap and cover it.

**Root cause**: Analog photo cards use `z-index: zCounter++` starting at 1. After ~100 spawns z-index exceeds 100. Mobile menu was at `z-index: 105`. So eventually the cards win.

**Fix**: Boosted `.nav__mobile` to `z-index: 9000` and `.nav__toggle` to `z-index: 9100`. Practically nothing will ever spawn that high.

---

## 🔴 BUG-11 — Email migration didn't catch already-patched HTML JSON-LD

**Symptom**: After running `update_email.py`, the contact email in `about.html` updated correctly but the JSON-LD blocks (already injected by `patch_seo_jsonld.py`) still contained the old icloud address.

**Root cause**: The JSON-LD patcher is idempotent — it skips files where the sentinel is already present. Running it again wouldn't re-inject. So updating the patcher script alone wasn't enough; existing files needed direct find-and-replace.

**Fix**: A one-shot `sed -i 's/wiesverbeke@icloud\.com/wiesverbeke-photo@proton.me/g'` across all HTML files, AND updating the patcher script itself for future page additions.

**Lesson**: When changing data that's been injected by an idempotent patcher, you need to update **both** the source patcher AND the already-patched files in place.

---

## 🔴 BUG-12 — Safari: lazy-loaded photos never faded in

**Symptom**: on Safari, gallery photos stayed invisible — the fade-in never fired,
so the page looked empty below the first photo.

**Root cause**: the scroll fade used an IntersectionObserver watching the `<img>`
elements. A `loading="lazy"` image that hasn't loaded yet has no intrinsic size in
Safari, so its box is 0×0 and it can never intersect the viewport. No intersection,
no `.is-visible`, no fade — the photo stayed at `opacity: 0` forever.

**Fix (two parts)**:
1. Commit `11f8c32` dropped the observer threshold to `0` so a zero-height box can
   still trigger.
2. The vertical gallery goes further: the observer now watches the `.gallery__item`
   figure rather than the image. A figure always has a real box (it reserves the
   photo's aspect ratio from the `width`/`height` attributes, plus the caption), so
   it intersects reliably whether or not the image has loaded.

**Rule**: if you ever point the fade observer back at the images, lazy loading must
go. Watch a container that has a size of its own.

---

## 🟡 Quirk — Favicon doesn't show locally

Not a bug, but a recurring confusion: the favicon never appears when opening via `file://` because the paths use `/favicon.ico` (root-relative). On `localhost:8000` and on the live site it works fine. Don't waste time debugging this locally.

---

## 🟡 Quirk — server case-sensitivity

macOS HFS+/APFS is case-insensitive by default. nginx on Linux is case-sensitive. Result: `<img src="photos/Photo.jpg">` referencing a file actually named `photo.jpg` works locally but breaks in production.

**Rule**: always write paths with the exact casing of the file on disk. When in doubt, run `ls photos/ | grep -i <name>`.
