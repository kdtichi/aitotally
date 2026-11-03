(function () {
  "use strict";
  var form = document.getElementById("search-form");
  if (!form) return;

  var input = document.getElementById("search-input");
  var results = document.getElementById("search-results");
  var indexEl = document.getElementById("brand-index");
  var index = [];
  try {
    index = JSON.parse(indexEl.textContent);
  } catch (e) {
    index = [];
  }

  var activeIndex = -1;

  // Subtle motion: focus the search bar shortly after load, desktop only,
  // so mobile visitors aren't ambushed by a keyboard popping up.
  if (window.matchMedia && window.matchMedia("(min-width: 720px)").matches) {
    window.requestAnimationFrame(function () {
      setTimeout(function () {
        input.focus({ preventScroll: true });
      }, 150);
    });
  }

  function normalize(s) {
    return s.toLowerCase().trim();
  }

  function matches(query) {
    var q = normalize(query);
    if (!q) return [];
    return index
      .filter(function (b) {
        if (normalize(b.name).indexOf(q) !== -1) return true;
        for (var i = 0; i < b.aliases.length; i++) {
          if (normalize(b.aliases[i]).indexOf(q) !== -1) return true;
        }
        return false;
      })
      .slice(0, 8);
  }

  function render(list) {
    results.innerHTML = "";
    activeIndex = -1;
    if (!list.length) {
      results.hidden = true;
      input.setAttribute("aria-expanded", "false");
      return;
    }
    list.forEach(function (b, i) {
      var a = document.createElement("a");
      a.href = "/brand/" + b.slug + "/";
      a.setAttribute("role", "option");
      a.id = "search-option-" + i;
      a.innerHTML =
        "<span>" + b.name + "</span><span class='cat-tag'>" + b.categoryLabel + "</span>";
      results.appendChild(a);
    });
    results.hidden = false;
    input.setAttribute("aria-expanded", "true");
  }

  input.addEventListener("input", function () {
    render(matches(input.value));
  });

  input.addEventListener("keydown", function (e) {
    var options = results.querySelectorAll("a");
    if (!options.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      activeIndex = Math.min(activeIndex + 1, options.length - 1);
      updateActive(options);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      activeIndex = Math.max(activeIndex - 1, 0);
      updateActive(options);
    } else if (e.key === "Escape") {
      results.hidden = true;
      input.setAttribute("aria-expanded", "false");
    }
  });

  function updateActive(options) {
    options.forEach(function (o, i) {
      o.classList.toggle("is-active", i === activeIndex);
    });
    if (activeIndex >= 0) {
      input.setAttribute("aria-activedescendant", options[activeIndex].id);
      options[activeIndex].scrollIntoView({ block: "nearest" });
    }
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var options = results.querySelectorAll("a");
    if (activeIndex >= 0 && options[activeIndex]) {
      window.location.href = options[activeIndex].href;
      return;
    }
    var list = matches(input.value);
    if (list.length) {
      window.location.href = "/brand/" + list[0].slug + "/";
    }
  });

  document.addEventListener("click", function (e) {
    if (!form.contains(e.target)) {
      results.hidden = true;
      input.setAttribute("aria-expanded", "false");
    }
  });

  input.addEventListener("focus", function () {
    if (input.value && results.children.length) results.hidden = false;
  });
})();
