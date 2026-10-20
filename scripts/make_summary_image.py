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
    return {
        "total": total, "n": len(contracts), "y0": years[0], "y1": years[-1],
        "direct": sum(c["value"] or 0 for c in direct), "direct_pct": 100 * sum(c["value"] or 0 for c in direct) / total,
        "paid": paid, "no_notice": no_notice,
        "tax_year": tax["year_end"][:4], "uk_ct": tax["uk_corporation_tax_current_gbp"], "pbt": tax["profit_before_tax_gbp"],
        "uk_sales": tax["uk_turnover_gbp"], "rate4": 100 * tax4 / profit4 if profit4 else None,
        "ministers": ministers.group(1) if ministers else None, "officials": officials.group(1) if officials else None,
        "moves": len(moves), "market": market,
    }


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
    return f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>Palantir in the UK</title><style>
:root {{ --bg:#16181b; --paper:#f5f1e6; --ink:#1c1c1c; --muted:#6b665c; --rule:#c9c1ae; --red:#b5102b; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html, body {{ width:1080px; height:1350px; }}
body {{ background:var(--bg); display:flex; align-items:center; justify-content:center; font-family:"Helvetica Neue",Helvetica,Arial,sans-serif; color:var(--ink); }}
.sheet {{ width:980px; height:1250px; background:var(--paper); padding:54px 56px 44px; display:flex; flex-direction:column; box-shadow:0 30px 80px rgba(0,0,0,.5); }}
.eyebrow {{ font:600 17px/1 "SF Mono",Menlo,monospace; letter-spacing:.24em; color:var(--muted); }}
h1 {{ font-size:66px; font-weight:800; letter-spacing:-.025em; margin:14px 0 6px; line-height:1; }}
.sub {{ font-size:22px; color:var(--muted); }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; margin:34px 0 26px; }}
.card {{ border-top:3px solid var(--ink); padding:16px 0 8px; }}
.card.hit {{ border-top-color:var(--red); }}
.big {{ font-size:68px; font-weight:800; letter-spacing:-.03em; line-height:1.02; }}
.card.hit .big {{ color:var(--red); }}
.what {{ font-size:21px; line-height:1.3; margin-top:8px; color:#2b2a27; }}
.what b {{ font-weight:700; }}
.stamp {{ display:inline-block; border:2.5px solid var(--red); color:var(--red); font:800 14px/1 "SF Mono",Menlo,monospace; letter-spacing:.12em; padding:5px 8px; transform:rotate(-3deg); margin-left:8px; vertical-align:12px; }}
.quote {{ border-left:5px solid var(--red); padding:4px 0 4px 20px; margin-top:auto; }}
.quote q {{ font-size:28px; font-weight:800; line-height:1.25; quotes:"\\201C" "\\201D"; }}
.quote .who {{ font-size:17px; color:var(--muted); margin-top:8px; }}
.foot {{ display:flex; justify-content:space-between; align-items:flex-end; border-top:2px dashed var(--rule); margin-top:26px; padding-top:16px; font-size:16px; color:var(--muted); }}
.foot .url {{ font:700 19px "SF Mono",Menlo,monospace; color:var(--ink); }}
</style></head><body><div class="sheet">
<div class="eyebrow">PALANTIR UK DEEP DIVE · THE PUBLIC RECORD</div>
<h1>Palantir in the UK</h1>
<div class="sub">What contract notices, spending files, accounts and official returns show</div>
<div class="grid">
  <div class="card"><div class="big">{money(f["total"])}</div><div class="what">awarded to Palantir in <b>{f["n"]} published contracts</b>, {f["y0"]}–{f["y1"]}</div></div>
  <div class="card hit"><div class="big">{f["direct_pct"]:.0f}%<span class="stamp">NO COMPETITION</span></div><div class="what">of that value, <b>{money(f["direct"])}</b>, was awarded directly with no competition</div></div>
  <div class="card"><div class="big">{money(f["paid"])}</div><div class="what">actually paid, from published spending files: <b>a floor, not a total</b></div></div>
  {market_card}
  <div class="card hit"><div class="big">{money(f["uk_ct"])}</div><div class="what">UK corporation tax in {f["tax_year"]}, on <b>{money(f["pbt"])} profit</b> and {money(f["uk_sales"])} of UK sales{f' ({f["rate4"]:.1f}% total tax rate, 2022–25)' if f["rate4"] else ''}</div></div>
  <div class="card"><div class="big">{f["moves"]}</div><div class="what">people moved from senior public roles to Palantir · <b>{access}</b> on record</div></div>
</div>
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
