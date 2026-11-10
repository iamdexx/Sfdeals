"""Join every distress signal onto the parcel table and rank leads."""
import datetime as dt, re
from collections import defaultdict
from .util import load, save, GOVBANK, ENTITY

WEAK_CITATIONS = {"Snow"}
W = {"absentee": 20, "out_of_state": 10, "tax": 30, "tax_big": 10, "citation": 15, "citation_repeat": 10,
     "preforeclosure": 35, "reo": 10, "entity": -5}


def run():
    parcels = load("parcels.json.gz", [])
    by_addr, by_cid = {}, {}
    for p in parcels:
        if p["addr"]:
            by_addr.setdefault(p["addr"], p)
        if p["cid"]:
            by_cid.setdefault(p["cid"].lstrip("0"), p)
    sig = defaultdict(lambda: defaultdict(list))

    for c in load("citations.json", []):
        p = by_addr.get(c["addr"])
        if p:
            sig[p["tag"]]["citations"].append(c)
    for d in load("delinquent.json", []):
        p = by_cid.get(d["cid"].lstrip("0"))
        if p:
            sig[p["tag"]]["tax"].append(d)
    sh = load("sheriff.json", {"upcoming": [], "results": []})
    for s in sh["upcoming"] + load("lincoln.json", []):
        p = by_addr.get(s["addr"])
        if p:
            sig[p["tag"]]["foreclosure"].append(s)
    for s in sh["results"]:
        p = by_addr.get(s["addr"])
        if p and "BANK" in (s.get("bidder") or "").upper():
            sig[p["tag"]]["reo"].append(s)

    today = dt.date.today().isoformat()
    leads = []
    for p in parcels:
        s = sig.get(p["tag"])
        absentee = p["occ"] == "N" or (p["mail"] and p["addr"] and p["mail"] != p["addr"])
        if not s and not absentee:
            continue
        if GOVBANK.search(p["owner"]):
            continue
        score, why = 0, []
        if absentee:
            score += W["absentee"]; why.append("absentee")
            if p["mail_state"] and p["mail_state"] != "SD":
                score += W["out_of_state"]; why.append("out of state")
        tax = sum(x["amount"] for x in s["tax"]) if s else 0
        if tax:
            score += W["tax"]; why.append("tax delinquent $%s" % format(int(tax), ","))
            if tax > 5000:
                score += W["tax_big"]
        cutoff = (dt.date.today() - dt.timedelta(days=548)).isoformat()
        cits = [c for c in (s["citations"] if s else []) if c["date"] >= cutoff and c["type"] not in WEAK_CITATIONS]
        if cits:
            score += min(W["citation"] * len({c["type"] for c in cits}) + W["citation_repeat"] * sum("1st" not in c["action"] for c in cits), 45)
            why.append("%d code citation%s" % (len(cits), "s" if len(cits) > 1 else ""))
        if s and s["foreclosure"]:
            score += W["preforeclosure"]; f = s["foreclosure"][0]
            why.append("sheriff sale %s, judgment $%s" % (f.get("sale_date") or "", format(int(f["judgment"]), ",")))
        if s and s["reo"]:
            score += W["reo"]; why.append("bank took it back")
        if ENTITY.search(p["owner"]):
            score += W["entity"]
        if not s and absentee:
            # absentee alone is a weak signal; keep but only surface it in the long tail
            pass
        if score <= 0:
            continue
        leads.append({**p, "score": score, "why": why, "signals": {k: (sorted(v, key=lambda c: c["date"], reverse=True) if k == "citations" else v) for k, v in (s or {}).items() if v}, "as_of": today})
    leads.sort(key=lambda x: (-x["score"], x["addr"]))
    hot = [l for l in leads if l["why"] != ["absentee"] and l["why"] != ["absentee", "out of state"]]
    save("leads.json", {"as_of": today, "count": len(leads), "hot": len(hot), "leads": hot[:2000],
                        "absentee_only": len(leads) - len(hot)})
    buyers = defaultdict(lambda: {"name": "", "buys": 0, "total": 0.0, "last": ""})
    for s in sh["results"]:
        b = re.sub(r"[,.]|\b(LLC|L L C|INC|CORP)\b", "", (s.get("bidder") or "").upper()).strip()
        b = re.sub(r"\s+", " ", b)
        if b and "BANK" not in b:
            buyers[b]["name"] = b; buyers[b]["buys"] += 1; buyers[b]["total"] += s.get("bid") or 0
            buyers[b]["last"] = max(buyers[b]["last"], s.get("sale_date") or "")
    save("buyers.json", sorted(buyers.values(), key=lambda b: -b["buys"]))
    return len(hot), len(leads)


if __name__ == "__main__":
    print(run())
