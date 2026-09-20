# 01 — Project Overview

## What this is

A minimalist photography portfolio website for **Wies Verbeke**, an amateur film photographer based in Belgium. It showcases four project galleries (Street, Hong Kong, Landscapes, Portraits — six curated photos each) plus an experimental "analog" interactive page. The site is intentionally simple, hand-coded, and deployed as static files.

## Tech stack

- **HTML / CSS / vanilla JS** — no frameworks, no React, no bundler, no `npm`.
- **Python 3** — used only for one-off / maintenance scripts (HTML patchers, JSON extractors).
- **macOS `sips`** — used by the image-resize shell scripts. macOS-only.
- **`cwebp`** (Google) — used by the WebP conversion script. Install via `brew install webp`.
- **Hosting**: self-managed Hetzner VPS (Helsinki, Ubuntu + nginx), deployed through Coolify on `git push`. Domain registered via zone.eu.

There is **no `package.json`**, **no `node_modules`**, **no build step**. The site is exactly the files in `~/my-portfolio/`. Whatever is committed in that folder is what Coolify deploys.

## Design system

- **Fonts**:
  - *Cormorant Garamond* — display/italic serif (page titles, hero, lightbox metadata location).
  - *Jost* — UI sans (nav, body text, buttons).
  - Loaded from Google Fonts in every `<head>`.
- **Palette** (CSS custom properties in `style.css`):
  - `--cream: #f5f2ee` — page background.
  - `--ink: #151210` — near-black, body/headings.
  - `--gold: #b89d72` — accent (links, the Instagram icon).
  - `--ink-light: #4a4540` — secondary text.
- **Layout**:
  - Masonry galleries via CSS `column-count` (3 → 2 → 1 across breakpoints).
  - Breakpoints: **900px** (tablet), **768px** (small tablet), **480px** (phone).
  - Single-column mobile nav uses a hamburger menu with a fullscreen overlay.

## Galleries — how they work now

Each project gallery has **two parts**:
1. **`project-*.html`** — a thin shell containing the nav, page header, and an empty `<div class="gallery__grid" id="gallery-grid"></div>`. It also has the lightbox markup.
2. **`data/*.json`** — the actual list of photos with metadata (`file`, `alt`, `location`, `date`, `filmstock`, optional `width`/`height`).

`script.js` detects the page via `<body data-project="street|hongkong|landscapes">`, fetches the matching JSON, and renders the gallery into `#gallery-grid`. Then the existing scroll-fade and lightbox code runs on the freshly-rendered DOM.

**To add/remove/reorder photos**, the user edits the JSON file. No HTML editing needed.

The **analog page is the exception** — it has its own self-contained JS with a `PHOTOS` array baked into the file. To edit that page, edit `analog.html` directly.

## The user

- **Name**: Wies Verbeke.
- **Skill level**: Zero coding background. Has learned to run shell commands you give them, copy files in/out of folders, and edit JSON carefully.
- **Tone**: Be friendly, concrete, explicit about every step. Always give exact paths and exact commands. Don't assume they know what `cd` does — but at this point in the project they do. They've been using the terminal for months now.
- **Workflow they prefer**: You produce files in `/mnt/user-data/outputs/`, present them with `present_files`, and they drop them into `~/my-portfolio/` manually replacing the old versions.
- **Email**: `wiesverbeke-photo@proton.me` (was `wiesverbeke@icloud.com` — fully migrated).
- **Instagram**: `https://www.instagram.com/wiesverbeke/`.
