"""Config-driven metros. A metro is a list of counties; each county names an ArcGIS parcel layer plus
any number of ArcGIS signal layers keyed by parcel number. Adding a metro is a config entry in
metros.py, not new code. Pullers: parcels.run, signals.run, score.run (see markets.py)."""
