"""Rank St. Louis City + County residential parcels by distress signals."""
import datetime as dt
from collections import defaultdict
from ..util import load, save, GOVBANK, ENTITY

W = {"absentee": 20, "out_of_state": 10, "tax": 30, "tax_big": 10, "vacant": 30, "vacant_bad": 10,
     "condemned": 35, "secure": 25, "violation": 15, "landtax": 35, "county_vacant": 15, "entity": -5}
INSPECT_DAYS = 548


def run():
    parcels = (load("city_parcels.json.gz", []) or []) + (load("county_parcels.json.gz", []) or [])
    by_tag, by_addr = {}, {}
    for p in parcels:
        by_tag.setdefault(p["tag"], p)
        if p["addr"]:
            by_addr.setdefault(p["addr"], p)
    sig = defaultdict(lambda: defaultdict(list))
    cutoff = (dt.date.today() - dt.timedelta(days=INSPECT_DAYS)).isoformat()
    for i in load("inspections.json", []) or []:
        if i["date"] < cutoff:
            continue
        p = by_tag.get(i["pid"]) or by_addr.get(i["addr"])
        if p:
            sig[p["tag"]]["inspections"].append(i)
    for l in load("landtax.json", []) or []:
        p = by_tag.get(l["pid"]) or by_addr.get(l["addr"])
        if p:
            sig[p["tag"]]["landtax"].append(l)
    for v in load("county_vacant.json", []) or []:
        p = by_tag.get(v["tag"]) or by_addr.get(v["addr"])
        if p:
            sig[p["tag"]]["county_vacant"].append(v)
    vac = load("vacant.json", {}) or {}

    today = dt.date.today().isoformat()
    leads = []
    for p in parcels:
        s = sig.get(p["tag"])
        absentee = p["occ"] == "N" or (p["mail"] and p["addr"] and p["mail"] != p["addr"])
        vb = vac.get(p.get("handle") or "") if p.get("vac_year") else None
        if not s and not absentee and not p["tax_bal"] and not p["vac_year"]:
            continue
        if GOVBANK.search(p["owner"]) or not p["owner"]:
            continue
        score, why, signals = 0, [], {}
        if absentee:
            score += W["absentee"]; why.append("absentee")
            if p["mail_state"] and p["mail_state"] != "MO":
                score += W["out_of_state"]; why.append("out of state")
        if p["tax_bal"] > 0:
            score += W["tax"]; why.append("tax delinquent $%s" % format(int(p["tax_bal"]), ","))
            if p["tax_bal"] > 5000:
                score += W["tax_big"]
            signals["tax"] = [{"amount": p["tax_bal"], "year": "", "legal": "city tax balance"}]
        if p["vac_year"]:
            score += W["vacant"]; why.append("vacant building since %s" % p["vac_year"])
            if vb and (vb.get("vmaj") or vb.get("unpd")):
                score += W["vacant_bad"]
            signals["vacant"] = [{**(vb or {}), "year": p["vac_year"]}]
        ins = (s or {}).get("inspections", [])
        if ins:
            kinds = {i["kind"] for i in ins}
            if "condemned" in kinds:
                score += W["condemned"]; why.append("condemned")
            elif "secure" in kinds:
                score += W["secure"]; why.append("notice to secure")
            viol = [i for i in ins if i["kind"] == "violation"]
            if viol:
                score += min(W["violation"] * len(viol), 45); why.append("%d code violation%s" % (len(viol), "s" if len(viol) > 1 else ""))
            signals["citations"] = [{"date": i["date"], "type": i["result"], "action": i["text"] or i["type"]} for i in sorted(ins, key=lambda i: i["date"], reverse=True)]
        if s and s["landtax"]:
            score += W["landtax"]; why.append("land tax sale"); signals["landtax"] = s["landtax"]
        if s and s["county_vacant"]:
            score += W["county_vacant"]; why.append("vacant (county survey)"); signals["county_vacant"] = s["county_vacant"]
        if ENTITY.search(p["owner"]):
            score += W["entity"]
        if score <= 0:
            continue
        leads.append({**p, "score": score, "why": why, "signals": signals, "as_of": today})
    leads.sort(key=lambda x: (-x["score"], x["addr"]))
    hot = [l for l in leads if l["why"] not in (["absentee"], ["absentee", "out of state"])]
    save("leads.json", {"as_of": today, "count": len(leads), "hot": len(hot), "leads": hot[:2500],
                        "absentee_only": len(leads) - len(hot),
                        "city": sum(l["county"] == "St. Louis City" for l in hot), "county": sum(l["county"] == "St. Louis County" for l in hot)})
    save("buyers.json", [])
    return len(hot), len(leads)


if __name__ == "__main__":
    print(run())
