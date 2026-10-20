import html, re, sys
s = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
t = re.search(r'"headline":"(.*?)"', s)
d = re.search(r'"datePublished":"([^"]+)"', s)
a = re.search(r'"author":"([^"]+)"', s)
print("TITLE:", html.unescape(t.group(1)) if t else "")
print("DATE:", d.group(1) if d else "", "| AUTHOR:", a.group(1) if a else "")
i = s.find('data-gu-name="body"')
seg = s[i:]
ends = [x for x in (seg.find("</article>"), seg.find("<footer")) if x > 0]
seg = seg[: min(ends)] if ends else seg
seg = re.sub(r"<script.*?</script>|<style.*?</style>|<aside.*?</aside>", "", seg, flags=re.S)
for p in re.findall(r"<(p|h2)[^>]*>(.*?)</\1>", seg, re.S):
    txt = html.unescape(re.sub(r"<[^>]+>", "", p[1])).strip()
    if len(txt) > 25:
        print(txt)
