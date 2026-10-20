#!/usr/bin/env python3
"""Turn each saved spend file into normalised payment lines.

iter_file(payer, rel_path, stats) yields one dict per published payment line:
    date (ISO or None), date_raw, amount (Decimal), supplier, category (label or None),
    category_col, txn, entity, sheet, row, cells
and records what it skipped (blank and text lines, total rows, lines it could not read)
in a FileStats object.

Column names differ between publishers and between years, so each field is found by an
ordered list of header names. Paths are relative to the project root.
"""
import csv
import re
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
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
# The first name present in a sheet's header is used. A sheet with none has no category.
CATEGORY_COLS = {
    "default": ["expense type", "expense type for report"],
    "hm-treasury": ["expense type", "account code description"],
    "ukhsa": ["expense type", "subjective level 4"],
    "coventry-city-council": ["account code(t)"],
    "bedfordshire-police": ["category description"],
    "cambridgeshire-pcc": ["category description"],
    "hertfordshire-pcc": ["purpose of expenditure"],
}

# Files in the manifest that hold no spend rows.
NOT_SPEND_DATA = {
    "sources/raw/payments/defra/financial-transactions-data-defra":
        "a data.gov.uk web page was saved instead of the March 2020 spend file; no spend rows",
    "sources/raw/payments/defra/spend-over-25-000-in-the-department-for-environment-food-and-rural-affairs":
        "a data.gov.uk web page was saved instead of the January 2020 spend file; no spend rows",
}

# Files without a usable header row whose columns are in a payer's standard order
# (checked against that payer's other files).
FIXED_LAYOUTS = {
    "sources/raw/payments/bedfordshire-police/payments-over-500-february2020.xlsx": (
        2, ["transaction reference", "transaction date", "amount", "supplier name", "expense area",
            "category description"],
        "header row split over two lines; columns read in the order of every other Bedfordshire file"),
    "sources/raw/payments/cabinet-office/Cabinet_Office_-_spend_data_over__25_000_-_January_2024_CSV.csv": (
        -1, ["ref", "departmental family", "entity", "date", "expense type", "expense area", "supplier",
             "transaction number", "amount"],
        "file has no header row; columns read in the order of the other Cabinet Office files from 2023 and 2024"),
}

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
MONTH_RE = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"


def norm_header(h):
    return re.sub(r"\s+", " ", (h or "").replace("\xa0", " ")).strip().lower()


def norm_label(s):
    return re.sub(r"\s+", " ", (s or "").replace("\xa0", " ")).strip()


def parse_amount(s):
    """Decimal, or None if the cell is not a sterling amount."""
    t = (s or "").replace(",", "").replace("\xa0", "").replace(" ", "").strip()
    if "$" in t or "€" in t:
        return None
    t = t.replace("£", "").strip("?")  # MoD files carry '?' where a £ sign lost its encoding
    if t == "-":
        return Decimal(0)  # accounting format for zero
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


SLASH = re.compile(r"(\d{1,2})[/.](\d{1,2})[/.](\d{2}|\d{4})")


def parse_date(s, order="dmy", file_year_for=None):
    """ISO date or None. order is 'dmy' (UK) or 'mdy' (US) for slash dates.
    file_year_for(month) gives the year for a day-month date with no year, from the file title."""
    s = (s or "").strip().rstrip(".]").strip()
    if not s:
        return None
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})(?:[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?)?", s)
    if m:
        if m.group(1) == "1900":
            return None  # spreadsheet zero date: the cell was empty
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = SLASH.fullmatch(s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = y + 2000 if y < 100 else y
        d, mo = (a, b) if order == "dmy" else (b, a)
        try:
            return date(y, mo, d).isoformat()
        except ValueError:
            return None
    m = re.fullmatch(r"(\d{1,2})[ -]([A-Za-z]{3,9})[ -](\d{2}|\d{4})", s)
    if m and m.group(2)[:3].lower() in MONTHS:
        y = int(m.group(3))
        y = y + 2000 if y < 100 else y
        try:
            return date(y, MONTHS[m.group(2)[:3].lower()], int(m.group(1))).isoformat()
        except ValueError:
            return None
    m = re.fullmatch(r"[A-Za-z]+,\s*([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)  # Friday, April 29, 2022
    if m and m.group(1)[:3].lower() in MONTHS:
        try:
            return date(int(m.group(3)), MONTHS[m.group(1)[:3].lower()], int(m.group(2))).isoformat()
        except ValueError:
            return None
    m = re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})", s)  # 25-May, no year
    if m and m.group(2).lower() in MONTHS and file_year_for:
        y = file_year_for(MONTHS[m.group(2).lower()])
        if y:
            return date(y, MONTHS[m.group(2).lower()], int(m.group(1))).isoformat()
        return None
    m = re.fullmatch(r"(\d{5})(?:\.0+)?", s)  # Excel serial day number
    if m and 40000 < int(m.group(1)) < 50000:
        return (date(1899, 12, 30) + timedelta(days=int(m.group(1)))).isoformat()
    return None


def date_order(raw_dates):
    """Decide whether a file's slash dates are day/month or month/day from the dates themselves."""
    n = first = second = 0
    for s in raw_dates:
        m = SLASH.fullmatch((s or "").strip().rstrip(".]").strip())
        if m:
            n += 1
            first += int(m.group(1)) > 12
            second += int(m.group(2)) > 12
    if not n:
        return "dmy", "no slash dates"
    if first and second:
        return ("dmy" if first >= second else "mdy"), f"mixed ({first} day-first, {second} month-first)"
    if second:
        return "mdy", "month/day/year"
    if first:
        return "dmy", "day/month/year"
    return "dmy", f"day/month/year assumed ({n} slash dates, none with a day above 12)"


MONTH_WORD = re.compile(r"(?<![a-z])(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|ocotober)[a-z]*", re.I)
MONTH_YEAR = re.compile(r"(?<![a-z])(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|ocotober)[a-z]*"
                        r"[^a-z0-9]{0,4}(20\d\d|\d\d)(?!\d)", re.I)
YEAR_TYPOS = (("20205", "2025"), ("20252", "2025"), ("20222", "2022"))


def _month_year(text):
    t = text.lower()
    for a, b in YEAR_TYPOS:
        t = t.replace(a, b)
    found = {(m.group(1)[:3].replace("oco", "oct"), m.group(2)) for m in MONTH_YEAR.finditer(t)}
    if len(found) != 1:
        return None
    mon, yr = found.pop()
    y = int(yr) + 2000 if len(yr) == 2 else int(yr)
    return f"{y}-{MONTHS[mon]:02d}"


def police_period(n, fy_start):
    """Police financial-year period n (1 = April) of the year starting in April fy_start -> 'YYYY-MM'."""
    m = (n + 2) % 12 + 1
    return f"{fy_start + (1 if n >= 10 else 0)}-{m:02d}"


def published_month(payer, rel_path, mrow, sheet, pdf_title=""):
    """The month a file (or sheet) says it covers, and where that came from; (None, '') if it does not say."""
    name = Path(rel_path).name
    fy = re.search(r"during-(?:the-)?(20\d\d)\d\d", (mrow or {}).get("source_page_url", ""))
    mw = MONTH_WORD.search(name)
    if payer == "bedfordshire-police" and fy and mw:
        # the financial-year page is the reliable year: "march2021-revised" sits on the 2021/22 page
        mon = MONTHS[mw.group(1)[:3].lower()]
        return f"{int(fy.group(1)) + (1 if mon <= 3 else 0)}-{mon:02d}", "month in file name, year from the financial-year page"
    got = _month_year(name)
    if got:
        return got, "file name"
    if sheet and sheet not in ("csv", "pdf", "txt"):
        got = _month_year(sheet)
        if got:
            return got, "sheet name"
    page = (mrow or {}).get("source_page_url", "")
    slug = page.rstrip("/").split("/")[-1]
    if "-to-" not in slug:
        got = _month_year(slug)
        if got:
            return got, "publication page"
    m = re.search(r"Period\s+(\d{1,2})\s+(20\d\d)", pdf_title or "")
    if m and payer == "cambridgeshire-pcc":
        return police_period(int(m.group(1)), int(m.group(2))), "report title (police period)"
    m = re.search(r"-p(\d{1,2})-(20\d\d|\d\d)(?:-\d\d)?(?:\.pdf)?$", name.lower())
    if m and payer == "cambridgeshire-pcc":
        y = int(m.group(2))
        return police_period(int(m.group(1)), y + 2000 if y < 100 else y), "file name (police period)"
    return None, ""


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
    skipped_total_rows: list = field(default_factory=list)   # (sheet, row, amount, cells)
    unparsed: list = field(default_factory=list)             # (sheet, row, reason, cells)
    category_col: set = field(default_factory=set)
    no_category_sheets: list = field(default_factory=list)
    date_order: str = ""
    other_order_dates: list = field(default_factory=list)
    pdf_title: str = ""
    note: str = ""
    unreadable: bool = False


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
    """Map field -> column index for a normalised header row."""
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


def is_total_row(cells, lay):
    g = lambda k: cells[lay[k]].strip() if lay[k] is not None and lay[k] < len(cells) else ""  # noqa: E731
    text = " ".join(c.strip().lower() for c in cells if c and parse_amount(c) is None)
    if re.search(r"\b(grand )?totals?\b", text) and not g("supplier"):
        return True
    return not g("supplier") and not g("date")


def file_year_resolver(rel_path):
    """For dates printed as day-month only: the year of that month in the file's title."""
    name = Path(rel_path).name.lower()
    m = re.search(MONTH_RE + r"[^a-z0-9]{0,3}(20\d\d)", name)
    if not m:
        return None
    fmon, fyear = MONTHS[m.group(1)], int(m.group(2))
    return lambda mon: fyear if mon == fmon else None


def _sheet_rows(payer, rel_path, stats):
    """Yield (sheet, row, cells, layout) for each data line of a spreadsheet file."""
    current = {}
    fixed = FIXED_LAYOUTS.get(rel_path)
    for sheet, i, cells in file_rows(rel_path):
        cells = [c if isinstance(c, str) else str(c) for c in cells]
        if sheet not in current:
            if fixed and (i == fixed[0] or (fixed[0] == -1 and i == 0)):
                current[sheet] = layout(payer, fixed[1])
                stats.sheets_used.append(sheet)
                stats.note = fixed[2]
                if fixed[0] != -1:
                    continue
            elif looks_like_header(cells):
                lay = layout(payer, [norm_header(c) for c in cells])
                if lay["date"] is None or lay["amount"] is None:
                    stats.sheets_skipped.append((sheet, "header without date/amount: " + "|".join(lay["header"])))
                    current[sheet] = None
                else:
                    current[sheet] = lay
                    stats.sheets_used.append(sheet)
                continue
            else:
                if any(c.strip() for c in cells):
                    stats.skipped_blank_or_text += 1
                continue
        lay = current[sheet]
        if lay is None:
            continue
        if lay["category"] is None and sheet not in stats.no_category_sheets:
            stats.no_category_sheets.append(sheet)
        elif lay["category"] is not None:
            stats.category_col.add(lay["category_name"])
        if not any(c.strip() for c in cells):
            stats.skipped_blank_or_text += 1
            continue
        if looks_like_header(cells) and lay["amount"] < len(cells) and norm_header(cells[lay["amount"]]) in AMOUNT_COLS:
            stats.skipped_blank_or_text += 1  # repeated header row
            continue
        yield sheet, i, cells, lay


def iter_file(payer, rel_path, stats):
    if rel_path in NOT_SPEND_DATA:
        stats.note = NOT_SPEND_DATA[rel_path]
        stats.unreadable = True
        return
    if (PROJECT / rel_path).read_bytes()[:5] == b"%PDF-":
        yield from pdf_records(payer, rel_path, stats)
        return
    pending = []
    for sheet, i, cells, lay in _sheet_rows(payer, rel_path, stats):
        g = lambda k: cells[lay[k]].strip() if lay[k] is not None and lay[k] < len(cells) else ""  # noqa: E731
        amt = parse_amount(g("amount"))
        if amt is None:
            if g("amount") or g("supplier"):
                stats.unparsed.append((sheet, i, "amount not a sterling number: " + g("amount")[:40], cells[:12]))
            else:
                stats.skipped_blank_or_text += 1
            continue
        if is_total_row(cells, lay):
            stats.skipped_total_rows.append((sheet, i, str(amt), cells[:12]))
            continue
        pending.append({
            "date_raw": g("date"), "amount": amt, "supplier": norm_label(g("supplier")),
            "category": norm_label(g("category")) if lay["category"] is not None else None,
            "category_col": lay["category_name"], "txn": g("txn"), "entity": g("entity"),
            "sheet": sheet, "row": i, "cells": cells,
        })
    order, desc = date_order(r["date_raw"] for r in pending)
    stats.date_order = desc
    fy = file_year_resolver(rel_path)
    other = "mdy" if order == "dmy" else "dmy"
    for r in pending:
        r["date"] = parse_date(r["date_raw"], order=order, file_year_for=fy)
        if r["date"] is None and SLASH.fullmatch(r["date_raw"].strip().rstrip(".]").strip()):
            # invalid in the file's order but valid the other way round (e.g. 17/06/2025 in a
            # month-first file): only one reading exists
            r["date"] = parse_date(r["date_raw"], order=other)
            if r["date"]:
                stats.other_order_dates.append((r["sheet"], r["row"], r["date_raw"], r["date"]))
        if r["date"] is None:
            stats.unparsed.append((r["sheet"], r["row"], "date not parsed: " + r["date_raw"][:40], r["cells"][:12]))
        stats.lines += 1
        yield r


def manifest_files():
    """Yield (payer, rel_path, manifest row) for every saved spend file, in manifest order."""
    with open(MANIFEST, newline="") as fh:
        for r in csv.DictReader(fh):
            if not r["saved_path"] or r["fetch_note"].startswith("FOI"):
                continue
            yield r["payer_slug"], r["saved_path"], r
