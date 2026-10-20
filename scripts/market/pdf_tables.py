#!/usr/bin/env python3
"""Read payment lines from the police PDF spend reports.

Three layouts are handled, all from `pdftotext -layout` text (the same command rows_from in
scripts/payments/fetch_scan.py uses; called here directly because str.splitlines() would also
split on the form feeds that some of these PDFs use for the letter f):

- Bedfordshire Police and Cambridgeshire Constabulary, "Transaction Disclosure over £500
  Report": Transaction Reference, Transaction Date, [Received Date], Amount, Supplier Name,
  Expense Area, Category Description. One line per payment.
- Police and Crime Commissioner for Hertfordshire, "Details of Invoices over £500":
  Organisation Name, Transaction Reference, Payment Date, Supplier Name, Cost Centre
  Description, Purpose Of Expenditure, Merchant Category, Net Value. Usually one line per
  payment; one file prints the columns in three blocks, one after another, which are paired
  row by row only when all three blocks have the same number of rows.

A file is read only if every line that carries a money amount is accounted for. Otherwise
the whole file is left out (never a partial sum) and the reason is recorded.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from readers import PROJECT  # noqa: E402

D = r"\d{1,2}/\d{1,2}/\d{2,4}"
AMT = r"\(?-?£?-?[\d,]+\.\d{2}-?\)?"
FORCE_ROW = re.compile(rf"^\s*(\d{{5,}})\s+({D})\s+(?:({D})\s+)?({AMT})\s+(\S.*?)\s*$")
HERTS_ORG = "Police And Crime Commissioner For Hertfordshire"
HERTS_ROW = re.compile(rf"^\s*{HERTS_ORG}\s+(\d{{5,}})(?:\s+({D}))?(?:\s+(\S.*?))?\s+({AMT})\s*$")
HERTS_PART = re.compile(rf"^\s*{HERTS_ORG}\s+(\d{{5,}})(?:\s+({D}))?\s*$")
HERTS_LAST = re.compile(rf"^\s*(\S.*?)\s+({AMT})\s*$")
MONEY = re.compile(r"\d\.\d\d\b")


def _lines(rel_path):
    p = PROJECT / rel_path
    text = subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, timeout=600,
                          check=True).stdout.decode("utf-8", "replace")
    out = []
    for line in text.split("\n"):
        # some PDFs map the letter f to a form feed; a real page break starts a line
        line = re.sub(r"(?<=[A-Za-z])\x0c(?=[A-Za-z ])", "f", line).replace("\x0c", "")
        out.append(line)
    return out


def _date_order(dates):
    first = [int(d.split("/")[0]) for d in dates if d]
    second = [int(d.split("/")[1]) for d in dates if d]
    if any(x > 12 for x in first) and not any(x > 12 for x in second):
        return "dmy"
    if any(x > 12 for x in second) and not any(x > 12 for x in first):
        return "mdy"
    if not any(x > 12 for x in first + second):
        return "dmy-unconfirmed"
    return "mixed"


def _chunks(text):
    return [c.strip() for c in re.split(r"\s{2,}", text.strip()) if c.strip()]


def pdf_records(payer, rel_path, stats):
    from common import parse_amount, parse_date, norm_label  # noqa: E402  (avoid import cycle)
    lines = _lines(rel_path)
    head = " ".join(ln.strip() for ln in lines[:12])
    t = re.search(r"Period\s+\d{1,2}\s+20\d\d", head)
    stats.pdf_title = t.group(0) if t else ""
    if sum("ÿ" in ln for ln in lines) > 20:
        stats.note = "the PDF text cannot be extracted: its font has no character map"
        stats.unreadable = True
        return
    recs, stray = [], []
    if payer == "hertfordshire-pcc":
        parts, middle, last, in_mid, in_last = [], [], [], False, False
        for i, ln in enumerate(lines):
            if not ln.strip():
                continue
            m = HERTS_ROW.match(ln)
            if m:
                ch = _chunks(m.group(3) or "")
                recs.append({"row": i, "txn": m.group(1), "date_raw": m.group(2) or "", "amount_raw": m.group(4),
                             "supplier": ch[0] if ch else "", "category": ch[2] if len(ch) == 4 else None,
                             "chunks": ch})
                continue
            m = HERTS_PART.match(ln)
            if m:
                parts.append((i, m.group(1), m.group(2) or ""))
                continue
            if ln.strip().startswith("Supplier Name") and "Purpose" in ln:
                in_mid, in_last = True, False
                continue
            if ln.strip().startswith("Merchant Category"):
                in_mid, in_last = False, True
                continue
            if in_mid:
                middle.append(_chunks(ln))
                continue
            if in_last:
                m = HERTS_LAST.match(ln)
                if m:
                    last.append((m.group(1), m.group(2)))
                    continue
            if MONEY.search(ln):
                stray.append((i, ln.strip()[:120]))
        if parts:
            if len(parts) == len(middle) == len(last) and all(len(c) == 3 for c in middle):
                for (i, txn, d), mid, (_, amt) in zip(parts, middle, last):
                    recs.append({"row": i, "txn": txn, "date_raw": d, "amount_raw": amt, "supplier": mid[0],
                                 "category": mid[2], "chunks": mid})
                stats.note = (f"columns printed in three blocks; {len(parts)} rows paired block by block "
                              "(equal row counts in each block)")
            else:
                stats.note = (f"rows split across blocks with unequal counts ({len(parts)}/{len(middle)}/{len(last)}); "
                              "file not read")
                stats.unreadable = True
                return
    else:
        for i, ln in enumerate(lines):
            if not ln.strip():
                continue
            m = FORCE_ROW.match(ln)
            if m:
                ch = _chunks(m.group(5))
                recs.append({"row": i, "txn": m.group(1), "date_raw": m.group(2), "amount_raw": m.group(4),
                             "supplier": ch[0] if ch else "", "category": ch[2] if len(ch) == 3 else None,
                             "chunks": ch})
            elif MONEY.search(ln):
                stray.append((i, ln.strip()[:120]))
    if stray:
        stats.note = f"{len(stray)} money lines not matched to a payment row; file not read"
        stats.unparsed.extend(("pdf", i, "unmatched money line", [t]) for i, t in stray[:20])
        stats.unreadable = True
        return
    if not recs:
        stats.note = "no payment rows found in PDF text; file not read"
        stats.unreadable = True
        return
    order = _date_order([r["date_raw"] for r in recs])
    stats.date_order = order
    if order == "mixed":
        stats.note = "dates in both day/month and month/day order; file not read"
        stats.unreadable = True
        return
    stats.sheets_used.append("pdf")
    has_cat = payer in ("hertfordshire-pcc", "bedfordshire-police", "cambridgeshire-pcc")
    catname = "purpose of expenditure" if payer == "hertfordshire-pcc" else "category description"
    if has_cat:
        stats.category_col.add(catname)
    for r in recs:
        amt = parse_amount(r["amount_raw"])
        d = parse_date(r["date_raw"], order="mdy" if order == "mdy" else "dmy") if r["date_raw"] else None
        if d is None:
            stats.unparsed.append(("pdf", r["row"], "date not parsed: " + r["date_raw"], r["chunks"][:4]))
        stats.lines += 1
        yield {"date": d, "date_raw": r["date_raw"], "amount": amt, "supplier": norm_label(r["supplier"]),
               "category": norm_label(r["category"]) if r["category"] else None,
               "category_col": catname, "txn": r["txn"], "entity": "", "sheet": "pdf", "row": r["row"],
               "cells": [r["txn"], r["date_raw"], r["amount_raw"]] + r["chunks"]}
