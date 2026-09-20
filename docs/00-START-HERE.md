# 📍 Start Here — Handoff to Claude Code

You are picking up an existing project: **Wies Verbeke's photography portfolio website**. The user has been working on this for a while in claude.ai and is now switching to Claude Code for continued maintenance.

## How to use these docs

Read these files **in order**. They are designed to bring you fully up to speed in one pass.

| File | What's in it |
| --- | --- |
| `00-START-HERE.md` | This file. |
| `01-project-overview.md` | What the site is, tech stack, who it's for. |
| `02-file-structure.md` | Every file in `~/my-portfolio/` and what it does. |
| `03-stages-history.md` | Everything that's been built, in chronological stages. |
| `04-scripts-reference.md` | Every helper script (shell + Python), what it does, when to run it. |
| `05-bugs-and-solutions.md` | Bugs we hit, root causes, fixes. Read this — many of these will bite again if you don't know them. |
| `06-maintenance-workflow.md` | The day-to-day "I added new photos, now what?" workflow. |
| `07-deployment.md` | Hosting (Hetzner VPS + Coolify), DNS, deploy flow. |
| `08-todo-and-gotchas.md` | Open tasks + non-obvious quirks of the codebase. |

## Quick context

- **User**: Wies Verbeke. Amateur photographer. **Zero coding experience.** Treat every interaction accordingly — explain steps in plain English, no jargon dumps, give exact shell commands.
- **OS**: macOS (uses `sips` for image work). Project lives at `~/my-portfolio/`.
- **Tech**: Pure HTML/CSS/JS, no frameworks, no build step (in the bundler sense). Python scripts for one-off patches.
- **Live host**: self-managed Hetzner VPS in Helsinki (Ubuntu + nginx), deployed via Coolify. Domain at zone.eu. **Deploy = `git push`** — Coolify watches the repo and auto-deploys.
- **Local dev**: `cd ~/my-portfolio && python3 -m http.server 8000` then visit `http://localhost:8000/<page>.html`. **You cannot use `file://` URLs** because `script.js` uses `fetch()` for JSON gallery data — browsers block fetch over `file://`.

## Golden rules

1. **Filenames are sacred.** The user has carefully named every photo. Never rename. `FP4+` in filenames must be `%2B` in HTML/JSON paths.
2. **`data/*.json` is the source of truth** for what photos exist in each project gallery. Editing HTML to add photos is a regression — galleries are rendered from JSON.
3. **Idempotent scripts only.** Every Python patcher in the repo can be re-run safely. If you write a new one, follow that pattern (use sentinels).
4. **The server is case-sensitive.** `Photo.jpg` ≠ `photo.jpg`. Local Mac is case-insensitive, nginx on Linux is not. Mismatches break in production but work locally.
5. **The analog page is special.** It has its own self-contained `<style>` and `<script>` blocks and does NOT use the JSON pipeline. It also loads `style.css` for the shared mobile nav classes. Don't refactor it casually.
