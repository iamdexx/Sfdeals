"""Attach owner phone numbers to the leads worth calling (pre-foreclosure, trustee sale, county tax sale)
using the Tracerfy instant trace API. Pay per hit (about $0.10), misses are free. Needs TRACERFY_API_KEY;
without it this step does nothing. Results are cached in phones.json so a parcel is traced once;
misses are retried after RETRY_DAYS. MAX_PER_RUN bounds the spend of any single heartbeat run."""
import datetime as dt
import json
import os
import time
from ..util import fetch, save, load

BASE = os.environ.get("TRACERFY_BASE", "https://tracerfy.com")
WANT = ("recorder", "trustee", "taxsale", "landtax")
MAX_PER_RUN = int(os.environ.get("SKIPTRACE_MAX", "60"))
RETRY_DAYS = 90



def targets(leads, cache, today):
    out = []
    for l in leads:
        if not any(k in l.get("signals", {}) for k in WANT):
            continue
        c = cache.get(l["tag"])
        if c and (c.get("hit") or c.get("traced", "") > (today - dt.timedelta(days=RETRY_DAYS)).isoformat()):
            continue
        out.append(l)
    return out[:MAX_PER_RUN]


def lookup(key, lead):
    body = {"address": lead["addr"].title(), "city": (lead.get("muni") or "Saint Louis"), "state": "MO",
            "zip": str(lead.get("zip") or "")[:5], "find_owner": True}
    raw = fetch(BASE + "/v1/api/trace/lookup/", data=json.dumps(body).encode(),
                headers={"Authorization": "Bearer " + key, "Content-Type": "application/json", "User-Agent": "sfdeals/1.0"}, timeout=60, retries=1)
    return parse(json.loads(raw))


def parse(d):
    persons = d.get("persons") or []
    phones, emails, name = [], [], ""
    for p in sorted(persons, key=lambda p: (not p.get("property_owner"), p.get("deceased", False))):
        if p.get("deceased"):
            continue
        if not name:
            name = p.get("full_name") or ""
        for ph in sorted(p.get("phones") or [], key=lambda x: x.get("rank", 9)):
            if ph.get("number") and ph["number"] not in [x["number"] for x in phones]:
                phones.append({"number": ph["number"], "type": ph.get("type", ""), "dnc": bool(ph.get("dnc"))})
        emails += [e["email"] for e in p.get("emails") or [] if e.get("email")]
    return {"hit": bool(d.get("hit")) and bool(phones), "phones": phones[:4], "emails": emails[:2], "name": name,
            "credits": d.get("credits_deducted", 0)}


def run():
    key = os.environ.get("TRACERFY_API_KEY")
    cache = load("phones.json", {}) or {}
    if not key:
        return "skipped (no TRACERFY_API_KEY)"
    leads = (load("leads.json", {}) or {}).get("leads", [])
    today = dt.date.today()
    done = hits = credits = 0
    for l in targets(leads, cache, today):
        try:
            r = lookup(key, l)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if "402" in msg:
                print("skiptrace: out of credits, stopping")
                break
            print("skiptrace:", l["tag"], msg[:120])
            continue
        r["traced"] = today.isoformat()
        cache[l["tag"]] = r
        done += 1; hits += r["hit"]; credits += r["credits"]
        time.sleep(0.5)
    save("phones.json", cache)
    return {"traced": done, "hits": hits, "credits": credits, "cached": len(cache)}


if __name__ == "__main__":
    print(run())
