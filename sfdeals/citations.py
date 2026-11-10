"""City of Sioux Falls code enforcement citations (rolling 12 months, ASP.NET GridView)."""
import re
from .util import fetch_text, save, load, norm_addr

URL = "https://epldata.siouxfalls.gov/Citations.aspx"
ROW = re.compile(r"<td[^>]*>(\d{1,2}-\d{1,2}-\d{4})</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>")


def _hidden(s, name):
    m = re.search(r'id="%s" value="([^"]*)"' % name, s)
    return m.group(1) if m else ""


def _form(s):
    f = {}
    for m in re.finditer(r'<input[^>]*name="(ctl00\$[^"]*)"[^>]*value="([^"]*)"', s):
        f[m.group(1)] = m.group(2)
    for sel in re.finditer(r'<select[^>]*name="(ctl00\$[^"]*)"(.*?)</select>', s, re.S):
        m = re.search(r'<option[^>]*selected[^>]*value="([^"]*)"', sel.group(2)) or re.search(r'<option[^>]*value="([^"]*)"[^>]*selected', sel.group(2))
        f[sel.group(1)] = m.group(1) if m else ""
    f.pop("ctl00$ContentPlaceHolder1$btnSearch", None); f.pop("ctl00$ContentPlaceHolder1$cmdReset", None)
    return f


def _rows(s):
    out = []
    for d, a, t, c in ROW.findall(s):
        mo, dy, yr = d.split("-")
        out.append({"date": "%s-%02d-%02d" % (yr, int(mo), int(dy)), "addr": norm_addr(a), "type": t.strip(), "action": c.strip()})
    return out


def run(max_pages=60):
    s = fetch_text(URL)
    rows = _rows(s)
    page = 2
    while page <= max_pages:
        if "Page$%d" % page not in s and page > 2:
            break
        data = _form(s)
        data.update({"__EVENTTARGET": "ctl00$ContentPlaceHolder1$GridView1", "__EVENTARGUMENT": "Page$%d" % page,
                "__VIEWSTATE": _hidden(s, "__VIEWSTATE"), "__VIEWSTATEGENERATOR": _hidden(s, "__VIEWSTATEGENERATOR"),
                "__EVENTVALIDATION": _hidden(s, "__EVENTVALIDATION")})
        s = fetch_text(URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        r = _rows(s)
        if not r:
            break
        rows.extend(r)
        page += 1
    seen, out = set(), []
    for r in (load("citations.json", []) or []) + rows:
        k = (r["date"], r["addr"], r["type"], r["action"])
        if k not in seen:
            seen.add(k)
            out.append(r)
    save("citations.json", out)
    return len(out)


if __name__ == "__main__":
    print(run())
