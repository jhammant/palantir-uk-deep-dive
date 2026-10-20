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

    table = []

    def flush_table():
        nonlocal table
        if not table:
            return
        cells = [[c.strip() for c in row.strip().strip("|").split("|")] for row in table]
        body = [r for r in cells if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]
        head, rows = body[0], body[1:]
        right = [bool(re.fullmatch(r"-{3,}:", c)) for c in (cells[1] if len(cells) > 1 else [])]
        # Right-aligned columns are numeric; any cell that is just a number, money or date never wraps.
        short = re.compile(r"^[\s£$€%+\-–−.,:/0-9()*]*\d[\s£$€%+\-–−.,:/0-9()*]*(bn|m|k)?$|^\d{4}-\d{2}(-\d{2})?$")
        cls = lambda i, c="": (' class="r num"' if i < len(right) and right[i] else (' class="nw"' if short.match(re.sub(r"\*\*", "", c)) else ""))
        out.append('<div class="table-wrap"><table><thead><tr>' + "".join(f"<th{cls(i)}>{inline(c)}</th>" for i, c in enumerate(head))
                   + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td{cls(i, c)}>{inline(c)}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
                   + "</tbody></table></div>")
        table = []

    for line in md.splitlines():
        s = line.rstrip()
        if s.lstrip().startswith("|"):
            flush()
            table.append(s)
            continue
        flush_table()
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
    flush_table()
    return "\n".join(out)


# Which contract buyers belong to each payer in the spend files. Agencies are grouped with their parent
# department only where the relationship is formal (e.g. Crown Commercial Service is a Cabinet Office agency).
PAYER_BUYERS = {
    "NHS England": [r"NHS England", r"ARDEN AND GREATER EAST MIDLANDS", r"NORTH OF ENGLAND COMMISSIONING", r"North of England CSU"],
    "Cabinet Office": [r"Cabinet Office", r"Crown Commercial Service"],
    "Ministry of Housing": [r"LEVELLING UP", r"Housing"],
    "Ministry of Defence": [r"Ministry of Defence", r"^MOD\b"],
    "Department of Health and Social Care": [r"Department of Health and Social Care"],
    "Coventry City Council": [r"COVENTRY"],
    "Department for Environment": [r"Defra", r"Environment, Food"],
    "London Ambulance Service": [r"London Ambulance"],
}
VAT = 1.2       # notices may be published ex-VAT while spend files often show the gross amount
GRACE_DAYS = 92  # invoices can arrive up to a quarter after a contract term ends


def reconcile(payments, contracts):
    """Per payer: what was paid, which notices we found, and what falls outside them."""
    out = []
    counted = [p for p in payments if p.get("counted")]
    for payer in sorted({p["payer"] for p in counted}):
        rows = [p for p in counted if p["payer"] == payer]
        key = next((k for k in PAYER_BUYERS if payer.lower().startswith(k.lower())), None)
        pats = PAYER_BUYERS.get(key, [])
        notices = [c for c in contracts if any(re.search(pt, c.get("buyer") or "", re.I) for pt in pats)]
        notice_total = sum(c["value"] or 0 for c in notices)

        def in_term(p):
            d = (p.get("period") or "")[:10]
            for c in notices:
                start, end = c.get("start") or c.get("awarded"), c.get("end")
                if not (start and end and d):
                    continue
                end_g = (dt.date.fromisoformat(end) + dt.timedelta(days=GRACE_DAYS)).isoformat()
                if start <= d <= end_g:
                    return True
            return False

        paid = sum(p["amount"] or 0 for p in rows)
        outside = [p for p in rows if notices and not in_term(p)]
        out.append({
            "payer": payer,
            "paid": paid,
            "lines": len(rows),
            "first": min((p.get("period") or "")[:10] for p in rows),
            "last": max((p.get("period") or "")[:10] for p in rows),
            "notices": len(notices),
            "notice_total": notice_total,
            "beyond_notices_plus_vat": max(0.0, paid - notice_total * VAT) if notices else None,
            "no_notice_found": not notices,
            "paid_outside_terms": sum(p["amount"] or 0 for p in outside),
            "lines_outside_terms": len(outside),
        })
    return sorted(out, key=lambda r: -r["paid"])


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

    def counted(r):
        """Count only payment lines where Palantir is the published supplier; FOI aggregates overlap them."""
        notes = (r.get("notes") or "").lower()
        return "palantir" in (r.get("supplier_name_as_published") or "").lower() \
            and "supplier is not palantir" not in notes and "aggregate figure" not in notes

    payments, seen_invoices = [], set()
    for r in read_csv("payments.csv"):
        row = {**r, "amount": num(r.get("amount_gbp")), "counted": counted(r), "repeat_of_invoice": False}
        # Some files republish an invoice already listed in an earlier month. Count each invoice once.
        ref = re.search(r"invoice/transaction ref ([^;]+);", r.get("notes") or "")
        inv = (r.get("payer"), ref.group(1).strip(), r.get("amount_gbp")) if ref else None
        if row["counted"] and inv:
            if inv in seen_invoices:
                row["counted"], row["repeat_of_invoice"] = False, True
            seen_invoices.add(inv)
        payments.append(row)

    reconciliation = reconcile(payments, contracts)

    notes = {}
    for name in ("tax-notes", "payments-notes", "influence-notes", "sovereignty-notes", "revolving-door-notes", "market-notes"):
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
        "revolving": sorted(read_csv("revolving-door.csv"), key=lambda r: r.get("joined_palantir") or r.get("left_public_office") or ""),
        "market": read_csv("market-share.csv"),
        "marketTop": read_csv("market-top-suppliers.csv"),
        "reconciliation": reconciliation,
        "groupTax": [{**r, "amount": num(r.get("amount_usd"))} for r in read_csv("palantir-group-tax.csv")],
        "notes": notes,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(bundle, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    OUT.write_text(f"window.PUK = {payload};\n")
    counts = {k: len(v) for k, v in bundle.items() if isinstance(v, list)}
    print(f"wrote {OUT.relative_to(ROOT)}: {counts}, notes: {sorted(notes)}")


if __name__ == "__main__":
    build()
