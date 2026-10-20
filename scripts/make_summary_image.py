#!/usr/bin/env python3
"""Render img/summary.png, a one-image summary of the dataset, from the same bundle the site uses.

    python3 scripts/build_site.py && python3 scripts/make_summary_image.py

Every number is computed from data/ at render time, so rerunning after a data update refreshes the image.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "site" / "assets" / "bundle.js"
OUT_HTML = ROOT / "img" / "summary.html"
OUT_PNG = ROOT / "img" / "summary.png"
SITE = "jhammant.github.io/palantir-uk-deep-dive"


def money(v):
    if v is None:
        return "n/a"
    if v >= 1e9:
        return f"£{v / 1e9:.2f}bn"
    if v >= 1e6:
        return f"£{v / 1e6:.1f}m"
    if v >= 1e3:
        return f"£{v / 1e3:.0f}k"
    return f"£{v:.0f}"


def num(v):
    try:
        return float(str(v).replace(",", "").replace("£", ""))
    except (TypeError, ValueError):
        return None


def figures(d):
    contracts = d["contracts"]
    total = sum(c["value"] or 0 for c in contracts)
    direct = [c for c in contracts if c["route"] == "Direct award"]
    paid = sum(p["amount"] or 0 for p in d["payments"] if p.get("counted"))
    recon = d.get("reconciliation", [])
    no_notice = sum(r["paid"] for r in recon if r["no_notice_found"])
    years = sorted(c["year"] for c in contracts if c["year"])
    tax = d["tax"][-1]
    recent = [t for t in d["tax"] if t["year_end"][:4] in ("2022", "2023", "2024", "2025")]
    profit4 = sum(t["profit_before_tax_gbp"] or 0 for t in recent)
    tax4 = sum(t["tax_charge_total_gbp"] or 0 for t in recent)
    notes = d["notes"].get("influence-notes", "")
    ministers = re.search(r"list (\d+) ministerial meetings", notes)
    officials = re.search(r"name (\d+) senior officials", notes)
    if d["revolving"]:
        moves = {r["person"] for r in d["revolving"] if r.get("direction") == "gov-to-palantir"}
    else:
        moves = {r["who"] for r in d["influence"] if r["category"] in ("revolving-door", "acoba")
                 and not re.match(r"The Nerve|Jon Trickett", r["who"])}
    market = None
    for row in d.get("market", []):
        if not re.fullmatch(r"\d{4}", row.get("period", "")) and num(row.get("it_total_gbp")):
            share = num(row.get("palantir_share_of_it"))
            if share is not None:
                share = share if share > 1 else share * 100
                if not market or share > market["share"]:
                    market = {"payer": row["payer"], "share": share, "period": row["period"]}
    g = d.get("groupTax", [])
    uk_cash = next((r["amount"] for r in g if r.get("measure") == "cash_income_tax_upper_bound"), None)
    uk_rev = next((r["amount"] for r in g if r.get("year") == "2025" and r.get("jurisdiction") == "United Kingdom" and r.get("measure") == "revenue"), None)
    routes = []
    for rt in ("Direct award", "Framework call-off", "Competitive", "Not stated", "Other"):
        v = sum(c["value"] or 0 for c in contracts if c["route"] == rt)
        if v:
            routes.append((rt, v))
    return {
        "routes": routes,
        "uk_cash": uk_cash, "uk_rev": uk_rev,
        "total": total, "n": len(contracts), "y0": years[0], "y1": years[-1],
        "direct": sum(c["value"] or 0 for c in direct), "direct_pct": 100 * sum(c["value"] or 0 for c in direct) / total,
        "paid": paid, "no_notice": no_notice,
        "tax_year": tax["year_end"][:4], "uk_ct": tax["uk_corporation_tax_current_gbp"], "pbt": tax["profit_before_tax_gbp"],
        "uk_sales": tax["uk_turnover_gbp"], "rate4": 100 * tax4 / profit4 if profit4 else None,
        "ministers": ministers.group(1) if ministers else None, "officials": officials.group(1) if officials else None,
        "moves": len(moves), "market": market,
    }


def donut_svg(parts, total):
    """Small donut: the first slice in the accent colour, the rest in greys, 2px paper gaps."""
    import math
    greys = ["#6f6a60", "#948e81", "#b6b0a2", "#d3cdbf"]
    R, r, C, a0, out, g = 120, 74, 130, -math.pi / 2, [], 0
    for i, (label, v) in enumerate(parts):
        a1 = a0 + v / total * 2 * math.pi
        large = 1 if a1 - a0 > math.pi else 0
        p = lambda a, rad: (C + rad * math.cos(a), C + rad * math.sin(a))
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p(a0, R), p(a1, R), p(a1, r), p(a0, r)
        fill = "#b5102b" if i == 0 else greys[min(g, 3)]
        g += 0 if i == 0 else 1
        out.append(f'<path d="M{x0:.1f},{y0:.1f}A{R},{R} 0 {large} 1 {x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}A{r},{r} 0 {large} 0 {x3:.1f},{y3:.1f}Z" fill="{fill}" stroke="#f5f1e6" stroke-width="3"/>')
        a0 = a1
    return f'<svg viewBox="0 0 260 260" width="230" height="230">{"".join(out)}</svg>', ["#b5102b"] + greys


def render(f):
    e = html.escape
    market_card = (
        f'<div class="card"><div class="big">{f["market"]["share"]:.0f}%</div>'
        f'<div class="what">of {e(f["market"]["payer"])}\'s IT &amp; software spending went to Palantir ({e(f["market"]["period"])})</div></div>'
        if f["market"] else
        f'<div class="card"><div class="big">{money(f["no_notice"])}</div>'
        f'<div class="what">paid by public bodies with no Palantir contract notice we could find</div></div>'
    )
    access = f'{f["ministers"]} ministerial meetings' if f["ministers"] else "ministerial meetings"
    svg, cols = donut_svg(f["routes"], f["total"])
    legend = "".join(
        f'<li><span class="sw" style="background:{cols[0] if i == 0 else cols[min(i, 4)]}"></span>{e(label)}<b>{money(v)} · {v / f["total"] * 100:.0f}%</b></li>'
        for i, (label, v) in enumerate(f["routes"]))
    routes_band = f'<div class="band"><div class="band-svg">{svg}</div><div><div class="band-title">How the {money(f["total"])} was awarded</div><ul class="band-legend">{legend}</ul></div></div>'
    usd = lambda v: f"${v / 1e6:.1f}m"
    tax_card = (
        f'<div class="card hit"><div class="big">&lt;{usd(f["uk_cash"])}</div><div class="what">UK cash income tax in 2025, on <b>{usd(f["uk_rev"])} of UK revenue</b>. Less than Palantir paid in Germany, Japan, France or South Korea</div></div>'
        if f.get("uk_cash") else
        f'<div class="card hit"><div class="big">{money(f["uk_ct"])}</div><div class="what">UK corporation tax in {f["tax_year"]}, on <b>{money(f["pbt"])} profit</b></div></div>'
    )
    return f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>Palantir in the UK</title><style>
:root {{ --bg:#16181b; --paper:#f5f1e6; --ink:#1c1c1c; --muted:#6b665c; --rule:#c9c1ae; --red:#b5102b; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html, body {{ width:1080px; height:1350px; }}
body {{ background:var(--bg); display:flex; align-items:center; justify-content:center; font-family:"Helvetica Neue",Helvetica,Arial,sans-serif; color:var(--ink); }}
.sheet {{ width:980px; height:1250px; background:var(--paper); padding:54px 56px 44px; display:flex; flex-direction:column; box-shadow:0 30px 80px rgba(0,0,0,.5); }}
.eyebrow {{ font:600 17px/1 "SF Mono",Menlo,monospace; letter-spacing:.24em; color:var(--muted); }}
h1 {{ font-size:66px; font-weight:800; letter-spacing:-.025em; margin:14px 0 6px; line-height:1; }}
.hero {{ font-size:84px; font-weight:800; letter-spacing:-.03em; line-height:1; margin:18px 0 12px; }}
.hero-who {{ font-size:19px; line-height:1.4; color:var(--muted); max-width:860px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:10px 40px; margin:26px 0 18px; }}
.card {{ border-top:3px solid var(--ink); padding:16px 0 8px; }}
.card.hit {{ border-top-color:var(--red); }}
.big {{ font-size:60px; font-weight:800; letter-spacing:-.03em; line-height:1.02; }}
.card.hit .big {{ color:var(--red); }}
.what {{ font-size:19px; line-height:1.3; margin-top:8px; color:#2b2a27; }}
.what b {{ font-weight:700; }}
.stamp {{ display:inline-block; border:2.5px solid var(--red); color:var(--red); font:800 14px/1 "SF Mono",Menlo,monospace; letter-spacing:.12em; padding:5px 8px; transform:rotate(-3deg); margin-left:8px; vertical-align:12px; }}
.band {{ display:grid; grid-template-columns:230px 1fr; gap:34px; align-items:center; border-top:3px solid var(--ink); padding-top:18px; }}
.band-title {{ font-size:26px; font-weight:800; margin-bottom:12px; }}
.band-legend {{ list-style:none; display:grid; gap:8px; font-size:19px; }}
.band-legend li {{ display:grid; grid-template-columns:18px 1fr auto; gap:10px; align-items:center; }}
.band-legend .sw {{ width:14px; height:14px; border-radius:3px; display:inline-block; }}
.quote {{ border-left:5px solid var(--red); padding:4px 0 4px 20px; margin-top:auto; }}
.quote q {{ font-size:24px; font-weight:800; line-height:1.25; quotes:"\\201C" "\\201D"; }}
.quote .who {{ font-size:17px; color:var(--muted); margin-top:8px; }}
.foot {{ display:flex; justify-content:space-between; align-items:flex-end; border-top:2px dashed var(--rule); margin-top:26px; padding-top:16px; font-size:16px; color:var(--muted); }}
.foot .url {{ font:700 17px "SF Mono",Menlo,monospace; color:var(--ink); white-space:nowrap; }}
</style></head><body><div class="sheet">
<div class="eyebrow">PALANTIR UK DEEP DIVE · THE PUBLIC RECORD</div>
<div class="hero">“Buying our way in…!”</div>
<div class="hero-who">Subject line of a 2021 internal email from Palantir's UK head about the NHS, reported by Bloomberg. Palantir called the language “regrettable”; he later called it “a thought experiment”. Here is what the public record shows.</div>
<div class="grid">
  <div class="card"><div class="big">{money(f["total"])}</div><div class="what">awarded to Palantir in <b>{f["n"]} published contracts</b>, {f["y0"]}–{f["y1"]}</div></div>
  <div class="card hit"><div class="big">{f["direct_pct"]:.0f}%<span class="stamp">NO COMPETITION</span></div><div class="what">of that value, <b>{money(f["direct"])}</b>, was awarded directly with no competition</div></div>
  <div class="card"><div class="big">{money(f["paid"])}</div><div class="what">actually paid, from published spending files: <b>a floor, not a total</b></div></div>
  {market_card}
  {tax_card}
  <div class="card"><div class="big">{f["moves"]}</div><div class="what">people moved from UK public roles to Palantir, including an Armed Forces Minister · <b>{access}</b> on record</div></div>
</div>
{routes_band}
<div class="quote"><q>proprietary architecture licensed exclusively by Palantir</q>
<div class="who">The UK's grid operator NESO, explaining why switching supplier "is not possible without significant cost", Aug 2026</div></div>
<div class="foot"><div>Every figure links to its public source.<br>Compiled by Jon Hammant (Orbital). Disclosure on the site.</div><div class="url">{SITE}</div></div>
</div></body></html>"""


def main():
    raw = BUNDLE.read_text()
    d = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    f = figures(d)
    OUT_HTML.write_text(render(f))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        pg.goto(OUT_HTML.resolve().as_uri())
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(OUT_PNG))
        b.close()
    print(json.dumps({k: (round(v, 1) if isinstance(v, float) else v) for k, v in f.items()}, default=str))
    print(f"wrote {OUT_PNG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
