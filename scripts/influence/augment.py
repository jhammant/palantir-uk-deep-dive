#!/usr/bin/env python3
"""Add per-organisation transparency publications mentioning meetings, and expand collections."""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

PUBS = Path(sys.argv[1])
UA = "palantir-uk-open-data/1.0 (public-interest research)"
ORGS = """cabinet-office home-office department-for-work-pensions department-for-transport hm-treasury
department-of-health-and-social-care ministry-of-justice department-for-digital-culture-media-sport
department-for-environment-food-rural-affairs department-for-international-development department-of-energy-climate-change
northern-ireland-office department-for-education department-for-business-innovation-skills
ministry-of-housing-communities-and-local-government-2018-2021 department-for-business-energy-and-industrial-strategy
office-of-the-advocate-general-for-scotland foreign-commonwealth-development-office office-of-the-secretary-of-state-for-wales
ministry-of-defence foreign-commonwealth-office department-for-business-and-trade department-for-culture-media-and-sport
hm-revenue-customs department-for-exiting-the-european-union department-for-science-innovation-and-technology
department-for-energy-security-and-net-zero ministry-of-housing-communities-local-government
department-for-levelling-up-housing-and-communities office-of-the-secretary-of-state-for-scotland attorney-generals-office
uk-health-security-agency department-for-international-trade prime-ministers-office-10-downing-street
government-digital-service public-health-england department-for-communities-and-local-government
uk-export-finance office-of-the-leader-of-the-house-of-commons office-of-the-leader-of-the-house-of-lords
scotland-office wales-office the-office-of-the-leader-of-the-house-of-commons department-for-digital-culture-media-and-sport
government-equalities-office cabinet-office-2 nhs-digital nhs-england central-digital-and-data-office
department-for-business-innovation-science-and-trade crown-commercial-service""".split()


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


pubs = {p["link"]: p for p in json.loads(PUBS.read_text())}
n0 = len(pubs)
for org in ORGS:
    for q in ("meetings", "hospitality"):
        start = 0
        while True:
            params = {"q": q, "count": 1000, "start": start, "filter_organisations": org,
                      "fields": "title,link,public_timestamp,organisations,content_store_document_type"}
            data = get("https://www.gov.uk/api/search.json?" + urllib.parse.urlencode(params))
            if not data:
                break
            res = data.get("results", [])
            for r in res:
                t = (r.get("title") or "").lower()
                if "meeting" not in t and "hospitality" not in t:
                    continue
                if r["link"] not in pubs:
                    orgs = [o.get("slug") for o in r.get("organisations", []) if isinstance(o, dict)]
                    pubs[r["link"]] = {"title": r.get("title"), "link": r["link"],
                                       "public_timestamp": r.get("public_timestamp"), "orgs": orgs,
                                       "type": r.get("content_store_document_type"), "via": "org:" + org}
            start += 1000
            if not res or start >= min(data.get("total", 0), 3000):
                break
            time.sleep(1)
    print(org, len(pubs), file=sys.stderr)
    time.sleep(0.5)

# expand document collections
for link, p in list(pubs.items()):
    if p.get("type") != "document_collection":
        continue
    data = get("https://www.gov.uk/api/content" + link)
    if not data:
        continue
    for d in data.get("links", {}).get("documents", []):
        bp = d.get("base_path")
        if bp and bp not in pubs:
            pubs[bp] = {"title": d.get("title"), "link": bp, "public_timestamp": d.get("public_updated_at"),
                        "orgs": p.get("orgs"), "type": d.get("document_type"), "via": "collection:" + link}
    time.sleep(0.3)

PUBS.write_text(json.dumps(sorted(pubs.values(), key=lambda x: x["link"]), indent=1))
print(n0, "->", len(pubs))
