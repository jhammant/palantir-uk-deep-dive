#!/usr/bin/env python3
"""Search ACOBA and business appointment publications (page body + every attachment) for Palantir.

Usage:
    python3 scripts/revolving/scan_pubs.py WORK_DIR [--ocr]

Reads WORK_DIR/publications.json (from enumerate_pubs.py), downloads each attachment into
WORK_DIR/files/, extracts its text (pdftotext, openpyxl, LibreOffice for ODS/ODT/DOC/XLS,
zip XML for DOCX, the content API for HTML attachments) and writes:
    WORK_DIR/hits.json      every match with surrounding text
    WORK_DIR/manifest.json  every file checked, how its text was read, and its size
With --ocr, PDFs with almost no text layer are OCR'd with tesseract.
"""
import concurrent.futures as cf
import hashlib
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

UA = "palantir-uk-open-data/1.0 (public-interest research)"
CONTENT = "https://www.gov.uk/api/content"
PATTERN = re.compile(r"p[ae]ll?[ae]n?t[ae]?i?r", re.I)


def http_get(url, binary=True):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", "20")))
                continue
            if e.code in (404, 410):
                return None
            time.sleep(3 * (attempt + 1))
        except Exception:  # noqa: BLE001
            time.sleep(3 * (attempt + 1))
    return None


def strip_html(s):
    s = re.sub(r"<(script|style).*?</\1>", " ", s or "", flags=re.S)
    s = re.sub(r"<br\s*/?>|</p>|</tr>|</li>|</h\d>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"[ \t\r\f\v]+", " ", s)


def soffice_convert(path, fmt, outdir):
    soffice = shutil.which("soffice")
    if not soffice:
        return None
    outdir.mkdir(parents=True, exist_ok=True)
    subprocess.run([soffice, "--headless", "--convert-to", fmt, "--outdir", str(outdir), str(path)],
                   capture_output=True, timeout=180)
    out = outdir / (path.stem + "." + fmt.split(":")[0])
    return out if out.exists() else None


def xlsx_text(path):
    import openpyxl  # noqa: PLC0415
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            cells = [str(c) for c in row if c is not None]
            if cells:
                rows.append(" | ".join(cells))
    return "\n".join(rows)


def zip_xml_text(path, member):
    with zipfile.ZipFile(path) as z:
        xml = z.read(member).decode("utf-8", "replace")
    xml = re.sub(r"</w:p>|</text:p>|</table:table-row>", "\n", xml)
    return html.unescape(re.sub(r"<[^>]+>", " ", xml))


def pdf_text(path, ocr):
    r = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, timeout=180)
    text = r.stdout.decode("utf-8", "replace")
    method = "pdftotext"
    if ocr and len(text.strip()) < 200:
        tmp = path.parent / (path.stem + "_ocr")
        tmp.mkdir(exist_ok=True)
        subprocess.run(["pdftoppm", "-r", "200", "-png", str(path), str(tmp / "p")],
                       capture_output=True, timeout=600)
        parts = []
        for png in sorted(tmp.glob("p*.png")):
            o = subprocess.run(["tesseract", str(png), "-", "--psm", "6"], capture_output=True, timeout=300)
            parts.append(o.stdout.decode("utf-8", "replace"))
        text = "\n".join(parts)
        method = "ocr"
    return text, method


def file_text(path, ocr):
    ext = path.suffix.lower()
    if ext == ".pdf":
        return pdf_text(path, ocr)
    if ext in (".csv", ".txt"):
        return path.read_bytes().decode("utf-8", "replace"), "raw"
    if ext in (".xlsx", ".xlsm"):
        return xlsx_text(path), "openpyxl"
    if ext == ".docx":
        return zip_xml_text(path, "word/document.xml"), "docx-xml"
    if ext == ".odt":
        return zip_xml_text(path, "content.xml"), "odt-xml"
    if ext == ".ods":
        return zip_xml_text(path, "content.xml"), "ods-xml"
    if ext in (".xls", ".doc", ".rtf", ".odp", ".pptx", ".ppt"):
        conv = soffice_convert(path, "txt:Text" if ext in (".doc", ".rtf") else "pdf", path.parent / "conv")
        if conv and conv.suffix == ".pdf":
            return pdf_text(conv, ocr)[0], "soffice-pdf"
        if conv:
            return conv.read_text("utf-8", "replace"), "soffice-txt"
    return "", "unsupported"


def hits_in(text, ctx=500):
    out = []
    for m in PATTERN.finditer(text or ""):
        a, b = max(0, m.start() - ctx), min(len(text), m.end() + ctx)
        out.append({"match": m.group(0), "context": re.sub(r"\s+", " ", text[a:b])})
    return out


def scan_pub(pub, files_dir, ocr):
    results, manifest = [], []
    body = strip_html(pub.get("body", ""))
    for h in hits_in(body):
        results.append(dict(h, page_url=pub["page_url"], title=pub["title"], file_url=pub["page_url"],
                            where="page body"))
    manifest.append({"page_url": pub["page_url"], "file_url": pub["page_url"], "method": "body",
                     "chars": len(body)})
    for a in pub.get("attachments", []):
        url = a.get("url") or ""
        if not url:
            continue
        if url.startswith("/"):
            url = "https://www.gov.uk" + url
        is_html = a.get("attachment_type") == "html" or (a.get("content_type") or "").startswith("text/html") \
            or url.startswith("https://www.gov.uk/government/")
        if is_html:
            path = urllib.parse.urlparse(url).path
            raw = http_get(CONTENT + path)
            text = ""
            if raw:
                try:
                    text = strip_html(json.loads(raw).get("details", {}).get("body", ""))
                except Exception:  # noqa: BLE001
                    text = ""
            method = "html-attachment"
        else:
            name = hashlib.sha1(url.encode()).hexdigest()[:16] + pathlib.Path(urllib.parse.urlparse(url).path).suffix
            dest = files_dir / name
            if not dest.exists():
                data = http_get(url)
                if data is None:
                    manifest.append({"page_url": pub["page_url"], "file_url": url, "method": "download-failed",
                                     "chars": 0})
                    continue
                dest.write_bytes(data)
            try:
                text, method = file_text(dest, ocr)
            except Exception as e:  # noqa: BLE001
                text, method = "", "error:" + type(e).__name__
        manifest.append({"page_url": pub["page_url"], "file_url": url, "method": method, "chars": len(text)})
        for h in hits_in(text):
            results.append(dict(h, page_url=pub["page_url"], title=pub["title"], file_url=url,
                                where=a.get("title") or ""))
    return results, manifest


def main():
    work = pathlib.Path(sys.argv[1])
    ocr = "--ocr" in sys.argv
    pubs = json.loads((work / "publications.json").read_text())
    files_dir = work / "files"
    files_dir.mkdir(exist_ok=True)
    all_hits, all_manifest = [], []
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(scan_pub, p, files_dir, ocr): p for p in pubs}
        for n, f in enumerate(cf.as_completed(futs)):
            try:
                h, m = f.result()
            except Exception as e:  # noqa: BLE001
                print("ERR", futs[f]["page_url"], e, file=sys.stderr)
                continue
            all_hits += h
            all_manifest += m
            if h:
                print("HIT", futs[f]["page_url"], len(h), file=sys.stderr)
            if n % 100 == 0:
                print(n, "of", len(pubs), file=sys.stderr)
    (work / "hits.json").write_text(json.dumps(all_hits, indent=1))
    (work / "manifest.json").write_text(json.dumps(all_manifest, indent=1))
    print(len(all_hits), "hits;", len(all_manifest), "files checked", file=sys.stderr)


if __name__ == "__main__":
    main()
