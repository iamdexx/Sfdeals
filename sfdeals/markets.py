"""Market registry. Each market has its own data/<key>/ directory and its own pull steps."""
from . import parcels, citations, sheriff, delinquent, lincoln, score
from functools import partial
from .metro import metros, ui as m_ui, parcels as m_parcels, signals as m_signals, score as m_score
from .stl import city_parcels, county_parcels, inspections, vacant, landtax, county_vacant, county_taxsale, trustee, city_recorder, skiptrace, score as stl_score

MARKETS = {
    "sf": {
        "name": "Sioux Falls, SD",
        "steps": {"parcels": parcels.run, "citations": citations.run, "sheriff": sheriff.run,
                  "delinquent": delinquent.run, "lincoln": lincoln.run, "score": score.run},
        "optional": {"lincoln"},
    },
    "stl": {
        "name": "St. Louis, MO",
        "steps": {"city_parcels": city_parcels.run, "county_parcels": county_parcels.run,
                  "inspections": inspections.run, "vacant": vacant.run, "landtax": landtax.run,
                  "county_vacant": county_vacant.run, "county_taxsale": county_taxsale.run, "trustee": trustee.run, "city_recorder": city_recorder.run, "skiptrace": skiptrace.run, "score": stl_score.run},
        "optional": {"inspections", "vacant", "landtax", "county_vacant", "county_taxsale", "trustee", "city_recorder", "skiptrace"},
    },
}

for _k, _m in metros.METROS.items():
    MARKETS[_k] = {"name": _m["name"], "ui": _m.get("ui"),
                   "steps": {"signals": partial(m_signals.run, _k), "parcels": partial(m_parcels.run, _k), "score": partial(m_score.run, _k), "markets": m_ui.run},
                   "optional": set()}
