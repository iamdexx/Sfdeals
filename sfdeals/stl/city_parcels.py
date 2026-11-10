"""City of St. Louis assessor parcel layer. Residential (AsrClassCode 100), 1-4 units, with a building."""
from ..util import save, norm_addr
from . import arcgis, ms_date, CITY

URL = "https://maps6.stlouis-mo.gov/arcgis/rest/services/St_Louis_Parcels/MapServer/0"
FIELDS = ("ParcelId,HANDLE,SITEADDR,ZIP,NBRHD,OWNERNAME,OWNERNAME2,OWNERADDR,OWNERCITY,OWNERSTATE,OWNERZIP,"
          "OWNEROCC,AsrLandUse1,NbrOfUnits,SQFT,TaxBalance,VacBldgYear,LendingAgcy,AsdTotal,ResSalePrice,ResSaleDate,FirstYearBuilt")
WHERE = "AsrClassCode=100 AND VacantLot=0 AND NbrOfUnits>=1 AND NbrOfUnits<=4"


def row(a):
    owner = " & ".join(x.strip() for x in [a.get("OWNERNAME"), a.get("OWNERNAME2")] if x and x.strip())
    return {
        "tag": a["ParcelId"], "cid": a["ParcelId"], "handle": a.get("HANDLE"), "addr": norm_addr(a.get("SITEADDR") or ""),
        "zip": str(a.get("ZIP") or ""), "county": CITY, "nbhd": a.get("NBRHD"),
        "owner": owner, "mail": norm_addr(a.get("OWNERADDR") or ""),
        "mail_city": (a.get("OWNERCITY") or "").strip().title(), "mail_state": (a.get("OWNERSTATE") or "").strip().upper(),
        "mail_zip": str(a.get("OWNERZIP") or "").strip()[:5],
        "occ": "Y" if a.get("OWNEROCC") == "1" else None,
        "landuse": a.get("AsrLandUse1"), "units": a.get("NbrOfUnits") or 1, "sqft": a.get("SQFT"), "year": a.get("FirstYearBuilt"),
        "value": a.get("AsdTotal"), "tax_bal": round(a.get("TaxBalance") or 0, 2), "vac_year": a.get("VacBldgYear") or 0,
        "lender": str(a.get("LendingAgcy") or "").strip(), "sale_price": a.get("ResSalePrice"), "sale_date": ms_date(a.get("ResSaleDate")),
    }


def run():
    out = [row(a) for a in arcgis(URL, WHERE, FIELDS)]
    save("city_parcels.json.gz", out)
    return len(out)


if __name__ == "__main__":
    print(run())
