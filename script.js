/**
 * script.js
 * 1. Render the gallery from a JSON data file (if on a project page)
 * 2. Scroll fade-in for gallery images
 * 3. Lightbox — click to enlarge, arrow keys / buttons to navigate, Esc to close
 *    + metadata display (location, date, filmstock)
 *
 * Project pages now declare which JSON to load via:
 *     <body class="page-project" data-project="street">
 * and contain an empty <div id="gallery-grid"></div>.
 */

(function () {
  "use strict";

  /* ── GALLERY RENDER (from JSON) ── */
  async function renderGallery() {
    const body = document.body;
    const projectId = body.dataset.project;
    const grid = document.getElementById("gallery-grid");

    // Not a project page (or grid is missing) → nothing to render.
    if (!projectId || !grid) return;

    try {
      const res = await fetch(`data/${projectId}.json`, { cache: "no-cache" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // Sync the header text with the JSON, so the JSON is the single
      // source of truth (the HTML values act as a fallback if JS fails).
      const titleEl   = document.getElementById("project-title");
      const eyebrowEl = document.getElementById("project-eyebrow");
      if (titleEl   && data.title)   titleEl.textContent   = data.title;
      if (eyebrowEl && data.eyebrow) eyebrowEl.textContent = data.eyebrow;

      // Build all figures
      const frag = document.createDocumentFragment();
      (data.photos || []).forEach(photo => {
        const fig = document.createElement("figure");
        fig.className = "gallery__item";
        fig.dataset.src = photo.src;
        if (photo.location)  fig.dataset.location  = photo.location;
        if (photo.date)      fig.dataset.date      = photo.date;
        if (photo.filmstock) fig.dataset.filmstock = photo.filmstock;

        // <picture> with WebP source + JPG fallback.
        // Derive .webp path by swapping the extension of the .jpg src.
        const webpSrc = photo.src.replace(/\.(jpe?g|png)$/i, ".webp");

        const picture = document.createElement("picture");
        const source  = document.createElement("source");
        source.srcset = webpSrc;
        source.type   = "image/webp";
        picture.appendChild(source);

        const img = document.createElement("img");
        img.src = photo.src;
        // Build a rich alt text from JSON metadata, for accessibility + image search.
        // Falls back to the JSON 'alt' field if no metadata is present.
        const altParts = [];
        if (photo.alt)       altParts.push(photo.alt);
        if (photo.location)  altParts.push(photo.location);
        if (photo.date)      altParts.push(photo.date);
        if (photo.filmstock) altParts.push("shot on " + photo.filmstock);
        img.alt = altParts.length ? altParts.join(" — ") : "Photograph by Wies Verbeke";
        img.loading  = "lazy";
        img.decoding = "async";

        // Explicit dimensions prevent layout shift while the photo loads.
        if (photo.width && photo.height) {
          img.width  = photo.width;
          img.height = photo.height;
        }

        picture.appendChild(img);
        fig.appendChild(picture);
        frag.appendChild(fig);
      });
      grid.appendChild(frag);
    } catch (err) {
      console.error(`Failed to load gallery for "${projectId}":`, err);
      grid.innerHTML =
        '<p style="padding:2rem;color:var(--ink-light);font-family:var(--font-display);font-style:italic;">' +
        "Sorry — the gallery couldn't be loaded.</p>";
    }
  }

  /* ── SCROLL FADE-IN ── */
  const STAGGER_MS = 80;

  function initFade() {
    const images = document.querySelectorAll(".gallery__item img");
    if (!images.length) return;

    if (!("IntersectionObserver" in window)) {
      images.forEach(img => img.classList.add("is-visible"));
      return;
    }

    const observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const pending = Array.from(document.querySelectorAll(".fade-target:not(.is-visible)"));
        const delay = Math.min(pending.indexOf(el), 6) * STAGGER_MS;
        setTimeout(() => el.classList.add("is-visible"), delay);
        obs.unobserve(el);
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -30px 0px" });

    images.forEach(function (img) {
      img.classList.add("fade-target");
      if (img.complete) { observer.observe(img); }
      else { img.addEventListener("load", () => observer.observe(img), { once: true }); }
    });
  }

  /* ── LIGHTBOX ── */
  function initLightbox() {
    const lb         = document.getElementById("lightbox");
    const lbImg      = document.getElementById("lb-img");
    const lbClose    = document.getElementById("lb-close");
    const lbPrev     = document.getElementById("lb-prev");
    const lbNext     = document.getElementById("lb-next");
    const lbLocation = document.getElementById("lb-location");
    const lbDate     = document.getElementById("lb-date");
    const lbFilm     = document.getElementById("lb-filmstock");
    const lbSep1     = document.getElementById("lb-sep-1");
    const lbSep2     = document.getElementById("lb-sep-2");

    if (!lb) return;

    // Feature-detect WebP support so we can use the smaller file in the lightbox too
    const supportsWebP = (function () {
      const el = document.createElement("canvas");
      if (!(el.getContext && el.getContext("2d"))) return false;
      return el.toDataURL("image/webp").indexOf("data:image/webp") === 0;
    })();

    function lightboxSrc(jpgPath) {
      if (!supportsWebP) return jpgPath;
      return jpgPath.replace(/\.(jpe?g|png)$/i, ".webp");
    }

    const items = Array.from(document.querySelectorAll(".gallery__item[data-src]"));
    if (!items.length) return;
    let current = 0;

    function open(index) {
      current = index;
      const fig = items[current];

      lbImg.src = lightboxSrc(fig.dataset.src);
      lbImg.alt = fig.querySelector("img")?.alt || "";

      const loc  = fig.dataset.location  || "";
      const date = fig.dataset.date      || "";
      const film = fig.dataset.filmstock || "";

      if (lbLocation) {
        lbLocation.textContent = loc;
        lbLocation.style.display = loc ? "" : "none";
      }
      if (lbDate) {
        lbDate.textContent = date;
        lbDate.style.display = date ? "" : "none";
      }
      if (lbFilm) {
        lbFilm.textContent = film;
        lbFilm.style.display = film ? "" : "none";
      }
      // Hide separators when adjacent fields are empty
      if (lbSep1) lbSep1.style.display = (loc && date) ? "" : "none";
      if (lbSep2) lbSep2.style.display = (date && film) || (loc && film && !date) ? "" : "none";

      lb.classList.add("is-open");
      document.body.style.overflow = "hidden";
      lbClose.focus();
    }

    function close() {
      lb.classList.remove("is-open");
      document.body.style.overflow = "";
      lbImg.src = "";
    }

    function prev() { open((current - 1 + items.length) % items.length); }
    function next() { open((current + 1) % items.length); }

    items.forEach((fig, i) => fig.addEventListener("click", () => open(i)));
    lbClose.addEventListener("click", close);
    lbPrev.addEventListener("click", prev);
    lbNext.addEventListener("click", next);

    lb.addEventListener("click", function (e) {
      if (e.target === lb || e.target === lb.querySelector(".lightbox__stage")) close();
    });

    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("is-open")) return;
      if (e.key === "Escape")     close();
      if (e.key === "ArrowLeft")  prev();
      if (e.key === "ArrowRight") next();
    });

    /* ── SWIPE (touch) ── */
    let touchStartX = 0;
    let touchStartY = 0;

    lb.addEventListener("touchstart", function (e) {
      touchStartX = e.changedTouches[0].clientX;
      touchStartY = e.changedTouches[0].clientY;
    }, { passive: true });

    lb.addEventListener("touchend", function (e) {
      if (!lb.classList.contains("is-open")) return;
      const dx = e.changedTouches[0].clientX - touchStartX;
      const dy = e.changedTouches[0].clientY - touchStartY;
      // Only trigger if horizontal swipe dominates (not an accidental scroll)
      if (Math.abs(dx) < 40 || Math.abs(dx) < Math.abs(dy)) return;
      if (dx < 0) next();
      else        prev();
    }, { passive: true });
  }

  async function init() {
    // 1. Render first (if we're on a project page), then wire up the rest.
    await renderGallery();
    // 2. Now the DOM has the figures, so fade-in + lightbox can bind to them.
    initFade();
    initLightbox();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})();
