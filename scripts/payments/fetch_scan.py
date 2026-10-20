#!/usr/bin/env python3
"""Download spend files politely, save under the project, scan every row for 'palantir'.

Input: a JSON list of jobs on argv[1]: [{payer, page_url, file_url, filename, period_hint}]
Outputs (appended): work/manifest.jsonl, work/hits.jsonl
"""
import csv
import hashlib
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
RAW = PROJECT / "sources" / "raw" / "payments"
WORK = Path(__file__).resolve().parents[2] / "sources" / "raw" / "payments" / "_work"  # local, not published
UA = "palantir-uk-open-data/1.0 (public-interest research)"
PAUSE = float(sys.argv[2]) if __name__ == "__main__" and len(sys.argv) > 2 else 2.5
PAT = re.compile(r"palantir", re.I)


def download(url):
    for attempt in range(6):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                cd = r.headers.get("Content-Disposition", "") or ""
                m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', cd)
                cdname = urllib.parse.unquote(m.group(1)).strip() if m else None
                return r.read(), r.headers.get("Content-Type", ""), cdname
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = int(e.headers.get("Retry-After", "60") or 60)
                print(f"  {e.code} -> wait {wait}s", file=sys.stderr)
                time.sleep(min(wait, 600))
                continue
            raise
        except Exception as e:  # noqa: BLE001
            print(f"  error {e}, retry", file=sys.stderr)
            time.sleep(20)
    raise RuntimeError("gave up " + url)


def decode(b):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode("latin-1", "replace")


def rows_from(data, name):
    """Yield (sheet, rownum, [cells as str])."""
    low = name.lower()
    if low.endswith(".csv") or low.endswith(".txt"):
        text = decode(data).replace("\r\n", "\n").replace("\r", "\n")
        for i, row in enumerate(csv.reader(io.StringIO(text, newline=""))):
            yield ("csv", i, row)
        return
    if low.endswith(".xlsx") or low.endswith(".xlsm") or data[:2] == b"PK" and not low.endswith(".ods"):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        for ws in wb.worksheets:
            for i, row in enumerate(ws.iter_rows(values_only=True)):
                yield (ws.title, i, ["" if c is None else str(c) for c in row])
        return
    if low.endswith(".xls"):
        import xlrd
        wb = xlrd.open_workbook(file_contents=data)
        for sh in wb.sheets():
            for i in range(sh.nrows):
                yield (sh.name, i, [str(c) for c in sh.row_values(i)])
        return
    if low.endswith(".ods"):
        import pandas as pd
        sheets = pd.read_excel(io.BytesIO(data), engine="odf", sheet_name=None, header=None, dtype=str)
        for sname, df in sheets.items():
            for i, row in enumerate(df.itertuples(index=False)):
                yield (sname, i, ["" if (c is None or str(c) == "nan") else str(c) for c in row])
        return
    if low.endswith(".pdf") or data[:5] == b"%PDF-":
        import subprocess, tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tf:
            tf.write(data)
            tf.flush()
            out = subprocess.run(["pdftotext", "-layout", tf.name, "-"], capture_output=True, timeout=300).stdout
        for i, line in enumerate(decode(out).splitlines()):
            yield ("pdf", i, [line])
        return
    # unknown: treat as text
    text = decode(data)
    for i, row in enumerate(csv.reader(io.StringIO(text))):
        yield ("txt", i, row)


HEADER_WORDS = ("supplier", "amount", "vendor", "payee", "expense", "value", "merchant", "date")


def is_header(cells):
    joined = " ".join(c.lower() for c in cells if c)
    return sum(w in joined for w in HEADER_WORDS) >= 2 and len([c for c in cells if c.strip()]) >= 3


def main():
    jobs = json.load(open(sys.argv[1]))
    done = set()
    mpath = WORK / "manifest.jsonl"
    if mpath.exists():
        for line in mpath.open():
            try:
                _r = json.loads(line)
                if not _r.get("error"):
                    done.add(_r["file_url"])
            except Exception:  # noqa: BLE001
                pass
    for n, job in enumerate(jobs):
        url = job["file_url"]
        if url in done:
            continue
        dest_dir = RAW / job["payer"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        print(f"[{n+1}/{len(jobs)}] {job['payer']} {job.get('filename') or url}", file=sys.stderr)
        rec = dict(job)
        try:
            data, ctype, cdname = download(url)
            fname = job.get("filename") or cdname or urllib.parse.unquote(url.rstrip("/").split("/")[-1])
            fname = fname.replace("/", "_")
            rec["filename"] = fname
            dest = dest_dir / fname
            if dest.exists() and dest.read_bytes() == data:
                pass  # identical file already saved (retry)
            elif dest.exists():
                # different file, same name: keep both, prefix with media id
                mid = url.rstrip("/").split("/")[-2][:12]
                dest = dest_dir / f"{mid}__{fname}"
            if b"<html" in data[:500].lower() and not fname.lower().endswith((".html", ".htm")):
                rec["warning"] = "response looks like HTML"
            dest.write_bytes(data)
            rec.update(saved=str(dest.relative_to(PROJECT)), sha256=hashlib.sha256(data).hexdigest(),
                       bytes=len(data), content_type=ctype)
            header, nrows, nhits = None, 0, 0
            with (WORK / "hits.jsonl").open("a") as hf:
                for sheet, i, cells in rows_from(data, fname):
                    nrows += 1
                    if (header is None or header[0] != sheet) and is_header(cells):
                        header = (sheet, i, cells)
                    if any(PAT.search(c) for c in cells):
                        nhits += 1
                        hf.write(json.dumps({"payer": job["payer"], "page_url": job["page_url"], "file_url": url,
                                             "saved": rec["saved"], "sheet": sheet, "row": i,
                                             "header": header[2] if header else None, "cells": cells}) + "\n")
            rec.update(rows=nrows, hits=nhits)
        except Exception as e:  # noqa: BLE001
            rec["error"] = repr(e)[:300]
        with mpath.open("a") as mf:
            mf.write(json.dumps(rec) + "\n")
        if rec.get("hits"):
            print(f"   HITS {rec['hits']}", file=sys.stderr)
        time.sleep(PAUSE)


if __name__ == "__main__":
    main()
