#!/usr/bin/env python3
"""Search the Register of Lords' Interests (current and deleted entries) via Parliament's Members API.

Usage:
    python3 scripts/revolving/lords_register.py OUT_JSON [TERM ...]

For each search term, pages through /api/LordsInterests/Register?includeDeleted=true and keeps
only the individual entries whose text contains the term (the API returns whole members).
"""
import json
import sys
import time
import urllib.parse
import urllib.request

UA = "palantir-uk-open-data/1.0 (public-interest research)"
API = "https://members-api.parliament.uk/api/LordsInterests/Register"


def get(url):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception:  # noqa: BLE001
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("failed " + url)


def walk(term, include_deleted):
    hits = []
    page = 1
    while True:
        q = {"searchTerm": term, "page": page, "includeDeleted": str(include_deleted).lower()}
        url = API + "?" + urllib.parse.urlencode(q)
        d = get(url)
        items = d.get("items", [])
        for it in items:
            v = it["value"]
            m = v["member"]
            for cat in v.get("interestCategories", []):
                for i in cat.get("interests", []):
                    texts = [i.get("interest") or ""] + [c.get("interest") or "" for c in i.get("childInterests") or []]
                    full = " || ".join(t for t in texts if t)
                    if term.lower() in full.lower():
                        hits.append({
                            "term": term,
                            "member_id": m["id"],
                            "member": m["nameDisplayAs"],
                            "category": cat.get("name"),
                            "interest_id": i.get("id"),
                            "interest": full,
                            "created": i.get("createdWhen"),
                            "amended": i.get("lastAmendedWhen"),
                            "deleted": i.get("deletedWhen"),
                            "api_url": url,
                        })
        total = d.get("totalResults", 0)
        if not items or page * 20 >= total:
            break
        page += 1
        time.sleep(0.5)
    return hits


def main():
    out = sys.argv[1]
    terms = sys.argv[2:] or ["palantir"]
    hits = []
    for t in terms:
        hits += walk(t, True)
    json.dump(hits, open(out, "w"), indent=1)
    for h in hits:
        print(h["term"], "|", h["member"], "|", (h["created"] or "")[:10], "| deleted:",
              (h["deleted"] or "")[:10], "|", h["interest"][:300])


if __name__ == "__main__":
    main()
