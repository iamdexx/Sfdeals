"""Rank St. Louis City + County residential parcels by distress signals."""
import datetime as dt
from collections import defaultdict
from ..util import load, save, GOVBANK, ENTITY

W = {"absentee": 20, "out_of_state": 10, "tax": 30, "tax_big": 10, "vacant_new": 30, "vacant_mid": 15, "vacant_old": 5, "vacant_bad": 10,
     "condemned": 35, "secure": 25, "violation": 15, "landtax": 35, "county_vacant": 15, "taxsale": 45, "trustee": 60, "preforeclosure": 50, "entity": -15}
INSPECT_DAYS = 548
CITY_ASSESS = 0.19          # city AsdTotal is 19% of market value; county TOTAPVAL is already market
CITY_TAX_RATE = 0.09        # about one year of city tax as a share of assessed value
MIN_MARKET = 25000          # below this it is a shell or a lot, not a wholesale deal
STRONG = ("trustee", "taxsale", "landtax", "recorder")


def market_value(p):
    v = p.get("value") or 0
    return round(v / CITY_ASSESS) if p["county"] == "St. Louis City" else v


def tax_delinquent(p):
    """City TaxBalance includes the current year's bill, which is not late until Jan 1. Only count
    balances clearly bigger than one year's tax."""
    bal = p.get("tax_bal") or 0
    one_year = CITY_TAX_RATE * (p.get("value") or 0)
    return bal > max(1500, 1.4 * one_year)


def vacant_weight(vac_year, this_year):
    """2018 is when the city registry was bulk loaded, so 2018 means 'at least since 2018'."""
    age = this_year - vac_year
    if age <= 3:
        return W["vacant_new"], "vacant building since %d" % vac_year
    if age <= 8 or vac_year == 2018:
        return W["vacant_mid"], "vacant building since %d" % vac_year
    return W["vacant_old"], "vacant %d+ years" % age


def street_key(addr):
    parts = addr.split(" ")
    if len(parts) < 2 or not parts[0][:1].isdigit():
        return None
    name = parts[2] if parts[1] in ("N", "S", "E", "W") and len(parts) > 2 else parts[1]
    return parts[0] + " " + name


KEEP = ("trustee", "taxsale", "landtax", "recorder")


def run():
    parcels = (load("city_parcels.json.gz", []) or []) + (load("county_parcels.json.gz", []) or [])
    by_tag, by_addr = {}, {}
    for p in parcels:
        by_tag.setdefault(p["tag"], p)
        if p["addr"]:
            by_addr.setdefault(p["addr"], p)
    by_street = defaultdict(list)
    for p in parcels:
        k = street_key(p["addr"])
        if k:
            by_street[k].append(p)

    def find(addr, county=None):
        """Exact normalised address, else the one parcel sharing house number + first street word
        (catches 'OSBORN' vs 'OSBORN DR', 'MCCARREN' vs 'MCCARRON' does not)."""
        p = by_addr.get(addr)
        if p and (county is None or p["county"] == county):
            return p
        c = [x for x in by_street.get(street_key(addr), []) if county is None or x["county"] == county]
        return c[0] if len(c) == 1 else None

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
    for t in load("county_taxsale.json", []) or []:
        p = by_tag.get(t["tag"]) or find(t["addr"], "St. Louis County")
        if p:
            sig[p["tag"]]["taxsale"].append(t)
    for t in load("trustee.json", []) or []:
        p = find(t["addr"], t["county"])
        if p:
            sig[p["tag"]]["trustee"].append(t)
    for r in load("recorder.json", []) or []:
        hits = {by_tag[t]["tag"] for t in r["pids"] if t in by_tag}
        if not hits:
            hits = {q["tag"] for q in (find(a, "St. Louis City") for a in r["addrs"]) if q}
        for t in hits:
            sig[t]["recorder"].append(r)
    vac = load("vacant.json", {}) or {}

    today = dt.date.today().isoformat()
    this_year = dt.date.today().year
    leads = []
    for p in parcels:
        s = sig.get(p["tag"])
        absentee = p["occ"] == "N" or (p["mail"] and p["addr"] and p["mail"] != p["addr"])
        vb = vac.get(p.get("handle") or "") if p.get("vac_year") else None
        if not s and not absentee and not p["tax_bal"] and not p["vac_year"]:
            continue
        if GOVBANK.search(p["owner"]) or not p["owner"]:
            continue
        score, why, signals, strong = 0, [], {}, bool(s and any(s.get(k) for k in STRONG))
        if absentee:
            score += W["absentee"]; why.append("absentee")
            if p["mail_state"] and p["mail_state"] != "MO":
                score += W["out_of_state"]; why.append("out of state")
        if tax_delinquent(p):
            strong = True
            score += W["tax"]; why.append("tax delinquent $%s" % format(int(p["tax_bal"]), ","))
            if p["tax_bal"] > 5000:
                score += W["tax_big"]
            signals["tax"] = [{"amount": p["tax_bal"], "year": "", "legal": "city tax balance, more than a year behind"}]
        if p["vac_year"]:
            w, label = vacant_weight(p["vac_year"], this_year)
            strong = strong or w >= W["vacant_mid"]
            score += w; why.append(label)
            if vb and (vb.get("vmaj") or vb.get("unpd")):
                score += W["vacant_bad"]
            signals["vacant"] = [{**(vb or {}), "year": p["vac_year"]}]
        ins = (s or {}).get("inspections", [])
        if ins:
            strong = True
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
            strong = True
            score += W["county_vacant"]; why.append("vacant (county survey)"); signals["county_vacant"] = s["county_vacant"]
        if s and s["taxsale"]:
            score += W["taxsale"]; why.append("county tax sale (%s)" % s["taxsale"][0]["status"].lower()); signals["taxsale"] = s["taxsale"]
        if s and s["trustee"]:
            score += W["trustee"]; why.append("trustee sale %s" % s["trustee"][0]["date"]); signals["trustee"] = s["trustee"]
        if s and s["recorder"]:
            score += W["preforeclosure"]; why.append("pre-foreclosure filed %s" % s["recorder"][0]["date"]); signals["recorder"] = s["recorder"]
        if ENTITY.search(p["owner"]):
            score += W["entity"]; why.append("investor owned")
        if score <= 0:
            continue
        mkt = market_value(p)
        cheap = mkt and mkt < MIN_MARKET and not (s and (s.get("trustee") or s.get("recorder")))
        leads.append({**p, "mkt": mkt, "score": score, "why": why, "signals": signals, "as_of": today, "hot": bool(strong and not cheap)})
    leads.sort(key=lambda x: (-x["score"], x["addr"]))
    hot = [l for l in leads if l.pop("hot")]
    top = hot[:2500] + [l for l in hot[2500:] if any(k in l["signals"] for k in KEEP)]
    save("leads.json", {"as_of": today, "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "count": len(leads), "hot": len(hot), "leads": top,
                        "absentee_only": len(leads) - len(hot),
                        "city": sum(l["county"] == "St. Louis City" for l in hot), "county": sum(l["county"] == "St. Louis County" for l in hot)})
    save("buyers.json", [])
    return len(hot), len(leads)


if __name__ == "__main__":
    print(run())
