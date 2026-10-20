#!/usr/bin/env python3
"""Re-read every saved file that had a Palantir hit and emit one record per matching row,
with the header of its sheet, so each line can be mapped to payments.csv fields.

Output: work/lines.jsonl  (payer, file_url, page_url, saved, sheet, row, header, cells, fields)
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fetch_scan import rows_from, PROJECT, WORK  # noqa: E402

PAT = re.compile(r"palantir", re.I)


def is_header(cells):
    low = [c.strip().lower() for c in cells]
    joined = " | ".join(low)
    if sum(bool(c) for c in low) < 3:
        return False
    keys = ("supplier", "amount", "vendor", "payee", "merchant", "date", "value", "expense", "description")
    hits = sum(k in joined for k in keys)
    # a header row has no long numeric amounts
    numeric = sum(bool(re.fullmatch(r"[£\-]?[\d,]+(\.\d+)?", c)) for c in low if c)
    return hits >= 2 and numeric <= 1


def pick(header, *keys, exclude=()):
    for k in keys:
        for i, h in enumerate(header):
            hl = h.strip().lower()
            if k in hl and not any(x in hl for x in exclude):
                return i
    return None


def fields(header, cells):
    if not header:
        return {}
    g = lambda i: cells[i].strip() if i is not None and i < len(cells) else ""  # noqa: E731
    out = {}
    out["date"] = g(pick(header, "payment date", "date paid", "transaction date", "invoice date", "date"))
    out["amount"] = g(pick(header, "ap amount", "amount", "net value", "net amount", "value", "total", "£", exclude=("vat reg",)))
    out["supplier"] = g(pick(header, "supplier name", "supplier", "vendor", "payee", "merchant name", "beneficiary", exclude=("postcode", "type", "number", "ref", "id")))
    out["entity"] = g(pick(header, "entity", "organisation name", "body name", "body"))
    desc = []
    for k in ("expense type", "expense area", "description", "purpose", "narrative", "service", "category", "cost centre", "account", "detail", "expenditure type"):
        i = pick(header, k, exclude=("supplier",))
        if i is not None and g(i) and header[i] not in [d[0] for d in desc]:
            desc.append((header[i].strip(), g(i)))
    out["description"] = "; ".join(f"{h}: {v}" for h, v in desc)
    out["txn"] = g(pick(header, "transaction number", "transaction no", "transaction ref", "invoice number", "document number", "reference"))
    return out


def main():
    manifest = {}
    for line in open(WORK / "manifest.jsonl"):
        r = json.loads(line)
        if r.get("hits") and r.get("saved"):
            manifest[r["saved"]] = r
    out = open(WORK / "lines.jsonl", "w")
    n = 0
    for saved, r in sorted(manifest.items()):
        data = (PROJECT / saved).read_bytes()
        header = {}
        for sheet, i, cells in rows_from(data, r.get("filename") or saved):
            if is_header(cells) and sheet not in header:
                header[sheet] = cells
            if any(PAT.search(c) for c in cells):
                h = header.get(sheet)
                rec = {"payer": r["payer"], "file_url": r["file_url"], "page_url": r["page_url"], "saved": saved,
                       "sheet": sheet, "row": i, "header": h, "cells": cells, "fields": fields(h, cells)}
                out.write(json.dumps(rec) + "\n")
                n += 1
    print(n, "lines", file=sys.stderr)


if __name__ == "__main__":
    main()
