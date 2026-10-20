#!/usr/bin/env python3
"""Rebuild data/contracts.csv and data/contracts.json from the official UK procurement APIs.

Sources (public, no key needed):
  - Contracts Finder: keyword search for "Palantir" over awarded notices, then each notice in full.
  - Find a Tender: each procurement in sources/fts_ocids.txt, read as an OCDS record package.

Only awards where Palantir is the sole named supplier are kept. Multi-supplier framework places
(where Palantir is one of dozens of approved suppliers and no money is committed) are left out.

Raw API responses are saved under sources/raw/ so every figure can be checked against what the
government published. Values are as published: some buyers publish ex-VAT, some inc-VAT.
"""
import csv
import html
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "sources" / "raw"
CF = "https://www.contractsfinder.service.gov.uk"
FTS = "https://www.find-tender.service.gov.uk/api/1.0"
UA = "palantir-uk-open-data/1.0 (public-interest research)"
PAUSE = 2.0

FIELDS = ["awarded", "buyer", "title", "value_gbp", "value_basis", "status", "procedure", "procedure_rationale",
          "start", "end", "source", "url", "notes"]


def get_json(url, body=None):
    req = urllib.request.Request(url, data=body, method="POST" if body else "GET",
                                 headers={"User-Agent": UA, "Accept": "application/json",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def is_sole_palantir(name):
    return bool(name) and "palantir" in name.lower() and name.count(",") <= 3


def contracts_finder():
    out_dir = RAW / "contracts-finder"
    body = json.dumps({"searchCriteria": {"statuses": ["Awarded"], "keyword": "Palantir"}, "size": 1000}).encode()
    search = get_json(f"{CF}/api/rest/2/search_notices/json", body)
    (out_dir / "search-palantir-awarded.json").write_text(json.dumps(search, indent=1))
    rows = []
    for n in search.get("noticeList") or []:
        item = n.get("item") or n
        if not is_sole_palantir(item.get("awardedSupplier")):
            continue
        time.sleep(PAUSE)
        detail = get_json(f"{CF}/api/rest/2/get_published_notice/json/{item['id']}")
        (out_dir / f"{item['id']}.json").write_text(json.dumps(detail, indent=1))
        notice = detail.get("notice") or detail
        award = next((a for a in detail.get("awards") or [] if is_sole_palantir(a.get("supplierName"))), {})
        rows.append({
            "awarded": (item.get("awardedDate") or "")[:10],
            "buyer": clean(notice.get("organisationName")),
            "title": clean(notice.get("title")),
            "value_gbp": award.get("value", item.get("awardedValue")),
            "value_basis": "as published on Contracts Finder",
            "status": "awarded",
            "procedure": notice.get("procedureType") or "",
            "procedure_rationale": clean(notice.get("reasonContractLawful")),
            "start": (award.get("startDate") or "")[:10],
            "end": (award.get("endDate") or "")[:10],
            "source": "Contracts Finder",
            "url": f"{CF}/Notice/{item['id']}",
            "notes": clean(notice.get("description"))[:400],
        })
    return rows


def find_a_tender():
    out_dir = RAW / "find-a-tender"
    rows = []
    for line in (ROOT / "sources" / "fts_ocids.txt").read_text().splitlines():
        ocid = line.split("#")[0].strip()
        if not ocid:
            continue
        time.sleep(PAUSE)
        pkg = get_json(f"{FTS}/ocdsRecordPackages/{ocid}")
        (out_dir / f"{ocid}.json").write_text(json.dumps(pkg, indent=1))
        record = (pkg.get("records") or [{}])[0]
        release = record.get("compiledRelease") or {}
        tender = release.get("tender") or {}
        contract_values = {c.get("awardID"): c.get("value") or {} for c in release.get("contracts") or []}
        contract_signed = {c.get("awardID"): c.get("dateSigned") for c in release.get("contracts") or []}
        for award in release.get("awards") or []:
            names = ", ".join(s.get("name", "") for s in award.get("suppliers") or [])
            if not is_sole_palantir(names) or award.get("status") == "cancelled":
                continue
            # Award notices sometimes leave the value to the contract details notice.
            value = award.get("value") or contract_values.get(award.get("id")) or {}
            period = award.get("contractPeriod") or {}
            rows.append({
                # Prefer the award date, then the signing date; the release date is only when it was published.
                "awarded": (award.get("date") or contract_signed.get(award.get("id")) or release.get("date") or "")[:10],
                "buyer": (release.get("buyer") or {}).get("name", ""),
                "title": clean(award.get("title") or tender.get("title")),
                "value_gbp": value.get("amountGross") or value.get("amount"),
                "value_basis": "inc. VAT" if value.get("amountGross") else "as published on Find a Tender",
                # "pending" = award decided, contract not yet confirmed on Find a Tender.
                "status": "decided, contract pending" if award.get("status") == "pending" else "awarded",
                "procedure": " / ".join(x for x in (tender.get("procurementMethod"), tender.get("procurementMethodDetails")) if x),
                "procedure_rationale": clean(tender.get("procurementMethodRationale"))[:1500],
                "start": (period.get("startDate") or "")[:10],
                "end": (period.get("endDate") or "")[:10],
                "source": "Find a Tender",
                "url": f"https://www.find-tender.service.gov.uk/procurement/{ocid}",
                "notes": clean(tender.get("description"))[:400],
            })
    return rows


def main():
    rows = contracts_finder() + find_a_tender()
    # The same procurement can appear on both services; keep one row per buyer + title, preferring
    # the row that carries a value, then Find a Tender (the fuller record).
    def key(r):
        return (re.sub(r"\W", "", r["buyer"].lower())[:12], r["title"].lower()[:40])

    best = {}
    for r in rows:
        k, have = key(r), best.get(key(r))
        rank = (float(r["value_gbp"] or 0) > 0, r["source"] == "Find a Tender")
        if not have or rank > (float(have["value_gbp"] or 0) > 0, have["source"] == "Find a Tender"):
            best[k] = r
    unique = list(best.values())
    unique.sort(key=lambda r: r["awarded"])
    with open(ROOT / "data" / "contracts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(unique)
    (ROOT / "data" / "contracts.json").write_text(json.dumps(unique, indent=1))
    total = sum(float(r["value_gbp"] or 0) for r in unique)
    print(f"{len(unique)} awards, £{total/1e6:,.1f}m as published")


if __name__ == "__main__":
    main()
