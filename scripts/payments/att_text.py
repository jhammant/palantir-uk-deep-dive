import sys, re, subprocess, zipfile
from pathlib import Path
root = Path(sys.argv[1])
for f in sorted(root.rglob("*")):
    if not f.is_file() or f.name == "manifest.json" or f.suffix.lower() in (".png", ".jpg", ".txtout"):
        continue
    suf = f.suffix.lower()
    try:
        if suf == ".pdf":
            t = subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, timeout=120).stdout.decode("utf-8", "replace")
        elif suf == ".docx":
            z = zipfile.ZipFile(f); x = z.read("word/document.xml").decode("utf-8", "replace")
            t = re.sub(r"<w:p[ >]", "\n<w:p ", x); t = re.sub(r"<[^>]+>", "", t)
        elif suf in (".doc", ".html", ".htm", ".rtf"):
            t = subprocess.run(["textutil", "-convert", "txt", "-stdout", str(f)], capture_output=True, timeout=120).stdout.decode("utf-8", "replace")
        else:
            t = f.read_text("utf-8", "replace")
    except Exception as e:
        t = f"ERR {e}"
    (f.parent / (f.name + ".txtout")).write_text(t)
    pounds = sorted(set(re.findall(r"£\s?[\d,]+(?:\.\d+)?(?:\s?(?:m|million|k|bn))?", t)))
    print(f"{f.parent.name[:28]:28} {f.name[:50]:50} len={len(t):6} £={pounds[:8]}")
