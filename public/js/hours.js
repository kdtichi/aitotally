(function () {
  "use strict";
  var el = document.getElementById("hours-widget");
  if (!el) return;

  var tz = el.getAttribute("data-tz");
  var is247 = el.getAttribute("data-247") === "true";
  var start = el.getAttribute("data-start"); // "HH:MM" in brand tz
  var end = el.getAttribute("data-end"); // "HH:MM" in brand tz
  var days = el.getAttribute("data-days"); // "daily" | "weekdays"
  var valueEl = document.getElementById("hours-value");
  var statusEl = document.getElementById("hours-status");

  var WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  function wallTimeIn(tzName, date) {
    // Returns a Date whose LOCAL getters reflect the wall-clock time in tzName.
    return new Date(date.toLocaleString("en-US", { timeZone: tzName }));
  }

  function toMinutes(hhmm) {
    var parts = hhmm.split(":");
    return parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
  }

  function run() {
    var now = new Date();
    var brandNow = wallTimeIn(tz, now);

    if (is247) {
      valueEl.textContent = "Open 24 hours a day, every day";
      setStatus(true);
      return;
    }

    // Minutes since midnight, in the brand's own timezone, right now.
    var nowMin = brandNow.getHours() * 60 + brandNow.getMinutes() + brandNow.getSeconds() / 60;
    var sMin = toMinutes(start);
    var eMinRaw = toMinutes(end);
    var eMin = eMinRaw <= sMin ? eMinRaw + 1440 : eMinRaw;

    // Shift "now" by the wall-clock-minute delta to today's start/end, in the
    // brand's own timezone. Since this instant and "now" share the same
    // timezone, the shift is valid without ever computing a UTC offset —
    // toLocaleTimeString() below then renders it in the *visitor's* timezone.
    var startInstant = new Date(now.getTime() + (sMin - nowMin) * 60000);
    var endInstant = new Date(now.getTime() + (eMin - nowMin) * 60000);

    var fmt = { hour: "numeric", minute: "2-digit" };
    var startLocal = startInstant.toLocaleTimeString([], fmt);
    var endLocal = endInstant.toLocaleTimeString([], fmt);
    var tzName = endInstant
      .toLocaleTimeString([], { timeZoneName: "short" })
      .split(" ")
      .pop();

    var dayText = days === "weekdays" ? "Mon–Fri" : "Every day";
    valueEl.textContent = startLocal + "–" + endLocal + " " + tzName + " · " + dayText;

    // Open/closed check, evaluated in the brand's own timezone.
    var withinWindow;
    if (eMinRaw <= sMin) {
      withinWindow = nowMin >= sMin || nowMin < eMinRaw;
    } else {
      withinWindow = nowMin >= sMin && nowMin < eMinRaw;
    }

    var dow = WEEKDAYS[brandNow.getDay()];
    var isWeekday = dow !== "Sun" && dow !== "Sat";
    var dayOk = days === "weekdays" ? isWeekday : true;

    setStatus(withinWindow && dayOk);
  }

  function setStatus(isOpen) {
    if (!statusEl) return;
    statusEl.textContent = isOpen ? "Open now" : "Closed now";
    statusEl.classList.toggle("is-open", isOpen);
    statusEl.classList.toggle("is-closed", !isOpen);
    statusEl.hidden = false;
  }

  try {
    run();
  } catch (e) {
    // Fall back silently to the server-rendered hours text already in the DOM.
  }
})();
