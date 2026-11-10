"""Generic ArcGIS parcel pull for a config-driven metro: absentee residential parcels by server-side
filter, plus every parcel that carries a signal (fetched by id so the filter never hides them)."""
import re
from ..util import save, load, norm_addr
from ..stl import arcgis, ms_date
from . import metros

NUM = re.compile(r"[^0-9.]")
STATES = {n: a for a, n in (x.split(":") for x in (
    "AL:ALABAMA AK:ALASKA AZ:ARIZONA AR:ARKANSAS CA:CALIFORNIA CO:COLORADO CT:CONNECTICUT DE:DELAWARE FL:FLORIDA GA:GEORGIA "
    "HI:HAWAII ID:IDAHO IL:ILLINOIS IN:INDIANA IA:IOWA KS:KANSAS KY:KENTUCKY LA:LOUISIANA ME:MAINE MD:MARYLAND MA:MASSACHUSETTS "
    "MI:MICHIGAN MN:MINNESOTA MS:MISSISSIPPI MO:MISSOURI MT:MONTANA NE:NEBRASKA NV:NEVADA NH:NEW_HAMPSHIRE NJ:NEW_JERSEY "
    "NM:NEW_MEXICO NY:NEW_YORK NC:NORTH_CAROLINA ND:NORTH_DAKOTA OH:OHIO OK:OKLAHOMA OR:OREGON PA:PENNSYLVANIA RI:RHODE_ISLAND "
    "SC:SOUTH_CAROLINA SD:SOUTH_DAKOTA TN:TENNESSEE TX:TEXAS UT:UTAH VT:VERMONT VA:VIRGINIA WA:WASHINGTON WV:WEST_VIRGINIA "
    "WI:WISCONSIN WY:WYOMING DC:DISTRICT_OF_COLUMBIA PR:PUERTO_RICO").split())}


def st_abbr(v):
    """'TX', 'Texas' or 'TEXAS' -> 'TX'; unknown names keep their first two letters."""
    v = (v or "").strip().upper()
    return STATES.get(v.replace(" ", "_"), v[:2])


def num(v):
    if v in (None, ""):
        return None
    try:
        return float(NUM.sub("", str(v))) if NUM.sub("", str(v)) else None
    except ValueError:
        return None


def sale_date(v):
    """'03/01/2013', '2013-03-01' or an ArcGIS ms epoch -> 'YYYY-MM-DD'."""
    if not v:
        return ""
    if isinstance(v, (int, float)):
        return ms_date(v)
    v = str(v).strip()
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", v)
    if m:
        return "%s-%02d-%02d" % (m.group(3), int(m.group(1)), int(m.group(2)))
    return v[:10] if re.match(r"\d{4}-\d{2}-\d{2}", v) else ""


def pick(a, f):
    if isinstance(f, list):
        return " ".join(str(a.get(x) or "").strip() for x in f if a.get(x) not in (None, ""))
    return a.get(f)


def row(a, spec, county, state):
    m = spec["map"]
    g = lambda k: pick(a, m[k]) if k in m else None  # noqa: E731
    year = num(g("year")); value = num(g("value")); price = num(g("sale_price"))
    occ = None
    if spec.get("occ_field"):
        occ = "Y" if num(a.get(spec["occ_field"])) else "N"
    addr = g("addr") or ""
    if spec.get("addr_strip"):
        addr = re.sub(spec["addr_strip"], "", addr.strip(), flags=re.I)
    return {
        "tag": str(g("tag")).strip(), "cid": str(g("tag")).strip(), "addr": norm_addr(addr),
        "zip": str(g("zip") or "")[:5], "county": county, "muni": (g("muni") or "").strip().title(),
        "owner": (g("owner") or "").strip(), "careof": "", "mail": norm_addr(g("mail") or ""),
        "mail_city": (g("mail_city") or "").strip().title(), "mail_state": st_abbr(g("mail_state")),
        "mail_zip": str(g("mail_zip") or "").strip()[:5], "occ": occ, "landuse": g("landuse"),
        "units": int(num(g("units")) or 1), "sqft": None, "res_sqft": int(num(g("res_sqft")) or 0) or None,
        "year": int(year) if year else None, "value": int(value) if value else None, "tax_bal": 0, "vac_year": 0,
        "sale_date": sale_date(g("sale_date")), "sale_price": int(price) if price else None,
        "home_state": state,
        "x": {k: a.get(k) for k in spec.get("extra", [])},
    }


def fields(spec):
    out = []
    for v in spec["map"].values():
        out += v if isinstance(v, list) else [v]
    return ",".join(dict.fromkeys(out + list(spec.get("extra", []))))


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
