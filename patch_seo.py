#!/usr/bin/env python3
"""
patch_seo.py
------------
Injects SEO-related meta tags into every HTML page:
- <meta name="description">
- <meta name="author">
- <link rel="canonical">
- Open Graph tags (og:title, og:description, og:image, og:url, og:type)
- Twitter Card tags

Run from the project root:
    python3 patch_seo.py

Idempotent: pages already containing these tags are skipped.
"""

import glob
import os
import re

SITE_URL  = "https://wiesverbeke.com"   # no trailing slash
AUTHOR    = "Wies Verbeke"

PAGES = {
    "index.html": {
        "title": "Wies Verbeke — Film Photographer",
        "description": "Film photographer. Portfolio of street, landscape, and analog photography by Wies Verbeke.",
        "image": "/photos/IMG_3914.jpg",
        "path": "/",
    },
    "work.html": {
        "title": "Work — Wies Verbeke",
        "description": "Photography projects by film photographer Wies Verbeke: Street, Hong Kong on Film, and Landscapes.",
        "image": "/photos/50y-Jubileum-34_copy.jpg",
        "path": "/work.html",
    },
    "about.html": {
        "title": "About — Wies Verbeke",
        "description": "About Wies Verbeke, film photographer. Get in touch for collaborations and prints.",
        "image": "/photos/Trasher-cat-with-sunglasses.jpg",
        "path": "/about.html",
    },
    "analog.html": {
        "title": "Analog — Wies Verbeke",
        "description": "An experimental analog photography canvas. Move your cursor to discover film photographs by Wies Verbeke.",
        "image": "/photos/IMG_3914.jpg",
        "path": "/analog.html",
    },
    "project-street.html": {
        "title": "Street Photography — Wies Verbeke",
        "description": "Street photography on film by Wies Verbeke. Series I.",
        "image": "/photos/50y-Jubileum-34_copy.jpg",
        "path": "/project-street.html",
    },
    "project-hongkong.html": {
        "title": "Hong Kong on Film — Wies Verbeke",
        "description": "Hong Kong photographed on 35mm film by Wies Verbeke. Series II.",
        "image": "/photos/IMG_3066_2.jpg",
        "path": "/project-hongkong.html",
    },
    "project-landscapes.html": {
        "title": "Landscapes — Wies Verbeke",
        "description": "Film landscape photography by Wies Verbeke. Series III.",
        "image": "/photos/1758190450-25276400-2_copy.jpg",
        "path": "/project-landscapes.html",
    },
    "project-portraits.html": {
        "title": "Portraits — Wies Verbeke",
        "description": "Film portraits by Wies Verbeke. Series IV.",
        "image": "/photos/PLACEHOLDER.jpg",
        "path": "/project-portraits.html",
    },
}

SENTINEL = '<meta property="og:title"'


def build_meta_block(meta):
    full_url   = SITE_URL + meta["path"]
    image_url  = SITE_URL + meta["image"]
    title      = meta["title"].replace('"', '&quot;')
    desc       = meta["description"].replace('"', '&quot;')

    return f"""  <!-- ── SEO meta ── -->
  <meta name="description" content="{desc}" />
  <meta name="author" content="{AUTHOR}" />
  <link rel="canonical" href="{full_url}" />

  <!-- ── Open Graph (Facebook, LinkedIn, WhatsApp, iMessage) ── -->
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{image_url}" />
  <meta property="og:url" content="{full_url}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="{AUTHOR}" />

  <!-- ── Twitter Card ── -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{image_url}" />
"""


def patch_html(path, meta):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    if SENTINEL in html:
        print(f"  ⏭  {path} — already patched, skipped")
        return False

    block = build_meta_block(meta)
    new_html, n = re.subn(r"</head>", block + "</head>", html, count=1)
    if n != 1:
        print(f"  ⚠️  {path} — no </head> found, skipping")
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"  ✓ patched {path}")
    return True


def main():
    patched = 0
    skipped = 0
    for filename, meta in PAGES.items():
        if not os.path.exists(filename):
            print(f"  ⚠️  {filename} not found")
            continue
        if patch_html(filename, meta):
            patched += 1
        else:
            skipped += 1
    print(f"\nDone. Patched {patched}, skipped {skipped}.")


if __name__ == "__main__":
    main()
