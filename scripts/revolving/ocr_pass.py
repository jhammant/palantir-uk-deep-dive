#!/usr/bin/env python3
"""Second pass over scan_pubs.py output: OCR PDFs with a thin text layer, re-read failed .doc files.

Usage:
    python3 scripts/revolving/ocr_pass.py WORK_DIR [CHARS_PER_PAGE]

A PDF is OCR'd when pdftotext gives fewer than CHARS_PER_PAGE characters per page (default 400).
Writes WORK_DIR/ocr_hits.json and WORK_DIR/ocr_manifest.json.
"""
import concurrent.futures as cf
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import urllib.parse

PATTERN = re.compile(r"p[ae]ll?[ae]n?t[ae]?i?r", re.I)


def local_name(url):
    return hashlib.sha1(url.encode()).hexdigest()[:16] + pathlib.Path(urllib.parse.urlparse(url).path).suffix


def pages(pdf):
    r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, timeout=60)
    m = re.search(rb"Pages:\s+(\d+)", r.stdout)
    return int(m.group(1)) if m else 1


def ocr(pdf):
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["pdftoppm", "-r", "200", "-gray", "-png", str(pdf), td + "/p"],
                       capture_output=True, timeout=900)
        parts = []
        for png in sorted(pathlib.Path(td).glob("p*.png")):
            o = subprocess.run(["tesseract", str(png), "-", "--psm", "6"], capture_output=True, timeout=300)
            parts.append(o.stdout.decode("utf-8", "replace"))
    return "\n".join(parts)


def doc_text(path):
    out = path.with_suffix(".textutil.txt")
    subprocess.run(["textutil", "-convert", "txt", "-output", str(out), str(path)], capture_output=True, timeout=120)
    return out.read_text("utf-8", "replace") if out.exists() else ""


def work_one(entry, files_dir, threshold):
    url = entry["file_url"]
    path = files_dir / local_name(url)
    if not path.exists():
        return entry, None, "missing"
    if path.suffix.lower() == ".pdf":
        n = pages(path)
        if entry["chars"] / max(n, 1) >= threshold:
            return entry, None, "skip"
        text, method = ocr(path), "ocr"
    else:
        text, method = doc_text(path), "textutil"
    hits = []
    for m in PATTERN.finditer(text):
        a, b = max(0, m.start() - 500), min(len(text), m.end() + 500)
        hits.append({"match": m.group(0), "context": re.sub(r"\s+", " ", text[a:b]),
                     "page_url": entry["page_url"], "file_url": url, "method": method})
    return entry, hits, method + ":" + str(len(text))


def main():
    work = pathlib.Path(sys.argv[1])
    threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    manifest = json.loads((work / "manifest.json").read_text())
    todo = [e for e in manifest if e["method"] == "pdftotext"
            or e["method"] == "unsupported" and e["file_url"].lower().endswith(".doc")]
    files_dir = work / "files"
    all_hits, log = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(work_one, e, files_dir, threshold) for e in todo]
        for n, f in enumerate(cf.as_completed(futs)):
            entry, hits, status = f.result()
            if status != "skip":
                log.append({"file_url": entry["file_url"], "page_url": entry["page_url"], "status": status})
            if hits:
                all_hits += hits
                print("HIT", entry["page_url"], len(hits), file=sys.stderr)
            if n % 200 == 0:
                print(n, "of", len(todo), file=sys.stderr)
    (work / "ocr_hits.json").write_text(json.dumps(all_hits, indent=1))
    (work / "ocr_manifest.json").write_text(json.dumps(log, indent=1))
    print(len(log), "files re-read;", len(all_hits), "hits", file=sys.stderr)


if __name__ == "__main__":
    main()
