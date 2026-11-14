// Routes into care on /pathway. Data: content/data/pathway.json, embedded as #pathway-data.
// Draws the map nodes, the Silta bands, the info panel and the data popup. Charts named in a
// step's `charts` (rows of chart ids) are embedded as #pw-fig-<id> and drawn with Plotly in the popup.
(function () {
  var root = document.querySelector(".silta-pathway");
  if (!root) return;
  var D = JSON.parse(document.getElementById("pathway-data").textContent);
  var NS = "http://www.w3.org/2000/svg";
  var svg = root.querySelector("svg.pw-routes");
  var panel = root.querySelector("[data-pw=panel]");
  var bandsEl = root.querySelector("[data-pw=bands]");
  var pop = document.getElementById("pw-pop"), popBody = root.querySelector("[data-pw=pop]"), popTitle = document.getElementById("pw-pop-title");
  var plotConfig = {displaylogo: false, responsive: true, displayModeBar: false};
  var sel = null, openBand = null;
  var bands = D.bands.map(function (b) { return Object.assign({}, b); });

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
    var g = el("g", {"class": "pw-node pw-" + n.level, tabindex: "0", role: "button", "data-id": n.id,
      "aria-label": n.aria || n.label.join(" ")}, svg);
    el("circle", {"class": "pw-hit", cx: n.x, cy: n.y, r: 20}, g);
    el("circle", {"class": "pw-ring", cx: n.x, cy: n.y, r: 13}, g);
    el("circle", {"class": "pw-dot", cx: n.x, cy: n.y, r: 7}, g);
    n.label.forEach(function (line, i) {
      var left = n.x < 90;
      el("text", {x: left ? n.x - 12 : n.x, y: n.y + 28 + i * 16, "text-anchor": left ? "start" : "middle"}, g).textContent = line;
    });
    if (n.sub) el("text", {x: n.x, y: n.y + 26, "text-anchor": "middle", "class": "pw-sub"}, g).textContent = n.sub;
    var pick = function () { sel = sel === n.id ? null : n.id; render(); };
    g.addEventListener("click", pick);
    g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
  });

  // Silta bands, on the map's x scale (viewBox 0–1000 → 0–100%)
  bands.forEach(function (b) {
    var btn = document.createElement("button");
    btn.type = "button"; btn.className = "pw-sbar"; btn.textContent = b.name;
    btn.style.marginLeft = b.x0 / 10 + "%"; btn.style.width = (b.x1 - b.x0) / 10 + "%";
    btn.setAttribute("aria-expanded", "false"); btn.setAttribute("aria-controls", "pw-band-" + b.id);
    var info = document.createElement("p");
    info.className = "pw-sinfo"; info.id = "pw-band-" + b.id; info.hidden = true; info.textContent = b.text;
    info.style.marginLeft = b.x0 / 10 + "%";
    btn.addEventListener("click", function () { openBand = openBand === b.id ? null : b.id; render(); });
    bandsEl.appendChild(btn); bandsEl.appendChild(info);
    b.btn = btn; b.info = info;
  });

  function table(t) {
    return "<table><thead><tr>" + t.head.map(function (h) { return "<th>" + esc(h) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      t.rows.map(function (r, i) {
        return "<tr" + (t.total && i === t.rows.length - 1 ? ' class="pw-total"' : "") + ">" +
          r.map(function (c) { return '<td class="' + (/^[−+]/.test(c) ? "pw-gapv" : "") + '">' + esc(c) + "</td>"; }).join("") + "</tr>";
      }).join("") + "</tbody></table>";
  }

  // Data popup
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
  document.getElementById("pw-pop-close").addEventListener("click", function () { pop.close(); });
  pop.addEventListener("click", function (e) { if (e.target === pop) pop.close(); });
  document.addEventListener("silta:theme", drawCharts);

  function render() {
    svg.querySelectorAll(".pw-node").forEach(function (g) { g.setAttribute("aria-pressed", g.dataset.id === sel ? "true" : "false"); });
    bands.forEach(function (b) {
      b.btn.classList.toggle("pw-on", b.steps.indexOf(sel) > -1);
      b.btn.setAttribute("aria-expanded", openBand === b.id ? "true" : "false");
      b.info.hidden = openBand !== b.id;
    });
    if (!sel) {
      panel.className = "pw-panel pw-empty";
      panel.innerHTML = "<p>" + esc(D.page.prompt) + "</p>";
      return;
    }
    var d = D.steps[sel];
    var hasData = (d.tables && d.tables.length) || (d.charts && d.charts.length);
    panel.className = "pw-panel";
    panel.innerHTML = '<div><span class="pw-tag"><svg width="28" height="8" aria-hidden="true">' + LINE[d.level] + "</svg>" + esc(D.levels[d.level]) + "</span>" +
      "<h3>" + esc(d.title) + "</h3><p>" + esc(d.text) + '</p><p class="pw-src">Source: ' + esc(d.src) + "</p></div>" +
      (hasData ? '<div><button class="pw-more" type="button" aria-haspopup="dialog">Show data</button></div>' : "");
    var more = panel.querySelector(".pw-more");
    if (more) more.addEventListener("click", function () { openData(d); });
  }
  render();
})();
