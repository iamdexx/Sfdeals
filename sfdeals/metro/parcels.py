"""Generic ArcGIS parcel pull for a config-driven metro: absentee residential parcels by server-side
filter, plus every parcel that carries a signal (fetched by id so the filter never hides them)."""
import re
from ..util import save, load, norm_addr
from ..stl import arcgis
from . import metros

NUM = re.compile(r"[^0-9.]")


def num(v):
    if v in (None, ""):
        return None
    try:
        return float(NUM.sub("", str(v))) if NUM.sub("", str(v)) else None
    except ValueError:
        return None


def pick(a, f):
    if isinstance(f, list):
        return " ".join(str(a.get(x) or "").strip() for x in f if a.get(x) not in (None, ""))
    return a.get(f)


def row(a, spec, county, state):
    m = spec["map"]
    g = lambda k: pick(a, m[k]) if k in m else None  # noqa: E731
    year = num(g("year")); value = num(g("value")); price = num(g("sale_price"))
    return {
        "tag": str(g("tag")).strip(), "cid": str(g("tag")).strip(), "addr": norm_addr(g("addr") or ""),
        "zip": str(g("zip") or "")[:5], "county": county, "muni": (g("muni") or "").strip().title(),
        "owner": (g("owner") or "").strip(), "careof": "", "mail": norm_addr(g("mail") or ""),
        "mail_city": (g("mail_city") or "").strip().title(), "mail_state": (g("mail_state") or "").strip().upper()[:2],
        "mail_zip": str(g("mail_zip") or "").strip()[:5], "occ": None, "landuse": g("landuse"),
        "units": int(num(g("units")) or 1), "sqft": None, "res_sqft": int(num(g("res_sqft")) or 0) or None,
        "year": int(year) if year else None, "value": int(value) if value else None, "tax_bal": 0, "vac_year": 0,
        "sale_date": (g("sale_date") or "") if isinstance(g("sale_date"), str) else "", "sale_price": int(price) if price else None,
        "home_state": state,
    }


def fields(spec):
    out = []
    for v in spec["map"].values():
        out += v if isinstance(v, list) else [v]
    return ",".join(dict.fromkeys(out))


def run(key):
    cfg = metros.METROS[key]
    want = {s["tag"] for s in load("signals.json.gz", []) or []}
    out, seen = [], set()
    for c in cfg["counties"]:
        spec = c["parcels"]
        for a in arcgis(spec["url"], spec["where"], fields(spec), page=spec.get("page", 2000)):
            r = row(a, spec, c["name"], cfg["state"])
            if r["tag"] not in seen:
                seen.add(r["tag"]); out.append(r)
        missing = sorted(t for t in want if t not in seen)
        idf = spec["map"]["tag"]
        for i in range(0, len(missing), 200):
            ids = ",".join("'%s'" % t.replace("'", "") for t in missing[i:i + 200])
            for a in arcgis(spec["url"], "%s IN (%s)" % (idf, ids), fields(spec), page=spec.get("page", 2000)):
                r = row(a, spec, c["name"], cfg["state"])
                if r["tag"] not in seen:
                    seen.add(r["tag"]); out.append(r)
    save("parcels.json.gz", out)
    return len(out)
