"""St. Louis County 2022 vacant parcel survey (static, ~630 parcels). Weak but free signal."""
from ..util import save, norm_addr
from . import arcgis

URL = "https://services2.arcgis.com/w657bnjzrjguNyOy/arcgis/rest/services/Vacany_Parcels_2022/FeatureServer/0"


def run():
    out = [{"tag": a.get("LOCATOR"), "addr": norm_addr(a.get("PROP_ADD") or ""), "status": a.get("USER_STATU"), "note": (a.get("USER_COMME") or "")[:120]}
           for a in arcgis(URL, "1=1", "LOCATOR,PROP_ADD,USER_STATU,USER_COMME", order="FID")]
    save("county_vacant.json", out)
    return len(out)


if __name__ == "__main__":
    print(run())
