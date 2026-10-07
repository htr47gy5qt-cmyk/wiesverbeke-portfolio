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

## Caching

**Done (2026-10-07).** Set in Coolify → application → General → **Custom Nginx Configuration**. That box was empty before (Coolify's built-in default was in use), so the config there is Coolify's generated default plus a `map` block and one `add_header Cache-Control $cache_control always;` line:

| Files | `Cache-Control` |
|---|---|
| `.woff2` fonts | `public, max-age=31536000, immutable` (1 year) |
| `.webp .jpg .jpeg .png .svg .ico` | `public, max-age=2592000` (30 days) |
| `.css .js` | `public, max-age=86400, must-revalidate` (1 day) |
| everything else (pages, JSON, sitemap) | `no-cache` (re-check every time; cheap 304) |

```nginx
map $uri $cache_control {
    default                                    "no-cache";
    ~*\.woff2$                                 "public, max-age=31536000, immutable";
    ~*\.(webp|jpg|jpeg|png|svg|ico)$           "public, max-age=2592000";
    ~*\.(css|js)$                              "public, max-age=86400, must-revalidate";
}

server {
    add_header Cache-Control $cache_control always;
    # ...then Coolify's default: location /, error_page 404 /404.html, error_page 50x
}
```

**Gotchas**
- Pasting a config in this box **replaces** Coolify's default entirely. Always start from "Generate Default Nginx Configuration" (it asks you to type the app name to confirm) and add to it.
- Rollback: empty the box, Save, Redeploy → back to Coolify's default.
- Verify with `curl -sI https://wiesverbeke.com/<path> | grep -i cache-control`.
- Photos cache for 30 days, so a replaced photo with the *same filename* can look stale for visitors. Rename it (`IMG_1234_v2.webp`) and update the JSON.
- CSS/JS have no version in their filenames, hence only 1 day.

The old Netlify-era `_headers` file was deleted from the repo on 2026-10-07 (nginx never read it).

## Replacing a photo with the same filename

Photos are cached for 30 days (see Caching above). A hard refresh usually fixes a stale photo for you, but other visitors may keep the old one. Most reliable:

1. Bump the filename (`IMG_1234.webp` → `IMG_1234_v2.webp`) and update the JSON. Most reliable.
2. Hard refresh (Cmd+Shift+R).

## Custom 404 page

**Done (2026-10-07).** `404.html` sits in project root. Coolify's default nginx config for static sites already contains `error_page 404 /404.html;`, so no manual nginx change was needed. Verified live: `wiesverbeke.com/nonsense` shows the page with a real 404 status. The page uses **root-relative** links (`/style.css`, `/work`) because it is served at whatever URL was missing — relative links would break at e.g. `/foo/bar`. It has `noindex`.

## Clean URLs (no `.html`)

The server already serves `/about` from `about.html`, and `/about.html` still works too. Since 2026-10-07 all internal links, canonical tags, `og:url`, JSON-LD and `sitemap.xml` use the extensionless form, so the address bar shows `/about`.

**Redirect done (2026-10-07).** nginx 301-redirects `/about.html` → `/about`, `/index.html` → `/`, and keeps any `?query`. Old links and Google results therefore land on the clean address in one hop. Verified with `curl -sI`.

The redirect lives in the same Custom Nginx Configuration box as the caching rules, inside `server { }`:

```nginx
absolute_redirect off;          # REQUIRED: without it Location is http://… (nginx sits behind a proxy), causing an extra hop
if ($request_uri ~ ^/index\.html(\?.*)?$) { return 301 /$1; }
if ($request_uri ~ ^/(.+)\.html(\?.*)?$)   { return 301 /$1$2; }
```

No loop: the internal `try_files $uri.html` step does not change `$request_uri`. Browsers cache 301s hard, so if this is ever changed, test with `curl`, not the browser.

## History

The site previously ran on **Netlify's free plan** (drag-and-drop deploys) and hit its 100GB/month bandwidth cap. A migration to **Cloudflare Pages** was planned but never executed — the site moved to the Hetzner VPS + Coolify instead, which is where it lives now. Any doc or comment still referring to Netlify, drag-and-drop deploys, or a pending Cloudflare migration is out of date.
