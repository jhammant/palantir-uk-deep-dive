#!/usr/bin/env python3
"""Enumerate GOV.UK publications about ministers', officials' and special advisers' meetings."""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(sys.argv[1])
UA = "palantir-uk-open-data/1.0 (public-interest research)"
QUERIES = [
    "ministers meetings",
    "ministers meetings with external organisations",
    "ministerial gifts hospitality travel and meetings",
    "ministerial meetings",
    "special advisers gifts hospitality and meetings",
    "special advisers meetings",
    "senior officials business expenses hospitality and meetings",
    "senior officials meetings",
    "permanent secretary meetings",
    "board members expenses hospitality meetings",
    "ministers transparency data meetings",
    "gifts hospitality travel meetings",
]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print("retry", url, e, file=sys.stderr)
            time.sleep(10 * (attempt + 1))
    return None


found = {}
for q in QUERIES:
    start = 0
    while True:
        params = {"q": q, "count": 1000, "start": start,
                  "fields": "title,link,public_timestamp,organisations,content_store_document_type"}
        data = get("https://www.gov.uk/api/search.json?" + urllib.parse.urlencode(params, doseq=True))
        if data is None:
            break
        before = len(found)
        res = data.get("results", [])
        for r in res:
            t = (r.get("title") or "").lower()
            if "meeting" not in t:
                continue
            link = r["link"]
            if link not in found:
                orgs = [o.get("slug") or o.get("title") for o in r.get("organisations", []) if isinstance(o, dict)]
                found[link] = {"title": r.get("title"), "link": link, "public_timestamp": r.get("public_timestamp"),
                               "orgs": orgs, "type": r.get("content_store_document_type")}
        print(q, start, len(res), "total", data.get("total"), "found", len(found), file=sys.stderr)
        start += 1000
        OUT.write_text(json.dumps(sorted(found.values(), key=lambda x: x["link"]), indent=1))
        if not res or start >= min(data.get("total", 0), 6000) or len(found) - before < 5:
            break
        time.sleep(2)

OUT.write_text(json.dumps(sorted(found.values(), key=lambda x: x["link"]), indent=1))
print(len(found))
