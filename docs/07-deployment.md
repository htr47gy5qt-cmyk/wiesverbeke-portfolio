# 07 — Deployment

## Current state

- **Host**: self-managed **Hetzner VPS in Helsinki** (Ubuntu), with **Coolify** as the deployment interface.
- **Web server**: nginx (confirmed live: `server: nginx/1.31.3`).
- **Domain**: `wiesverbeke.com`, registered at **zone.eu**.
- **DNS**: A record at zone.eu → `89.167.57.164`. `www` resolves to the same address.
- **SSL**: Let's Encrypt, provisioned and renewed by Coolify. HTTP/2 and HTTP/3 (`alt-svc: h3`) are both live.
- **Deploy method**: **push to GitHub → Coolify watches the repo and auto-deploys.** There is no drag-and-drop step and no build step — whatever is committed is what gets served.

## Deploying

```bash
cd ~/my-portfolio
git add -A
git commit -m "describe what changed"
git push
```

Coolify picks up the push and redeploys within a minute or so. Confirm at https://wiesverbeke.com — a hard refresh (Cmd+Shift+R) rules out browser cache.

**Consequence of this flow:** anything not committed does not exist on the live site. Photos in `photos/` must be committed like any other file. Anything listed in `.gitignore` (`photos-unused/`, `photos/originals/`) is never deployed.

## Deploy checklist (every time)

1. ✅ All photos referenced in `data/*.json` exist in `photos/`.
2. ✅ `python3 add_dimensions_to_json.py` ran cleanly (no warnings about missing files).
3. ✅ `./check-photo-sizes.sh` reports no oversized files.
4. ✅ Tested locally: `python3 -m http.server 8000`, clicked through every project page + lightbox + analog.
5. ✅ Tested mobile view (DevTools device emulation, narrow to 380px).
6. ✅ Hamburger menu opens/closes on every page (including analog).
7. ✅ No console errors.
8. ✅ If photos were added, ran `./convert-to-webp.sh` so `.webp` companions exist.
9. ✅ `git status` shows nothing unexpectedly untracked.

## Rolling back

Two options:

1. **Coolify** keeps a deployment history — redeploy a previous one from its dashboard.
2. **Git** — `git revert <hash>` then push. This is the safer one, because it keeps the repo and the live site in agreement. Coolify always deploys the latest commit, so a dashboard-only rollback will be undone by the next push.

## Caching — currently unconfigured

The `_headers` file in project root is a **Netlify-era leftover**. nginx does not read it, so its rules have no effect. Live responses carry `etag` and `last-modified` (so browsers revalidate) but **no `cache-control`**, which means photos are revalidated on every visit rather than cached hard.

If this ever matters for performance, the fix is in the nginx config on the VPS (or Coolify's per-service headers), not in `_headers`:

```nginx
location ~* \.(webp|jpg|png|woff2)$ { add_header Cache-Control "public, max-age=31536000, immutable"; }
location ~* \.html$              { add_header Cache-Control "no-cache"; }
```

`_headers` is kept in the repo for now as documentation of the intended policy. It is harmless but inert.

## Replacing a photo with the same filename

Because there is no long cache today, a hard refresh is normally enough. If a stale photo persists:

1. Bump the filename (`IMG_1234.webp` → `IMG_1234_v2.webp`) and update the JSON. Most reliable.
2. Hard refresh (Cmd+Shift+R).

## Custom 404 page

**Done (2026-10-07).** `404.html` sits in project root and nginx points at it with `error_page 404 /404.html;` (set in Coolify). Verified live: `wiesverbeke.com/nonsense` shows the page with a real 404 status. The page uses **root-relative** links (`/style.css`, `/work`) because it is served at whatever URL was missing — relative links would break at e.g. `/foo/bar`. It has `noindex`.

## Clean URLs (no `.html`)

The server already serves `/about` from `about.html`, and `/about.html` still works too. Since 2026-10-07 all internal links, canonical tags, `og:url`, JSON-LD and `sitemap.xml` use the extensionless form, so the address bar shows `/about`.

**Not done (optional):** a 301 redirect from `/about.html` → `/about` in nginx. Without it both addresses load the same page. If added, test carefully for redirect loops.

## History

The site previously ran on **Netlify's free plan** (drag-and-drop deploys) and hit its 100GB/month bandwidth cap. A migration to **Cloudflare Pages** was planned but never executed — the site moved to the Hetzner VPS + Coolify instead, which is where it lives now. Any doc or comment still referring to Netlify, drag-and-drop deploys, or a pending Cloudflare migration is out of date.
