#!/usr/bin/env python3
"""Bundle everything in data/ into site/assets/bundle.js so the site runs with no server and no build tools.

Run after any change to data/:
    python3 scripts/build_site.py

The site reads window.PUK. Missing data files are fine: their pages show "research in progress".
"""
import csv
import datetime as dt
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "site" / "assets" / "bundle.js"

SECTORS = [  # order is the chart's colour order; keep it fixed
    ("Health", r"\bNHS\b|health|hospital|commissioning|ambulance|integrated care|\bCSU\b|foundation trust"),
    ("Defence", r"defence|\bMOD\b"),
    ("Policing & Home Office", r"police|policing|home office|firearms|blue ?light"),
    ("Energy", r"energy|\bNESO\b|grid"),
    ("Central government", r"."),
    ("Local government", r"council|combined authority|borough"),
]


def sector_of(buyer):
    b = buyer or ""
    for name, pattern in SECTORS:
        if name == "Central government":
            continue
        if re.search(pattern, b, re.I):
            return name
    return "Central government"


def route_of(row):
    p = (row.get("procedure") or "").lower()
    text = f"{row.get('notes', '')} {row.get('title', '')}".lower()
    if "direct" in p:
        return "Direct award", "notice"
    if "calloff" in p or "framework" in p:
        return "Framework call-off", "notice"
    if any(k in p for k in ("open", "competitive", "selective", "restricted")):
        return "Competitive", "notice"
    if p == "other":
        return "Other", "notice"
    if "g-cloud" in text or "g cloud" in text or "framework" in text:
        return "Framework call-off", "notice description"
    return "Not stated", ""


def read_csv(name):
    path = DATA / name
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return [{k: (v or "").strip() for k, v in r.items() if k} for r in csv.DictReader(f)]


def read_json(name):
    path = DATA / name
    return json.loads(path.read_text()) if path.exists() else []


def num(v):
    try:
        return float(str(v).replace(",", "").replace("£", "")) if str(v).strip() else None
    except ValueError:
        return None


def md_to_html(md):
    """Small, safe Markdown subset: headings, paragraphs, lists, quotes, bold, italics, code, links."""
    def inline(s):
        s = html.escape(s, quote=False)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                   lambda m: f'<a href="{html.escape(m.group(2))}" rel="noopener">{m.group(1)}</a>', s)
        s = re.sub(r"(?<![\"=>])(https?://[^\s<)]+)", r'<a href="\1" rel="noopener">\1</a>', s)
        return s

    out, para, items, kind = [], [], [], None

    def flush():
        nonlocal para, items, kind
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para = []
        if items:
            out.append(f"<{kind}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{kind}>")
            items, kind = [], None

    for line in md.splitlines():
        s = line.rstrip()
        if not s.strip():
            flush()
            continue
        if m := re.match(r"^(#{1,4})\s+(.*)", s):
            flush()
            level = min(len(m.group(1)) + 1, 5)
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
        elif m := re.match(r"^\s*[-*]\s+(.*)", s):
            if para:
                flush()
            if kind not in (None, "ul"):
                flush()
            kind = "ul"
            items.append(m.group(1))
        elif m := re.match(r"^\s*\d+[.)]\s+(.*)", s):
            if para:
                flush()
            if kind not in (None, "ol"):
                flush()
            kind = "ol"
            items.append(m.group(1))
        elif s.startswith(">"):
            flush()
            out.append(f"<blockquote>{inline(s.lstrip('> '))}</blockquote>")
        elif items and line.startswith(("  ", "\t")):
            items[-1] += " " + s.strip()
        else:
            if items:
                flush()
            para.append(s.strip())
    flush()
    return "\n".join(out)


def build():
    contracts = []
    for r in read_csv("contracts.csv"):
        route, route_basis = route_of(r)
        contracts.append({
            **r,
            "value": num(r.get("value_gbp")),
            "year": (r.get("awarded") or "")[:4],
            "sector": sector_of(r.get("buyer")),
            "route": route,
            "route_basis": route_basis,
        })

    tax = [{**r, **{k: num(r.get(k)) for k in (
        "turnover_gbp", "uk_turnover_gbp", "profit_before_tax_gbp", "tax_charge_total_gbp",
        "uk_corporation_tax_current_gbp", "tax_at_standard_rate_gbp", "standard_rate", "avg_employees")}}
        for r in read_csv("tax.csv")]
    tax.sort(key=lambda r: r.get("year_end") or "")

    payments = [{**r, "amount": num(r.get("amount_gbp"))} for r in read_csv("payments.csv")]

    notes = {}
    for name in ("tax-notes", "payments-notes", "influence-notes", "sovereignty-notes"):
        path = DATA / f"{name}.md"
        if path.exists():
            notes[name] = md_to_html(path.read_text())

    bundle = {
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "sectors": [s for s, _ in SECTORS],
        "contracts": contracts,
        "tax": tax,
        "payments": payments,
        "influence": sorted(read_csv("influence.csv"), key=lambda r: r.get("date", ""), reverse=True),
        "timeline": sorted(read_csv("timeline.csv"), key=lambda r: r.get("date", "")),
        "quotes": sorted(read_json("quotes.json"), key=lambda r: r.get("date", "")),
        "notes": notes,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(bundle, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    OUT.write_text(f"window.PUK = {payload};\n")
    counts = {k: len(v) for k, v in bundle.items() if isinstance(v, list)}
    print(f"wrote {OUT.relative_to(ROOT)}: {counts}, notes: {sorted(notes)}")


if __name__ == "__main__":
    build()
