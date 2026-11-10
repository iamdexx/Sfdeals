"""Write data/markets.json: the per-metro UI blocks the app loads at startup (built-in sf/stl stay in index.html)."""
import json
from ..util import DATA
from .metros import METROS


def run():
    out = {k: {"key": "sfdeals_" + k, **m["ui"]} for k, m in METROS.items() if m.get("ui")}
    DATA.mkdir(exist_ok=True)
    (DATA / "markets.json").write_text(json.dumps(out, separators=(",", ":")))
    return len(out)
