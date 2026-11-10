"""St. Louis County tax sale leftovers. After a parcel fails to sell at three annual Collector tax sales it is
'Post Third' (still owned by the taxpayer, buyable from the Collector) or 'Trustee' (deeded to the County
trustee). The County publishes both in one ArcGIS layer, refreshed about monthly. Its website is behind
Cloudflare so the pre-sale list itself is not pullable."""
from ..util import save, norm_addr
from . import arcgis

URL = "https://services2.arcgis.com/w657bnjzrjguNyOy/arcgis/rest/services/Combined_Trustee_and_Post_Third/FeatureServer/42"
FIELDS = "LOCATOR,OWNER_NAME,PROP_ADD,PROP_ZIP,OWN_ADD,OWN_CITY,OWN_STATE,MUNICIPALITY,STATUS,STRUCTURE,LUCODE,LIVUNIT,YEARBLT,TOTAPVAL"


def row(a):
    return {"tag": (a.get("LOCATOR") or "").strip(), "addr": norm_addr(a.get("PROP_ADD") or ""), "zip": str(a.get("PROP_ZIP") or "")[:5],
            "owner": (a.get("OWNER_NAME") or "").strip(), "status": a.get("STATUS") or "", "structure": a.get("STRUCTURE") or "",
            "use": a.get("LUCODE") or "", "units": a.get("LIVUNIT") or 0, "muni": (a.get("MUNICIPALITY") or "").title(),
            "value": a.get("TOTAPVAL") or 0}


def run():
    out = [row(a) for a in arcgis(URL, "LIVUNIT>=1 AND LIVUNIT<=4", FIELDS)]
    save("county_taxsale.json", out)
    return len(out)


if __name__ == "__main__":
    print(run())
