"""City of Sioux Falls parcel layer (covers Minnehaha + Lincoln parts of the city)."""
from .util import fetch_json, save, norm_addr

URL = "https://gis.siouxfalls.gov/arcgis/rest/services/Data/Property/MapServer/1/query"
FIELDS = "TAG,COUNTYID,ADDRESS,OWNNAME1,OWNNAME2,OWNADDRESS,OWNCITY,OWNSTATE,OWNZIP,OWNEROCCSTATUS,LANDUSE,NUMUNITS,PARCELTYPE,ZIPCODE,COUNTY,ACREAGE,SQFT,ACTIVITY"
# LANDUSE 1xx = residential. Keep 1-4 units.
WHERE = "LANDUSE >= 100 AND LANDUSE < 200 AND NUMUNITS <= 4"


def run():
    out, offset, page = [], 0, 1000
    while True:
        q = f"{URL}?where={WHERE}&outFields={FIELDS}&returnGeometry=false&orderByFields=OBJECTID&resultOffset={offset}&resultRecordCount={page}&f=json"
        d = fetch_json(q.replace(" ", "%20"))
        feats = d.get("features", [])
        for f in feats:
            a = f["attributes"]
            situs = norm_addr(a.get("ADDRESS") or "")
            mail = norm_addr(a.get("OWNADDRESS") or "")
            out.append({
                "tag": a["TAG"], "cid": (a.get("COUNTYID") or "").strip(), "addr": situs,
                "zip": a.get("ZIPCODE"), "county": a.get("COUNTY"),
                "owner": " & ".join(x for x in [a.get("OWNNAME1"), a.get("OWNNAME2")] if x),
                "mail": mail, "mail_city": (a.get("OWNCITY") or "").strip(), "mail_state": (a.get("OWNSTATE") or "").strip(),
                "mail_zip": (a.get("OWNZIP") or "").strip() if a.get("OWNZIP") else "",
                "occ": a.get("OWNEROCCSTATUS"), "landuse": a.get("LANDUSE"), "units": a.get("NUMUNITS"),
                "acres": a.get("ACREAGE"), "sqft": a.get("SQFT"), "activity": a.get("ACTIVITY"),
            })
        if len(feats) < page or not d.get("exceededTransferLimit", True) and len(feats) < page:
            break
        offset += page
        if offset > 200000:
            break
    save("parcels.json.gz", out)
    return len(out)


if __name__ == "__main__":
    print(run())
