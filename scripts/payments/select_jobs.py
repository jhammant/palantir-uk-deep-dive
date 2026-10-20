#!/usr/bin/env python3
"""Turn enum-*.json files into download jobs for 2020 onwards, spend-over files only."""
import json
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parents[2] / "sources" / "raw" / "payments" / "_work"  # local, not published
MIN_YEAR = 2020

# enum file -> (payer slug, publication title must contain any of, publication title must not contain)
CONF = {
    "enum-mod.json": ("ministry-of-defence", ["over £25,000"], ["exemptions", "April 2010"]),
    "enum-dhsc.json": ("dhsc", ["£25,000"], []),
    "enum-co.json": ("cabinet-office", ["spend data over £25,000"], []),
    "enum-ho.json": ("home-office", ["spending over £25,000"], ["2010 to 2013"]),
    "enum-mhclg.json": ("mhclg", ["spending over"], []),
    "enum-dluhc.json": ("mhclg", ["spending over"], []),
    "enum-mhclg-old.json": ("mhclg", ["spending over"], []),
    "enum-defra.json": ("defra", ["£25,000"], []),
    "enum-hmt.json": ("hm-treasury", ["£25,000", "25k", "25,000"], []),
    "enum-ukhsa.json": ("ukhsa", ["£25,000"], []),
    "enum-dbt.json": ("dbt", ["£25,000"], []),
}

YEAR = re.compile(r"(20[12]\d)")


def year_of(*texts):
    for t in texts:
        m = YEAR.findall(t or "")
        if m:
            return int(m[-1])
    return None


def main():
    jobs = []
    for fname, (payer, must, mustnot) in CONF.items():
        p = WORK / fname
        if not p.exists():
            continue
        d = json.load(open(p))
        for pub in d["publications"]:
            t = pub["title"]
            if not any(m.lower() in t.lower() for m in must) or any(x.lower() in t.lower() for x in mustnot):
                continue
            for a in pub["attachments"]:
                if not a.get("url") or not a["url"].startswith("http"):
                    continue
                y = year_of(a.get("title"), a.get("filename"), t)
                if y is None:
                    y = year_of(pub.get("first_published_at"))
                if y is None or y < MIN_YEAR:
                    continue
                ct = (a.get("content_type") or "").lower()
                if "pdf" in ct or (a.get("filename") or "").lower().endswith(".pdf"):
                    continue
                jobs.append({"payer": payer, "page_url": pub["page_url"], "file_url": a["url"],
                             "filename": a.get("filename"), "att_title": a.get("title"),
                             "pub_title": t, "year_hint": y})
    # de-dupe by url
    seen, out = set(), []
    for j in jobs:
        if j["file_url"] in seen:
            continue
        seen.add(j["file_url"])
        out.append(j)
    from collections import Counter
    print(Counter(j["payer"] for j in out), file=sys.stderr)
    json.dump(out, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
