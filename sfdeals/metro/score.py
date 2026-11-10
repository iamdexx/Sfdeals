"""Generic scorer: absentee + out of state + whatever signal layers the metro config declares.
Hot = a real house (street number, living space or build year) with at least one distress signal
(not just absentee) and a value at or above the metro's floor; lots and slivers never make the call list."""
import datetime as dt
import time
from collections import defaultdict
from ..util import load, save, GOVBANK, ENTITY
from . import metros

W = {"absentee": 20, "out_of_state": 10, "entity": -15}
KEEP = ("taxsale", "trustee", "recorder", "preforeclosure")


def derived(p, rules, today_ms):
    """Signals read off the parcel record itself (building condition, deed type, no homestead...).
    rule: {name, weight, label, field, in|contains, since_field?, since_days?}"""
    out = {}
    x = p.get("x") or {}
    for r in rules:
        v = x.get(r["field"])
        sv = str(v or "").strip().upper()
        hit = (sv in [o.upper() for o in r["in"]]) if "in" in r else (r["contains"].upper() in sv) if "contains" in r else bool(v)
        if hit and r.get("since_field"):
            d = x.get(r["since_field"])
            hit = bool(d) and (today_ms - float(d)) / 86400000 <= r.get("since_days", 730)
        if hit:
            out[r["name"]] = [{"sig": r["name"], "weight": r["weight"], "label": r["label"], "value": v}]
    return out


def run(key):
    cfg = metros.METROS[key]
    parcels = load("parcels.json.gz", []) or []
    phones = load("phones.json", {}) or {}
    sig = defaultdict(lambda: defaultdict(list))
    by_addr = {p["addr"]: p["tag"] for p in parcels if p["addr"]}
    tags = {p["tag"] for p in parcels}
    for s in load("signals.json.gz", []) or []:
        t = s["tag"] if s["tag"] in tags else by_addr.get(s["addr"])
        if t:
            sig[t][s["sig"]].append(s)
    today = dt.date.today().isoformat()
    today_ms = time.time() * 1000
    rules = [r for c in cfg["counties"] for r in c.get("derived", [])]
    leads = []
    for p in parcels:
        s = dict(sig.get(p["tag"]) or {})
        s.update(derived(p, rules, today_ms))
        p.pop("x", None)
        absentee = p["occ"] == "N" or (p["mail"] and p["addr"] and p["mail"] != p["addr"])
        if not s and not absentee:
            continue
        if GOVBANK.search(p["owner"]) or not p["owner"]:
            continue
        score, why, signals = 0, [], {}
        if absentee:
            score += W["absentee"]; why.append("absentee")
            if p["mail_state"] and p["mail_state"] != cfg["state"]:
                score += W["out_of_state"]; why.append("out of state")
        for name, items in s.items():
            score += items[0]["weight"]; why.append(items[0]["label"]); signals[name] = items
        if ENTITY.search(p["owner"]):
            score += W["entity"]; why.append("investor owned")
        if score <= 0:
            continue
        cheap = (p.get("value") or 0) < cfg.get("min_value", 25000)
        house = p["addr"][:1] not in ("", "0") and (p.get("res_sqft") or p.get("year"))
        ph = phones.get(p["tag"])
        leads.append({**p, "mkt": p.get("value"), "score": score, "why": why, "signals": signals, "as_of": today, "hot": bool(s and house and not cheap),
                      **({"phones": ph["phones"], "emails": ph.get("emails", []), "contact": ph.get("name", "")} if ph and ph.get("hit") else {})})
    leads.sort(key=lambda x: (-x["score"], x["addr"]))
    hot = [l for l in leads if l.pop("hot")]
    top = hot[:2500] + [l for l in hot[2500:] if any(k in l["signals"] for k in KEEP)]
    save("leads.json", {"as_of": today, "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "count": len(leads),
                        "hot": len(hot), "leads": top, "absentee_only": len(leads) - len(hot)})
    save("buyers.json", [])
    return len(hot), len(leads)
