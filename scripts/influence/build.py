#!/usr/bin/env python3
"""Build data/influence.csv and data/influence-parliament.csv."""
import csv
import glob
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRATCH = HERE.parent
sys.path.insert(0, str(HERE))
import curated  # noqa: E402

PROJECT = Path(__file__).resolve().parents[2]
FIELDS = ["date", "category", "who", "organisation", "summary", "source_url", "source_type", "notes"]
HANSARD_UQ = "https://hansard-api.parliament.uk/debates/debate/FECED111-4FA8-4343-BFAF-18D6C13808D0.json"


def clean(s):
    return re.sub(r"\s+", " ", (s or "").replace("\n", " / ")).strip()


def returns_rows():
    rows = json.load(open(SCRATCH / "out" / "returns-rows.json"))
    # Docherty 26 May 2022 appears in both Cabinet Office and MOD returns: keep MOD, cite CO in notes
    co = [r for r in rows if r["who"] == "Leo Docherty" and r["organisation"] == "Cabinet Office"]
    for r in rows:
        if r["who"] == "Leo Docherty" and r["organisation"] == "Ministry of Defence" and co:
            r["notes"] += f" Also listed in the Cabinet Office ministerial meetings return for April to June 2022: {co[0]['source_url']}."
            r["notes"] += " He later joined Palantir as an adviser (ACOBA, February 2025)."
    rows = [r for r in rows if r not in co]
    for r in rows:
        w, d = r["who"], r["date"]
        if d == "2023-04-19" and r["category"] == "lobbying" and ";" in w:
            r["notes"] += " The MOD ministerial return lists James Heappey attending the 'Palantir / MOD Enterprise Agreement Launch Reception' the same day."
        if d == "2026-02-11" and r["category"] == "lobbying":
            r["notes"] += (" On 10 February 2026 Dr Ellie Chowns MP referred in the Commons to a Times report that Palantir was hosting a party for MOD officials the next day: " + HANSARD_UQ)
        if w == "Wes Streeting" and d == "2025-06-04":
            r["notes"] += " DHSC described this meeting in a written answer (PQ 67613): https://questions-statements-api.parliament.uk/api/writtenquestions/questions/1822776."
        if w == "John Healey" and d == "2025-09-10":
            r["notes"] += " A written answer (PQ 113369) refers to a separate 28 September 2025 meeting with Palantir's CEO in London."
        if w == "Barnaby Kistruck":
            r["notes"] += " He joined Palantir as Senior Counsellor on 9 September 2025 (MOD business appointment record)."
        if w == "Andy Bamford":
            r["notes"] += " Laurence Lee took up his Palantir role in February 2024; ACOBA's conditions ran for two years from his last day in Crown service."
        if w == "Oliver Robbins" and d == "2024-07-29":
            r["notes"] += " Date as published; the return is for July to September 2025."
        if w == "James Hockenhull" and d == "2025-04-03":
            r["notes"] += " Polly Scully, a former MOD Strategy Director, joined Palantir in November 2022 (MOD business appointment record)."
        if w == "Laurence Lee" or w.startswith("Laurence Lee;"):
            r["notes"] += " Laurence Lee was MOD Second Permanent Secretary from March 2021 to May 2023 and joined Palantir in February 2024 (ACOBA)."
        if w == "Rupert Pearce":
            r["notes"] += " Listed as National Armaments Director on the Defence Industrial Joint Council page."
        if w == "Leo Docherty":
            pass
        if re.match(r"^\d{4}-\d{2}$", d):
            r["notes"] += " The return gives the month only."
        if w == "The Rt Hon Jeremy Hunt MP":
            r["notes"] += " The same return lists introductory discussions with Apple Inc, Google Life Sciences and Microsoft on the same date (dates in this return are shown as the first of the month)."
    return rows


def main():
    rows = returns_rows()
    cur = curated.ROWS
    for r in cur:
        if r["who"] == "Wes Streeting" and r["date"] == "2025-06-04" and r["category"] == "meeting":
            r["date"], r["category"] = "2025-07-22", "parliament"
    rows += cur
    for r in rows:
        for k in FIELDS:
            r[k] = clean(r.get(k, ""))
    rows.sort(key=lambda r: (r["date"][:10], r["category"], r["who"]))
    out = PROJECT / "data" / "influence.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print("influence.csv rows:", len(rows))
    json.dump(rows, open(SCRATCH / "out" / "influence-final.json", "w"), indent=1, ensure_ascii=False)

    # ------------------------------------------------------------ full parliamentary index
    idx = []
    for f in glob.glob(str(SCRATCH / "dl/parl/pqid/*.json")):
        v = json.load(open(f))["value"]
        if not re.search(r"palantir", (v.get("questionText") or "") + (v.get("answerText") or "") + (v.get("heading") or ""), re.I):
            continue
        a = clean(html.unescape(re.sub(r"<[^>]+>", " ", v.get("answerText") or "")))
        q = clean(v.get("questionText"))
        asker = (v.get("askingMember") or {}).get("name") or ""
        answerer = (v.get("answeringMember") or {}).get("name") or ""
        da = (v.get("dateAnswered") or "")[:10]
        summ = f"Q ({asker}): {q[:400]}{'…' if len(q) > 400 else ''}"
        summ += f" A ({answerer}, {da}): {a[:500]}{'…' if len(a) > 500 else ''}" if a else " No answer recorded at time of collection."
        idx.append(dict(date=v["dateTabled"][:10], record_type="written question", house=v["house"],
                        reference=v["uin"], title=clean(v.get("heading")), member=asker,
                        body=v.get("answeringBodyName") or "", summary=summ,
                        source_url=f"https://questions-statements-api.parliament.uk/api/writtenquestions/questions/{v['id']}",
                        web_url=f"https://questions-statements.parliament.uk/written-questions/detail/{v['dateTabled'][:10]}/{v['uin']}"))
    spoken = []
    for f in glob.glob(str(SCRATCH / "dl/parl/hansard-spoken-*.json")):
        spoken += json.load(open(f))["Results"]
    by = {}
    for c in spoken:
        by.setdefault(c["DebateSectionExtId"], []).append(c)
    for ext, cs in by.items():
        d = json.load(open(SCRATCH / f"dl/parl/debates/{ext}.json"))["Overview"]
        title = clean(d.get("Title"))
        slug = "".join(w[:1].upper() + w[1:] for w in re.sub(r"[^A-Za-z0-9 ]", " ", title).split())
        speakers = sorted({c.get("MemberName") or c.get("AttributedTo") or "" for c in cs} - {""})
        first = clean(re.sub(r"<[^>]+>", "", cs[0].get("ContributionTextFull") or ""))
        m = re.search(r"[^.]*palantir[^.]*\.", first, re.I)
        excerpt = m.group(0).strip() if m else first[:250]
        idx.append(dict(date=d["Date"][:10], record_type=f"debate ({cs[0].get('Section') or ''})".replace(" ()", ""),
                        house=d.get("House") or cs[0].get("House"), reference=ext, title=title, member="; ".join(speakers),
                        body=cs[0].get("Section") or "",
                        summary=f"{len(cs)} contribution(s) mentioning Palantir. Example: \"{excerpt[:400]}\"",
                        source_url=f"https://hansard-api.parliament.uk/debates/debate/{ext}.json",
                        web_url=f"https://hansard.parliament.uk/{d.get('House') or cs[0].get('House')}/{d['Date'][:10]}/debates/{ext}/{slug}"))
    ws = json.load(open(SCRATCH / "dl/parl/hcws57.json"))["value"]
    idx.append(dict(date=ws["dateMade"][:10], record_type="written statement", house=ws["house"], reference=ws["uin"],
                    title=clean(ws["title"]), member=ws.get("memberRole") or "", body="Department of Health and Social Care",
                    summary="Announces NHS England's award of the Federated Data Platform contract to a group led by Palantir Technologies UK; up to £330 million over seven years.",
                    source_url="https://questions-statements-api.parliament.uk/api/writtenstatements/statements/1671624",
                    web_url="https://questions-statements.parliament.uk/written-statements/detail/2023-11-21/hcws57"))
    for kind, fid in (("WrittenEvidence", 107376), ("WrittenEvidence", 120296), ("WrittenEvidence", 127784),
                      ("OralEvidence", 13042), ("OralEvidence", 14358), ("OralEvidence", 16290)):
        pre = "we" if kind == "WrittenEvidence" else "oe"
        d = json.load(open(SCRATCH / f"dl/parl/committees/{pre}-{fid}.json"))
        date = ((d.get("meetingDate") if pre == "oe" else d.get("publicationDate")) or "")[:10]
        biz = d.get("committeeBusiness", {}).get("title") if kind == "WrittenEvidence" else "; ".join(b["title"] for b in d.get("committeeBusinesses", []))
        comms = "; ".join(c["name"] for c in d.get("committees", []))
        wit = "; ".join((w.get("name") or "") + " (" + ", ".join(o["name"] + (" " + o["role"] if o.get("role") else "") for o in (w.get("organisations") or [])) + ")" for w in d.get("witnesses", []))
        idx.append(dict(date=date, record_type="committee " + ("written evidence" if pre == "we" else "oral evidence"),
                        house="", reference=str(fid), title=biz, member=clean(wit), body=comms,
                        summary=("Written evidence submitted by Palantir." if pre == "we" else f"Oral evidence session with witnesses: {clean(wit)}."),
                        source_url=f"https://committees-api.parliament.uk/api/{kind}/{fid}",
                        web_url=f"https://committees.parliament.uk/{kind.lower()}/{fid}/html/"))
    for pid, doc, date, title, body, summ in (
            (53352, 298462, "2026-06-03", "Rewiring the state: Delivering digital government (HC 61)", "Science, Innovation and Technology Committee (Commons)",
             "Report concluding that Palantir 'should not have such a significant role in the UK public sector' and recommending exercising the February 2027 Federated Data Platform break clause."),
            (54095, 302120, "2026-07-09", "Correspondence to Minister Gill re Palantir", "Health and Social Care Committee (Commons)",
             "Letter (8 July 2026) recommending that Palantir's Federated Data Platform contract not be extended when it ends in March 2027.")):
        idx.append(dict(date=date, record_type="committee publication", house="Commons", reference=str(pid), title=title, member="",
                        body=body, summary=summ, source_url=f"https://committees-api.parliament.uk/api/Publications/{pid}/Document/{doc}/OriginalFormat",
                        web_url=f"https://committees.parliament.uk/publications/{pid}/"))
    idx.sort(key=lambda r: (r["date"], r["record_type"], r["reference"]))
    f2 = ["date", "record_type", "house", "reference", "title", "member", "body", "summary", "source_url", "web_url"]
    with open(PROJECT / "data" / "influence-parliament.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=f2)
        w.writeheader()
        for r in idx:
            w.writerow({k: clean(str(r.get(k, ""))) for k in f2})
    print("influence-parliament.csv rows:", len(idx))


if __name__ == "__main__":
    main()
