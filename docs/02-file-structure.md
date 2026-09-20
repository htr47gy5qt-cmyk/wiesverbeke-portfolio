# 02 — File Structure

Everything is rooted at `~/my-portfolio/`. The whole folder is what Coolify deploys — there is no "src/dist" split.

```
my-portfolio/
├── index.html              ← Home: white bg, one centered photo (IMG_3914.jpg)
├── work.html               ← Project landing: 4 cards (Street, HK, Landscapes, Portraits)
├── about.html              ← Bio + portrait (Trasher-cat-with-sunglasses.webp — placeholder)
├── analog.html             ← Experimental mouse-trail page (self-contained)
│
├── project-street.html     ← Empty shell, gallery rendered from data/street.json
├── project-hongkong.html   ← Empty shell, rendered from data/hongkong.json
├── project-landscapes.html ← Empty shell, rendered from data/landscapes.json
├── project-portraits.html  ← Empty shell, rendered from data/portraits.json
│
├── style.css               ← Single shared stylesheet for ALL pages
├── script.js               ← Vertical gallery + captions + lightbox + fade-in
├── nav.js                  ← Tiny script: mobile hamburger toggle (every page)
├── theme-toggle.js         ← Curtain dark/light mode toggle
│
├── data/
│   ├── street.json         ← 5 photos with metadata
│   ├── hongkong.json       ← 6 photos with metadata
│   ├── landscapes.json     ← 6 photos with metadata
│   └── portraits.json      ← 6 photos with metadata
│
├── photos/                 ← ALL images, flat, webp-only (108 tracked files)
│   └── originals/          ← Full-resolution source JPGs (gitignored, not served)
│
├── fonts/                  ← (Optional: if any custom fonts are self-hosted)
│
├── favicon.ico             ← Generated via realfavicongenerator.net
├── favicon.svg
├── favicon-96x96.png
├── apple-touch-icon.png
├── web-app-manifest-192x192.png
├── web-app-manifest-512x512.png
├── site.webmanifest
│
├── _headers                ← INERT: Netlify-era header rules, nginx ignores them
├── robots.txt              ← SEO crawl rules
├── sitemap.xml             ← SEO sitemap (regenerate when adding pages)
│
├── resize-photos.sh        ← KEEP: resize new photos to max 2400px @ 85%
├── check-photo-sizes.sh    ← KEEP: scan photos/ for >1.5MB outliers
├── convert-to-webp.sh      ← KEEP: generate .webp companions for new jpgs
├── deploy-photos.sh        ← KEEP: runs the four above in sequence
├── add_dimensions_to_json.py  ← KEEP: fills width/height in data/*.json
│
├── patch_mobile_nav.py     ← KEEP (rarely used): adds hamburger to new HTML
├── patch_seo.py            ← KEEP (rarely used): injects meta+OG+twitter+canonical
├── patch_seo_jsonld.py     ← KEEP (rarely used): injects JSON-LD structured data
│
└── (deleted, but historical)
    ├── extract_to_json.py  ← One-time: HTML photos → JSON. Done.
    ├── fix_nav_placement.py ← One-time: fixed hamburger placement bug. Done.
    ├── update_email.py     ← One-time: icloud → proton email swap. Done.
    └── lightbox-metadata.css ← Merged into style.css. Done.
```

## Naming conventions (memorize these)

- Photos live **flat** in `photos/` — no subfolders for project grouping. Project assignment lives in the JSON files.
- Spaces in filenames → replaced with `_`.
- `+` in filenames (e.g. `FP4+OM4`) → must be written as `%2B` in **HTML and JSON paths**. The file on disk keeps the literal `+`.
- `_2` suffix → variant version of a photo (e.g. `IMG_3088_2.jpg`).
- `_copy` suffix → film-strip-bordered thumbnail version, used as project cover photos (e.g. `50y-Jubileum-34_copy.jpg`).
- `originals/` → kept as untouched backups after `resize-photos.sh` runs. Gitignored, never deployed.

## Page → body class → JSON mapping

`script.js` uses `document.body.dataset.project` to pick the JSON:

| HTML file | `<body data-project="...">` | JSON file |
| --- | --- | --- |
| `project-street.html` | `street` | `data/street.json` |
| `project-hongkong.html` | `hongkong` | `data/hongkong.json` |
| `project-landscapes.html` | `landscapes` | `data/landscapes.json` |
| `project-portraits.html` | `portraits` | `data/portraits.json` |
| any other page | (no attribute) | script.js no-ops, just runs nav.js |

## JSON schema (each project file)

```json
{
  "id": "street",
  "title": "Street Photography",
  "eyebrow": "Series I",
  "cover": "photos/50y-Jubileum-34_copy.jpg",
  "photos": [
    {
      "file": "photos/IMG_3088_2.jpg",
      "alt": "Street scene in Antwerp",
      "location": "Antwerp",
      "date": "2024",
      "filmstock": "HP5+",
      "width": 2400,
      "height": 1600
    }
  ]
}
```

`width`/`height` are filled in by `add_dimensions_to_json.py` and used to reserve space (prevent layout shift).
