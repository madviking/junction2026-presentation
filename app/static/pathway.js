// Routes into care: the pathway slide (/presentation/pathway, embedded in the deck).
// Data: content/data/pathway.json, embedded as #pathway-data. Draws the map nodes and the Silta bands, and shows
// a card over the map: at rest the takeaway, on click a step or a band. Charts named in a step's `charts` (rows of
// chart ids) are embedded as #pw-fig-<id> and drawn with Plotly in the data popup. The footer links open the
// <template id="pw-sec-*"> drill-downs (key findings, limitations) in the same popup.
// Two views share the map: "analysis" (gaps) and "impact" (costs, from D.impact). The view is set as data-mode
// on .silta-pw-page (CSS hides pw-for-* elements) and kept in the frame's URL as #impact.
(function () {
  var root = document.querySelector(".silta-pathway");
  if (!root) return;
  var D = JSON.parse(document.getElementById("pathway-data").textContent);
  var page = root.closest(".silta-pw-page") || root;
  var modeBtns = document.querySelectorAll("[data-pw-mode]");
  var mode = location.hash === "#impact" ? "impact" : "analysis";
  var NS = "http://www.w3.org/2000/svg";
  var svg = root.querySelector("svg.pw-routes");
  var pathsG = svg.querySelector(".pw-paths") || svg;
  var card = root.querySelector("[data-pw=panel]");
  var bandsEl = root.querySelector("[data-pw=bands]");
  var pop = document.getElementById("pw-pop"), popBody = root.querySelector("[data-pw=pop]"), popTitle = document.getElementById("pw-pop-title");
  var plotConfig = {displaylogo: false, responsive: true, displayModeBar: false};
  var sel = null, openBand = null;
  var bands = D.bands.map(function (b) { return Object.assign({}, b); });
  var nodeX = {};

  function esc(t) { var d = document.createElement("div"); d.textContent = t; return d.innerHTML; }
  function el(tag, attrs, parent) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; }
  function theme() { return document.documentElement.getAttribute("data-bs-theme") === "dark" ? "dark" : "light"; }
  function figure(id) { var f = document.getElementById("pw-fig-" + id); return f ? JSON.parse(f.textContent) : null; }

  var LINE = {
    lang: '<line x1="2" y1="4" x2="26" y2="4" class="pw-seg pw-lang"/>',
    other: '<line x1="3" y1="4" x2="25" y2="4" class="pw-seg pw-other"/>',
    none: '<line x1="3" y1="4" x2="25" y2="4" class="pw-seg pw-none"/>'
  };

  // Map nodes
  D.nodes.forEach(function (n) {
    if (!(n.id in nodeX)) nodeX[n.id] = n.x;
    var g = el("g", {"class": "pw-node pw-" + n.level, tabindex: "0", role: "button", "data-id": n.id,
      "aria-label": n.aria || n.label.join(" ")}, pathsG);
    el("circle", {"class": "pw-hit", cx: n.x, cy: n.y, r: 22}, g);
    el("circle", {"class": "pw-ring", cx: n.x, cy: n.y, r: 13}, g);
    el("circle", {"class": "pw-dot", cx: n.x, cy: n.y, r: 7}, g);
    n.label.forEach(function (line, i) {
      var left = n.x < 90;
      el("text", {x: left ? n.x - 12 : n.x, y: n.y + 28 + i * 16, "text-anchor": left ? "start" : "middle"}, g).textContent = line;
    });
    if (n.sub) el("text", {x: n.x, y: n.y + 26, "text-anchor": "middle", "class": "pw-sub"}, g).textContent = n.sub;
    var pick = function () { sel = sel === n.id ? null : n.id; openBand = null; render(); };
    g.addEventListener("click", pick);
    g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
  });

  // Silta bands on the map's x scale (viewBox 0–1000 → 0–100%), packed into as few rows as fit.
  var rowEnds = [];
  bands.slice().sort(function (a, b) { return a.x0 - b.x0; }).forEach(function (b) {
    var row = rowEnds.findIndex(function (end) { return end + 10 <= b.x0; });
    if (row < 0) { row = rowEnds.length; rowEnds.push(0); }
    rowEnds[row] = b.x1;
    b.row = row;
  });
  bandsEl.style.setProperty("--rows", rowEnds.length);
  bands.forEach(function (b) {
    var btn = document.createElement("button");
    btn.type = "button"; btn.className = "pw-sbar"; btn.textContent = b.name;
    btn.style.left = b.x0 / 10 + "%"; btn.style.width = (b.x1 - b.x0) / 10 + "%";
    btn.style.setProperty("--row", b.row);
    btn.setAttribute("aria-pressed", "false");
    btn.addEventListener("click", function () { openBand = openBand === b.id ? null : b.id; sel = null; render(); });
    bandsEl.appendChild(btn);
    b.btn = btn;
  });

  function table(t) {
    return "<table><thead><tr>" + t.head.map(function (h) { return "<th>" + esc(h) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      t.rows.map(function (r, i) {
        return "<tr" + (t.total && i === t.rows.length - 1 ? ' class="pw-total"' : "") + ">" +
          r.map(function (c) { return '<td class="' + (/^[−+]/.test(c) ? "pw-gapv" : "") + '">' + esc(c) + "</td>"; }).join("") + "</tr>";
      }).join("") + "</tbody></table>";
  }

  // Popup: a step's charts and tables, or one of the footer drill-downs
  function drawCharts() {
    if (!window.Plotly || !pop.open) return;
    popBody.querySelectorAll("[data-pw-chart]").forEach(function (c) {
      var f = figure(c.dataset.pwChart)[theme()];
      Plotly.react(c, f.data, f.layout, plotConfig);
    });
  }
  function openData(d) {
    var rows = (d.charts || []).map(function (row) {
      return '<div class="pw-chartrow">' + row.map(function (id) {
        var f = figure(id);
        if (!f) return "";
        return '<figure class="pw-chart"><figcaption><b>' + esc(f.title) + "</b><span>" + esc(f.subtitle) + '</span></figcaption><div data-pw-chart="' + id + '" style="min-height:' + f.height + 'px"></div></figure>';
      }).join("") + "</div>";
    }).join("");
    popTitle.textContent = d.title;
    popBody.innerHTML = rows + (d.tables || []).map(function (t) { return '<div class="pw-tscroll">' + table(t) + "</div>"; }).join("") +
      (d.notes || []).map(function (n) { return '<p class="pw-note">' + esc(n) + "</p>"; }).join("") +
      '<p class="pw-src">Source: ' + esc(d.src) + "</p>";
    pop.classList.toggle("pw-wide", !!rows);
    pop.showModal();
    drawCharts();
  }
  function openSection(name) {
    var tpl = document.getElementById("pw-sec-" + name);
    if (!tpl) return;
    popTitle.textContent = tpl.dataset.title;
    popBody.innerHTML = "";
    popBody.appendChild(tpl.content.cloneNode(true));
    pop.classList.add("pw-wide");
    pop.showModal();
  }
  document.querySelectorAll("[data-pw-open]").forEach(function (b) {
    b.addEventListener("click", function () { openSection(b.dataset.pwOpen); });
  });
  document.getElementById("pw-pop-close").addEventListener("click", function () { pop.close(); });
  pop.addEventListener("click", function (e) { if (e.target === pop) pop.close(); });
  document.addEventListener("silta:theme", drawCharts);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !pop.open && (sel || openBand)) { sel = null; openBand = null; render(); }
  });

  // View switch: Analysis / Impact
  function setMode(m, fromHash) {
    mode = m === "impact" ? "impact" : "analysis";
    page.setAttribute("data-mode", mode);
    modeBtns.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.pwMode === mode ? "true" : "false"); });
    if (!fromHash && window.history && history.replaceState) {
      history.replaceState(null, "", mode === "impact" ? "#impact" : location.pathname + location.search);
    }
    render();
  }
  modeBtns.forEach(function (b) { b.addEventListener("click", function () { setMode(b.dataset.pwMode); }); });
  window.addEventListener("hashchange", function () { setMode(location.hash === "#impact" ? "impact" : "analysis", true); });

  // The card over the map. It sits on the side away from what was clicked; at rest, bottom right.
  var CLOSE = '<button class="pw-x pw-over-x" type="button" aria-label="Close">×</button>';
  function show(html, where, cls) {
    card.className = "pw-over pw-at-" + where + (cls ? " " + cls : "");
    card.innerHTML = html;
    var x = card.querySelector(".pw-over-x");
    if (x) x.addEventListener("click", function () { sel = null; openBand = null; render(); });
  }
  function side(x) { return x < 500 ? "right" : "left"; }

  function stepCard() {
    var d = D.steps[sel];
    if (mode === "impact") {
      var c = D.impact.steps[sel];
      return '<span class="pw-tag pw-costtag">What it costs</span>' +
        (c ? "<h3>" + esc(c.title) + "</h3><p>" + esc(c.text) + '</p><p class="pw-src">Source: ' + esc(c.src) + "</p>"
           : "<h3>" + esc(d.title) + "</h3><p>" + esc(D.impact.missing) + "</p>");
    }
    var hasData = (d.tables && d.tables.length) || (d.charts && d.charts.length);
    return '<span class="pw-tag"><svg width="28" height="8" aria-hidden="true">' + LINE[d.level] + "</svg>" + esc(D.levels[d.level]) + "</span>" +
      "<h3>" + esc(d.title) + "</h3><p>" + esc(d.text) + '</p><p class="pw-src">Source: ' + esc(d.src) + "</p>" +
      (hasData ? '<button class="pw-more" type="button" aria-haspopup="dialog">Show data</button>' : "");
  }

  function render() {
    var band = bands.find(function (b) { return b.id === openBand; });
    var lit = sel ? [sel] : band ? band.steps : [];
    svg.classList.toggle("pw-focus", lit.length > 0);
    svg.querySelectorAll(".pw-node").forEach(function (g) {
      g.setAttribute("aria-pressed", g.dataset.id === sel ? "true" : "false");
      g.classList.toggle("pw-lit", lit.indexOf(g.dataset.id) > -1);
    });
    bands.forEach(function (b) {
      b.btn.classList.toggle("pw-on", sel ? b.steps.indexOf(sel) > -1 : b.id === openBand);
      b.btn.setAttribute("aria-pressed", b.id === openBand ? "true" : "false");
    });
    if (sel) {
      show(CLOSE + stepCard(), side(nodeX[sel]), mode === "impact" ? "pw-impact" : "");
      var more = card.querySelector(".pw-more");
      if (more) more.addEventListener("click", function () { openData(D.steps[sel]); });
    } else if (band) {
      show(CLOSE + '<span class="pw-tag pw-silta-tag">Where Silta helps</span><h3>' + esc(band.name) + "</h3><p>" + esc(band.text) + "</p>",
        side((band.x0 + band.x1) / 2));
    } else {
      // At rest: the prompt only. The analysis view's lede is the deck slide before this one (/presentation#/routes)
      // and stays in the "Limitations and sources" popup; the impact view keeps its own lede here.
      var lede = mode === "impact" ? "<p>" + esc(D.impact.lede) + "</p>" : "";
      show(lede + '<p class="pw-hint"><i></i>' + esc(mode === "impact" ? D.impact.prompt : D.page.prompt) +
        " Or select a Silta band.</p>", "rest");
    }
  }
  setMode(mode, true);

  // Arrival animation, about 2.5 s: draw the routes left to right, pop in the gap labels, then the
  // "Where Silta helps" bands and the prompt. In the deck the slide is in an iframe, so the deck says when:
  // {silta: "play"} when the slide is shown, {silta: "prime"} (hide, ready to play) when another slide is.
  // Standalone, it plays on load. Without messages (the PDF export) the diagram simply stays drawn.
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var silta = root.querySelector(".pw-silta");
  var anims = [], primeTimer = null;
  function stopAnims() { anims.forEach(function (a) { a.cancel(); }); anims = []; }
  function add(node, frames, opts) {
    var a = node.animate(frames, Object.assign({fill: "backwards", easing: "ease-out"}, opts));
    anims.push(a);
  }
  function prime() {
    clearTimeout(primeTimer);
    // Wait for the deck's fade out before hiding, so a slide being left does not blank mid-fade.
    primeTimer = setTimeout(function () { stopAnims(); page.classList.add("pw-primed"); }, 700);
  }
  function play() {
    clearTimeout(primeTimer);
    stopAnims();
    page.classList.remove("pw-primed");
    if (still) return;
    add(pathsG, [{clipPath: "inset(0 100% 0 0)"}, {clipPath: "inset(0 0 0 0)"}], {duration: 900, easing: "cubic-bezier(.4,0,.2,1)"});
    var pills = svg.querySelectorAll(".pw-for-" + mode + " > .pw-pill");
    pills.forEach(function (pill, i) {
      var m = /translate\(([-\d.]+)[ ,]+([-\d.]+)\)/.exec(pill.getAttribute("transform") || "");
      var at = m ? "translate(" + m[1] + "px, " + m[2] + "px)" : "";
      add(pill, [{opacity: 0, transform: at + " scale(.6)"}, {opacity: 1, transform: at + " scale(1)"}],
        {duration: 280, delay: 850 + i * 140, easing: "cubic-bezier(.3,1.4,.6,1)"});
    });
    var bandsAt = 850 + pills.length * 140 + 250;
    add(silta, [{opacity: 0}, {opacity: 1}], {duration: 250, delay: bandsAt});
    bands.forEach(function (b, i) {
      add(b.btn, [{opacity: 0, transform: "scaleX(.2)"}, {opacity: 1, transform: "scaleX(1)"}],
        {duration: 380, delay: bandsAt + 120 + i * 70, easing: "cubic-bezier(.4,0,.2,1)"});
    });
    add(card, [{opacity: 0}, {opacity: 1}], {duration: 300, delay: bandsAt + 200 + bands.length * 70});
  }
  if (window.parent !== window) {
    window.addEventListener("message", function (e) {
      if (e.origin !== location.origin || !e.data) return;
      if (e.data.silta === "play") play();
      else if (e.data.silta === "prime") prime();
    });
    window.parent.postMessage({silta: "ready?"}, location.origin);
  } else {
    play();
  }
})();
