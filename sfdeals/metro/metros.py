"""Config-driven metros: one JSON file per metro in sfdeals/metro/configs/<key>.json.

Each file: {"name","short","state","min_value","counties":[{"name","parcels":{url,where,page,map,extra?,occ_field?,addr_strip?},
"signals":[{name,weight,label,url,where?,map}],"derived":[{name,weight,label,field,in|contains,since_field?,since_days?}],"lookup"}],
"ui":{name,st,q,sigs,lookup,title_cos,title_call,law,groups,prefc,sos,buyers_h,buyers_note,buyers_empty,repairs,sources,contracts}}
`map` goes from our schema to the layer's field names; `addr` may be a list of fields joined with spaces.
`where` should keep the pull small (residential land use plus a server-side absentee filter); parcels that carry a
signal are fetched by id afterwards so nothing with a signal is lost. Adding a metro = adding a file; no shared file changes."""
import json
from pathlib import Path

CONFIGS = Path(__file__).parent / "configs"


def _load():
    out = {}
    for f in sorted(CONFIGS.glob("*.json")):
        out[f.stem] = json.loads(f.read_text())
    return out


METROS = _load()
