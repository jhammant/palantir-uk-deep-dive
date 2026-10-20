/* Palantir UK Deep Dive: every page's behaviour. Data comes from window.PUK (assets/bundle.js). */
(function () {
  "use strict";
  const D = window.PUK || { contracts: [], tax: [], payments: [], influence: [], timeline: [], quotes: [], notes: {}, sectors: [] };
  const PAGES = [
    ["index.html", "Overview"], ["contracts.html", "Contracts"], ["payments.html", "Payments"],
    ["tax.html", "Tax"], ["lock-in.html", "Lock-in"], ["people.html", "People"],
    ["influence.html", "Influence"], ["timeline.html", "Timeline"], ["about.html", "Method"],
  ];
  const REPO = "https://github.com/jhammant/palantir-uk-deep-dive";

  /* ---------- helpers ---------- */
  const $ = (s, r = document) => r.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const safeUrl = (u) => (/^https?:\/\//i.test(u || "") ? u : "");
  const link = (u, text) => (safeUrl(u) ? `<a href="${esc(u)}" rel="noopener" target="_blank">${esc(text)}</a>` : esc(text || ""));
  const sum = (rows, f) => rows.reduce((a, r) => a + (f(r) || 0), 0);
  function money(v, { exact = false } = {}) {
    if (v == null || isNaN(v)) return "not published";
    if (v < 0) return "−" + money(-v, { exact });
    const a = Math.abs(v);
    if (exact) return "£" + Math.round(v).toLocaleString("en-GB");
    if (a >= 1e9) return "£" + (v / 1e9).toFixed(2) + "bn";
    if (a >= 1e6) return "£" + (v / 1e6).toFixed(1) + "m";
    if (a >= 1e3) return "£" + Math.round(v / 1e3) + "k";
    return "£" + Math.round(v);
  }
  const fmtDate = (d) => {
    if (!d) return "";
    const t = new Date(d.length === 4 ? d + "-01-01" : d.length === 7 ? d + "-01" : d);
    if (isNaN(t)) return d;
    return d.length === 4 ? d : t.toLocaleDateString("en-GB", d.length === 7 ? { month: "short", year: "numeric" } : { day: "numeric", month: "short", year: "numeric" });
  };
  const colourOf = (sector) => `var(--s${Math.max(1, D.sectors.indexOf(sector) + 1)})`;
  const uniq = (xs) => [...new Set(xs.filter(Boolean))];

  function hashState() {
    const p = new URLSearchParams(location.hash.slice(1));
    return Object.fromEntries(p.entries());
  }
  function setHash(state) {
    const p = new URLSearchParams();
    Object.entries(state).forEach(([k, v]) => v && p.set(k, v));
    const h = p.toString();
    history.replaceState(null, "", h ? "#" + h : location.pathname);
  }
  function downloadCsv(name, rows, cols) {
    const q = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const csv = [cols.map(q).join(","), ...rows.map((r) => cols.map((c) => q(r[c])).join(","))].join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  function pending(what) {
    return `<div class="pending"><b>Research in progress.</b> ${esc(what)} This page fills in automatically when the data lands in <code>data/</code> and the site is rebuilt.</div>`;
  }

  /* ---------- layout ---------- */
  function layout() {
    const here = location.pathname.split("/").pop() || "index.html";
    const nav = PAGES.map(([href, label]) => `<a href="${href}"${href === here ? ' aria-current="page"' : ""}>${label}</a>`).join("");
    document.body.insertAdjacentHTML("afterbegin", `
      <header class="site-head"><div class="wrap">
        <a class="brand" href="index.html"><span>Palantir</span> UK Deep Dive</a>
        <nav class="nav" aria-label="Sections">${nav}</nav>
      </div></header>`);
    document.body.insertAdjacentHTML("beforeend", `
      <footer class="site-foot"><div class="wrap">
        Every figure links to a public record. Data rebuilt ${esc(D.generated || "")}.
        <a href="about.html">Method, gaps and corrections</a> · <a href="${REPO}" rel="noopener">Source and data on GitHub</a> ·
        Public sector information under the Open Government Licence v3.0.
      </div></footer>`);
  }

  /* ---------- charts ---------- */
  function tooltip(host) {
    let t = $(".tooltip", host);
    if (!t) { t = document.createElement("div"); t.className = "tooltip"; t.setAttribute("role", "status"); host.appendChild(t); }
    return {
      show(html, x, y) { t.innerHTML = html; t.style.left = x + "px"; t.style.top = y + "px"; t.classList.add("show"); },
      hide() { t.classList.remove("show"); },
    };
  }
  // Round tick steps (1, 2, 2.5, 5 × 10^k) so the axis reads £0, £50m, £100m…
  function niceMax(v, ticks = 4) {
    const raw = (v || 1) / ticks, p = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map((m) => m * p).find((s) => s >= raw);
    return step * ticks;
  }
  const tickLabel = (v) => (v < 0 ? "−" + tickLabel(-v) : v === 0 ? "£0" : v >= 1e6 ? `£${+(v / 1e6).toFixed(1)}m` : v >= 1e3 ? `£${+(v / 1e3).toFixed(1)}k` : `£${v}`);
  // Rounded top corners only: the data end, not the baseline.
  function barPath(x, y, w, h, r) {
    r = Math.min(r, w / 2, h);
    return `M${x},${y + h}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h}Z`;
  }

  /* Stacked bars: columns = [{key, label, parts:[{series, value, n}]}] */
  function stackedBars(host, columns, { series, onClick, labelOver = 0 } = {}) {
    const W = 760, H = 300, m = { t: 22, r: 8, b: 26, l: 52 };
    const iw = W - m.l - m.r, ih = H - m.t - m.b;
    const totals = columns.map((c) => sum(c.parts, (p) => p.value));
    const max = niceMax(Math.max(...totals, 1));
    const bw = Math.min(44, (iw / columns.length) * 0.62);
    const step = iw / columns.length;
    const y = (v) => m.t + ih - (v / max) * ih;
    let g = "";
    for (let i = 0; i <= 4; i++) {
      const v = (max / 4) * i, yy = y(v);
      g += `<line class="${i ? "gridline" : "baseline"}" x1="${m.l}" x2="${W - m.r}" y1="${yy}" y2="${yy}"/>`;
      g += `<text class="tick" x="${m.l - 8}" y="${yy + 4}" text-anchor="end">${tickLabel(v)}</text>`;
    }
    columns.forEach((c, i) => {
      const x = m.l + step * i + (step - bw) / 2;
      // Full-height hit area behind the bars, so thin slices and empty years are still reachable.
      g += `<rect class="col-hit" x="${m.l + step * i}" y="${m.t}" width="${step}" height="${ih}" fill="transparent" data-col="${i}" tabindex="0" aria-label="${esc(`${c.label}: ${money(totals[i])}`)}"/>`;
      let acc = 0;
      const parts = c.parts.filter((p) => p.value > 0);
      parts.forEach((p, j) => {
        const y0 = y(acc), y1 = y(acc + p.value);
        const top = j === parts.length - 1;
        const h = Math.max(1, y0 - y1 - (j ? 2 : 0)); // 2px surface gap between stacked fills
        const d = top ? barPath(x, y1, bw, h, 4) : `M${x},${y1 + h}V${y1}H${x + bw}V${y1 + h}Z`;
        g += `<path class="seg" d="${d}" fill="${colourOf(p.series)}" data-col="${i}" data-part="${j}" tabindex="0" aria-label="${esc(`${c.label}, ${p.series}: ${money(p.value)}`)}"/>`;
        acc += p.value;
      });
      if (totals[i] >= labelOver && totals[i] > 0) g += `<text class="total-label" x="${x + bw / 2}" y="${y(totals[i]) - 6}" text-anchor="middle">${money(totals[i])}</text>`;
      g += `<text class="tick" x="${x + bw / 2}" y="${H - 6}" text-anchor="middle">${esc(c.label)}</text>`;
    });
    const legend = series.map((s) => `<span><span class="sw" style="background:${colourOf(s)}"></span>${esc(s)}</span>`).join("");
    host.classList.add("chart");
    host.innerHTML = `<div class="legend">${legend}</div><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Contract awards by year and sector">${g}</svg>`;
    const tip = tooltip(host);
    const svg = $("svg", host);
    const partOf = (el) => { const c = columns[+el.dataset.col]; return [c, c.parts.filter((p) => p.value > 0)[+el.dataset.part]]; };
    const show = (el) => {
      const [c, p] = partOf(el);
      const r = el.getBoundingClientRect(), hr = host.getBoundingClientRect();
      tip.show(`${esc(c.label)} · ${esc(p.series)}<br><b>${money(p.value)}</b> across ${p.n} award${p.n === 1 ? "" : "s"}<br><span style="opacity:.75">Click to see them</span>`, r.left - hr.left + r.width / 2, r.top - hr.top);
    };
    svg.querySelectorAll(".col-hit").forEach((el) => {
      const c = columns[+el.dataset.col];
      const show = () => {
        const r = el.getBoundingClientRect(), hr = host.getBoundingClientRect();
        const rows = c.parts.filter((p) => p.value > 0).sort((a, b) => b.value - a.value)
          .map((p) => `<span class="sw" style="background:${colourOf(p.series)};width:9px;height:9px;display:inline-block;border-radius:2px;margin-right:5px"></span>${esc(p.series)} <b>${money(p.value)}</b>`).join("<br>");
        const n = sum(c.parts, (p) => p.n);
        tip.show(`<b>${esc(c.label)}: ${money(sum(c.parts, (p) => p.value))}</b> · ${n} award${n === 1 ? "" : "s"}${rows ? "<br>" + rows : ""}`, r.left - hr.left + r.width / 2, svg.getBoundingClientRect().top - hr.top + y(sum(c.parts, (p) => p.value)) * (svg.getBoundingClientRect().width / W));
      };
      el.addEventListener("mouseenter", show); el.addEventListener("focus", show);
      el.addEventListener("mouseleave", () => tip.hide()); el.addEventListener("blur", () => tip.hide());
      const go = () => onClick && onClick(c, null);
      el.addEventListener("click", go);
      el.addEventListener("keydown", (e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), go()));
    });
    svg.querySelectorAll(".seg").forEach((el) => {
      el.addEventListener("mouseenter", () => show(el));
      el.addEventListener("focus", () => show(el));
      el.addEventListener("mouseleave", () => tip.hide());
      el.addEventListener("blur", () => tip.hide());
      const go = () => { const [c, p] = partOf(el); onClick && onClick(c, p); };
      el.addEventListener("click", go);
      el.addEventListener("keydown", (e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), go()));
    });
  }

  /* Grouped bars, one £ axis: groups = [{label, values:[{series, value}]}] */
  function groupedBars(host, groups, series, colours) {
    const W = 760, H = 300, m = { t: 22, r: 8, b: 26, l: 56 };
    const iw = W - m.l - m.r, ih = H - m.t - m.b;
    const vals = groups.flatMap((g) => g.values.map((v) => v.value).filter((v) => v != null));
    const hiRaw = Math.max(0, ...vals), loRaw = Math.min(0, ...vals);
    const step = niceMax(Math.max(hiRaw, -loRaw, 1)) / 4;
    const hi = Math.ceil(hiRaw / step) * step || step, lo = Math.floor(loRaw / step) * step;
    const y = (v) => m.t + ((hi - v) / (hi - lo)) * ih;
    const gstep = iw / groups.length, bw = Math.min(28, (gstep * 0.7) / series.length);
    let g = "";
    for (let v = lo; v <= hi + 1e-6; v += step) {
      const yy = y(v);
      g += `<line class="${Math.abs(v) < 1e-6 ? "baseline" : "gridline"}" x1="${m.l}" x2="${W - m.r}" y1="${yy}" y2="${yy}"/><text class="tick" x="${m.l - 8}" y="${yy + 4}" text-anchor="end">${tickLabel(Math.round(v))}</text>`;
    }
    groups.forEach((grp, i) => {
      const x0 = m.l + gstep * i + (gstep - bw * series.length - 2 * (series.length - 1)) / 2;
      grp.values.forEach((v, j) => {
        if (v.value == null) return;
        const x = x0 + j * (bw + 2), y0 = y(0), y1 = y(v.value);
        const h = Math.max(1, Math.abs(y0 - y1));
        // The rounded end is the data end: the top for positives, the bottom for negatives.
        const d = v.value >= 0 ? barPath(x, y1, bw, h, 4)
          : `M${x},${y0}V${y0 + h - 4}Q${x},${y0 + h} ${x + 4},${y0 + h}H${x + bw - 4}Q${x + bw},${y0 + h} ${x + bw},${y0 + h - 4}V${y0}Z`;
        g += `<path class="seg" d="${d}" fill="${colours[j]}" tabindex="0" data-g="${i}" data-v="${j}" aria-label="${esc(`${grp.label}, ${v.series}: ${money(v.value)}`)}"/>`;
      });
      g += `<text class="tick" x="${m.l + gstep * i + gstep / 2}" y="${H - 6}" text-anchor="middle">${esc(grp.label)}</text>`;
    });
    host.classList.add("chart");
    host.innerHTML = `<div class="legend">${series.map((s, j) => `<span><span class="sw" style="background:${colours[j]}"></span>${esc(s)}</span>`).join("")}</div><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Tax by year">${g}</svg>`;
    const tip = tooltip(host);
    host.querySelectorAll(".seg").forEach((el) => {
      const show = () => {
        const grp = groups[+el.dataset.g], v = grp.values[+el.dataset.v];
        const r = el.getBoundingClientRect(), hr = host.getBoundingClientRect();
        tip.show(`${esc(grp.label)} · ${esc(v.series)}<br><b>${money(v.value, { exact: true })}</b>`, r.left - hr.left + r.width / 2, r.top - hr.top);
      };
      el.addEventListener("mouseenter", show); el.addEventListener("focus", show);
      el.addEventListener("mouseleave", () => tip.hide()); el.addEventListener("blur", () => tip.hide());
    });
  }

  function hbars(host, items, { colour, hrefOf } = {}) {
    const max = Math.max(...items.map((i) => i.value), 1);
    host.className = "hbars";
    host.innerHTML = items.map((i) => {
      const tag = hrefOf ? "a" : "div";
      const href = hrefOf ? ` href="${esc(hrefOf(i))}"` : "";
      return `<${tag} class="hbar"${href}><span class="name">${esc(i.label)}</span>
        <span class="track"><span class="fill" style="width:${(i.value / max) * 100}%;background:${colour ? colour(i) : "var(--s1)"}"></span></span>
        <span class="num"><b>${money(i.value)}</b> <span class="muted">· ${i.n}</span></span></${tag}>`;
    }).join("");
  }

  /* ---------- sortable, filterable table ---------- */
  function dataTable(host, { rows, cols, sort, detail, empty = "Nothing matches these filters." }) {
    let key = sort.key, dir = sort.dir, open = new Set();
    function render() {
      const col = cols.find((c) => c.key === key);
      const val = col.sortValue || ((r) => r[key]);
      const sorted = [...rows()].sort((a, b) => {
        const x = val(a), y = val(b);
        const cmp = typeof x === "number" || typeof y === "number" ? (x ?? -Infinity) - (y ?? -Infinity) : String(x ?? "").localeCompare(String(y ?? ""));
        return dir === "asc" ? cmp : -cmp;
      });
      const head = cols.map((c) => `<th class="${c.right ? "r" : ""}" aria-sort="${c.key === key ? (dir === "asc" ? "ascending" : "descending") : "none"}">${c.sortable === false ? esc(c.label) : `<button data-k="${c.key}">${esc(c.label)}</button>`}</th>`).join("");
      const body = sorted.length ? sorted.map((r, i) => {
        const id = r._id ?? i;
        const tr = `<tr class="row" data-id="${esc(id)}" tabindex="0" aria-expanded="${open.has(String(id))}">${cols.map((c) => `<td class="${c.right ? "r num" : ""}">${c.render ? c.render(r) : esc(r[c.key])}</td>`).join("")}</tr>`;
        return tr + (detail && open.has(String(id)) ? `<tr class="detail"><td colspan="${cols.length}">${detail(r)}</td></tr>` : "");
      }).join("") : `<tr><td colspan="${cols.length}" class="empty">${esc(empty)}</td></tr>`;
      host.innerHTML = `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
      host.querySelectorAll("th button").forEach((b) => b.addEventListener("click", () => {
        if (key === b.dataset.k) dir = dir === "asc" ? "desc" : "asc"; else { key = b.dataset.k; dir = cols.find((c) => c.key === key).right ? "desc" : "asc"; }
        render();
      }));
      if (detail) host.querySelectorAll("tr.row").forEach((tr) => {
        const toggle = (e) => {
          if (e.target.closest("a")) return;
          const id = tr.dataset.id;
          open.has(id) ? open.delete(id) : open.add(id);
          render();
        };
        tr.addEventListener("click", toggle);
        tr.addEventListener("keydown", (e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), toggle(e)));
      });
    }
    render();
    return { render };
  }

  /* ---------- pages ---------- */
  const C = D.contracts.map((c, i) => ({ ...c, _id: i }));
  const total = sum(C, (c) => c.value);
  const lastYear = (() => { const t = new Date(); t.setFullYear(t.getFullYear() - 1); return t.toISOString().slice(0, 10); })();
  const directRecent = C.filter((c) => c.route === "Direct award" && c.awarded >= lastYear);
  const latestTax = D.tax[D.tax.length - 1];

  function yearColumns(rows) {
    const years = rows.map((r) => +r.year).filter(Boolean);
    const lo = Math.min(...years), hi = Math.max(...years);
    const cols = [];
    for (let yv = lo; yv <= hi; yv++) {
      const inYear = rows.filter((r) => +r.year === yv);
      cols.push({ key: String(yv), label: String(yv), parts: D.sectors.map((s) => { const xs = inYear.filter((r) => r.sector === s); return { series: s, value: sum(xs, (r) => r.value), n: xs.length }; }) });
    }
    return cols;
  }
  function bySector(rows) {
    return D.sectors.map((s) => { const xs = rows.filter((r) => r.sector === s); return { label: s, value: sum(xs, (r) => r.value), n: xs.length }; })
      .filter((x) => x.n).sort((a, b) => b.value - a.value);
  }

  const page = {
    overview() {
      $("#tiles").innerHTML = `
        <div class="tile"><div class="label">Published contract awards to Palantir</div><div class="value">${money(total)}</div><div class="foot">${C.length} awards, ${esc(uniq(C.map((c) => c.year)).sort()[0] || "")}–${esc(uniq(C.map((c) => c.year)).sort().pop() || "")}, values as published</div></div>
        <div class="tile"><div class="label">Direct awards in the past 12 months</div><div class="value">${money(sum(directRecent, (c) => c.value))}</div><div class="foot">${directRecent.length} contracts awarded with no competition</div></div>
        <div class="tile"><div class="label">Palantir UK sales in the UK, ${esc((latestTax?.year_end || "").slice(0, 4))}</div><div class="value">${money(latestTax?.uk_turnover_gbp)}</div><div class="foot">from its filed accounts</div></div>
        <div class="tile"><div class="label">UK corporation tax, ${esc((latestTax?.year_end || "").slice(0, 4))}</div><div class="value hit">${money(latestTax?.uk_corporation_tax_current_gbp)}</div><div class="foot">on ${money(latestTax?.profit_before_tax_gbp)} profit before tax</div></div>`;
      stackedBars($("#by-year"), yearColumns(C), {
        series: D.sectors.filter((s) => C.some((c) => c.sector === s)), labelOver: 20e6,
        onClick: (c, p) => (location.href = `contracts.html#year=${c.key}` + (p ? `&sector=${encodeURIComponent(p.series)}` : "")),
      });
      hbars($("#by-sector"), bySector(C), { colour: (i) => colourOf(i.label), hrefOf: (i) => `contracts.html#sector=${encodeURIComponent(i.label)}` });
      const neso = C.find((c) => /NESO/i.test(c.title) && c.procedure_rationale);
      if (neso) $("#evidence").innerHTML = `<div class="evidence"><blockquote>“…underpinned by proprietary architecture licensed exclusively by Palantir… Transitioning to an alternative supplier is not possible without significant cost, resource commitment and delivery risk…”</blockquote><div class="who">National Energy System Operator, explaining why it gave Palantir ${money(neso.value)} with no competition (${fmtDate(neso.awarded)}). ${link(neso.url, "Read the notice")}</div></div>`;
      const biggest = [...C].sort((a, b) => (b.value || 0) - (a.value || 0)).slice(0, 6);
      $("#biggest").innerHTML = biggest.map((c) => `<div class="hbar" style="grid-template-columns:1fr auto"><span>${esc(c.title)} <span class="muted small">· ${esc(c.buyer)}, ${esc(c.year)}</span> ${c.route === "Direct award" ? '<span class="stamp">No competition</span>' : ""}</span><span class="num"><b>${money(c.value)}</b></span></div>`).join("");
    },

    contracts() {
      const st = hashState();
      const years = uniq(C.map((c) => c.year)).sort();
      const opt = (xs, sel) => xs.map((x) => `<option${x === sel ? " selected" : ""}>${esc(x)}</option>`).join("");
      $("#filters").innerHTML = `
        <label>Search<input type="search" id="q" placeholder="Buyer, title, description…" value="${esc(st.q || "")}"></label>
        <label>Sector<select id="sector"><option value="">All sectors</option>${opt(D.sectors.filter((s) => C.some((c) => c.sector === s)), st.sector)}</select></label>
        <label>How it was awarded<select id="route"><option value="">Any route</option>${opt(uniq(C.map((c) => c.route)).sort(), st.route)}</select></label>
        <label>From<select id="from"><option value="">Any year</option>${opt(years, st.from || st.year)}</select></label>
        <label>To<select id="to"><option value="">Any year</option>${opt(years, st.to || st.year)}</select></label>
        <button class="btn" id="reset" type="button">Clear</button>
        <button class="btn" id="dl" type="button">Download these rows (CSV)</button>`;
      const get = () => ({ q: $("#q").value.trim(), sector: $("#sector").value, route: $("#route").value, from: $("#from").value, to: $("#to").value });
      const filtered = () => {
        const f = get(), q = f.q.toLowerCase();
        return C.filter((c) => (!f.sector || c.sector === f.sector) && (!f.route || c.route === f.route) &&
          (!f.from || c.year >= f.from) && (!f.to || c.year <= f.to) &&
          (!q || [c.buyer, c.title, c.notes, c.procedure_rationale].join(" ").toLowerCase().includes(q)));
      };
      const table = dataTable($("#table"), {
        rows: filtered, sort: { key: "awarded", dir: "desc" },
        cols: [
          { key: "awarded", label: "Awarded", render: (r) => `<span class="num">${esc(fmtDate(r.awarded))}</span>` },
          { key: "buyer", label: "Buyer", render: (r) => `${esc(r.buyer)}<div class="muted small">${esc(r.sector)}</div>` },
          { key: "title", label: "What for", render: (r) => esc(r.title) },
          { key: "value", label: "Value", right: true, render: (r) => money(r.value) },
          { key: "route", label: "Route", render: (r) => (r.route === "Direct award" ? '<span class="stamp">No competition</span>' : `<span class="pill">${esc(r.route)}</span>`) },
          { key: "url", label: "Notice", sortable: false, render: (r) => link(r.url, r.source) },
        ],
        detail: (r) => `<dl>
          <dt>Description</dt><dd>${esc(r.notes || "None published")}</dd>
          ${r.procedure_rationale ? `<dt>Buyer's reason</dt><dd>${esc(r.procedure_rationale)}</dd>` : ""}
          <dt>Exact value</dt><dd class="num">${money(r.value, { exact: true })} <span class="muted">(${esc(r.value_basis)})</span></dd>
          <dt>Term</dt><dd>${esc(fmtDate(r.start) || "?")} to ${esc(fmtDate(r.end) || "?")}</dd>
          <dt>Procedure</dt><dd>${esc(r.procedure || "not stated")}${r.route_basis === "notice description" ? " (route taken from the notice description)" : ""}</dd>
          <dt>Status</dt><dd>${esc(r.status || "awarded")}</dd>
          <dt>Source</dt><dd>${link(r.url, r.url)}</dd></dl>`,
      });
      const update = () => {
        const rows = filtered();
        $("#summary").innerHTML = `<b>${rows.length}</b> of ${C.length} awards · <b>${money(sum(rows, (r) => r.value))}</b> as published · ${rows.filter((r) => r.route === "Direct award").length} with no competition. Click a row for the detail.`;
        const f = get(); setHash(f);
        table.render();
      };
      $("#filters").addEventListener("input", update);
      $("#reset").addEventListener("click", () => { $("#filters").querySelectorAll("input,select").forEach((e) => (e.value = "")); update(); });
      $("#dl").addEventListener("click", () => downloadCsv("palantir-uk-contracts.csv", filtered(), ["awarded", "buyer", "sector", "title", "value_gbp", "value_basis", "route", "procedure", "procedure_rationale", "start", "end", "status", "source", "url"]));
      update();
    },

    payments() {
      const ALL = D.payments.map((p, i) => ({ ...p, _id: i }));
      const P = ALL.filter((p) => p.counted);
      if (!ALL.length) { $("#content").innerHTML = pending("We are reading departmental, NHS, police and council spending files and FOI answers for payments to Palantir."); return; }
      const payers = uniq(P.map((p) => p.payer)).map((name) => { const xs = P.filter((p) => p.payer === name); return { label: name, value: sum(xs, (p) => p.amount), n: xs.length }; }).sort((a, b) => b.value - a.value);
      $("#content").innerHTML = `
        <div class="tiles">
          <div class="tile"><div class="label">Paid to Palantir, from published spend files</div><div class="value">${money(sum(P, (p) => p.amount))}</div><div class="foot">${P.length} payment lines from ${payers.length} public bodies, net of credit notes. A floor, not a total: see the gaps below.</div></div>
          <div class="tile"><div class="label">Published contract awards, for comparison</div><div class="value">${money(total)}</div><div class="foot">award values, which are ceilings or estimates</div></div>
        </div>
        <div class="grid-2"><section><h2 style="margin-top:0">Who paid</h2><div id="payers"></div></section><section><h2 style="margin-top:0">By year paid</h2><div id="years"></div></section></div>
        <div class="filters"><label>Search<input type="search" id="q" placeholder="Payer, description…"></label>
        <label>Payer type<select id="type"><option value="">All</option>${uniq(P.map((p) => p.payer_type)).sort().map((t) => `<option>${esc(t)}</option>`).join("")}</select></label>
        <button class="btn" id="dl" type="button">Download these rows (CSV)</button></div>
        <p class="summary" id="summary"></p><div id="table"></div>
        ${D.notes["payments-notes"] ? `<h2>Notes</h2><div class="prose">${D.notes["payments-notes"]}</div>` : ""}`;
      hbars($("#payers"), payers.slice(0, 15));
      hbars($("#years"), uniq(P.map((p) => (p.period || "").slice(0, 4))).sort().map((yv) => { const xs = P.filter((p) => (p.period || "").startsWith(yv)); return { label: yv, value: sum(xs, (p) => p.amount), n: xs.length }; }));
      const filtered = () => { const q = $("#q").value.toLowerCase(), t = $("#type").value; return ALL.filter((p) => (!t || p.payer_type === t) && (!q || [p.payer, p.description_as_published, p.notes].join(" ").toLowerCase().includes(q))); };
      const table = dataTable($("#table"), {
        rows: filtered, sort: { key: "period", dir: "desc" },
        cols: [
          { key: "period", label: "When", render: (r) => `<span class="num">${esc(fmtDate(r.period))}</span>` },
          { key: "payer", label: "Payer" },
          { key: "description_as_published", label: "Description as published" },
          { key: "amount", label: "Amount", right: true, render: (r) => money(r.amount, { exact: true }) + (r.counted ? "" : `<div class="muted small">not counted in totals</div>`) },
          { key: "source_file_url", label: "Source", sortable: false, render: (r) => link(r.source_file_url || r.source_page_url, "File") },
        ],
        detail: (r) => `<dl><dt>Supplier as published</dt><dd>${esc(r.supplier_name_as_published)}</dd><dt>Notes</dt><dd>${esc(r.notes)}</dd><dt>Source page</dt><dd>${link(r.source_page_url, r.source_page_url)}</dd></dl>`,
      });
      const update = () => { const rows = filtered(), c = rows.filter((r) => r.counted); $("#summary").innerHTML = `<b>${rows.length}</b> lines · <b>${money(sum(c, (r) => r.amount))}</b> counted${rows.length > c.length ? ` · ${rows.length - c.length} not counted (FOI aggregate or not a Palantir supplier line; click for why)` : ""}`; table.render(); };
      $("#content").addEventListener("input", update);
      $("#dl").addEventListener("click", () => downloadCsv("palantir-uk-payments.csv", filtered(), ["period", "payer", "payer_type", "amount_gbp", "supplier_name_as_published", "description_as_published", "source_file_url", "source_page_url", "notes"]));
      update();
    },

    tax() {
      const T = D.tax.filter((t) => t.year_end);
      if (!T.length) { $("#content").innerHTML = pending("Filed accounts are being read."); return; }
      // A rate is only meaningful on a profit with a positive charge no bigger than the profit.
      const rate = (t) => {
        if (!(t.profit_before_tax_gbp > 0) || t.tax_charge_total_gbp == null) return null;
        const r = (t.tax_charge_total_gbp / t.profit_before_tax_gbp) * 100;
        return r >= 0 && r <= 100 ? r : null;
      };
      const l = T[T.length - 1];
      $("#content").innerHTML = `
        <div class="tiles">
          <div class="tile"><div class="label">UK sales, ${esc(l.year_end.slice(0, 4))}</div><div class="value">${money(l.uk_turnover_gbp)}</div><div class="foot">total turnover ${money(l.turnover_gbp)}</div></div>
          <div class="tile"><div class="label">Profit before tax</div><div class="value">${money(l.profit_before_tax_gbp)}</div><div class="foot">${esc(l.year_end.slice(0, 4))}</div></div>
          <div class="tile"><div class="label">UK corporation tax</div><div class="value hit">${money(l.uk_corporation_tax_current_gbp)}</div><div class="foot">total tax charge ${money(l.tax_charge_total_gbp)}</div></div>
          <div class="tile"><div class="label">At the ${l.standard_rate ? Math.round(l.standard_rate * 100) : 25}% headline rate</div><div class="value">${money(l.tax_at_standard_rate_gbp)}</div><div class="foot">from the accounts' own reconciliation</div></div>
        </div>
        <h2>Tax at the headline rate vs the tax actually charged</h2>
        <div id="tax-chart" class="card"></div>
        <h2>Year by year</h2><div id="table"></div>
        ${D.notes["tax-notes"] ? `<h2>What the accounts say</h2><div class="prose">${D.notes["tax-notes"]}</div>` : ""}`;
      groupedBars($("#tax-chart"), T.map((t) => ({ label: t.year_end.slice(0, 4), values: [
        { series: "Tax at the headline rate", value: t.tax_at_standard_rate_gbp }, { series: "Tax actually charged", value: t.tax_charge_total_gbp }] })),
      ["Tax at the headline rate", "Tax actually charged"], ["var(--s1)", "var(--s2)"]);
      dataTable($("#table"), {
        rows: () => T.map((t, i) => ({ ...t, _id: i, rate: rate(t) })), sort: { key: "year_end", dir: "desc" },
        cols: [
          { key: "year_end", label: "Year", render: (r) => esc(r.year_end.slice(0, 4)) },
          { key: "turnover_gbp", label: "Turnover", right: true, render: (r) => money(r.turnover_gbp) },
          { key: "uk_turnover_gbp", label: "UK turnover", right: true, render: (r) => money(r.uk_turnover_gbp) },
          { key: "profit_before_tax_gbp", label: "Profit before tax", right: true, render: (r) => money(r.profit_before_tax_gbp) },
          { key: "uk_corporation_tax_current_gbp", label: "UK corp. tax", right: true, render: (r) => money(r.uk_corporation_tax_current_gbp) },
          { key: "tax_charge_total_gbp", label: "Total tax", right: true, render: (r) => money(r.tax_charge_total_gbp) },
          { key: "rate", label: "Effective rate", right: true, render: (r) => (r.rate == null ? `<span class="muted" title="Loss, tax credit or prior-year adjustment: see the notes for this year">n/m</span>` : r.rate.toFixed(1) + "%") },
          { key: "avg_employees", label: "Staff", right: true, render: (r) => (r.avg_employees ? Math.round(r.avg_employees).toLocaleString("en-GB") : "–") },
          { key: "source_url", label: "Accounts", sortable: false, render: (r) => link(r.source_url, "PDF") },
        ],
        detail: (r) => `<dl><dt>Pages used</dt><dd>${esc(r.page_refs)}</dd><dt>Notes</dt><dd>${esc(r.notes)}</dd></dl>`,
      });
    },

    lockin() {
      const reasons = C.filter((c) => c.procedure_rationale);
      const exit = C.find((c) => /Transition & Exit/i.test(c.title));
      const fdp = C.find((c) => /Federated Data Platform/i.test(c.title));
      $("#evidence").innerHTML = reasons.map((c) => `<div class="evidence"><blockquote>${esc(c.procedure_rationale)}</blockquote><div class="who">${esc(c.buyer)} · ${esc(c.title)} · ${money(c.value)} · ${esc(fmtDate(c.awarded))} · ${link(c.url, "notice")}</div></div>`).join("");
      if (exit && fdp) $("#nhs").innerHTML = `<ol class="timeline">
        <li><div class="date">${esc(fmtDate(exit.awarded))}</div><div class="event">NHS England signs a <b>${money(exit.value)}</b> “${esc(exit.title)}” with Palantir: twelve months to move Covid-era products off Palantir Foundry to whoever wins the new Federated Data Platform. ${link(exit.url, "Notice")}</div></li>
        <li><div class="date">${esc(fmtDate(fdp.awarded))}</div><div class="event">The new Federated Data Platform is awarded to Palantir: <b>${money(fdp.value)}</b> for the initial term, widely reported as £330m over seven years. ${link(fdp.url, "Notice")}</div></li></ol>`;
      $("#notes").innerHTML = D.notes["sovereignty-notes"] ? `<h2>What the record says about control of the data</h2><div class="prose">${D.notes["sovereignty-notes"]}</div>` : pending("We are collecting what NHS England, the MoD and others have said about hosting, data control, US law exposure and exit terms.");
    },

    people() {
      const Q = D.quotes;
      if (!Q.length) { $("#content").innerHTML = pending("Quotes are being verified."); return; }
      const people = uniq(Q.map((q) => q.who));
      $("#content").innerHTML = `<div class="filters"><label>Person<select id="who"><option value="">Everyone</option>${people.map((p) => `<option>${esc(p)}</option>`).join("")}</select></label><label>Search<input type="search" id="q" placeholder="Word or topic…"></label></div><div class="quotes" id="list"></div>`;
      const render = () => {
        const who = $("#who").value, q = $("#q").value.toLowerCase();
        const rows = Q.filter((x) => (!who || x.who === who) && (!q || [x.quote, x.context].join(" ").toLowerCase().includes(q)));
        $("#list").innerHTML = rows.map((x) => `<article class="quote"><blockquote>${esc(x.quote)}</blockquote>
          <div class="meta"><b>${esc(x.who)}</b>${x.role ? `, ${esc(x.role)}` : ""} · ${esc(fmtDate(x.date))} · ${link(x.source_url, "source")} <span class="pill">${esc(x.source_type || "")}</span>${/caption/i.test(x.source_type || "") ? ' <span class="pill caption" title="Transcribed from the broadcaster\'s own video by automatic captions. Check the audio before relying on exact wording.">Auto-captions, not yet checked against the audio</span>' : ""}</div>
          ${x.context ? `<div class="ctx">${esc(x.context)}</div>` : ""}</article>`).join("") || `<div class="empty">No quotes match.</div>`;
      };
      $("#content").addEventListener("input", render);
      render();
    },

    influence() {
      const I = D.influence.map((r, i) => ({ ...r, _id: i }));
      if (!I.length) { $("#content").innerHTML = pending("We are reading ministerial meeting releases, ACOBA advice, lobbying registers and Hansard."); return; }
      $("#content").innerHTML = `<div class="filters"><label>Search<input type="search" id="q" placeholder="Name, department, topic…"></label>
        <label>Kind<select id="cat"><option value="">All</option>${uniq(I.map((r) => r.category)).sort().map((c) => `<option>${esc(c)}</option>`).join("")}</select></label></div>
        <p class="summary" id="summary"></p><div id="table"></div>
        ${D.notes["influence-notes"] ? `<h2>What the record shows</h2><div class="prose">${D.notes["influence-notes"]}</div>` : ""}`;
      const filtered = () => { const q = $("#q").value.toLowerCase(), c = $("#cat").value; return I.filter((r) => (!c || r.category === c) && (!q || [r.who, r.organisation, r.summary, r.notes].join(" ").toLowerCase().includes(q))); };
      const table = dataTable($("#table"), {
        rows: filtered, sort: { key: "date", dir: "desc" },
        cols: [
          { key: "date", label: "Date", render: (r) => `<span class="num">${esc(fmtDate(r.date))}</span>` },
          { key: "category", label: "Kind", render: (r) => `<span class="pill">${esc(r.category)}</span>` },
          { key: "who", label: "Who", render: (r) => `${esc(r.who)}<div class="muted small">${esc(r.organisation)}</div>` },
          { key: "summary", label: "What the record says" },
          { key: "source_url", label: "Source", sortable: false, render: (r) => link(r.source_url, r.source_type || "source") },
        ],
        detail: (r) => (r.notes ? `<dl><dt>Notes</dt><dd>${esc(r.notes)}</dd></dl>` : `<span class="muted">No further notes.</span>`),
      });
      const update = () => { $("#summary").innerHTML = `<b>${filtered().length}</b> of ${I.length} records`; table.render(); };
      $("#content").addEventListener("input", update);
      update();
    },

    timeline() {
      const T = D.timeline;
      if (!T.length) { $("#content").innerHTML = pending("The UK timeline is being compiled from official and press sources."); return; }
      $("#content").innerHTML = `<div class="filters"><label>Area<select id="cat"><option value="">Everything</option>${uniq(T.map((t) => t.category)).sort().map((c) => `<option>${esc(c)}</option>`).join("")}</select></label><label>Search<input type="search" id="q" placeholder="Word…"></label></div><ol class="timeline" id="list"></ol>`;
      const render = () => {
        const c = $("#cat").value, q = $("#q").value.toLowerCase();
        $("#list").innerHTML = T.filter((t) => (!c || t.category === c) && (!q || [t.event, t.notes].join(" ").toLowerCase().includes(q)))
          .map((t) => `<li><div class="date">${esc(fmtDate(t.date))} · <span class="pill">${esc(t.category)}</span>${t.date > new Date().toISOString().slice(0, 10) ? ' <span class="stamp">Upcoming</span>' : ""}</div><div class="event">${esc(t.event)} ${link(t.source_url, "source")}</div>${t.notes ? `<div class="muted small">${esc(t.notes)}</div>` : ""}</li>`).join("");
      };
      $("#content").addEventListener("input", render);
      render();
    },
  };

  layout();
  const fn = page[document.body.dataset.page];
  if (fn) fn();
})();
