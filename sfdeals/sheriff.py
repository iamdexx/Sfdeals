"""Minnehaha County sheriff mortgage foreclosure sales (upcoming + results). Page sits behind a bot
challenge, so it is read through a text proxy."""
import re
from .util import via_proxy, save, norm_addr

UPCOMING = "https://www.minnehahacounty.gov/dept/so/mortgageForeclosures/mortgageForeclosures.php"
RESULTS = "https://www.minnehahacounty.gov/dept/so/mortgageForeclosures/mortgageForeclosuresResults.php"
DATE = re.compile(r"(Monday|Tuesday|Wednesday|Thursday|Friday),\s+([A-Z][a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?,\s+(\d{4})")
CASE = re.compile(r"(\d{2}CIV\d{2}-\d{4,6})\s+(.*?)\s+VS?\.?\s+(.*?)(?:\s*\(([^)]*)\))?\.\s+(.*?)\.\s+JUDGMENT AMT\s*\$?([\d,]+(?:\.\d\d)?)(.*)", re.I | re.S)
BID = re.compile(r"BID BY\s+(.*?)(?:\s+\$?([\d,]+(?:\.\d\d)?))?\s*$", re.I)
MONTHS = {m: i for i, m in enumerate("January February March April May June July August September October November December".split(), 1)}


def parse(text, kind):
    out, cur = [], None
    for line in text.splitlines():
        line = line.replace("**", "").strip().lstrip("#- ").strip()
        m = DATE.search(line)
        if m and len(line) < 60:
            cur = "%s-%02d-%02d" % (m.group(4), MONTHS.get(m.group(2), 0), int(m.group(3)))
            continue
        for c in CASE.finditer(line):
            rest = c.group(7).strip(" .")
            bid = BID.search(rest)
            out.append({
                "case": c.group(1), "plaintiff": c.group(2).strip(), "defendant": c.group(3).strip(),
                "attorney": (c.group(4) or "").strip(), "addr_raw": c.group(5).strip(), "addr": norm_addr(c.group(5)),
                "judgment": float(c.group(6).replace(",", "")), "sale_date": cur, "kind": kind,
                "bidder": (bid.group(1).strip() if bid else ""), "bid": float(bid.group(2).replace(",", "")) if bid and bid.group(2) else None,
                "note": rest if not bid else "",
            })
    return out


def run():
    up = parse(via_proxy(UPCOMING), "upcoming")
    res = parse(via_proxy(RESULTS), "result")
    save("sheriff.json", {"upcoming": up, "results": res})
    return len(up), len(res)


if __name__ == "__main__":
    print(run())
