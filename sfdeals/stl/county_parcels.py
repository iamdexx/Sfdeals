"""St. Louis County parcel layer (all 88 municipalities + unincorporated). Residential, 1-4 living units."""
from ..util import save, norm_addr
from . import arcgis, COUNTY

URL = "https://maps.stlouisco.com/hosting/rest/services/Maps/AGS_Parcels/MapServer/0"
FIELDS = ("LOCATOR,OWNER_NAME,CAREOF,PROP_ADD,PROP_ZIP,OWN_ADD,OWN_CITY,OWN_STATE,OWN_ZIP,MUNICIPALITY,"
          "TENURE,LIVUNIT,YEARBLT,RESQFT,TOTAPVAL,LUCODE")
WHERE = "PROPCLASS='R' AND LIVUNIT>=1 AND LIVUNIT<=4"


def row(a):
    return {
        "tag": a["LOCATOR"], "cid": a["LOCATOR"], "addr": norm_addr(a.get("PROP_ADD") or ""),
        "zip": str(a.get("PROP_ZIP") or "")[:5], "county": COUNTY, "muni": (a.get("MUNICIPALITY") or "").strip().title(),
        "owner": (a.get("OWNER_NAME") or "").strip(), "careof": (a.get("CAREOF") or "").strip(),
        "mail": norm_addr(a.get("OWN_ADD") or ""), "mail_city": (a.get("OWN_CITY") or "").strip().title(),
        "mail_state": (a.get("OWN_STATE") or "").strip().upper(), "mail_zip": str(a.get("OWN_ZIP") or "").strip()[:5],
        "occ": {"OWNER": "Y", "NOT OWNER": "N"}.get((a.get("TENURE") or "").strip().upper()),
        "landuse": a.get("LUCODE"), "units": a.get("LIVUNIT") or 1, "sqft": None, "res_sqft": a.get("RESQFT"),
        "year": a.get("YEARBLT"), "value": a.get("TOTAPVAL"), "tax_bal": 0, "vac_year": 0,
    }


def run():
    out = [row(a) for a in arcgis(URL, WHERE, FIELDS, page=5000)]
    save("county_parcels.json.gz", out)
    return len(out)


if __name__ == "__main__":
    print(run())
