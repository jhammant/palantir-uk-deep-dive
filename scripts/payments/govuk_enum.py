#!/usr/bin/env python3
"""Enumerate GOV.UK spend collections -> publications -> attachments (read-only, polite)."""
import json
import sys
import time
import urllib.request

UA = "palantir-uk-open-data/1.0 (public-interest research)"
API = "https://www.gov.uk/api/content"


def get(path):
    for attempt in range(5):
        req = urllib.request.Request(API + path, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = int(e.headers.get("Retry-After", "30"))
                print(f"429, waiting {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("too many retries " + path)


def main():
    slug, collection = sys.argv[1], sys.argv[2]
    title_filter = sys.argv[3].lower() if len(sys.argv) > 3 else ""
    out = []
    col = get(collection)
    docs = col.get("links", {}).get("documents", [])
    for d in docs:
        if title_filter and title_filter not in d["title"].lower():
            continue
        time.sleep(0.7)
        try:
            pub = get(d["base_path"])
        except Exception as e:  # noqa: BLE001
            print("ERR", d["base_path"], e, file=sys.stderr)
            continue
        atts = []
        for a in pub.get("details", {}).get("attachments", []):
            atts.append({k: a.get(k) for k in ("title", "url", "filename", "content_type", "file_size")})
        out.append({
            "page_url": "https://www.gov.uk" + d["base_path"],
            "title": d["title"],
            "public_updated_at": d.get("public_updated_at"),
            "first_published_at": pub.get("first_published_at"),
            "attachments": atts,
        })
        print(d["title"][:90], len(atts), file=sys.stderr)
    json.dump({"payer": slug, "collection": "https://www.gov.uk" + collection, "publications": out}, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
