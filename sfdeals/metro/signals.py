"""Pull every signal layer named in the metro config into one list: {sig, weight, label, tag, addr, ...}."""
from ..util import save, norm_addr
from ..stl import arcgis
from . import metros


def row(a, s):
    m = s["map"]
    r = {"sig": s["name"], "weight": s["weight"], "label": s["label"], "tag": str(a.get(m["tag"]) or "").strip(),
         "addr": norm_addr(a.get(m.get("addr")) or "") if m.get("addr") else ""}
    for k, f in m.items():
        if k not in ("tag", "addr"):
            r[k] = a.get(f)
    return r


def run(key):
    cfg = metros.METROS[key]
    out = []
    for c in cfg["counties"]:
        for s in c.get("signals", []):
            flds = ",".join(dict.fromkeys(s["map"].values()))
            out += [r for r in (row(a, s) for a in arcgis(s["url"], s.get("where", "1=1"), flds)) if r["tag"]]
    save("signals.json.gz", out)
    return len(out)
