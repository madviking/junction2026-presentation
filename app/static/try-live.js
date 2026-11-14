// Try page (templates/try.html): "Maximise for a demo" turns the live-app phone into a large
// overlay on a darkened page. Only classes and the --s scale change; the iframe stays where it
// is in the DOM, so the app keeps its state. Esc, the button or a click on the dark area closes it.
(function () {
  var live = document.querySelector(".silta-live");
  var toggle = live && live.querySelector("[data-live-toggle]");
  if (!toggle) return;
  var slot = live.parentElement;
  var label = toggle.querySelector("span");
  var icon = toggle.querySelector(".ti");
  var restLabel = label.textContent;

  // Fit the 390 x 835 app (plus screen margin, phone frame and caption) in the window.
  function fit() {
    var s = Math.min((window.innerHeight - 250) / 835, (window.innerWidth - 80) / 390, 1.25);
    live.style.setProperty("--s", Math.max(s, 0.5).toFixed(3));
  }

  function open() {
    // keep the hero's layout while the phone is out of the flow
    slot.style.width = slot.offsetWidth + "px";
    slot.style.height = slot.offsetHeight + "px";
    live.classList.add("is-max");
    document.body.classList.add("silta-live-open");
    fit();
    window.addEventListener("resize", fit);
    toggle.setAttribute("aria-pressed", "true");
    label.textContent = "Back to the page (Esc)";
    icon.className = "ti ti-arrows-minimize";
  }

  function close() {
    live.classList.remove("is-max");
    document.body.classList.remove("silta-live-open");
    live.style.removeProperty("--s");
    window.removeEventListener("resize", fit);
    slot.style.width = slot.style.height = "";
    toggle.setAttribute("aria-pressed", "false");
    label.textContent = restLabel;
    icon.className = "ti ti-arrows-maximize";
  }

  function isOpen() { return live.classList.contains("is-max"); }

  toggle.addEventListener("click", function () { isOpen() ? close() : open(); });
  live.addEventListener("click", function (e) { if (isOpen() && e.target === live) close(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && isOpen()) close(); });
})();
