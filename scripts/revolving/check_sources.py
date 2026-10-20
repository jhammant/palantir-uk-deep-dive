#!/usr/bin/env python3
"""Re-open every URL cited in data/revolving-door.csv and check that each row's source names the person.

Usage:
    python3 scripts/revolving/check_sources.py [data/revolving-door.csv] [WORK_DIR]

For each row: fetches source_url, extracts text (HTML, JSON, CSV, PDF via pdftotext, DOCX), and checks the
person's surname appears in it. Every other URL in the notes column is fetched for its HTTP status.
Downloads go to WORK_DIR (default: a temporary directory). Prints a report and exits 1 on any failure.
"""
import csv
import hashlib
import html
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

UA = "Mozilla/5.0 (compatible; palantir-uk-open-data/1.0; public-interest research)"
URL_RE = re.compile(r"https?://[^\s,;)'\"]+")
# Sites that refuse automated clients; their pages were read in a browser-like session during collection.
BLOCKED_HOSTS = ("hansard.parliament.uk", "questions-statements.parliament.uk")


def fetch(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, r.read(), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(15)
                continue
            return e.code, b"", ""
        except Exception:  # noqa: BLE001
            time.sleep(3)
    return 0, b"", ""


def to_text(url, data, ctype, work):
    path = url.lower().split("?")[0]
    if path.endswith(".pdf") or "pdf" in ctype:
        f = work / (hashlib.sha1(url.encode()).hexdigest()[:12] + ".pdf")
        f.write_bytes(data)
        return subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True).stdout.decode("utf-8", "replace")
    if path.endswith(".docx"):
        f = work / (hashlib.sha1(url.encode()).hexdigest()[:12] + ".docx")
        f.write_bytes(data)
        return html.unescape(re.sub(r"<[^>]+>", " ", zipfile.ZipFile(f).read("word/document.xml").decode("utf-8", "replace")))
    text = data.decode("utf-8", "replace")
    text = re.sub(r"<(script|style).*?</\1>", " ", text, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


def surname(person):
    name = re.sub(r"\(.*?\)", "", person)
    for title in ("Lord ", "Baroness ", "Sir ", "Major General ", "Lieutenant General ", " CMG", " CBE"):
        name = name.replace(title, " ")
    name = name.split(" of ")[0].strip()
    return name.split()[-1]


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/revolving-door.csv"
    work = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(tempfile.mkdtemp())
    work.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    failures = 0
    seen = {}
    for r in rows:
        url = r["source_url"]
        status, data, ctype = fetch(url)
        text = to_text(url, data, ctype, work) if status == 200 else ""
        key = surname(r["person"])
        ok = status == 200 and key.lower() in text.lower()
        failures += not ok
        print(f"{'OK ' if ok else 'BAD'} {status} source  {r['person'][:40]:40} [{key}] {url}")
        seen[url] = status
        for u in URL_RE.findall(r["notes"]):
            u = u.rstrip(".")
            if u in seen:
                continue
            if any(h in u for h in BLOCKED_HOSTS):
                seen[u] = "skipped (blocks automated clients)"
                print(f"--- skip   notes   {u}")
                continue
            st, _, _ = fetch(u)
            seen[u] = st
            failures += st != 200
            print(f"{'OK ' if st == 200 else 'BAD'} {st} notes   {u}")
            time.sleep(0.5)
    print(f"\n{len(rows)} rows, {len(seen)} unique URLs, {failures} failures")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
