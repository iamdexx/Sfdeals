"""Lincoln County sheriff sales (CivicPlus calendar, category 27). Often empty; parse what is there."""
import re, html
from .util import fetch_text, save, norm_addr

URL = "https://www.lincolncountysd.gov/calendar.aspx?CID=27&view=list"
CASE = re.compile(r"(41CIV\d{2}-\d{3,6})\s+(.*?)\s+VS?\.?\s+(.*?)\s+(?:Location:)?\s*(\d+\s+[^$]*?)\s+(?:Judgment:?\s*)?\$([\d,]+(?:\.\d\d)?)", re.I)


def run():
    s = fetch_text(URL)
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))
    out = [{"case": m.group(1), "plaintiff": m.group(2).strip(), "defendant": m.group(3).strip(), "addr_raw": m.group(4).strip(),
            "addr": norm_addr(m.group(4)), "judgment": float(m.group(5).replace(",", "")), "kind": "upcoming", "county": "LINCOLN"}
           for m in CASE.finditer(t)]
    save("lincoln.json", out)
    return len(out)


if __name__ == "__main__":
    print(run())
