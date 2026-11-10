"""City of St. Louis Recorder of Deeds index (Fidlar Direct Search, free, anonymous JSON API).
Before a Missouri lender forecloses it records an Appointment of Successor Trustee, usually 2 to 6
weeks before the newspaper notice. That filing is the earliest public foreclosure signal.
Party1 = lender + borrowers, Party2 = the new trustee (a foreclosure law firm)."""
import datetime as dt
import json
import re
from ..util import fetch, save, load, norm_addr

BASE = "https://mostlouiscity.fidlar.com/MOStLouis/Scrap.WebService.DirectSearch/"
TYPES = {"16": "pre-foreclosure", "151": "notice of sale"}  # APPOINT SUCC TRUSTEE, NOTICE OF SALE
DAYS = 120
PID = re.compile(r"^(\d{4})-(\d)-(\d{3})\.(\d{3})$")


def token():
    d = json.loads(fetch(BASE + "token", data=b"grant_type=password&username=anonymous&password=anonymous",
                         headers={"Content-Type": "application/x-www-form-urlencoded"}))
    return d["access_token"]


def search(tok, doc_type, start, end):
    body = {"FirstName": "", "LastBusinessName": "", "StartDate": start, "EndDate": end, "DocumentName": "",
            "DocumentType": doc_type, "SubdivisionName": "", "SubdivisionLot": "", "SubdivisionBlock": "",
            "MunicipalityName": "", "TractSection": "", "TractTownship": "", "TractRange": "", "TractQuarter": "",
            "TractQuarterQuarter": "", "AddressHouseNo": "", "AddressStreet": "", "AddressCity": "", "AddressZip": "",
            "ParcelNumber": "", "Book": "", "Page": "", "ReferenceNumber": ""}
    d = json.loads(fetch(BASE + "breeze/Search", data=json.dumps(body).encode(),
                         headers={"Content-Type": "application/json", "Authorization": "Bearer " + tok}, timeout=120))
    return d.get("DocResults", [])


def pid(legal):
    """'5901-9-200.000' is the assessor ParcelId 59019200000 with punctuation."""
    m = PID.match((legal or "").strip())
    return "".join(m.groups()) if m else ""


def row(doc, kind):
    legals = doc.get("Legals") or []
    addrs = [norm_addr(l["Description"]) for l in legals if l.get("LegalType") == "A" and l.get("Description")]
    pids = [p for p in (pid(l["Description"]) for l in legals if l.get("LegalType") == "P") if p]
    parties = doc.get("Parties") or []
    people = [(" ".join(filter(None, [p.get("Name"), p.get("AdditionalName")]))).strip() for p in parties if p.get("PartyTypeId") == 1]
    rec = doc.get("RecordedDateTime") or ""
    try:
        date = dt.datetime.strptime(rec.split(" ")[0], "%m/%d/%Y").date().isoformat()
    except ValueError:
        date = ""
    return {"doc": doc.get("DocumentName"), "kind": kind, "type": doc.get("DocumentType"), "date": date,
            "addrs": sorted(set(a for a in addrs if a)), "pids": sorted(set(pids)),
            "lender": (doc.get("Party1") or "").strip(), "trustee": (doc.get("Party2") or "").strip(),
            "parties": people[:6]}


def run():
    old = {r["doc"]: r for r in (load("recorder.json", []) or [])}
    today = dt.date.today()
    start = (today - dt.timedelta(days=DAYS)).isoformat()
    tok = token()
    for code, kind in TYPES.items():
        for doc in search(tok, code, start, today.isoformat()):
            r = row(doc, kind)
            if r["doc"]:
                old[r["doc"]] = r
    cutoff = (today - dt.timedelta(days=DAYS)).isoformat()
    out = sorted((r for r in old.values() if r["date"] >= cutoff), key=lambda r: r["date"], reverse=True)
    save("recorder.json", out)
    return len(out)


if __name__ == "__main__":
    print(run())
