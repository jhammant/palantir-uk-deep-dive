#!/usr/bin/env python3
"""Palantir's share of each public body's IT/software/data spend, from the published spend files.

Reads every saved spend file listed in data/payments-files-checked.csv (one file in memory at a
time) and writes:
    data/market-share.csv          totals and Palantir's share, per payer, per calendar year and overall
    data/market-top-suppliers.csv  top 10 suppliers in the IT/software/data labels, per payer and period
    data/market-categories.csv     every label counted as IT/software/data, and every borderline label left out

Run from anywhere:  python3 scripts/market/build_market.py [details.json]
The optional argument is a path for a JSON file of the checks behind the figures (kept out of data/).

Method in brief (data/market-notes.md has the full version):
- every payment line in every file is read; total rows, blank rows and header rows are skipped
- a file with at least 90% of its lines in another file of the same payer is a copy and is not
  counted (amounts compared to the nearest pound)
- a line repeated in a later file with the same date, supplier, amount and transaction reference
  is counted once; lines repeated inside one file are kept (they are separate published lines)
- IT/software/data spend is the lines whose published category label is classified as such by
  categories.py, in files whose category column can separate IT spend at all
- Palantir lines are lines whose supplier name contains "palantir", net of credit notes
- the share of IT spend counts only the Palantir lines that sit under IT labels, so it is a true
  share of that total; Palantir lines booked under other labels are reported in the coverage note
- shares are written as fractions from 0 to 1 (0.106428 is 10.6428%)
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import PAYERS, FileStats, iter_file, manifest_files, published_month, PROJECT  # noqa: E402
from categories import NO_IT_SCHEME, classify, it_scheme, norm  # noqa: E402

DATA = PROJECT / "data"
PAL = re.compile(r"palantir", re.I)
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# legal-form words only; "UK" is kept so that, for example, Accenture PLC and Accenture (UK) Ltd stay apart
SUFFIXES = {"LIMITED", "LTD", "PLC", "LLP", "LP", "INC", "INCORPORATED", "CORP", "CORPORATION", "CO", "COMPANY"}


def q2(v):
    return Decimal(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def money(v):
    return f"{q2(v):.2f}"


def gbp(v):
    v = q2(v)
    return ("-£" if v < 0 else "£") + f"{abs(v):,.2f}"


def merge_key(name):
    """Key that merges obvious variants of one company's name (case, punctuation, legal suffixes)."""
    s = (name or "").upper().replace("&", " AND ")
    s = re.sub(r"^\d{5,}\s*-?\s*", "", s)          # leading supplier codes, e.g. "00000664-WATES ..."
    s = re.sub(r"[^\w\s]", " ", s)
    words = s.split()
    while words and words[-1] in SUFFIXES:
        words.pop()
    while words and words[0] == "THE":
        words.pop(0)
    return " ".join(words) or (name or "").upper().strip()


def month_label(ym):
    y, m = ym.split("-")
    return f"{MON[int(m) - 1]} {y}"


def month_ranges(months):
    """['2020-01','2020-02','2020-04'] -> 'Jan 2020 to Feb 2020, Apr 2020'"""
    ms = sorted(months)
    if not ms:
        return ""
    idx = [int(m[:4]) * 12 + int(m[5:]) - 1 for m in ms]
    out, start, prev = [], idx[0], idx[0]
    for i in idx[1:] + [None]:
        if i is not None and i == prev + 1:
            prev = i
            continue
        a = f"{MON[start % 12]} {start // 12}"
        b = f"{MON[prev % 12]} {prev // 12}"
        out.append(a if start == prev else f"{a} to {b}")
        if i is not None:
            start = prev = i
    return ", ".join(out)


def missing_months(months, first, last):
    have = set(months)
    a = int(first[:4]) * 12 + int(first[5:]) - 1
    b = int(last[:4]) * 12 + int(last[5:]) - 1
    return [f"{i // 12}-{i % 12 + 1:02d}" for i in range(a, b + 1) if f"{i // 12}-{i % 12 + 1:02d}" not in have]


class Agg:
    def __init__(self):
        self.all_total = Decimal(0)
        self.all_rows = 0
        self.files = set()
        self.it_total = Decimal(0)
        self.it_rows = 0
        self.it_files = set()
        self.pal_total = Decimal(0)
        self.pal_rows = 0
        self.pal_it = Decimal(0)
        self.pal_capable = Decimal(0)
        self.pal_other_labels = Counter()
        self.pal_nocap = Decimal(0)
        self.sup_amount = Counter()
        self.sup_names = defaultdict(Counter)
        self.dupes = 0
        self.dupe_amount = Decimal(0)
        self.undated = 0
        self.undated_amount = Decimal(0)


def find_copies(payer, paths, mrows):
    """Files that repeat another file: at least 90% of their lines (date, supplier, amount, reference)
    are also in one other file of the same payer. Returns {copy_path: kept_path}."""
    fps, modal, named, pence = {}, {}, {}, {}
    for path in paths:
        st = FileStats(path)
        fp = Counter()
        months = Counter()
        pence[path] = 0
        for r in iter_file(payer, path, st):
            # amounts compared to the nearest pound: one Home Office CSV rounds amounts that its ODS twin
            # gives in pence
            amt = r["amount"].quantize(Decimal("1"), rounding=ROUND_HALF_UP) if r["amount"] is not None else None
            fp[(r["date"], re.sub(r"\s+", " ", r["supplier"].upper()).strip(), amt, r["txn"].strip().upper())] += 1
            if r["amount"] is not None and r["amount"] != r["amount"].quantize(Decimal("1")):
                pence[path] += 1
            if r["date"]:
                months[r["date"][:7]] += 1
        fps[path] = fp
        modal[path] = months.most_common(1)[0][0] if months else None
        named[path] = published_month(payer, path, mrows.get(path), None, st.pdf_title)[0]
    order = {p: i for i, p in enumerate(paths)}
    contained = {}
    for a in paths:
        na = sum(fps[a].values())
        if not na:
            continue
        for b in paths:
            if a == b or not fps[b]:
                continue
            nb = sum(fps[b].values())
            if nb < 0.9 * na:
                continue
            small, big = (fps[a], fps[b]) if len(fps[a]) <= len(fps[b]) else (fps[b], fps[a])
            overlap = sum(min(v, big[k]) for k, v in small.items() if k in big)
            if overlap >= 0.9 * na:
                contained.setdefault(a, []).append(b)
    copies = {}
    for a, holders in contained.items():
        for b in holders:
            if b in copies:
                continue
            mutual = a in contained.get(b, [])
            if mutual:                             # the two files hold the same lines: keep one
                def score(p):  # keep the file whose name matches its dates, then the one with pence
                    return (named[p] == modal[p], pence[p], -order[p])
                if score(a) > score(b):
                    continue
            # a copy inside a larger file still covers its own month (its lines are in the larger file);
            # an identical copy covers only the month its lines are dated in
            copies[a] = {"kept": b, "mutual": mutual, "month": named[a] or modal[a]}
            break
    return copies


def process_payer(payer, paths, details, mrows):
    aggs = defaultdict(Agg)
    months_all, months_it, nocap_reasons = set(), set(), defaultdict(Counter)
    nocap_months = defaultdict(set)
    seen, ref_seen = {}, {}
    sheet_info, removed_in_file = [], Counter()
    labels = defaultdict(lambda: [0, Decimal(0), Decimal(0), Counter()])  # norm label -> rows, amt, pal, forms
    d = details[payer] = {"files": [], "dupes_removed": [], "same_ref_other_date": [], "same_ref_other_date_n": 0,
                          "same_ref_other_date_amount": "0", "within_file_same_key": 0, "unreadable_files": [],
                          "lines_left_out": [], "undated_lines": [], "other_order_dates": 0, "entities": Counter(),
                          "year_corrections": [], "copies_dropped": []}
    sroa = Decimal(0)
    copies = find_copies(payer, paths, mrows)
    for c, info in copies.items():
        d["copies_dropped"].append({"path": c, "copy_of": info["kept"], "identical": info["mutual"],
                                    "month": info["month"]})
    for path in paths:
        if path in copies:
            continue
        st = FileStats(path)
        recs = list(iter_file(payer, path, st))
        info = {"path": path, "lines": len(recs), "sheets": st.sheets_used, "note": st.note,
                "date_order": st.date_order, "category_col": sorted(st.category_col),
                "no_category_sheets": st.no_category_sheets, "unreadable": st.unreadable,
                "total_rows_skipped": len(st.skipped_total_rows)}
        d["files"].append(info)
        if st.unreadable:
            d["unreadable_files"].append({"path": path, "reason": st.note})
        for u in st.unparsed:
            if u[2].startswith("date not parsed"):
                continue
            d["lines_left_out"].append({"path": path, "sheet": u[0], "row": u[1], "reason": u[2], "cells": u[3]})
        d["other_order_dates"] += len(st.other_order_dates)
        # per sheet: reporting month and whether its labels can separate IT
        by_sheet = defaultdict(list)
        for r in recs:
            by_sheet[r["sheet"]].append(r)
        sheet_cap = {}
        for sh, rs in by_sheet.items():
            pm, how = published_month(payer, path, mrows.get(path), sh, st.pdf_title)
            cnt = Counter(r["date"][:7] for r in rs if r["date"])
            modal = cnt.most_common(1)[0][0] if cnt else None
            if not pm:
                pm, how = (modal, "most common payment month") if modal else (None, "")
            elif modal and pm[5:] == modal[5:] and abs(int(pm[:4]) - int(modal[:4])) == 1:
                d["year_corrections"].append({"path": path, "sheet": sh, "named": pm, "payment_dates": modal})
                pm, how = modal, how + "; year corrected to the payment dates (the name gives the wrong year)"
            labs = {r["category"] for r in rs if r["category"]}
            cap, why = it_scheme(payer, labs)
            sheet_cap[sh] = cap
            sheet_info.append({"path": path, "sheet": sh, "month": pm, "month_source": how, "cap": cap, "why": why,
                               "lines": len(rs)})
        seen_rows = set()
        for r in recs:
            k = (r["sheet"],) + tuple(r["cells"])
            if k in seen_rows and r["amount"] is not None:
                d["within_file_identical_n"] = d.get("within_file_identical_n", 0) + 1
                d["within_file_identical_amount"] = str(Decimal(d.get("within_file_identical_amount", "0")) + r["amount"])
            seen_rows.add(k)
        for r in recs:
            amt = r["amount"]
            if amt is None:
                d["lines_left_out"].append({"path": path, "sheet": r["sheet"], "row": r["row"],
                                            "reason": "amount not read", "cells": r["cells"][:10]})
                continue
            sup = r["supplier"]
            supkey = re.sub(r"\s+", " ", sup.upper()).strip()
            txn = r["txn"].strip().upper()
            if txn:
                key = (r["date"], supkey, q2(amt), txn)
                if key in seen and seen[key] != path:
                    removed_in_file[path] += 1
                    for per in ("all", r["date"][:4] if r["date"] else None):
                        if per:
                            aggs[per].dupes += 1
                            aggs[per].dupe_amount += amt
                    d.setdefault("dupes_by_file", Counter())[f"{Path(path).name} <= {Path(seen[key]).name}"] += 1
                    if len(d["dupes_removed"]) < 400:
                        d["dupes_removed"].append({"path": path, "first_seen_in": seen[key], "date": r["date"],
                                                   "supplier": sup, "amount": str(amt), "txn": r["txn"]})
                    continue
                if key in seen:
                    d["within_file_same_key"] += 1
                seen.setdefault(key, path)
                k2 = (supkey, q2(amt), txn)
                prev = ref_seen.get(k2)
                if prev is None:
                    ref_seen[k2] = (path, r["date"])
                elif prev[0] != path and prev[1] != r["date"]:
                    d["same_ref_other_date_n"] += 1
                    sroa += amt
                    d.setdefault("sroa_by_file", Counter())[f"{Path(path).name} <= {Path(prev[0]).name}"] += 1
                    if PAL.search(sup) or len(d["same_ref_other_date"]) < 60:
                        d["same_ref_other_date"].append({"path": path, "first_seen_in": prev[0], "first_date": prev[1],
                                                         "date": r["date"], "supplier": sup, "amount": str(amt),
                                                         "txn": r["txn"], "palantir": bool(PAL.search(sup))})
            if r["entity"]:
                d["entities"][(r["date"] or "")[:4] + " | " + r["entity"]] += 1
            cap = sheet_cap[r["sheet"]]
            lab = norm(r["category"]) if r["category"] else ""
            included = False
            if lab:
                lv = labels[lab]
                lv[0] += 1
                lv[1] += amt
                lv[3][r["category"]] += 1
                lv.append(r["category_col"]) if len(lv) == 4 else None
                if PAL.search(sup):
                    lv[2] += amt
                included = cap and classify(payer, lab)[0]
            is_pal = bool(PAL.search(sup))
            pers = ["all"] + ([r["date"][:4]] if r["date"] else [])
            if not r["date"]:
                d["undated_lines"].append({"path": path, "row": r["row"], "date_raw": r["date_raw"],
                                           "supplier": sup, "amount": str(amt)})
            for per in pers:
                a = aggs[per]
                a.all_total += amt
                a.all_rows += 1
                a.files.add(path)
                if per == "all" and not r["date"]:
                    a.undated += 1
                    a.undated_amount += amt
                if cap:
                    a.it_files.add(path)
                if included:
                    a.it_total += amt
                    a.it_rows += 1
                    mk = merge_key(sup)
                    a.sup_amount[mk] += amt
                    a.sup_names[mk][sup] += amt
                if is_pal:
                    a.pal_total += amt
                    a.pal_rows += 1
                    if cap:
                        a.pal_capable += amt
                        if included:
                            a.pal_it += amt
                        else:
                            a.pal_other_labels[r["category"] or "(no label)"] += amt
                    else:
                        a.pal_nocap += amt
        del recs
    d["same_ref_other_date_amount"] = str(sroa)
    # months covered: a file whose lines are (almost) all repeats of another file's lines is a copy,
    # so it does not cover the month its name gives
    d["copy_files"] = sorted(copies)
    d["sheet_months"] = sheet_info
    for si in sheet_info:
        if si["path"] in copies or not si["month"]:
            continue
        months_all.add(si["month"])
        if si["cap"]:
            months_it.add(si["month"])
    for c, info in copies.items():
        if not info["mutual"] and info["month"]:
            months_all.add(info["month"])
            if any(si["cap"] for si in sheet_info if si["path"] == info["kept"]):
                months_it.add(info["month"])
    for si in sheet_info:
        if si["path"] in copies or not si["month"] or si["cap"] or si["month"] in months_it:
            continue
        nocap_reasons[si["month"][:4]][si["why"]] += 1
        nocap_reasons["all"][si["why"]] += 1
        nocap_months[si["why"]].add(si["month"])
    d["months_all"] = sorted(months_all)
    d["months_it"] = sorted(months_it)
    d["nocap_reasons"] = {k: dict(v) for k, v in nocap_reasons.items()}
    d["entities"] = dict(d["entities"].most_common(80))
    d["nocap_months"] = {k: sorted(v) for k, v in nocap_months.items()}
    return aggs, months_all, months_it, nocap_reasons, labels, nocap_months


def coverage_note(payer, per, a, months_all, months_it, nocap, details, stray=None):
    parts = []
    if per == "all":
        ms = sorted(months_all)
        if ms:
            miss = missing_months(ms, ms[0], ms[-1])
            parts.append(f"files for {len(ms)} months, {month_label(ms[0])} to {month_label(ms[-1])}"
                         + (f"; no readable file for {month_ranges(miss)}" if miss else ""))
        mit = sorted(months_it)
    else:
        ms = sorted(m for m in months_all if m.startswith(per))
        parts.append(f"files for {len(ms)} of 12 months" + (f" ({month_ranges(ms)})" if len(ms) < 12 else ""))
        mit = sorted(m for m in months_it if m.startswith(per))
    if payer in NO_IT_SCHEME:
        parts.append("IT figures not computable: " + NO_IT_SCHEME[payer])
    elif not mit:
        why = "; ".join(sorted(nocap.get(per, {}))) or "no file has a usable category column"
        parts.append(f"IT figures not computable for this period: {why}")
    elif set(mit) != set(ms):
        other = sorted(set(ms) - set(mit))
        why = "; ".join(sorted(nocap.get(per, {})))
        parts.append(f"IT figures cover {month_ranges(mit)} only; not computable for {month_ranges(other)} ({why})")
    if a.pal_total:
        if a.pal_other_labels and mit:
            labs = "; ".join(f"{k} {gbp(v)}" for k, v in a.pal_other_labels.most_common())
            parts.append(f"Palantir lines under non-IT labels: {labs}; the share of IT counts only the "
                         f"{gbp(a.pal_it)} under IT labels")
        if a.pal_nocap and mit:
            parts.append(f"Palantir {gbp(a.pal_nocap)} falls in months without IT figures and is not in the share of IT")
    if a.dupes:
        parts.append(f"{a.dupes} lines repeated from an earlier file removed ({gbp(a.dupe_amount)})")
    if per == "all" and a.undated:
        parts.append(f"{a.undated} lines with no readable date ({gbp(a.undated_amount)}) are counted here but in no year")
    if stray:
        n = sum(x.all_rows for x in stray.values())
        amt = sum((x.all_total for x in stray.values()), Decimal(0))
        yrs = ", ".join(stray)
        parts.append(f"{n} lines ({gbp(amt)}) dated in years with no monthly file ({yrs}) are counted here but in no year")
    if per == "all":
        left = details["lines_left_out"]
        if left:
            reasons = Counter(x["reason"].split(":")[0] for x in left)
            parts.append("lines left out because the amount could not be read as pounds: "
                         + ", ".join(f"{n} ({k})" for k, n in reasons.items()))
        for u in details["unreadable_files"]:
            if "web page" not in u["reason"]:
                why = u["reason"].replace("; file not read", "")
                parts.append(f"file not read: {Path(u['path']).name} ({why})")
            else:
                parts.append(u["reason"])
        if details["copies_dropped"]:
            items = [f"{Path(c['path']).name} ({'same lines as' if c['identical'] else 'all its lines are in'} "
                     f"{Path(c['copy_of']).name})" for c in details["copies_dropped"]]
            parts.append(f"{len(items)} file{'s' if len(items) > 1 else ''} not counted because "
                         f"{'they repeat' if len(items) > 1 else 'it repeats'} another file: " + ", ".join(items))
    return "; ".join(parts)


def share(num, den):
    """Share as a fraction from 0 to 1, to six decimal places (0.106430 is 10.643%)."""
    if den is None or den <= 0:
        return ""
    return f"{(Decimal(num) / Decimal(den)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)}"


def main():
    out_details = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    by_payer, mrows = defaultdict(list), {}
    for payer, path, mrow in manifest_files():
        if payer in PAYERS:
            by_payer[payer].append(path)
            mrows[path] = mrow
    details = {}
    share_rows, top_rows, cat_rows = [], [], []
    summary = {}
    for payer in PAYERS:
        if payer not in by_payer:
            continue
        name, ptype = PAYERS[payer]
        print(f"{payer}: {len(by_payer[payer])} files", file=sys.stderr)
        aggs, months_all, months_it, nocap, labels, nocap_months = process_payer(payer, by_payer[payer], details, mrows)
        file_years = {m[:4] for m in months_all}
        years = sorted(p for p in aggs if p != "all" and p in file_years)
        stray = sorted(p for p in aggs if p != "all" and p not in file_years)
        details[payer]["stray_years"] = {p: {"rows": aggs[p].all_rows, "amount": str(q2(aggs[p].all_total)),
                                             "palantir": str(q2(aggs[p].pal_total))} for p in stray}
        for per in ["all"] + years:
            a = aggs[per]
            if per == "all":
                mit = months_it
            else:
                mit = {m for m in months_it if m.startswith(per)}
            it_ok = payer not in NO_IT_SCHEME and bool(mit)
            share_rows.append({
                "payer": name, "payer_type": ptype, "period": per,
                "it_total_gbp": money(a.it_total) if it_ok else "",
                "all_total_gbp": money(a.all_total),
                "palantir_gbp": money(a.pal_total),
                "palantir_share_of_it": share(a.pal_it, a.it_total) if it_ok else "",
                "palantir_share_of_all": share(a.pal_total, a.all_total),
                "it_rows": a.it_rows if it_ok else "",
                "all_rows": a.all_rows, "files": len(a.files),
                "coverage_note": coverage_note(payer, per, a, months_all, months_it, nocap, details[payer],
                                               {p: aggs[p] for p in stray} if per == "all" else None),
            })
            if it_ok and a.sup_amount:
                for rank, (mk, amt) in enumerate(a.sup_amount.most_common(10), 1):
                    names = a.sup_names[mk]
                    display = names.most_common(1)[0][0]
                    top_rows.append({"payer": name, "period": per, "rank": rank, "supplier": display,
                                     "amount_gbp": money(amt),
                                     "raw_names_merged": " | ".join(n for n, _ in names.most_common()) if len(names) > 1 else ""})
            summary.setdefault(payer, {})[per] = {
                "it": str(q2(a.it_total)) if it_ok else None, "all": str(q2(a.all_total)), "pal": str(q2(a.pal_total)),
                "pal_it": str(q2(a.pal_it)), "pal_capable": str(q2(a.pal_capable)), "pal_nocap": str(q2(a.pal_nocap)),
                "pal_other": {k: str(q2(v)) for k, v in a.pal_other_labels.items()},
                "months": sorted(m for m in months_all if per == "all" or m.startswith(per)),
                "it_months": sorted(m for m in mit), "rows": a.all_rows, "it_rows": a.it_rows,
                "dupes": a.dupes, "dupe_amount": str(q2(a.dupe_amount)),
            }
        # categories
        for lab, (rows, amt, pal, forms, *col) in sorted(labels.items(), key=lambda kv: -kv[1][1]):
            shown = forms.most_common(1)[0][0]
            if payer in NO_IT_SCHEME:
                inc, why, listed = classify(payer, lab)
                if listed or pal:
                    cat_rows.append({"payer": name, "label": shown, "included": "no",
                                     "reason": "supplier-type code, not a spend category"
                                               + (f"; Palantir's lines carry this label ({gbp(pal)})" if pal else ""),
                                     "category_column": col[0] if col else "", "rows": rows, "amount_gbp": money(amt)})
                continue
            inc, why, listed = classify(payer, lab)
            if listed or pal:
                if pal and not inc:
                    why = (why + "; " if why else "not named as IT; ") + f"Palantir's lines carry this label ({gbp(pal)})"
                elif pal:
                    why = why + f"; includes Palantir lines ({gbp(pal)})"
                cat_rows.append({"payer": name, "label": shown, "included": "yes" if inc else "no", "reason": why,
                                 "category_column": col[0] if col else "", "rows": rows, "amount_gbp": money(amt)})
        if payer in NO_IT_SCHEME:
            cat_rows.append({"payer": name, "label": "(every label)", "included": "no", "reason": NO_IT_SCHEME[payer],
                             "category_column": "category description", "rows": "", "amount_gbp": ""})
        else:
            for why, ms in sorted(nocap_months.items()):
                cat_rows.append({"payer": name, "label": "(files without a usable IT category)", "included": "no",
                                 "reason": f"{why}: files for {month_ranges(ms)}; only the all-spend total is "
                                           "computed for these months",
                                 "category_column": "", "rows": "", "amount_gbp": ""})

    with open(DATA / "market-share.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["payer", "payer_type", "period", "it_total_gbp", "all_total_gbp",
                                           "palantir_gbp", "palantir_share_of_it", "palantir_share_of_all", "it_rows",
                                           "all_rows", "files", "coverage_note"])
        w.writeheader()
        w.writerows(share_rows)
    with open(DATA / "market-top-suppliers.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["payer", "period", "rank", "supplier", "amount_gbp", "raw_names_merged"])
        w.writeheader()
        w.writerows(top_rows)
    with open(DATA / "market-categories.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["payer", "label", "included", "reason", "category_column", "rows",
                                           "amount_gbp"])
        w.writeheader()
        w.writerows(cat_rows)
    print(f"{len(share_rows)} share rows, {len(top_rows)} top-supplier rows, {len(cat_rows)} category rows",
          file=sys.stderr)
    if out_details:
        out_details.write_text(json.dumps({"details": details, "summary": summary}, default=str, indent=1))


if __name__ == "__main__":
    main()
