/**
 * theme-toggle.js
 * Curtain dark/light mode toggle. Injected into every page via <script> tag.
 * Theme is applied early (anti-FOUC) by an inline script in each page's <head>;
 * this file handles the button UI and curtain animation only.
 */
(function () {
  "use strict";

  var DURATION  = 550;
  var EASING    = "cubic-bezier(0.76, 0, 0.24, 1)";
  var LIGHT_BG  = "#f5f2ee";
  var DARK_BG   = "#131210";

  function current() {
    return document.documentElement.classList.contains("dark") ? "dark" : "light";
  }

  var MOON_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  var SUN_SVG  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';

  function updateBtn(btn, theme) {
    btn.innerHTML = theme === "light" ? MOON_SVG : SUN_SVG;
    btn.setAttribute("aria-label",   theme === "light" ? "Switch to dark mode" : "Switch to light mode");
    btn.setAttribute("aria-pressed", theme === "dark"  ? "true" : "false");
  }

  function init() {
    // Curtain overlay — covers the page during the theme transition
    var curtain = document.createElement("div");
    curtain.setAttribute("aria-hidden", "true");
    curtain.style.cssText =
      "position:fixed;inset:0;z-index:9997;pointer-events:none;" +
      "transform:scaleY(0);transform-origin:top;";
    document.body.appendChild(curtain);

    // Toggle button — injected into the nav before the hamburger
    var btn = document.createElement("button");
    btn.className = "theme-toggle";
    updateBtn(btn, current());

    var nav = document.querySelector(".nav");
    if (nav) {
      var hamburger = nav.querySelector(".nav__toggle");
      hamburger ? nav.insertBefore(btn, hamburger) : nav.appendChild(btn);
    }

    var animating = false;

    btn.addEventListener("click", function () {
      if (animating) return;
      animating = true;

      var next = current() === "light" ? "dark" : "light";

      // Reset curtain silently, then trigger the fall
      curtain.style.background      = next === "dark" ? DARK_BG : LIGHT_BG;
      curtain.style.transition      = "none";
      curtain.style.transformOrigin = "top";
      curtain.style.transform       = "scaleY(0)";
      void curtain.offsetHeight; // force reflow before re-enabling transition

      curtain.style.transition = "transform " + DURATION + "ms " + EASING;
      curtain.style.transform  = "scaleY(1)";

      setTimeout(function () {
        // Mid-point: curtain fully covers the page — switch the theme
        document.documentElement.classList.toggle("dark", next === "dark");
        try { localStorage.setItem("theme", next); } catch (e) {}
        updateBtn(btn, next);

        // Rise from bottom
        curtain.style.transformOrigin = "bottom";
        curtain.style.transform       = "scaleY(0)";

        setTimeout(function () {
          curtain.style.transformOrigin = "top";
          animating = false;
        }, DURATION + 60);
      }, DURATION);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

}());
