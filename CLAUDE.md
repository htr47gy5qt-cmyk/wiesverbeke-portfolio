# CLAUDE.md

This file is read automatically by Claude Code at the start of every session in this directory. It is the entry point for understanding this project.

## What this project is

**Wies Verbeke's photography portfolio website.** A minimalist, hand-coded static site built with HTML / CSS / vanilla JS. No frameworks, no bundler, no `npm`. The whole project ships as the files in this folder.

Live at https://wiesverbeke.com. Domain registered at zone.eu. Hosted on a self-managed Hetzner VPS in Helsinki (Ubuntu), using Coolify as the deployment interface.

## Before doing anything, read the docs

The full context lives in `docs/`. Read those files **in numerical order** before making changes:

1. `docs/00-START-HERE.md` — overview of how the docs are structured
2. `docs/01-project-overview.md` — tech stack, design system, user profile
3. `docs/02-file-structure.md` — every file in this folder explained
4. `docs/03-stages-history.md` — chronological history of what's been built
5. `docs/04-scripts-reference.md` — every helper script (shell + Python)
6. `docs/05-bugs-and-solutions.md` — 11 documented bugs and their fixes (do NOT skip)
7. `docs/06-maintenance-workflow.md` — day-to-day workflows
8. `docs/07-deployment.md` — hosting (Hetzner + Coolify), DNS, deploy flow
9. `docs/08-todo-and-gotchas.md` — open work + non-obvious quirks

If the user asks for something that touches a topic in the docs, **read the relevant file first** instead of pattern-matching from memory.

## The user

**Wies Verbeke.** Amateur film photographer, based in Belgium. **Zero coding background.** Has learned over many months to:
- Run shell commands you give them
- Edit JSON carefully (knows about trailing commas)
- Drag files in/out of folders
- Use `cd`, `ls`, `python3 -m http.server`

Communicate accordingly: plain English, exact commands, exact file paths. No jargon dumps. They will tell you if they want more depth. Assume they will not catch unclear pronouns ("just edit it") — be specific about which file.

## Critical rules (full detail in `docs/`)

1. **JSON is the source of truth.** Each project gallery is rendered by `script.js` from `data/<project>.json`. Adding a photo means editing the JSON, NOT the HTML. The HTML files are thin shells with empty `<div id="gallery-grid"></div>` placeholders.

2. **The analog page is the exception.** `analog.html` is fully self-contained with its own `<style>` block, `<script>` block, and hardcoded `PHOTOS` array. It does NOT use the JSON pipeline. It DOES load `style.css` (only for the shared mobile-nav classes — do not "fix" this).

3. **Filenames with `+`.** Files like `FP4+OM4-T_24.jpg` exist on disk with a literal `+`. In **HTML and JSON paths**, encode as `%2B`. Browsers interpret `+` in URLs as space. Never rename files to remove `+`.

4. **The server is case-sensitive, macOS is not.** Paths like `photos/Photo.jpg` may work locally but break in production (nginx on Linux) if the file is actually `photo.jpg`. Always match casing exactly. When in doubt: `ls photos/ | grep -i <name>`.

5. **Local dev requires a server.** `script.js` uses `fetch()` for JSON, which browsers block over `file://`. The user must run `python3 -m http.server 8000` and visit `http://localhost:8000/<page>.html`. Never tell them to double-click the HTML file.

6. **Every Python patcher must be idempotent.** Use a sentinel string check at the top so re-running is a no-op on already-patched files. The existing patchers (`patch_mobile_nav.py`, `patch_seo.py`, `patch_seo_jsonld.py`) all follow this pattern. Any new patcher you write must too.

7. **macOS-specific commands in scripts.** `sips` (image resize), BSD `stat -f%z`, BSD `sed -i ''` (empty string required on macOS). Do not "modernize" these to GNU equivalents.

8. **Don't run deleted scripts.** Especially `extract_to_json.py` — it would overwrite the hand-curated `data/*.json` files with empty values. It lived once, did its one-time job, and is gone for a reason.

## Project file structure (quick reference)

```
my-portfolio/
├── CLAUDE.md                     ← this file
├── docs/                         ← full project documentation
│
├── index.html                    ← home page
├── work.html                     ← project landing (4 cards)
├── about.html                    ← bio + portrait
├── analog.html                   ← experimental mouse-trail page
├── project-street.html           ← JSON-rendered gallery
├── project-hongkong.html         ← JSON-rendered gallery
├── project-landscapes.html       ← JSON-rendered gallery
├── project-portraits.html        ← JSON-rendered gallery
│
├── style.css                     ← shared stylesheet
├── script.js                     ← gallery render + film-strip + lightbox + fade
├── nav.js                        ← hamburger toggle
├── theme-toggle.js               ← curtain dark/light mode toggle
│
├── data/
│   ├── street.json
│   ├── hongkong.json
│   ├── landscapes.json
│   └── portraits.json
│
├── photos/                       ← ALL images flat (incl. .webp companions)
│   └── originals/                ← full-res backups (not served)
│
├── *.sh                          ← maintenance scripts (resize, webp, etc.)
├── *.py                          ← patchers (mobile nav, SEO, JSON-LD)
│
└── (favicon files, sitemap.xml, robots.txt, site.webmanifest, _headers*)
```

\* `_headers` is a leftover from the Netlify era. nginx does not read it, so it currently
has no effect on the live site. Caching rules now belong in the nginx config on the VPS.

## Standard workflows

### Local dev
```bash
cd ~/my-portfolio
python3 -m http.server 8000
# then visit http://localhost:8000/<page>.html
```

### Adding new photos
```bash
# 1. Drop photos into photos/
# 2. Run the all-in-one workflow:
./deploy-photos.sh
# 3. Edit the relevant data/<project>.json to add entries
# 4. Re-run dimensions:
python3 add_dimensions_to_json.py
# 5. Test locally, then deploy
```

### Deploying
Push to GitHub. Coolify watches the repo and auto-deploys on push. See `docs/07-deployment.md` for details.

## How the user prefers to work with you

- For **file changes**: produce the full file, present it as a download, they'll drop it into the folder replacing the old version.
- For **small one-line tweaks**: a single `sed` command they can paste is often quicker.
- For **multi-file refactors**: ask first whether they want a one-shot script (Python patcher) or individual edited files.
- **Always** test locally with `python3 -m http.server 8000` before declaring something done.
- **Never** invent values for `location` / `date` / `filmstock` in photo metadata. Only the user knows those.

## When you're stuck

In order:
1. Check `docs/05-bugs-and-solutions.md` — most symptoms are documented.
2. Check the browser console + Network tab — silent JSON parse errors and 404s on photos show up there.
3. Ask the user. They know things about their photos and life that aren't in the code.
