#!/usr/bin/env python3
"""Turn scan hits into one JSON line per matching table row, with header and carried-forward name."""
import csv
import io
import json
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HITS = Path(sys.argv[1])          # hits.jsonl
DIR = Path(sys.argv[2])           # hits dir
PAT = re.compile(r"palantir|palantír|alex(ander)?\s+karp|louis\s+mosley|peter\s+thiel", re.I)


def decode(b):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode("latin-1", "ignore")


def csv_tables(b):
    text = decode(b)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    rows = list(csv.reader(io.StringIO(text, newline="")))
    return [("csv", rows)]


def xlsx_tables(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        rows = [["" if c is None else str(c) for c in r] for r in ws.iter_rows(values_only=True)]
        out.append((ws.title, rows))
    return out


def ods_tables(path):
    ns = {"table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
          "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("content.xml"))
    out = []
    for t in root.iter("{%s}table" % ns["table"]):
        rows = []
        for r in t.iter("{%s}table-row" % ns["table"]):
            cells = []
            for c in r:
                if not c.tag.endswith("table-cell") and not c.tag.endswith("covered-table-cell"):
                    continue
                rep = int(c.get("{%s}number-columns-repeated" % ns["table"], "1"))
                txt = " ".join("".join(p.itertext()) for p in c.iter("{%s}p" % ns["text"]))
                cells.extend([txt] * min(rep, 50))
            rows.append(cells)
        out.append((t.get("{%s}name" % ns["table"]), rows))
    return out


def html_tables(b):
    s = decode(b)
    out = []
    for ti, t in enumerate(re.findall(r"<table.*?</table>", s, re.S)):
        rows = []
        for r in re.findall(r"<tr.*?</tr>", t, re.S):
            cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip()
                     for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
            rows.append(cells)
        out.append((f"table{ti}", rows))
    return out


def pdf_tables(path):
    txt = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True).stdout.decode("utf-8", "ignore")
    return [("pdf", [[ln] for ln in txt.splitlines()])]


def find_header(rows, idx):
    for j in range(idx - 1, -1, -1):
        joined = " ".join(rows[j]).lower()
        if re.search(r"\b(name|minister|date|organisation|purpose|official)\b", joined) and not PAT.search(joined):
            return rows[j]
    return []


for line in HITS.read_text().splitlines():
    h = json.loads(line)
    path = DIR / h["saved"]
    name = path.name.lower()
    b = path.read_bytes()
    try:
        if name.endswith(".csv"):
            tables = csv_tables(b)
        elif name.endswith(".xlsx"):
            tables = xlsx_tables(path)
        elif name.endswith(".ods"):
            tables = ods_tables(path)
        elif name.endswith(".html"):
            tables = html_tables(b)
        elif name.endswith(".pdf"):
            tables = pdf_tables(path)
        else:
            tables = csv_tables(b)
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"error": str(e), "file": h["saved"]}))
        continue
    for tname, rows in tables:
        last_name = ""
        for i, r in enumerate(rows):
            r = [c.strip() for c in r]
            if r and r[0] and not re.match(r"^\d", r[0]) and r[0].lower() not in ("nil return", "nil", "n/a"):
                last_name = r[0]
            if PAT.search(" ".join(r)):
                print(json.dumps({"pub": h["pub"], "title": h.get("title"), "att_title": h.get("att_title"),
                                  "url": h["url"], "pub_date": (h.get("date") or "")[:10], "orgs": h.get("orgs"),
                                  "table": tname, "row": [c for c in r if c], "carry_name": last_name,
                                  "header": [c for c in find_header(rows, i) if c]}, ensure_ascii=False))
