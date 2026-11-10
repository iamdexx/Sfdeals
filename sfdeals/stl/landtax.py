"""City of St. Louis sheriff land tax sale list. The PDF is only posted about two weeks before each sale;
in between the page links a placeholder, so this usually saves an empty list."""
import re
from ..util import fetch, fetch_text, save, norm_addr

PAGE = "https://www.stlouis-mo.gov/government/departments/sheriff/documents/current-land-tax-sale-properties.cfm"
PID = re.compile(r"\b(\d{11})\b")
ADDR = re.compile(r"\b(\d{2,5}(?:-\d{2,5})?\s+[A-Z][A-Z0-9 ]{2,40}?\s(?:AV|AVE|ST|BLVD|DR|PL|CT|LN|RD|TER|PKWY|WAY|CIR))\b")


def parse(text):
    out, seen = [], set()
    for line in text.splitlines():
        m = PID.search(line)
        if not m or m.group(1) in seen:
            continue
        a = ADDR.search(line.upper())
        seen.add(m.group(1))
        out.append({"pid": m.group(1), "addr": norm_addr(a.group(1)) if a else "", "line": line.strip()[:160]})
    return out


def run():
    page = fetch_text(PAGE)
    links = [l for l in re.findall(r'href="([^"]+\.pdf)"', page, re.I) if "not-available" not in l.lower()]
    out = []
    for l in links:
        url = l if l.startswith("http") else "https://www.stlouis-mo.gov" + l
        import fitz  # pymupdf
        doc = fitz.open(stream=fetch(url), filetype="pdf")
        text = "\n".join(p.get_text() for p in doc)
        if "not available" in text.lower()[:400]:
            continue
        out += parse(text)
    save("landtax.json", out)
    return len(out)


if __name__ == "__main__":
    print(run())
