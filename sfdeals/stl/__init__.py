"""St. Louis City + St. Louis County pullers."""
import time
from ..util import fetch_json

CITY = "St. Louis City"
COUNTY = "St. Louis County"


def arcgis(url, where, fields, page=2000, order="OBJECTID", limit=1_000_000):
    """Yield attribute dicts from an ArcGIS layer, paging with resultOffset."""
    offset = 0
    while offset < limit:
        q = (f"{url}/query?where={where}&outFields={fields}&returnGeometry=false&orderByFields={order}"
             f"&resultOffset={offset}&resultRecordCount={page}&f=json")
        d = fetch_json(q.replace(" ", "%20").replace("'", "%27"), timeout=120)
        if "error" in d:
            raise RuntimeError(d["error"])
        feats = d.get("features", [])
        for f in feats:
            yield f["attributes"]
        if len(feats) < page:
            break
        offset += page
        time.sleep(0.2)


def ms_date(v):
    if not v:
        return ""
    try:
        return time.strftime("%Y-%m-%d", time.gmtime(int(v) / 1000))
    except (TypeError, ValueError, OSError):
        return ""
