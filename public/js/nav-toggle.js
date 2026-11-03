(function () {
  "use strict";
  var btn = document.getElementById("nav-toggle");
  var nav = document.getElementById("site-nav");
  if (!btn || !nav) return;

  btn.addEventListener("click", function () {
    var open = nav.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });

  document.addEventListener("click", function (e) {
    if (!nav.contains(e.target) && e.target !== btn && nav.classList.contains("is-open")) {
      nav.classList.remove("is-open");
      btn.setAttribute("aria-expanded", "false");
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && nav.classList.contains("is-open")) {
      nav.classList.remove("is-open");
      btn.setAttribute("aria-expanded", "false");
      btn.focus();
    }
  });
})();
