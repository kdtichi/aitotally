/* Open the answer a link points to (e.g. /brand/delta/#faq-what-are-delta-s-...)
   and bring it into view, on page load and when the hash changes. */
(function () {
  "use strict";
  function openTarget() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    var el = document.getElementById(id);
    if (!el || el.tagName !== "DETAILS") return;
    el.open = true;
    el.scrollIntoView({ block: "start" });
    var summary = el.querySelector("summary");
    if (summary) summary.focus({ preventScroll: true });
  }
  window.addEventListener("hashchange", openTarget);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", openTarget);
  } else {
    openTarget();
  }
})();
