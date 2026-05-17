/**
 * nav.js
 * Mobile hamburger menu toggle. Included on every page.
 * Adds/removes the 'nav-open' class on <body> when the hamburger is tapped.
 * Also closes the menu when a link inside it is tapped, so navigating
 * to another page feels natural.
 */
(function () {
  "use strict";

  function init() {
    const toggle = document.querySelector(".nav__toggle");
    const menu   = document.querySelector(".nav__mobile");
    if (!toggle || !menu) return;

    function setOpen(open) {
      document.body.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    }

    toggle.addEventListener("click", function () {
      const isOpen = document.body.classList.contains("nav-open");
      setOpen(!isOpen);
    });

    // Tap a link → close menu (so the new page loads with menu closed)
    menu.querySelectorAll("a").forEach(a => {
      a.addEventListener("click", () => setOpen(false));
    });

    // Esc closes the menu (handy on tablets with keyboards)
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("nav-open")) {
        setOpen(false);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
