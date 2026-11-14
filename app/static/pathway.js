// Pathway timeline on /pathway. Data: content/data/pathway.json, embedded as #pathway-data.
// Charts named in a step's `charts` are embedded as #pw-fig-<id> and drawn with Plotly when the step is selected.
// Steps are columns, language groups are lanes, and the node shape shows the evidence level.
(function () {
  var root = document.querySelector(".silta-pathway");
  if (!root) return;
  var D = JSON.parse(document.getElementById("pathway-data").textContent);
  var prog = "colorectal", sel = "attended";
  var main = root.querySelector("[data-pw=main]"), sym = root.querySelector("[data-pw=sym]");
  var problem = root.querySelector("[data-pw=problem]"), solve = root.querySelector("[data-pw=solve]");
  var chartsBox = root.querySelector("[data-pw=charts]");
  var plotConfig = {displaylogo: false, responsive: true, displayModeBar: false};

  function theme() { return document.documentElement.getAttribute("data-bs-theme") === "dark" ? "dark" : "light"; }
  function figure(id) { var el = document.getElementById("pw-fig-" + id); return el ? JSON.parse(el.textContent) : null; }
  function drawCharts() {
    if (!chartsBox || !window.Plotly) return;
    chartsBox.querySelectorAll("[data-pw-chart]").forEach(function (el) {
      var f = figure(el.dataset.pwChart)[theme()];
      Plotly.react(el, f.data, f.layout, plotConfig);
    });
  }
  function renderCharts(ids) {
    if (!chartsBox) return;
    var figs = (ids || []).map(function (id) { return [id, figure(id)]; }).filter(function (x) { return x[1]; });
    chartsBox.hidden = !figs.length;
    chartsBox.innerHTML = figs.map(function (x) {
      return '<figure class="pw-chart"><figcaption><b>' + esc(x[1].title) + "</b><span>" + esc(x[1].subtitle) + '</span></figcaption><div data-pw-chart="' + x[0] + '" style="min-height:' + x[1].height + 'px"></div><p class="pw-src">Source: ' + esc(x[1].source) + "</p></figure>";
    }).join("");
    drawCharts();
  }
  document.addEventListener("silta:theme", drawCharts);

  function neg(v) { return (v < 0 ? "−" : "+") + Math.abs(v).toFixed(1); }
  function esc(t) { var d = document.createElement("div"); d.textContent = t; return d.innerHTML; }

  function renderTimeline() {
    var steps = D.programmes[prog].steps;
    var h = '<div class="pw-lanes"><div class="pw-lane-hd">Step</div><div><i class="pw-k pw-a"></i>Finnish, Swedish or Sámi</div><div></div><div><i class="pw-k pw-b"></i>Other native language</div></div>';
    D.steps.forEach(function (s, i) {
      var d = steps[s.id];
      var cls = "pw-col" + (i === 0 ? " pw-first" : "") + (i === D.steps.length - 1 ? " pw-last" : "");
      var tg = (s.tgt || []).map(function (t) { return '<span class="pw-tgt">' + t + "</span>"; }).join("");
      var hd = '<div class="pw-hd"><span class="pw-sn">' + s.n + '</span><span class="pw-sl">' + s.label + "</span>" + tg + "</div>";
      var body;
      if (d.level === "lang") {
        var pill = d.gapPill ? '<span class="pw-pill ' + (d.gapPill[1] ? "pw-sig" : "pw-ns") + '">' + neg(d.gapPill[0]) + " pp" + (d.note ? "<br>" + d.note : "") + "</span>" : "";
        body = '<div class="pw-lane pw-a"><span class="pw-dot">' + d.a + '</span></div><div class="pw-gap">' + pill + '</div><div class="pw-lane pw-b"><span class="pw-dot">' + d.b + "</span></div>";
      } else {
        body = '<div class="pw-lane pw-dash"></div><div class="pw-gap"></div><div class="pw-lane pw-dash"></div><div class="pw-solo"><span class="pw-mk pw-' + d.level + '"></span><small>' + d.solo + "</small></div>";
      }
      h += '<button type="button" class="' + cls + '" data-s="' + s.id + '" aria-pressed="' + (sel === s.id) + '" aria-label="' + esc(s.label) + ": " + esc(D.levels[d.level]) + '">' + hd + body + "</button>";
    });
    main.innerHTML = h;

    var g = '<div class="pw-lanes"><div class="pw-lane-hd">Step</div><div>Anyone</div><div></div></div>';
    D.symptom_steps.forEach(function (s, i) {
      var d = D.symptom[s.id];
      g += '<button type="button" class="pw-col' + (i === 0 ? " pw-first" : "") + '" data-s="' + s.id + '" aria-pressed="' + (sel === s.id) + '" aria-label="' + esc(s.label) + ": " + esc(D.levels[d.level]) + '"><div class="pw-hd"><span class="pw-sn">' + s.n + '</span><span class="pw-sl">' + s.label + '</span></div><div class="pw-lane pw-dash"><span class="pw-mk pw-' + d.level + '"></span></div><div class="pw-cap">' + d.solo + "</div></button>";
    });
    g += '<div class="pw-join"><div></div><div class="pw-lane pw-dash"><span>→ joins at step 4, diagnostic exam</span></div><div></div></div>';
    sym.innerHTML = g;

    root.querySelectorAll(".pw-col").forEach(function (b) {
      b.addEventListener("click", function () { sel = b.dataset.s; render(); });
    });
  }

  function renderDetail() {
    var isSym = sel.charAt(0) === "s";
    var meta = (isSym ? D.symptom_steps : D.steps).filter(function (s) { return s.id === sel; })[0];
    var d = isSym ? D.symptom[sel] : D.programmes[prog].steps[sel];
    var scope = isSym ? "Symptom route" : D.programmes[prog].name + " screening";
    var who = "";
    if (d.who) {
      var r = D.programmes[prog].region;
      who = '<div class="pw-who"><h4>Who is most affected · attendance by region of birth</h4>' + D.regions.map(function (n, i) {
        return '<div class="pw-wrow"><span>' + n + '</span><span class="pw-wtrack"><span class="pw-wfill' + (i === 0 ? " pw-ref" : i === 4 ? " pw-low" : "") + '" style="width:' + r[i] + '%"></span></span><span class="pw-v">' + r[i].toFixed(1) + "%</span></div>";
      }).join("") + '<p class="pw-wnote">' + D.programmes[prog].who_note + "</p></div>";
    }
    var big = d.big ? '<div class="pw-big">' + d.big.map(function (b) { return '<div class="' + (b[2] ? "pw-" + b[2] : "") + '"><b>' + b[0] + "</b><span>" + b[1] + "</span></div>"; }).join("") + "</div>" : "";
    problem.innerHTML =
      '<div class="pw-ph"><span class="pw-eyebrow">' + scope + " · step " + meta.n + ": " + meta.label + '</span><span class="pw-chip"><i class="pw-k pw-' + d.level + '"></i>' + D.levels[d.level] + "</span></div>" +
      "<h3>" + d.title + "</h3>" + big + '<p class="pw-finding">' + d.finding + "</p>" +
      (d.why ? '<p class="pw-why">' + d.why + "</p>" : "") + who +
      '<p class="pw-src">Source: ' + d.src + "</p>";
    solve.innerHTML =
      '<span class="pw-eyebrow">Solving</span>' +
      '<div class="pw-blk"><h4>What Silta does</h4><p>' + d.silta + "</p></div>" +
      '<div class="pw-blk"><h4>What the county can do</h4><ul>' + d.county.map(function (x) { return "<li>" + x + "</li>"; }).join("") + "</ul></div>" +
      '<div class="pw-blk"><h4>How the county measures it</h4><p>' + d.measure + "</p></div>" +
      '<p class="pw-cost">Cost estimate: to be added, using THL national unit costs 2023–24.</p>';
    renderCharts(d.charts);
  }

  function render() {
    root.querySelectorAll("[data-p]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.p === prog); });
    renderTimeline();
    renderDetail();
  }
  root.querySelectorAll("[data-p]").forEach(function (b) {
    b.addEventListener("click", function () { prog = b.dataset.p; render(); });
  });
  render();
})();
