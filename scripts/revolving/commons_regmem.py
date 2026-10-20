#!/usr/bin/env python3
"""Search every archived edition of the Commons Register of Members' Financial Interests for a term.

Source: the parsed register editions mySociety publishes for TheyWorkForYou
(https://www.theyworkforyou.com/pwdata/scrapedxml/regmem/), one XML file per edition.
Files are streamed and only the matching entries are kept.

Usage:
    python3 scripts/revolving/commons_regmem.py OUT_JSON [FROM_YEAR] [TERM ...]
"""
import json
import re
import sys
import time
import urllib.request

UA = "palantir-uk-open-data/1.0 (public-interest research)"
BASE = "https://www.theyworkforyou.com/pwdata/scrapedxml/regmem/"


def fetch(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            time.sleep(5 * (attempt + 1))
    return ""


def main():
    out = sys.argv[1]
    from_year = int(sys.argv[2]) if len(sys.argv) > 2 else 2009
    terms = [t.lower() for t in sys.argv[3:]] or ["palantir"]
    index = fetch(BASE)
    files = sorted(set(re.findall(r"regmem(\d{4}-\d{2}-\d{2})\.xml", index)))
    files = [f for f in files if int(f[:4]) >= from_year]
    hits = []
    for n, date in enumerate(files):
        url = f"{BASE}regmem{date}.xml"
        xml = fetch(url)
        time.sleep(1.0)
        if not any(t in xml.lower() for t in terms):
            continue
        for m in re.finditer(r'<regmem [^>]*?membername="([^"]+)"[^>]*>(.*?)</regmem>', xml, re.S):
            body = m.group(2)
            for cat in re.finditer(r'<category [^>]*?name="([^"]+)"[^>]*>(.*?)</category>', body, re.S):
                for item in re.findall(r"<item[^>]*>(.*?)</item>", cat.group(2), re.S):
                    text = re.sub(r"<[^>]+>", " ", item)
                    text = re.sub(r"\s+", " ", text).strip()
                    if any(t in text.lower() for t in terms):
                        hits.append({"edition": date, "member": m.group(1), "category": cat.group(1),
                                     "text": text, "source_url": url})
        print(n, date, "hits so far", len(hits), file=sys.stderr)
    json.dump(hits, open(out, "w"), indent=1)
    seen = set()
    for h in hits:
        key = (h["member"], h["text"])
        if key in seen:
            continue
        seen.add(key)
        print(h["edition"], "|", h["member"], "|", h["category"], "|", h["text"][:300])


if __name__ == "__main__":
    main()
