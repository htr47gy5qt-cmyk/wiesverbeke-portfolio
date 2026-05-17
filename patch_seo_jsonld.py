#!/usr/bin/env python3
"""
patch_seo_jsonld.py
-------------------
Injects JSON-LD structured data into pages so search engines and AI
engines understand:
  - WHO you are (Person schema, on every page in <head>)
  - WHAT collection a project page represents (ImageGallery on projects)

Run AFTER patch_seo.py from the project root:
    python3 patch_seo_jsonld.py

Idempotent.
"""

import json
import os
import re

SITE_URL = "https://wiesverbeke.com"

PERSON = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Wies Verbeke",
    "jobTitle": "Film Photographer",
    "url": SITE_URL,
    "image": f"{SITE_URL}/photos/Trasher-cat-with-sunglasses.jpg",
    "email": "wiesverbeke-photo@proton.me",
    "sameAs": [
        "https://www.instagram.com/wiesverbeke/",
    ],
}

PAGES_PERSON = [
    "index.html",
    "work.html",
    "about.html",
    "analog.html",
    "project-street.html",
    "project-hongkong.html",
    "project-landscapes.html",
    "project-portraits.html",
]

PROJECT_PAGES = {
    "project-street.html": {
        "name": "Street Photography",
        "description": "Street photography on film by Wies Verbeke. Series I.",
        "path": "/project-street.html",
    },
    "project-hongkong.html": {
        "name": "Hong Kong on Film",
        "description": "Hong Kong photographed on 35mm film by Wies Verbeke. Series II.",
        "path": "/project-hongkong.html",
    },
    "project-landscapes.html": {
        "name": "Landscapes",
        "description": "Film landscape photography by Wies Verbeke. Series III.",
        "path": "/project-landscapes.html",
    },
    "project-portraits.html": {
        "name": "Portraits",
        "description": "Film portraits by Wies Verbeke. Series IV.",
        "path": "/project-portraits.html",
    },
}

PERSON_SENTINEL  = '"@type": "Person"'
GALLERY_SENTINEL = '"@type": "ImageGallery"'


def inject_jsonld(html, json_data, sentinel):
    if sentinel in html:
        return html, False
    block = (
        '  <script type="application/ld+json">\n'
        + json.dumps(json_data, indent=2, ensure_ascii=False)
        + "\n  </script>\n"
    )
    new_html, n = re.subn(r"</head>", block + "</head>", html, count=1)
    if n != 1:
        return html, False
    return new_html, True


def patch_person(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    new_html, changed = inject_jsonld(html, PERSON, PERSON_SENTINEL)
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"  ✓ Person → {path}")
    else:
        print(f"  ⏭  {path} — Person already present")


def patch_gallery(path, project):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    gallery = {
        "@context": "https://schema.org",
        "@type": "ImageGallery",
        "name": project["name"],
        "description": project["description"],
        "url": SITE_URL + project["path"],
        "author": {"@type": "Person", "name": "Wies Verbeke"},
    }
    new_html, changed = inject_jsonld(html, gallery, GALLERY_SENTINEL)
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"  ✓ ImageGallery → {path}")
    else:
        print(f"  ⏭  {path} — ImageGallery already present")


def main():
    print("Adding Person schema to every page:")
    for p in PAGES_PERSON:
        if os.path.exists(p):
            patch_person(p)
        else:
            print(f"  ⚠️  {p} not found")

    print("\nAdding ImageGallery schema to project pages:")
    for path, proj in PROJECT_PAGES.items():
        if os.path.exists(path):
            patch_gallery(path, proj)
        else:
            print(f"  ⚠️  {path} not found")

    print("\nDone.")


if __name__ == "__main__":
    main()
