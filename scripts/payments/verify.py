import csv, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_scan import rows_from, PROJECT
rows = list(csv.DictReader(open(PROJECT / "data" / "payments.csv")))
cache = {}
bad = 0
for r in rows:
    m = re.search(r"saved copy: ([^;]+)$", r["notes"].strip())
    if not m:
        print("NO SAVED COPY", r["payer"], r["amount_gbp"]); bad += 1; continue
    p = PROJECT / m.group(1)
    if not p.exists():
        print("MISSING FILE", p); bad += 1; continue
    if p not in cache:
        cache[p] = [cells for _, _, cells in rows_from(p.read_bytes(), p.name)]
    amt = float(r["amount_gbp"])
    ok = False
    for cells in cache[p]:
        if not any(re.search("palantir", c, re.I) for c in cells) and "FOI" not in r["notes"][:20]:
            continue
        for c in cells:
            for tok in re.findall(r"-?[£]?[\d,]+\.?\d*", c):
                try:
                    if abs(abs(float(tok.replace("£", "").replace(",", ""))) - abs(amt)) < 0.005:
                        ok = True
                except ValueError:
                    pass
    if not ok:
        print("NOT FOUND", r["payer"], r["period"], r["amount_gbp"], p.name); bad += 1
print(len(rows), "rows checked,", bad, "problems")
