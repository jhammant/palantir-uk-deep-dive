#!/usr/bin/env python3
"""Convert matched transparency-return rows (meeting-rows.jsonl) into influence.csv rows.

One output row per (department, person, date): meetings, hospitality and travel-expense records for the
same person on the same day are merged. Group hospitality at a single Palantir event (same file, date and
provider) is merged into one row listing every official named.
"""
import json
import re
import sys
from collections import OrderedDict
from datetime import datetime

DEPTS = {
    "cabinet-office": "Cabinet Office",
    "department-for-business-and-trade": "Department for Business and Trade",
    "department-for-business-energy-and-industrial-strategy": "Department for Business, Energy and Industrial Strategy",
    "department-for-digital-culture-media-sport": "Department for Digital, Culture, Media and Sport",
    "department-for-levelling-up-housing-and-communities": "Department for Levelling Up, Housing and Communities",
    "department-for-science-innovation-and-technology": "Department for Science, Innovation and Technology",
    "department-for-transport": "Department for Transport",
    "department-of-health-and-social-care": "Department of Health and Social Care",
    "foreign-commonwealth-development-office": "Foreign, Commonwealth and Development Office",
    "hm-revenue-customs": "HM Revenue and Customs",
    "hm-treasury": "HM Treasury",
    "home-office": "Home Office",
    "ministry-of-defence": "Ministry of Defence",
    "ministry-of-justice": "Ministry of Justice",
}
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
PAL = re.compile(r"palantir|palantair|louis mos", re.I)


def parse_date(cells, title):
    for c in cells:
        c = c.strip()
        m = re.match(r"^(\d{4})[-/](\d{2})[-/](\d{2})", c)
        if m:
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", c)
        if m:
            return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    for c in cells:
        if c.strip().lower() in MONTHS:
            years = re.findall(r"20\d{2}", title)
            return f"{years[-1]}-{MONTHS[c.strip().lower()]:02d}"
    return ""


def kind_of(att_title, table="", header=()):
    t = att_title.lower()
    combined = "gifts" in t and "meeting" in t
    if combined:
        tb = (table or "").lower()
        for k, v in (("meeting", "meeting"), ("hospitality", "hospitality"), ("travel", "travel")):
            if k in tb:
                return v
        h = " ".join(header).lower()
        if "hospitality" in h and "meeting" not in h:
            return "hospitality"
        return "meeting"
    if "hospitality" in t:
        return "hospitality"
    if "expenses" in t or "travel" in t:
        return "travel"
    return "meeting"


def clean_name(n):
    n = re.sub(r"\s+", " ", n.replace("\n", ", ")).strip(" ,")
    if n.isupper():
        n = n.title()
    return n


def dept_of(r):
    t = (r.get("att_title") or "") + " " + (r.get("title") or "")
    if "Number 10" in t or "Boris Johnson MP meetings" in t or "Keir Starmer" in t:
        return "Prime Minister's Office, 10 Downing Street"
    org = (r.get("orgs") or [None])[0]
    d = DEPTS.get(org, org or "")
    if d == "Department of Health and Social Care" and r["pub_date"] < "2018-01-08":
        d = "Department of Health"
    return d


def describe_counterparty(cell):
    cell = re.sub(r"\s+", " ", cell).strip()
    m = re.match(r"^(.{3,90}?)(?:\s+-\s+|\s*\((?:Attendees:)?\s*|\s+including\s+(?:representatives\s+from\s+)?|:\s+)(.*)$", cell)
    prefix, rest = (m.group(1).strip(), m.group(2)) if m else ("", cell)
    parts = [p for p in re.split(r"[;,]\s*|\s+and\s+", rest) if p.strip()]
    if len(parts) > 3:
        label = f"'{prefix}'" if prefix and not re.search(r"palantir", prefix, re.I) else "a group meeting"
        return f"{label}, with {len(parts)} listed attendees (as published) including Palantir", True
    return f"'{cell}'", False


def main(src, out):
    rows = [json.loads(l) for l in open(src) if '"row"' in l]
    pdf_pubs = {r["pub"] for r in rows if not r["url"].lower().endswith(".pdf")}
    recs = []
    for r in rows:
        if r["url"].lower().endswith(".pdf") and r["pub"] in pdf_pubs:
            continue  # same publication has a CSV version
        cells = r["row"]
        who = clean_name(r["carry_name"] if not PAL.search(r["carry_name"]) else cells[0])
        if parse_date([who], r["title"]):
            who = clean_name(r["carry_name"])
        date = parse_date(cells, r["att_title"] + " " + r["title"])
        kind = kind_of(r["att_title"], r.get("table", ""), r.get("header") or [])
        pal_idx = next((i for i, c in enumerate(cells) if PAL.search(c)), None)
        pal_cell = cells[pal_idx] if pal_idx is not None else ""
        after = cells[pal_idx + 1] if pal_idx is not None and pal_idx + 1 < len(cells) else ""
        recs.append(dict(dept=dept_of(r), who=who, date=date, kind=kind, pal=pal_cell, after=after,
                         url=r["url"], att=r["att_title"].strip(), pub="https://www.gov.uk" + r["pub"]))

    # merge group hospitality at a single event (same file, date, provider)
    out_rows = []
    groups = OrderedDict()
    for x in recs:
        if x["kind"] == "hospitality":
            prov = "palantir" if re.search(r"^\W*palantir", x["pal"], re.I) else re.sub(r"[^a-z]", "", x["pal"].lower())
            key = (x["url"], x["date"], prov)
            groups.setdefault(key, []).append(x)
    used = set()
    for key, xs in groups.items():
        if len(xs) > 1:
            for x in xs:
                used.add(id(x))
            names = "; ".join(dict.fromkeys(x["who"] for x in xs))
            types = sorted({x["after"] for x in xs if x["after"]})
            out_rows.append(dict(
                date=xs[0]["date"], category="lobbying", who=names, organisation=xs[0]["dept"],
                summary=(f"{xs[0]['att']} records {len(xs)} officials receiving hospitality from Palantir "
                         f"on {xs[0]['date']} (types listed: {', '.join(dict.fromkeys(t.lower() for t in types))})."),
                source_url=xs[0]["url"], source_type="official",
                notes=f"Hospitality received. Publication: {xs[0]['pub']}"))

    # merge same person + date + dept across meeting/hospitality/travel
    persons = OrderedDict()
    for x in recs:
        if id(x) in used:
            continue
        key = (x["dept"], re.sub(r"[^a-z]", "", x["who"].lower()), x["date"])
        persons.setdefault(key, []).append(x)
    for key, xs in persons.items():
        kinds = [x["kind"] for x in xs]
        parts = []
        for x in xs:
            if x["kind"] == "meeting":
                cp, multi = describe_counterparty(x["pal"])
                if multi:
                    parts.append(f"{cp}; purpose given: '{x['after']}'" if x["after"] else cp)
                    multi_seen = True
                else:
                    parts.append(f"a meeting with {cp}" + (f"; purpose given: '{x['after']}'" if x["after"] else ""))
            elif x["kind"] == "hospitality":
                parts.append(f"hospitality from '{x['pal']}'" + (f" ({x['after'].lower()})" if x["after"] else ""))
            else:
                parts.append(f"travel claimed with the stated purpose '{x['pal']}'")
        parts = list(dict.fromkeys(parts))
        first = xs[0]
        returns = xs[0]["att"]
        who = first["who"]
        summary = f"{first['dept']} transparency return ({returns}) lists {who}: " + "; ".join(parts) + f", on {first['date']}."
        category = "lobbying" if set(kinds) == {"hospitality"} else "meeting"
        other_urls = [x["url"] for x in xs[1:] if x["url"] != first["url"]]
        notes = "Hospitality received. " if category == "lobbying" else ""
        if other_urls:
            notes += "Also in: " + " ; ".join(dict.fromkeys(other_urls)) + ". "
        notes += f"Publication: {first['pub']}"
        out_rows.append(dict(date=first["date"], category=category, who=who, organisation=first["dept"],
                             summary=summary, source_url=first["url"], source_type="official", notes=notes.strip()))
    json.dump(out_rows, open(out, "w"), indent=1, ensure_ascii=False)
    print(len(recs), "records ->", len(out_rows), "rows")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
