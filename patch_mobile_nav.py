#!/usr/bin/env python3
"""
patch_mobile_nav.py
-------------------
One-time patch script. Adds the mobile hamburger menu to every HTML page
in the project root, and includes nav.js before the closing </body>.

Run from the project root:
    python3 patch_mobile_nav.py

Idempotent: running it twice is safe — it detects pages that are already
patched and skips them.
"""

import glob
import os
import re

# HTML files to patch
HTML_PATTERN = "*.html"

# The mobile-nav block to inject right after the existing </nav>
MOBILE_NAV_BLOCK = """
  <!-- ── HAMBURGER (mobile only, shown via CSS) ── -->
  <button class="nav__toggle" id="nav-toggle" aria-label="Open menu" aria-expanded="false">
    <span class="nav__toggle-bar"></span>
    <span class="nav__toggle-bar"></span>
    <span class="nav__toggle-bar"></span>
  </button>

  <!-- ── MOBILE FULL-SCREEN MENU ── -->
  <div class="nav__mobile" id="nav-mobile">
    <a href="work.html">Work</a>
    <a href="analog.html">Analog</a>
    <a href="about.html">About</a>
  </div>
"""

NAV_JS_TAG = '<script src="nav.js"></script>'

# Sentinels — used to detect "already patched"
NAV_SENTINEL  = 'class="nav__toggle"'
JS_SENTINEL   = 'nav.js'


def patch_html(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    changed = False

    # 1. Inject mobile nav block after the closing </nav>
    if NAV_SENTINEL not in html:
        new_html, n = re.subn(r"</nav>", "</nav>\n" + MOBILE_NAV_BLOCK, html, count=1)
        if n == 1:
            html = new_html
            changed = True
        else:
            print(f"  ⚠️  {path}: no </nav> tag found — manual edit needed")

    # 2. Insert nav.js before </body> (after other <script> tags if present)
    if JS_SENTINEL not in html:
        # Try to insert before </body>
        new_html, n = re.subn(
            r"</body>",
            f"  {NAV_JS_TAG}\n</body>",
            html,
            count=1,
        )
        if n == 1:
            html = new_html
            changed = True
        else:
            print(f"  ⚠️  {path}: no </body> tag found — manual edit needed")

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ patched {path}")
    else:
        print(f"  ⏭  {path} — already patched, skipped")


def main():
    files = sorted(glob.glob(HTML_PATTERN))
    if not files:
        print("❌  No HTML files found. Run from the project root.")
        return
    print(f"Patching {len(files)} HTML files …")
    for f in files:
        patch_html(f)
    print("\nDone. Now make sure style.css and nav.js are also updated.")


if __name__ == "__main__":
    main()
