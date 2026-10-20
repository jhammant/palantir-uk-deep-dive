#!/usr/bin/env python3
"""Scan GOV.UK meetings/hospitality transparency attachments for mentions of Palantir.

Usage: scan.py pubs.json outdir
Writes outdir/manifest.jsonl (one line per attachment processed) and outdir/hits.jsonl
(attachments whose text matches). Matching files are kept in outdir/hits/.
"""
import hashlib
import json
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

PUBS = Path(sys.argv[1])
OUT = Path(sys.argv[2])
HITS = OUT / "hits"
HITS.mkdir(parents=True, exist_ok=True)
UA = "palantir-uk-open-data/1.0 (public-interest research)"
PAT = re.compile(r"palantir|palantír|alex(ander)?\s+karp|louis\s+mosley|peter\s+thiel", re.I)
KEEP_TYPES = {"transparency", "corporate_report", "foi_release", "official_statistics", "statistical_data_set",
              "national_statistics", "policy_paper", None, ""}
lock = threading.Lock()
done = set()
if (OUT / "manifest.jsonl").exists():
    for line in (OUT / "manifest.jsonl").read_text().splitlines():
        try:
            done.add(json.loads(line)["url"])
        except Exception:  # noqa: BLE001
            pass


def fetch(url, accept="*/*", tries=4):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read(), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return None, f"HTTP {e.code}"
            time.sleep(5 * (attempt + 1))
        except Exception:  # noqa: BLE001
            time.sleep(5 * (attempt + 1))
    return None, "failed"


def text_of(data, name):
    n = name.lower()
    try:
        if n.endswith((".xlsx", ".xlsm", ".docx", ".ods", ".odt", ".pptx")) or data[:2] == b"PK":
            out = []
            with zipfile.ZipFile(BytesIO(data)) as z:
                for member in z.namelist():
                    if member.endswith(".xml"):
                        out.append(z.read(member).decode("utf-8", "ignore"))
            return re.sub(r"<[^>]+>", " ", " ".join(out))
        if n.endswith(".pdf") or data[:4] == b"%PDF":
            p = subprocess.run(["pdftotext", "-layout", "-", "-"], input=data, capture_output=True, timeout=180)
            return p.stdout.decode("utf-8", "ignore")
        if n.endswith((".xls", ".doc")) or data[:4] == b"\xd0\xcf\x11\xe0":
            return data.decode("latin-1", "ignore") + " " + data.decode("utf-16-le", "ignore")
        return data.decode("utf-8", "ignore") if b"\x00" not in data[:1000] else data.decode("utf-16", "ignore")
    except Exception as e:  # noqa: BLE001
        return data.decode("latin-1", "ignore")


def record(entry, hit_text=None, data=None, name=None):
    with lock:
        with open(OUT / "manifest.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
        if hit_text is not None:
            if data is not None:
                h = hashlib.sha1(entry["url"].encode()).hexdigest()[:10]
                safe = re.sub(r"[^A-Za-z0-9._-]+", "_", (name or "file"))[-80:]
                (HITS / f"{h}_{safe}").write_bytes(data)
                entry["saved"] = f"{h}_{safe}"
            entry["context"] = hit_text
            with open(OUT / "hits.jsonl", "a") as f:
                f.write(json.dumps(entry) + "\n")


def contexts(text):
    out = []
    for m in PAT.finditer(text):
        s = max(0, m.start() - 300)
        out.append(re.sub(r"\s+", " ", text[s:m.end() + 300]))
        if len(out) >= 12:
            break
    return out


def process_pub(p):
    link = p["link"]
    data, _ = fetch("https://www.gov.uk/api/content" + urllib.parse.quote(link), "application/json")
    if not data:
        record({"pub": link, "url": "content:" + link, "status": "nocontent"})
        return
    try:
        c = json.loads(data)
    except Exception:  # noqa: BLE001
        return
    details = c.get("details", {})
    urls = []
    for a in details.get("attachments", []) or []:
        if a.get("attachment_type") == "html" or a.get("content_type") == "text/html":
            urls.append(("html", a.get("url"), a.get("title")))
        elif a.get("url"):
            urls.append(("file", a.get("url"), a.get("title")))
    for doc in details.get("documents", []) or []:
        for href in re.findall(r'href="([^"]+)"', doc or ""):
            if "/uploads/" in href or "assets.publishing" in href:
                urls.append(("file", href, None))
    body = details.get("body") or ""
    if isinstance(body, str) and PAT.search(body):
        record({"pub": link, "title": p.get("title"), "url": "body:" + link, "status": "ok"}, contexts(body))
    seen = set()
    for kind, u, title in urls:
        if not u or u in seen:
            continue
        seen.add(u)
        full = u if u.startswith("http") else "https://www.gov.uk" + u
        if full in done:
            continue
        entry = {"pub": link, "title": p.get("title"), "att_title": title, "url": full,
                 "date": p.get("public_timestamp"), "orgs": p.get("orgs")}
        if kind == "html":
            path = urllib.parse.urlparse(full).path
            d, st = fetch("https://www.gov.uk/api/content" + urllib.parse.quote(path), "application/json")
            if not d:
                entry["status"] = st
                record(entry)
                continue
            try:
                hb = json.loads(d).get("details", {}).get("body", "")
            except Exception:  # noqa: BLE001
                hb = ""
            txt = re.sub(r"<[^>]+>", " ", hb or "")
            entry["status"] = "ok"
            entry["size"] = len(txt)
            if PAT.search(txt):
                record(entry, contexts(txt), hb.encode(), path.split("/")[-1] + ".html")
            else:
                record(entry)
            continue
        d, st = fetch(full)
        if d is None:
            entry["status"] = st
            record(entry)
            continue
        name = urllib.parse.unquote(urllib.parse.urlparse(full).path.split("/")[-1])
        txt = text_of(d, name)
        entry["status"] = "ok"
        entry["size"] = len(d)
        if PAT.search(txt):
            record(entry, contexts(txt), d, name)
        else:
            record(entry)


pubs = json.loads(PUBS.read_text())
import os
todo = [p for p in pubs if os.environ.get("NOFILTER") or p.get("type") in KEEP_TYPES
        and (os.environ.get("NOFILTER") or re.search(r"meeting|hospitality|gifts|transparency", (p.get("title") or ""), re.I))]
print("publications to scan:", len(todo), file=sys.stderr)
count = 0
with ThreadPoolExecutor(max_workers=5) as ex:
    for _ in ex.map(process_pub, todo):
        count += 1
        if count % 100 == 0:
            print("done", count, file=sys.stderr, flush=True)
print("finished", count, file=sys.stderr)
