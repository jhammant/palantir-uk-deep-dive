#!/usr/bin/env python3
"""Turn each saved spend file into normalised payment lines.

iter_file(payer, rel_path) yields one dict per published payment line:
    date (ISO or None), date_raw, amount (Decimal), supplier, category (label or None),
    category_col, txn, entity, sheet, row, cells
and records every skipped line (headers, totals, blanks, unparsed) in a FileStats object.

Column names differ between publishers and between years, so each field is found by
an ordered list of header names. Paths are relative to the project root.
"""
import csv
import re
import sys
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from readers import PROJECT, file_rows  # noqa: E402
from pdf_tables import pdf_records  # noqa: E402

MANIFEST = PROJECT / "data" / "payments-files-checked.csv"

PAYERS = {
    "ministry-of-defence": ("Ministry of Defence", "central"),
    "dhsc": ("Department of Health and Social Care", "central"),
    "cabinet-office": ("Cabinet Office", "central"),
    "mhclg": ("Ministry of Housing, Communities and Local Government (DLUHC Sep 2021 to Jul 2024)", "central"),
    "defra": ("Department for Environment, Food and Rural Affairs", "central"),
    "hm-treasury": ("HM Treasury", "central"),
    "home-office": ("Home Office", "central"),
    "ukhsa": ("UK Health Security Agency (Public Health England before October 2021)", "central"),
    "dbt": ("Department for Business and Trade", "central"),
    "nhs-england": ("NHS England", "nhs"),
    "nhs-improvement-monitor-tda": ("Monitor and NHS Trust Development Authority (NHS Improvement)", "nhs"),
    "chelsea-and-westminster-hospital-nhs-ft": ("Chelsea and Westminster Hospital NHS Foundation Trust", "nhs"),
    "london-ambulance-service": ("London Ambulance Service NHS Trust", "nhs"),
    "bedfordshire-police": ("Bedfordshire Police", "police"),
    "cambridgeshire-pcc": ("Cambridgeshire Constabulary", "police"),
    "hertfordshire-pcc": ("Police and Crime Commissioner for Hertfordshire", "police"),
    "coventry-city-council": ("Coventry City Council", "council"),
}

DATE_COLS = ["payment date", "date of payment", "date paid", "transaction date", "date",
             "invoice date", "invoice entered date"]
AMOUNT_COLS = ["ap amount (£)", "amount in sterling", "amount", "spend", "total", "net value",
               "line amount sum", "invoice amount", "paid amount £"]
SUPPLIER_COLS = ["supplier(t)", "supplier (t)", "supplier(t) 2", "supplier name", "supplier"]
TXN_COLS = ["transaction number", "transction number", "transaction no", "transaction reference",
            "voucher number", "po/voucher number", "invoice number", "invoice no", "invoice id",
            "reference no", "their reference", "purchase invoice number"]
ENTITY_COLS = ["entity", "organisation name"]

# The column whose published labels are classified as IT/software/data or not.
# First name present in a sheet's header wins. A sheet with none of them has no category.
CATEGORY_COLS = {
    "default": ["expense type", "expense type for report"],
    "hm-treasury": ["expense type", "account code description"],
    "ukhsa": ["expense type", "subjective level 4"],
    "coventry-city-council": ["account code(t)"],
    "bedfordshire-police": ["category description"],
    "cambridgeshire-pcc": ["category description"],
    "hertfordshire-pcc": ["merchant category"],
}

# Files saved in the manifest that are not spend data (web pages or FOI letters).
NOT_SPEND_DATA = {
    "sources/raw/payments/defra/financial-transactions-data-defra":
        "data.gov.uk web page saved instead of the March 2020 spend file; no spend rows",
    "sources/raw/payments/defra/spend-over-25-000-in-the-department-for-environment-food-and-rural-affairs":
        "data.gov.uk web page saved instead of the January 2020 spend file; no spend rows",
}

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def norm_header(h):
    return re.sub(r"\s+", " ", (h or "").replace("\xa0", " ")).strip().lower()


def norm_label(s):
    return re.sub(r"\s+", " ", (s or "").replace("\xa0", " ")).strip()


def parse_amount(s):
    t = (s or "").replace("£", "").replace(",", "").replace("\xa0", "").replace(" ", "").strip()
    if not t:
        return None
    neg = False
    if t.startswith("(") and t.endswith(")"):
        neg, t = True, t[1:-1]
    if t.endswith("-") and t[:-1].replace(".", "", 1).isdigit():
        neg, t = True, t[:-1]
    try:
        v = Decimal(t)
    except InvalidOperation:
        return None
    if not v.is_finite():
        return None
    return -v if neg else v


def parse_date(s, order="dmy"):
    """Return ISO date or None. order is 'dmy' (UK) or 'mdy' (US) for slash dates."""
    s = (s or "").strip()
    if not s:
        return None
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})(?:[ T]00:00:00(?:\.0+)?)?", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.fullmatch(r"(\d{1,2})[/.](\d{1,2})[/.](\d{2}|\d{4})", s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = y + 2000 if y < 100 else y
        d, mo = (a, b) if order == "dmy" else (b, a)
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return f"{y}-{mo:02d}-{d:02d}"
        return None
    m = re.fullmatch(r"(\d{1,2})[ -]([A-Za-z]{3,9})[ -](\d{2}|\d{4})", s)
    if m and m.group(2)[:3].lower() in MONTHS:
        y = int(m.group(3))
        y = y + 2000 if y < 100 else y
        return f"{y}-{MONTHS[m.group(2)[:3].lower()]:02d}-{int(m.group(1)):02d}"
    m = re.fullmatch(r"(\d{5})(?:\.0+)?", s)  # Excel serial day number
    if m and 40000 < int(m.group(1)) < 50000:
        from datetime import date, timedelta
        return (date(1899, 12, 30) + timedelta(days=int(m.group(1)))).isoformat()
    return None


def find_col(header, names):
    for n in names:
        for i, h in enumerate(header):
            if h == n:
                return i
    return None


@dataclass
class FileStats:
    path: str
    sheets_used: list = field(default_factory=list)
    sheets_skipped: list = field(default_factory=list)
    lines: int = 0
    skipped_blank_or_text: int = 0
    skipped_total_rows: list = field(default_factory=list)   # (sheet,row,amount,cells)
    unparsed: list = field(default_factory=list)             # (sheet,row,reason,cells)
    category_col: set = field(default_factory=set)
    no_category_sheets: list = field(default_factory=list)
    date_order: str = "dmy"
    note: str = ""


HEADER_KEYS = ("supplier", "amount", "vendor", "payee", "merchant", "date", "value", "expense",
               "description", "transaction", "spend", "total")


def looks_like_header(cells):
    low = [norm_header(c) for c in cells]
    if sum(bool(c) for c in low) < 3:
        return False
    joined = " | ".join(low)
    numeric = sum(bool(re.fullmatch(r"[£\-]?[\d,]+(\.\d+)?", c)) for c in low if c)
    return sum(k in joined for k in HEADER_KEYS) >= 2 and numeric <= 1


def layout(payer, header):
    """Map field -> column index for a header row (already normalised)."""
    h = list(header)
    if payer == "london-ambulance-service" and "supplier" not in h:
        # 16 LAS files leave the supplier column's header blank; the names are in it
        ea, tn = find_col(h, ["expense area"]), find_col(h, ["transaction number"])
        if ea is not None and tn == ea + 2 and h[ea + 1] == "":
            h[ea + 1] = "supplier"
    cats = CATEGORY_COLS.get(payer, CATEGORY_COLS["default"])
    lay = {
        "date": find_col(h, DATE_COLS),
        "amount": find_col(h, AMOUNT_COLS),
        "supplier": find_col(h, SUPPLIER_COLS),
        "txn": find_col(h, TXN_COLS),
        "entity": find_col(h, ENTITY_COLS),
        "category": find_col(h, cats),
    }
    lay["category_name"] = h[lay["category"]] if lay["category"] is not None else None
    lay["header"] = h
    return lay


# Bedfordshire's February 2020 file has a broken two-line header; its columns are in the
# same order as every other Bedfordshire file.
BEDS_FIXED = ["transaction reference", "transaction date", "amount", "supplier name", "expense area",
              "category description"]


def is_total_row(cells, lay):
    sup = cells[lay["supplier"]].strip() if lay["supplier"] is not None and lay["supplier"] < len(cells) else ""
    dt = cells[lay["date"]].strip() if lay["date"] is not None and lay["date"] < len(cells) else ""
    text = " ".join(c.strip().lower() for c in cells if c and parse_amount(c) is None)
    if re.search(r"\b(grand )?totals?\b", text) and not sup:
        return True
    if not sup and not dt:
        return True
    return False


def iter_file(payer, rel_path, stats):
    if rel_path in NOT_SPEND_DATA:
        stats.note = NOT_SPEND_DATA[rel_path]
        return
    if rel_path.lower().endswith(".pdf") or (PROJECT / rel_path).read_bytes()[:5] == b"%PDF-":
        yield from pdf_records(payer, rel_path, stats)
        return
    current = {}  # sheet -> layout
    for sheet, i, cells in file_rows(rel_path):
        cells = [c if isinstance(c, str) else str(c) for c in cells]
        if sheet not in current:
            if looks_like_header(cells):
                lay = layout(payer, [norm_header(c) for c in cells])
                if lay["date"] is None or lay["amount"] is None:
                    stats.sheets_skipped.append((sheet, "header without date/amount: " + "|".join(lay["header"])))
                    current[sheet] = None
                    continue
                current[sheet] = lay
                stats.sheets_used.append(sheet)
                if lay["category"] is None:
                    stats.no_category_sheets.append(sheet)
                else:
                    stats.category_col.add(lay["category_name"])
                continue
            if payer == "bedfordshire-police" and rel_path.endswith("february2020.xlsx") and i == 2:
                current[sheet] = layout(payer, BEDS_FIXED)
                stats.sheets_used.append(sheet)
                stats.category_col.add("category description")
                stats.note = "header row split over two lines; columns read in the standard Bedfordshire order"
                continue
            if any(c.strip() for c in cells):
                stats.skipped_blank_or_text += 1
            continue
        lay = current[sheet]
        if lay is None:
            continue
        if not any(c.strip() for c in cells):
            stats.skipped_blank_or_text += 1
            continue
        if looks_like_header(cells) and norm_header(cells[lay["amount"]] if lay["amount"] < len(cells) else "") in AMOUNT_COLS:
            stats.skipped_blank_or_text += 1  # repeated header row
            continue
        g = lambda k: cells[lay[k]].strip() if lay[k] is not None and lay[k] < len(cells) else ""  # noqa: E731
        amt = parse_amount(g("amount"))
        if amt is None:
            if g("amount") or g("supplier"):
                stats.unparsed.append((sheet, i, "amount not a number: " + g("amount")[:40], cells[:12]))
            else:
                stats.skipped_blank_or_text += 1
            continue
        if is_total_row(cells, lay):
            stats.skipped_total_rows.append((sheet, i, str(amt), cells[:12]))
            continue
        d = parse_date(g("date"))
        if d is None:
            stats.unparsed.append((sheet, i, "date not parsed: " + g("date")[:40], cells[:12]))
        stats.lines += 1
        yield {
            "date": d, "date_raw": g("date"), "amount": amt, "supplier": norm_label(g("supplier")),
            "category": norm_label(g("category")) if lay["category"] is not None else None,
            "category_col": lay["category_name"], "txn": g("txn"), "entity": g("entity"),
            "sheet": sheet, "row": i, "cells": cells,
        }


def manifest_files():
    """Yield (payer, rel_path, manifest row) for every saved spend file, in manifest order."""
    with open(MANIFEST, newline="") as fh:
        for r in csv.DictReader(fh):
            if not r["saved_path"]:
                continue
            if r["fetch_note"].startswith("FOI"):
                continue
            yield r["payer_slug"], r["saved_path"], r
