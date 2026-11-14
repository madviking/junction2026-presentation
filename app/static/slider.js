// Phone slider (templates/_slider.html): native horizontal scroll-snap; buttons, dots and
// arrow keys move it. Advances by itself every 5 s until the visitor touches it; never with
// reduced motion.
(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll(".silta-slider").forEach(function (slider) {
    var track = slider.querySelector(".silta-slider-track");
    var slides = slider.querySelectorAll(".silta-slide");
    var dots = slider.querySelectorAll(".silta-slider-dots button");
    var caption = slider.querySelector(".silta-slider-caption");
    var current = 0;
    var timer = null;

    function go(i, smooth) {
      current = (i + slides.length) % slides.length;
      track.scrollTo({ left: current * track.clientWidth, behavior: smooth && !reduce ? "smooth" : "auto" });
    }
    function show(i) {
      if (!slides[i]) return;
      current = i;
      caption.textContent = slides[i].dataset.caption;
      dots.forEach(function (d, n) {
        if (n === i) d.setAttribute("aria-current", "true");
        else d.removeAttribute("aria-current");
      });
    }
    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
    }

    track.addEventListener("scroll", function () {
      show(Math.round(track.scrollLeft / track.clientWidth));
    }, { passive: true });
    slider.addEventListener("click", function (e) {
      var b = e.target.closest("[data-slider]");
      if (!b) return;
      stop();
      var v = b.dataset.slider;
      go(v === "prev" ? current - 1 : v === "next" ? current + 1 : Number(v), true);
    });
    track.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      e.preventDefault();
      stop();
      go(current + (e.key === "ArrowRight" ? 1 : -1), true);
    });
    ["pointerdown", "wheel", "focusin"].forEach(function (ev) {
      slider.addEventListener(ev, stop, { passive: true });
    });
    if (!reduce && slides.length > 1) timer = setInterval(function () { go(current + 1, true); }, 5000);
  });
})();
