#!/usr/bin/env python3
"""List ACOBA and departmental business appointment publications on GOV.UK, with attachments.

Read-only and polite: uses the public GOV.UK search and content APIs.

Usage:
    python3 scripts/revolving/enumerate_pubs.py WORK_DIR

Writes WORK_DIR/publications.json: one record per publication page, with its attachments
(downloadable files and HTML attachments) and the page body.
"""
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "palantir-uk-open-data/1.0 (public-interest research)"
SEARCH = "https://www.gov.uk/api/search.json"
CONTENT = "https://www.gov.uk/api/content"

# Phrase searches that catch departmental business appointment releases from every department.
PHRASES = [
    '"business appointment"',
    '"business appointments"',
    '"business appointment rules"',
    '"outside appointments"',
    '"appointment rules"',
]
ACOBA = "advisory-committee-on-business-appointments"
SKIP_FORMATS = {"organisation", "about", "accessible_documents_policy", "complaints_procedure",
                "personal_information_charter", "publication_scheme", "person", "ministerial_role",
                "worldwide_organisation", "detailed_guide", "manual", "manual_section"}


def get_json(url):
    for attempt in range(6):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", "20")))
                continue
            if e.code in (404, 410):
                return None
            time.sleep(3 * (attempt + 1))
        except Exception:  # noqa: BLE001
            time.sleep(3 * (attempt + 1))
    return None


def search_all(params):
    out = []
    start = 0
    while True:
        p = dict(params, count=1000, start=start,
                 fields="title,link,public_timestamp,format,organisations")
        d = get_json(SEARCH + "?" + urllib.parse.urlencode(p))
        if not d:
            break
        res = d.get("results", [])
        out.extend(res)
        start += len(res)
        if not res or start >= d.get("total", 0):
            break
        time.sleep(0.5)
    return out


def title_is_bar(title):
    t = title.lower()
    keys = ("business appointment", "acoba", "outside appointment", "appointment rules",
            "post-government employment", "post government employment", "business appointments")
    return any(k in t for k in keys)


def main():
    work = pathlib.Path(sys.argv[1])
    work.mkdir(parents=True, exist_ok=True)
    found = {}
    for r in search_all({"filter_organisations": ACOBA}):
        if r.get("format") in SKIP_FORMATS:
            continue
        found[r["link"]] = dict(r, why="acoba-org")
    for ph in PHRASES:
        for r in search_all({"q": ph}):
            if r.get("format") in SKIP_FORMATS or not r["link"].startswith("/government/"):
                continue
            if r["link"] in found:
                continue
            if title_is_bar(r.get("title", "")):
                found[r["link"]] = dict(r, why="phrase:" + ph)
    print(len(found), "candidate publications", file=sys.stderr)

    pubs = []
    for i, (link, r) in enumerate(sorted(found.items())):
        time.sleep(0.25)
        c = get_json(CONTENT + link)
        if not c:
            continue
        det = c.get("details", {})
        atts = []
        for a in det.get("attachments", []) or []:
            atts.append({k: a.get(k) for k in ("title", "url", "filename", "content_type",
                                               "attachment_type", "file_size")})
        orgs = [o.get("title") for o in c.get("links", {}).get("organisations", [])]
        pubs.append({
            "page_url": "https://www.gov.uk" + link,
            "title": c.get("title"),
            "document_type": c.get("document_type"),
            "first_published_at": c.get("first_published_at"),
            "public_updated_at": c.get("public_updated_at"),
            "organisations": orgs,
            "why": r["why"],
            "body": det.get("body", ""),
            "attachments": atts,
        })
        if i % 50 == 0:
            print(i, link[:100], len(atts), file=sys.stderr)
    (work / "publications.json").write_text(json.dumps(pubs, indent=1))
    print(len(pubs), "publications written", file=sys.stderr)


if __name__ == "__main__":
    main()
