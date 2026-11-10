"""City vacant building registry overview, keyed by parcel HANDLE:
mo = months on the list, vmin/vmaj = open minor/major violations, csb = open 311 requests, unpd = unpaid fees $."""
from ..util import fetch_json, save

URL = "https://www.stlcitypermits.com/API/VacantBuilding/GetVacantBuildingOverview"


def run():
    d = fetch_json(URL, timeout=180)
    out = {h: v for h, v in d.items() if isinstance(v, dict)}
    save("vacant.json", out)
    return len(out)


if __name__ == "__main__":
    print(run())
