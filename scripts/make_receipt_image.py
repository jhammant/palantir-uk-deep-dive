#!/usr/bin/env python3
"""Render img/palantir-bill-full.png: the itemised "UK's Palantir bill" receipt, from the site's data bundle.

    python3 scripts/build_site.py && python3 scripts/make_receipt_image.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "site" / "assets" / "bundle.js"
OUT_HTML = ROOT / "img" / "palantir-bill-full.html"
OUT_PNG = ROOT / "img" / "palantir-bill-full.png"
SITE = "jhammant.github.io/palantir-uk-deep-dive"
LINES = [  # (match on title, buyer pattern, label) for the itemised awards, biggest first
    (r"MOD Palantir Enterprise Agreement", r"Defence", "MoD enterprise agreement, 2025"),
    (r"Federated Data Platform", r"NHS England", "NHS Federated Data Platform, 2023*"),
    (r"UK MoD\s+Enterprise Agreement", r"DEFENCE", "MoD enterprise agreement, 2022"),
    (r"Foundry Data Connector", r"Crown Commercial", "Crown Commercial Service, 2020"),
    (r"Transition & Exit", r"NHS England", 'NHS "Transition & Exit" from Palantir, 2023'),
    (r"National Health Service Commissioning Board", r"ARDEN", "NHS Covid data platform, 2020"),
    (r"NESO Interim Capability", r"ENERGY SYSTEM", "NESO, the grid operator, 2026"),
]


def money(v):
    if v is None:
        return "n/a"
    return f"£{v / 1e9:.2f}bn" if v >= 1e9 else f"£{v / 1e6:.1f}m" if v >= 1e6 else f"£{v / 1e3:.0f}k"


def usd(v):
    return f"${v / 1e6:.1f}m"


def num(v):
    try:
        return float(str(v).replace(",", "").replace("£", ""))
    except (TypeError, ValueError):
        return None


def build(d):
    e = html.escape
    C = d["contracts"]
    total = sum(c["value"] or 0 for c in C)
    used, rows = set(), []
    for title_rx, buyer_rx, label in LINES:
        c = next((c for i, c in enumerate(C) if i not in used and re.search(title_rx, c["title"], re.I) and re.search(buyer_rx, c["buyer"], re.I)), None)
        if c:
            used.add(C.index(c))
            rows.append((label, c["value"] or 0, c["route"] == "Direct award"))
    rest = [c for i, c in enumerate(C) if i not in used]
    direct = sum(c["value"] or 0 for c in C if c["route"] == "Direct award")
    paid = sum(p["amount"] or 0 for p in d["payments"] if p.get("counted"))
    R = d.get("reconciliation", [])
    no_notice = sum(r["paid"] for r in R if r["no_notice_found"])
    beyond = sum(r["beyond_notices_plus_vat"] for r in R
                 if r["beyond_notices_plus_vat"] and r["beyond_notices_plus_vat"] > max(50000, 0.05 * r["notice_total"] * 1.2))

    mk = {r["payer"]: r for r in d.get("market", []) if r["period"] == "all"}
    yr = {(r["payer"], r["period"]): r for r in d.get("market", [])}
    nhs, co = mk.get("NHS England"), yr.get(("Cabinet Office", "2021"))
    nhs_rank = next((t["rank"] for t in d.get("marketTop", []) if t["payer"] == "NHS England" and t["period"] == "all" and "PALANTIR" in t["supplier"].upper()), None)

    g = d.get("groupTax", [])
    gt = lambda j, m: next((r["amount"] for r in g if r["jurisdiction"] == j and r["measure"] == m and r["year"] == "2025"), None)
    uk_cash, uk_rev = gt("United Kingdom", "cash_income_tax_upper_bound"), gt("United Kingdom", "revenue")
    others = [(j, gt(j, "cash_income_tax")) for j in ("South Korea", "Japan", "France", "Germany")]

    moved = {r["person"] for r in d.get("revolving", []) if r.get("direction") == "gov-to-palantir"}
    mins = re.search(r"list (\d+) ministerial meetings", d["notes"].get("influence-notes", ""))
    tax = d["tax"]
    recent = [t for t in tax if t["year_end"][:4] >= "2022"]
    rate = 100 * sum(t["tax_charge_total_gbp"] or 0 for t in recent) / sum(t["profit_before_tax_gbp"] or 0 for t in recent)

    # The tax box: everything to scale, so the gap is visible at a glance.
    import math
    cents = math.ceil(10000 * uk_cash / uk_rev)  # cents of income tax per $100 of UK revenue; rounded up, since uk_cash is an upper bound
    pbt = tax[-1]["profit_before_tax_gbp"]
    mx = max(v for _, v in others if v)
    bars = "".join(
        f'<div class="cbar"><span class="cn">{e(j)}</span><span class="ct"><span class="cf" style="width:{100 * v / mx:.1f}%"></span></span><span class="cv">{usd(v)}</span></div>'
        for j, v in others if v)
    bars += (f'<div class="cbar uk"><span class="cn">United Kingdom</span><span class="ct"><span class="cf" style="width:{100 * uk_cash / mx:.1f}%"></span></span>'
             f'<span class="cv">under {usd(uk_cash)}</span></div>')
    tax_box = f"""
    <div class="taxbox">
      <div class="section">TAX, 2025 · PALANTIR'S OWN ANNUAL REPORT</div>
      <div class="scale"><span class="lbl">Revenue from UK customers</span><span class="val">{usd(uk_rev)}</span></div>
      <div class="bar"><span style="width:100%"></span></div>
      <div class="scale hit"><span class="lbl">UK cash income tax paid</span><span class="val">under {usd(uk_cash)}</span></div>
      <div class="bar tax"><span style="width:{max(0.4, 100 * uk_cash / uk_rev):.2f}%"></span><em>← to scale</em></div>
      <div class="big">Under {cents}¢ in every $100.</div>
      <div class="sub2">Palantir paid more income tax in each of these countries, none of which is even 10% of its revenue. The UK is 10%.</div>
      {bars}
      <div class="fine">Income tax is charged on profit; Palantir's UK company reported {money(pbt)} profit before tax for {tax[-1]['year_end'][:4]}, and a {rate:.1f}% net tax rate for 2022–{tax[-1]['year_end'][:4]} (its UK accounts).</div>
    </div>"""

    def line(label, amount, stamp=False, cls=""):
        st = '<span class="tag">NO COMPETITION</span>' if stamp else ""
        return f'<div class="row {cls}"><span class="what">{e(label)}{st}</span><span class="amt">{amount}</span></div>'

    award_lines = "".join(line(lbl, money(v), stamp) for lbl, v, stamp in rows)
    award_lines += line(f"{len(rest)} smaller awards", money(sum(c["value"] or 0 for c in rest)), cls="small")
    sections = f"""
    <div class="section">CONTRACTS AWARDED, 2015–2026</div>
    {award_lines}
    <div class="rule"></div>
    {line("TOTAL", money(total), cls="total")}
    {line(f"  of which, no competition", f"{money(direct)} · {100 * direct / total:.0f}%", cls="hitline")}
    <div class="rule"></div>
    <div class="section">MONEY ACTUALLY PAID (SPEND FILES)</div>
    {line("Paid to Palantir (a floor, not a total)", money(paid))}
    {line("Paid with no Palantir notice found", money(no_notice))}
    {line("Paid beyond notice values, even +20% VAT", money(beyond))}
    <div class="rule"></div>
    <div class="section">SHARE OF IT SPENDING</div>
    {line(f"NHS England, Apr–Sep 2025 · no. {nhs_rank} supplier" if nhs_rank else "NHS England, Apr–Sep 2025", f'{100 * num(nhs["palantir_share_of_it"]):.1f}%') if nhs else ""}
    {line("Cabinet Office, 2021", f'{100 * num(co["palantir_share_of_it"]):.1f}%') if co else ""}
    <div class="rule"></div>
    {tax_box}
    <div class="rule"></div>
    <div class="section">ACCESS</div>
    {line("Ministerial meetings on record", mins.group(1) if mins else "n/a")}
    {line("People moved from UK public roles", str(len(moved)))}
    {line("  incl. an MoD Second Permanent Secretary", "", cls="small")}
    {line("  and an Armed Forces Minister", "", cls="small")}
    """
    words = [
        ("“Buying our way in…!”", "Louis Mosley, who runs Palantir in the UK: subject line of a 2021 internal email about the NHS (Bloomberg). Palantir called it “regrettable”; he calls it “a thought experiment”."),
        ("“The NHS makes people sick.”", "Peter Thiel, Palantir's chairman and co-founder, Oxford Union speech, 2023"),
        ("“proprietary architecture licensed exclusively by Palantir”", "NESO, giving Palantir £21.2m with no competition: switching “is not possible without significant cost”, 2026"),
    ]
    quotes = "".join(f'<div class="q"><div class="qt">{e(q)}</div><div class="qw">{e(w)}</div></div>' for q, w in words)
    return f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>The UK's Palantir bill</title><style>
:root {{ --bg:#16181b; --paper:#f5f1e6; --ink:#1c1c1c; --muted:#6b665c; --rule:#b9b2a2; --red:#c4122f; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html, body {{ width:1080px; height:1920px; }}
body {{ background:var(--bg); display:flex; align-items:center; justify-content:center; font-family:"SF Mono",Menlo,"DejaVu Sans Mono",monospace; color:var(--ink); }}
.receipt {{ width:900px; background:var(--paper); padding:44px 54px 36px; box-shadow:0 30px 80px rgba(0,0,0,.55);
  -webkit-mask: conic-gradient(from -45deg at bottom, #0000, #000 1deg 89deg, #0000 90deg) bottom/24px 51% repeat-x,
                conic-gradient(from 135deg at top, #0000, #000 1deg 89deg, #0000 90deg) top/24px 51% repeat-x; }}
.head {{ text-align:center; }}
.eyebrow {{ font-size:18px; letter-spacing:.26em; color:var(--muted); }}
h1 {{ font-family:"Helvetica Neue",Helvetica,Arial,sans-serif; font-weight:800; font-size:58px; letter-spacing:-.02em; margin:8px 0 6px; }}
.sub {{ font-size:18px; color:var(--muted); }}
.rule {{ border-top:2px dashed var(--rule); margin:11px 0 8px; }}
.section {{ font-size:15px; letter-spacing:.2em; color:var(--muted); margin:6px 0 6px; }}
.row {{ display:grid; grid-template-columns:1fr auto; gap:14px; font-size:19px; line-height:1.22; padding:3px 0; align-items:baseline; }}
.row .amt {{ font-weight:700; font-variant-numeric:tabular-nums; white-space:nowrap; }}
.row.small {{ color:var(--muted); font-size:17px; padding:2px 0; }}
.row.total {{ font-size:30px; font-weight:800; }}
.row.total .amt {{ font-size:38px; }}
.row.hitline .amt, .row.hitline .what {{ color:var(--red); font-weight:700; }}
.tag {{ display:inline-block; margin-left:10px; vertical-align:2px; border:2px solid var(--red); color:var(--red); font-size:12px; font-weight:800; letter-spacing:.12em; padding:2px 6px; transform:rotate(-3deg); }}
.taxbox {{ border:3px solid var(--ink); padding:16px 18px 14px; margin:4px 0 6px; background:#fbf8ef; }}
.taxbox .section {{ margin-top:0; }}
.scale {{ display:grid; grid-template-columns:1fr auto; font-size:21px; margin-top:8px; }}
.scale .val {{ font-weight:800; font-size:24px; }}
.scale.hit .lbl, .scale.hit .val {{ color:var(--red); font-weight:800; }}
.bar {{ height:22px; background:#e6e0d1; margin:6px 0 2px; position:relative; }}
.bar span {{ display:block; height:100%; background:var(--ink); }}
.bar.tax {{ background:#efe9db; }}
.bar.tax span {{ background:var(--red); }}
.bar em {{ position:absolute; left:14px; top:0; font-style:normal; font-size:14px; color:var(--red); line-height:22px; font-weight:700; }}
.big {{ font-family:"Helvetica Neue",Helvetica,Arial,sans-serif; font-size:40px; font-weight:800; color:var(--red); margin:10px 0 2px; letter-spacing:-.01em; }}
.sub2 {{ font-size:16px; color:var(--ink); line-height:1.4; margin:4px 0 10px; }}
.cbar {{ display:grid; grid-template-columns:170px 1fr 130px; gap:10px; align-items:center; font-size:17px; margin:3px 0; }}
.cbar .ct {{ height:16px; background:#e6e0d1; }}
.cbar .cf {{ display:block; height:100%; background:#8f897d; }}
.cbar .cv {{ text-align:right; font-weight:700; }}
.cbar.uk .cn, .cbar.uk .cv {{ color:var(--red); font-weight:800; }}
.cbar.uk .cf {{ background:var(--red); }}
.fine {{ font-size:13.5px; color:var(--muted); line-height:1.4; margin-top:10px; }}
.q {{ margin:8px 0; }}
.qt {{ font-family:"Helvetica Neue",Helvetica,Arial,sans-serif; font-size:23px; font-weight:800; line-height:1.2; }}
.qw {{ font-size:15px; color:var(--muted); line-height:1.4; margin-top:5px; }}
.foot {{ font-size:14px; color:var(--muted); line-height:1.5; margin-top:14px; }}
.foot b {{ color:var(--ink); }}
</style></head><body><div class="receipt">
<div class="head"><div class="eyebrow">UK PUBLIC SECTOR → PALANTIR</div><h1>The UK's Palantir bill</h1><div class="sub">Itemised from the public record · October 2026</div></div>
<div class="rule"></div>
{sections}
<div class="rule"></div>
<div class="section">IN THEIR OWN WORDS</div>
{quotes}
<div class="rule"></div>
<div class="foot">Values as published. *Initial term; widely reported as £330m over seven years.<br>
Sources: Contracts Finder · Find a Tender · government spend files · Companies House 07042994 · Palantir 10-K 2025<br>
<b>{SITE}</b> · Compiled by Jon Hammant (Orbital)</div>
</div></body></html>"""


def main():
    raw = BUNDLE.read_text()
    d = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    OUT_HTML.write_text(build(d))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=2)
        pg.goto(OUT_HTML.resolve().as_uri())
        pg.wait_for_timeout(300)
        h = pg.evaluate("document.querySelector('.receipt').getBoundingClientRect().height")
        pg.screenshot(path=str(OUT_PNG))
        b.close()
    print(f"receipt height {h:.0f}px of 1920; wrote {OUT_PNG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
