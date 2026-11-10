import json, re, time, urllib.request, urllib.parse, gzip, os
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MARKET = "sf"


def set_market(m):
    """Select which data/<market>/ directory save() and load() use."""
    global MARKET
    MARKET = m


def market_dir():
    return DATA / MARKET


def fetch(url, data=None, headers=None, timeout=60, retries=3):
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    body = urllib.parse.urlencode(data).encode() if isinstance(data, dict) else data
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise last


def fetch_json(url, **kw):
    return json.loads(fetch(url, **kw).decode("utf-8", "replace"))


def fetch_text(url, **kw):
    return fetch(url, **kw).decode("utf-8", "replace")


def via_proxy(url):
    """Read-only text proxy for pages behind a bot challenge."""
    return fetch_text("https://r.jina.ai/" + url, headers={"Accept": "text/plain"})


def save(name, obj):
    d = market_dir()
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    if name.endswith(".gz"):
        with gzip.open(p, "wt", encoding="utf-8") as f:
            json.dump(obj, f, separators=(",", ":"))
    else:
        p.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    return p


def load(name, default=None):
    p = market_dir() / name
    if not p.exists():
        return default
    if name.endswith(".gz"):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(p.read_text())


SUFFIX = {
    "STREET": "ST", "AVENUE": "AVE", "AV": "AVE", "DRIVE": "DR", "ROAD": "RD", "LANE": "LN",
    "COURT": "CT", "CIRCLE": "CIR", "PLACE": "PL", "BOULEVARD": "BLVD", "TRAIL": "TRL",
    "TERRACE": "TER", "PARKWAY": "PKWY", "HIGHWAY": "HWY", "WAY": "WAY",
}
_TAIL = re.compile(r"[,.]?\s*(SIOUX FALLS|SFSD|SF|S\.F\.|HARRISBURG|TEA|BRANDON|ST LOUIS|SAINT LOUIS|ST\.? LOUIS|FLORISSANT|FERGUSON|KIRKWOOD|UNIVERSITY CITY|AFFTON|HAZELWOOD|MARYLAND HEIGHTS|CHESTERFIELD)?,?\s*(SD|S\.D\.|SOUTH DAKOTA|MO|MISSOURI)?\s*\d{5}(-\d{4})?\s*$", re.I)
_UNIT = re.compile(r"\s+(APT|UNIT|#|STE|SUITE|LOT)\s*\S+$", re.I)


DIRS = {"NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}


def norm_addr(a):
    """Normalise a situs address to the city GIS style: '1400 E 24TH ST'.
    Directionals are only abbreviated right after the house number or at the end,
    so '3008 S WEST AVE' keeps WEST as the street name."""
    if not a:
        return ""
    a = a.upper().replace(".", "").replace(",", " ")
    a = _TAIL.sub("", a)
    a = _UNIT.sub("", a)
    parts = re.sub(r"\s+", " ", a).strip().split(" ")
    if len(parts) > 2 and parts[1] in DIRS:
        parts[1] = DIRS[parts[1]]
    if len(parts) > 2 and parts[1] == "SAINT":
        parts[1] = "ST"
    if len(parts) > 2 and parts[-1] in DIRS:
        parts[-1] = DIRS[parts[-1]]
    if len(parts) > 2 and parts[-1] in SUFFIX:
        parts[-1] = SUFFIX[parts[-1]]
    elif len(parts) > 3 and parts[-1] in DIRS.values() and parts[-2] in SUFFIX:
        parts[-2] = SUFFIX[parts[-2]]
    return " ".join(parts)


ENTITY = re.compile(r"\b(LLC|L\.L\.C|INC|CORP|CO\b|LP|LLP|TRUST|TR\b|BANK|CHURCH|CITY OF|COUNTY|STATE OF|USA|HOUSING|AUTHORITY|ASSOC|PARTNERS|PROPERTIES|HOLDINGS|DEVELOPMENT|HOMES|CONSTRUCTION|BUILDERS)\b", re.I)
GOVBANK = re.compile(r"\b(BANK|CITY OF|COUNTY|STATE OF|USA|UNITED STATES|HOUSING|AUTHORITY|SCHOOL|CHURCH|FEDERAL|CREDIT UNION|MORTGAGE|HUD|FANNIE|FREDDIE|VETERANS|LAND REUTILIZATION|LRA|LCRA|SLDC|LAND CLEARANCE|METROPOLITAN SEWER|MSD|REDEVELOPMENT CORP)\b", re.I)
