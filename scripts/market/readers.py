#!/usr/bin/env python3
"""File readers for the market-share pipeline.

CSV and XLSX files are read with rows_from() from scripts/payments/fetch_scan.py.
ODS files are read here with a streaming parser (zipfile + xml iterparse, standard
library only), because odfpy is not installed and pandas loads a whole ODS file at once.
PDF reports are read by pdf_tables.py.

All paths are relative to the project root.
"""
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "payments"))
from fetch_scan import rows_from as _rows_from  # noqa: E402

PROJECT = HERE.parents[1]

NS_TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
NS_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
T_TABLE = f"{{{NS_TABLE}}}table"
T_ROW = f"{{{NS_TABLE}}}table-row"
T_CELL = f"{{{NS_TABLE}}}table-cell"
T_COVERED = f"{{{NS_TABLE}}}covered-table-cell"
A_NAME = f"{{{NS_TABLE}}}name"
A_ROWS_REP = f"{{{NS_TABLE}}}number-rows-repeated"
A_COLS_REP = f"{{{NS_TABLE}}}number-columns-repeated"
A_VTYPE = f"{{{NS_OFFICE}}}value-type"
A_VALUE = f"{{{NS_OFFICE}}}value"
A_DATE = f"{{{NS_OFFICE}}}date-value"
T_P = f"{{{NS_TEXT}}}p"
T_S = f"{{{NS_TEXT}}}s"


def _cell_text(el):
    vtype = el.get(A_VTYPE)
    if vtype in ("float", "currency", "percentage") and el.get(A_VALUE) is not None:
        return el.get(A_VALUE)
    if vtype == "date" and el.get(A_DATE):
        return el.get(A_DATE).replace("T", " ")
    parts = []
    for p in el.iter(T_P):
        buf = [p.text or ""]
        for ch in p:
            if ch.tag == T_S:
                buf.append(" " * int(ch.get(f"{{{NS_TEXT}}}c", "1")))
            else:
                buf.append("".join(ch.itertext()))
            buf.append(ch.tail or "")
        parts.append("".join(buf))
    return "\n".join(parts)


def ods_rows(path):
    """Yield (sheet, rownum, [cells as str]) from an ODS file, streaming content.xml."""
    with zipfile.ZipFile(path) as z, z.open("content.xml") as fh:
        sheet, rownum = None, 0
        for event, el in ET.iterparse(fh, events=("start", "end")):
            if event == "start":
                if el.tag == T_TABLE:
                    sheet, rownum = el.get(A_NAME), 0
                continue
            if el.tag == T_ROW:
                cells = []
                for c in el:
                    if c.tag not in (T_CELL, T_COVERED):
                        continue
                    txt = _cell_text(c)
                    rep = int(c.get(A_COLS_REP, "1"))
                    cells.extend([txt] * min(rep, 1000) if txt else [""] * min(rep, 1000))
                while cells and not cells[-1].strip():
                    cells.pop()
                rep = int(el.get(A_ROWS_REP, "1"))
                if cells:
                    for _ in range(min(rep, 100000)):
                        yield (sheet, rownum, cells)
                        rownum += 1
                else:
                    rownum += rep
                el.clear()
            elif el.tag == T_TABLE:
                el.clear()


def file_rows(rel_path):
    """Yield (sheet, rownum, cells) for a saved spend file, given its project-relative path."""
    p = PROJECT / rel_path
    if p.name.lower().endswith(".ods"):
        yield from ods_rows(p)
        return
    yield from _rows_from(p.read_bytes(), p.name)
