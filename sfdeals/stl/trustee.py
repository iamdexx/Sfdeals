"""Missouri trustee (foreclosure) sales. Missouri foreclosures are non-judicial: the trustee law firm
publishes the notice in a newspaper and most also post a public sale report. SouthLaw is one of the
largest Missouri trustees and posts a statewide PDF; we keep the St. Louis City and County rows."""
import re
from ..util import fetch, save, norm_addr
from . import CITY, COUNTY

URL = "https://www.southlaw.com/app/uploads/report/Sales_Report_MO.pdf"
COUNTIES = {"st. louis": COUNTY, "saint louis": COUNTY, "st louis": COUNTY,
            "city of st. louis": CITY, "city of saint louis": CITY, "st. louis city": CITY}
SKIP = {"Foreclosure Sales Report: Missouri", "Property Address", "Property City", "Sale Date", "Sale Time",
        "Continued Date/Time", "Opening Bid", "Sale Location(City)", "Civil Case No.", "Firm File#", "Property Zip"}
ADDR = re.compile(r"^\d+[A-Z]?\s+\S")
ZIP = re.compile(r"^\d{5}$")
DATE = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")
FILE = re.compile(r"^\d{5,7}$")
CASE = re.compile(r"^\d{2}[A-Z]{2}-[A-Z]{2}\d+")


def _lines(text):
    for raw in text.splitlines():
        l = raw.strip()
        if not l or l in SKIP or l.startswith("Information Reported") or l.startswith("13160 Foster") or re.fullmatch(r"\d{1,2}", l):
            continue
        yield l


def _is_row(lines, i):
    return i + 3 < len(lines) and ADDR.match(lines[i]) and ZIP.match(lines[i + 2]) and DATE.match(lines[i + 3])


def parse(text):
    """Rows are: county header (once per group), then addr, city, zip, date, time, continued, bid, location,
    [case no], file no."""
    lines = list(_lines(text))
    out, county, i = [], "", 0
    while i < len(lines):
        if not _is_row(lines, i):
            county = lines[i]
            i += 1
            continue
        r = {"addr_raw": lines[i], "city": lines[i + 1], "zip": lines[i + 2], "date": lines[i + 3], "time": lines[i + 4],
             "continued": lines[i + 5], "bid": lines[i + 6], "sale_at": lines[i + 7], "case": "", "file": ""}
        j = i + 8
        while j < len(lines) and not _is_row(lines, j) and (CASE.match(lines[j]) or FILE.match(lines[j])):
            if CASE.match(lines[j]):
                r["case"] = lines[j]
            else:
                r["file"] = lines[j]
            j += 1
        r["county_raw"] = county
        r["county"] = COUNTIES.get(county.lower().strip(), "")
        r["addr"] = norm_addr(r["addr_raw"])
        r["firm"] = "SouthLaw"
        out.append(r)
        i = j
    return out


def iso(d):
    m, day, y = d.split("/")
    return "%s-%02d-%02d" % (y, int(m), int(day))


def run():
    import fitz  # pymupdf
    doc = fitz.open(stream=fetch(URL), filetype="pdf")
    rows = parse("\n".join(p.get_text() for p in doc))
    out = []
    for r in rows:
        if not r["county"]:
            continue
        out.append({"addr": r["addr"], "addr_raw": r["addr_raw"], "city": r["city"], "zip": r["zip"], "county": r["county"],
                    "date": iso(r["date"]), "time": r["time"], "continued": "" if r["continued"] == "N/A" else r["continued"],
                    "bid": "" if r["bid"] == "N/A" else r["bid"], "sale_at": r["sale_at"], "case": r["case"], "file": r["file"], "firm": r["firm"]})
    save("trustee.json", out)
    return len(out), len(rows)


if __name__ == "__main__":
    print(run())
