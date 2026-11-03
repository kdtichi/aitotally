(function () {
  "use strict";
  var KEY = "aitotally-fonts-optout";
  var btn = document.getElementById("fonts-optout-toggle");
  if (!btn) return;

  function isOptedOut() {
    try {
      return localStorage.getItem(KEY) === "1";
    } catch (e) {
      return false;
    }
  }

  function render() {
    btn.textContent = isOptedOut()
      ? "Turn Google Fonts back on"
      : "Turn off Google Fonts";
  }

  btn.addEventListener("click", function () {
    try {
      if (isOptedOut()) {
        localStorage.removeItem(KEY);
      } else {
        localStorage.setItem(KEY, "1");
      }
    } catch (e) {
      return;
    }
    location.reload();
  });

  render();
})();
