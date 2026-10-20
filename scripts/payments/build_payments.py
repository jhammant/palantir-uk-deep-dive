#!/usr/bin/env python3
"""Build data/payments.csv from work/lines.jsonl plus PDF lines and FOI disclosures (all hand-checked)."""
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

WORK = Path(__file__).resolve().parents[2] / "sources" / "raw" / "payments" / "_work"  # local, not published
OUT = Path(__file__).resolve().parents[2] / "data" / "payments.csv"
FIELDS = ["payer", "payer_type", "period", "amount_gbp", "supplier_name_as_published",
          "description_as_published", "source_file_url", "source_page_url", "notes"]

PAYERS = {
    "ministry-of-defence": ("Ministry of Defence", "central"),
    "dhsc": ("Department of Health and Social Care", "central"),
    "cabinet-office": ("Cabinet Office", "central"),
    "mhclg": ("Ministry of Housing, Communities and Local Government (DLUHC Sep 2021 to Jul 2024)", "central"),
    "defra": ("Department for Environment, Food and Rural Affairs", "central"),
    "ukhsa": ("UK Health Security Agency", "central"),
    "nhs-england": ("NHS England", "nhs"),
    "chelsea-and-westminster-hospital-nhs-ft": ("Chelsea and Westminster Hospital NHS Foundation Trust", "nhs"),
    "london-ambulance-service": ("London Ambulance Service NHS Trust", "nhs"),
    "bedfordshire-police": ("Bedfordshire Police", "police"),
    "cambridgeshire-pcc": ("Cambridgeshire Constabulary", "police"),
    "coventry-city-council": ("Coventry City Council", "council"),
}

# columns whose values describe the payment (never personal-name columns such as Director)
DESC_COLS = ["expense type", "expense area", "narrative", "description", "po line description", "po description",
             "payment description", "proclass(t)", "directorate(t)", "cost centre(t)", "account code(t)",
             "category description", "purpose"]
SKIP_COLS = ("director", "postcode", "post code", "postal code", "vat", "d-u-n-s", "sme", "sole trader",
             "voluntary", "grant?", "supplier type", "vendor account", "item text", "purchasing item text",
             "pspes", "profit center")

MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def parse_date(s):
    s = s.strip()
    if not s:
        return None
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})(?: 00:00:00)?", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)  # UK day/month/year
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.fullmatch(r"(\d{1,2})[ -]([A-Za-z]+)[ -](\d{2,4})", s)
    if m:
        mon = MONTHS[m.group(2)[:3].lower()]
        y = int(m.group(3))
        y = y + 2000 if y < 100 else y
        return f"{y}-{mon:02d}-{int(m.group(1)):02d}"
    raise ValueError("unparsed date " + s)


def parse_amount(s):
    t = s.replace("£", "").replace(",", "").replace("\xa0", "").strip()
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()")
    v = float(t)
    v = -v if neg else v
    return f"{v:.2f}"


def describe(header, cells):
    parts = []
    for i, h in enumerate(header or []):
        hl = h.strip().lower()
        if i >= len(cells) or not cells[i].strip():
            continue
        if any(x in hl for x in SKIP_COLS) and not hl.startswith("directorate"):
            continue
        if any(hl == d or hl.startswith(d) for d in DESC_COLS):
            parts.append(f"{h.strip()}: {' '.join(cells[i].split())}")
    # de-duplicate identical values (e.g. Narrative repeated in Purchasing Item Text)
    seen, out = set(), []
    for p in parts:
        v = p.split(": ", 1)[1]
        if v in seen:
            continue
        seen.add(v)
        out.append(p)
    return "; ".join(out)


def col(header, cells, *names):
    for n in names:
        for i, h in enumerate(header or []):
            if h.replace(" ", "").lower() == n.replace(" ", "") and i < len(cells):
                return cells[i].strip()
    return ""


def main():
    lines = [json.loads(l) for l in open(WORK / "lines.jsonl")]
    rows = []
    txn_count = Counter()
    for x in lines:
        f, h, c = x["fields"], x["header"], x["cells"]
        if x["payer"] in ("bedfordshire-police", "cambridgeshire-pcc") and x["sheet"] == "pdf":
            continue  # handled below
        txn_count[(x["saved"], f.get("txn"))] += 1
    for x in lines:
        f, h, c = x["fields"], x["header"], x["cells"]
        payer, ptype = PAYERS[x["payer"]]
        if x["sheet"] == "pdf":
            continue
        notes = []
        supplier = f["supplier"]
        if x["payer"] == "coventry-city-council":
            supplier = col(h, c, "supplier(t)")
            date = parse_date(col(h, c, "transaction date"))
            amount = parse_amount(col(h, c, "amount"))
            notes.append(f"Coventry supplier code {col(h, c, 'supplier')}; transaction no {col(h, c, 'transaction no')}; "
                         f"council period {col(h, c, 'period')}")
        else:
            date = parse_date(f["date"])
            amount = parse_amount(f["amount"])
        desc = describe(h, c)
        if x["payer"] == "coventry-city-council":
            desc = "; ".join(f"{k}: {col(h, c, k.lower())}" for k in ("Proclass(T)", "Directorate(T)", "Cost Centre(T)", "Account Code(T)") if col(h, c, k.lower()))
        ent = f.get("entity") or ""
        if ent and x["payer"] in ("nhs-england", "mhclg", "ukhsa", "dhsc", "cabinet-office"):
            notes.append(f"Entity as published: {ent}")
        if f.get("txn") and x["payer"] != "coventry-city-council":
            label = "invoice/transaction ref" if x["payer"] in ("dhsc", "defra") else "transaction number"
            notes.append(f"{label} {f['txn']}")
        if x["payer"] == "nhs-england":
            inv = col(h, c, "purchase invoice number")
            if inv:
                notes.append(f"invoice {inv}")
        if txn_count[(x["saved"], f.get("txn"))] > 1 and f.get("txn"):
            notes.append(f"transaction number appears on {txn_count[(x['saved'], f.get('txn'))]} lines in this file")
        if float(amount) < 0:
            notes.append("negative amount as published (credit/reversal)")
        if not re.search(r"palantir", supplier, re.I):
            notes.append("SUPPLIER IS NOT PALANTIR: line mentions Palantir in its description only; excluded from totals of payments to Palantir")
        notes.append(f"date as published: {f['date'] if x['payer'] != 'coventry-city-council' else col(h, c, 'transaction date')}")
        notes.append(f"saved copy: {x['saved']}")
        rows.append({"payer": payer, "payer_type": ptype, "period": date, "amount_gbp": amount,
                     "supplier_name_as_published": supplier, "description_as_published": desc,
                     "source_file_url": x["file_url"], "source_page_url": x["page_url"], "notes": "; ".join(notes)})

    # PDF lines (checked by hand against pdftotext output)
    beds_page = "https://www.beds.police.uk/foi-ai/bedfordshire-police/what-we-spend-and-how-we-spend-it/payments-over-500/payments-over-500-during-2025262/"
    rows.append({"payer": "Bedfordshire Police", "payer_type": "police", "period": "2025-11-30", "amount_gbp": "900000.00",
                 "supplier_name_as_published": "Palantir Technologies Uk Ltd",
                 "description_as_published": "Expense Area: Home Force",
                 "source_file_url": "https://www.beds.police.uk/SysSiteAssets/foi-media/bedfordshire/payment-over-500/202526/transactions-over-500-disclosure---december-2025.pdf",
                 "source_page_url": beds_page,
                 "notes": "PDF 'Transaction Disclosure over £500 Report, Period 9 2025'; transaction reference 232778; transaction date as published 30/11/2025; saved copy: sources/raw/payments/bedfordshire-police/transactions-over-500-disclosure---december-2025.pdf"})
    rows.append({"payer": "Cambridgeshire Constabulary", "payer_type": "police", "period": "2025-08-05", "amount_gbp": "11998.80",
                 "supplier_name_as_published": "Palantir Technologies Uk Ltd",
                 "description_as_published": "Expense Area: Home Force; Category Description: PROVISION OF GOODS & SERVICE",
                 "source_file_url": "https://www.cambridgeshire-pcc.gov.uk/SysSiteAssets/media/downloads/cambs-pcc/money-downloads/spend-over-500-2025/transactions-over-500-disclosure-p5-2025-26.pdf",
                 "source_page_url": "https://www.cambridgeshire-pcc.gov.uk/what-we-do/money/spend-over-500/",
                 "notes": "Published by the Police and Crime Commissioner for Cambridgeshire and Peterborough ('Transaction Disclosure over £500 Report, Period 5 2025'); transaction reference 189575; transaction date as published 8/5/25 and received date 8/13/25 (file uses month/day/year); saved copy: sources/raw/payments/cambridgeshire-pcc/transactions-over-500-disclosure-p5-2025-26.pdf"})
    # FOI disclosure (aggregate, not a single payment line)
    rows.append({"payer": "Ministry of Defence", "payer_type": "central", "period": "2021-01-01 to 2024-07-03",
                 "amount_gbp": "79100169.11", "supplier_name_as_published": "Palantir",
                 "description_as_published": "\"The amount spent from 01/01/2021, for contracts that can be published, is £79,100,169.11.\"",
                 "source_file_url": "https://www.whatdotheyknow.com/request/palantir_contracts_foi_request_u_19/response/2693480/attach/3/20240614%20Amin%20FOI2024%2004261%201.pdf",
                 "source_page_url": "https://www.whatdotheyknow.com/request/palantir_contracts_foi_request_u_19",
                 "notes": "FOI response FOI2024/04261 dated 3 July 2024 (aggregate figure, not a payment line). The request asked for payments since 01/01/2022; the response gives a figure from 01/01/2021 and covers only 'contracts that can be published'; other contracts withheld under FOIA s24, s26, s43. Overlaps the MoD spend-file lines for 2021-2022, so it must not be added to them. saved copy: sources/raw/payments/ministry-of-defence/foi/20240614 Amin FOI2024 04261 1.pdf"})

    rows.sort(key=lambda r: (r["payer"], r["period"], r["amount_gbp"]))
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "rows written", file=sys.stderr)


if __name__ == "__main__":
    main()
