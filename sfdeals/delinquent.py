"""Minnehaha County delinquent tax list. Published every December as a legal notice PDF
(the county does not host it; local papers do). URLs live in config.json."""
import io, json, re
from .util import fetch, save, ROOT

ROW = re.compile(r"^(.*?)\s+(\d{6})\s+\$([\d,]+\.\d\d)\s*(.*)$")
SECTION = re.compile(r"\*\*\s*([^*]+?)\s*\*\*")


def parse_pdf(data):
    import fitz  # pymupdf
    doc = fitz.open(stream=data, filetype="pdf")
    text = "\n".join(p.get_text() for p in doc)
    out, section = [], ""
    for line in text.splitlines():
        line = line.strip()
        s = SECTION.search(line)
        if s:
            section = s.group(1).strip()
            continue
        m = ROW.match(line)
        if m:
            out.append({"owner": m.group(1).strip(), "cid": m.group(2), "amount": float(m.group(3).replace(",", "")),
                        "legal": m.group(4).strip(), "section": section})
    return out


def run():
    cfg = json.loads((ROOT / "config.json").read_text())
    out = []
    for src in cfg.get("delinquent_pdfs", []):
        rows = parse_pdf(fetch(src["url"]))
        for r in rows:
            r["year"] = src["year"]
        out.extend(rows)
    save("delinquent.json", out)
    return len(out)


if __name__ == "__main__":
    print(run())
