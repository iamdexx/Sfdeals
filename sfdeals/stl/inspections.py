"""City of St. Louis building division, existing structure inspections (complaints, condemnations, notices to secure).
The API only returns the last 30 days, so we accumulate nightly and dedupe on InspectionID."""
from ..util import fetch_json, save, load, norm_addr

URL = "https://www.stlcitypermits.com/API/HCES/GetExistingStructureInspections"
KEEP = {"Violation Letter": "violation", "Notice to Secure": "secure", "Structural Condemnation": "condemned",
        "Condemned for Occupancy": "condemned", "Emergency Structural Condemnation": "condemned",
        "Emergency Condemnation and Demo Notice": "condemned", "Emergency CFO": "condemned"}


def row(r):
    result = (r.get("CurrentResult") or "").strip()
    kind = KEEP.get(result) or ("condemned" if "ondemn" in result else "violation" if "iolation" in result else "")
    if not kind:
        return None
    v = r.get("Violations") or []
    return {"id": r["InspectionID"], "date": (r.get("CurrentResultDate") or r.get("CreatedDate") or "")[:10],
            "addr": norm_addr(r.get("ProjectAddress") or ""), "pid": (r.get("ProjectASRParcelID") or "").strip(),
            "type": (r.get("InspectionType") or "").strip(), "result": result, "kind": kind,
            "major": sum(1 for x in v if (x.get("ViolationSeverity") or "").lower() == "major"), "minor": sum(1 for x in v if (x.get("ViolationSeverity") or "").lower() == "minor"),
            "text": "; ".join(sorted({(x.get("ViolationType") or "").strip() for x in v if x.get("ViolationType")}))[:200]}


def run():
    rows = [x for x in (row(r) for r in fetch_json(URL, timeout=180)) if x]
    seen, out = set(), []
    for r in rows + (load("inspections.json", []) or []):
        if r["id"] not in seen:
            seen.add(r["id"])
            out.append(r)
    out.sort(key=lambda r: r["date"], reverse=True)
    save("inspections.json", out)
    return len(out)


if __name__ == "__main__":
    print(run())
