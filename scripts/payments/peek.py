import sys, re, collections
sys.path.insert(0, sys.argv[1])
from fetch_scan import rows_from
path = sys.argv[2]
data = open(path, 'rb').read()
rows = list(rows_from(data, path))
print('rows', len(rows))
for r in rows[:3]: print(r[2][:12])
col = int(sys.argv[3]) if len(sys.argv) > 3 else 5
c = collections.Counter(r[2][col].strip().upper() for r in rows if len(r[2]) > col)
pat = re.compile(sys.argv[4], re.I) if len(sys.argv) > 4 else None
for k, v in c.most_common(400):
    if pat is None or pat.search(k): print(v, k)
