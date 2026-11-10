# Chicago (Cook County) sources

Status: blocked on the framework, not on the data. Cook County publishes everything we need, but the owner name and mailing
address are only on the county's Socrata open data portal, and Chicago's code enforcement is Socrata too. The config-driven
metro code (`sfdeals/metro/`) only reads ArcGIS layers, so Chicago cannot ship as a `configs/<key>.json` file alone. No config
was added, because a config that cannot pull would register a broken market in `markets.py` and fail the heartbeat.

## Parcels

ArcGIS (works, but no owner):
- `https://gis.cookcountyil.gov/traditional/rest/services/cookVwrDynmc/MapServer/44` "Current Parcel", 1,419,180 rows, maxRecordCount 2000,
  pagination supported. Fields: `PIN14`, `Pin10`, `BLDGClass`, `BldgConst`, `BldgSqft`, `BldgAge`, `TotalValue` (string), `Address`, `City`,
  `Zip_Code`, `Town`, `TAXYR` (2024). No owner, no mailing address, no sale.
- `parcel_current_beta/FeatureServer/0` and `CookViewer3Parcels/MapServer/0` on the same server: same story (`CURRENTVALUE_TOTAL`, `BCLASS`,
  `BLDGSQFT`, `BLDGAGE`, `assessor_link`), no owner. The `Assessor` folder answers "Token Required". The county hub's "Property Open Data" link is dead.
- Chicago's own server `gisapps.chicago.gov/arcgis/rest/services` has basemaps, zoning, 311 admin boundaries and a `Parcel Addresses` layer
  (PIN14 + address range), no owner and no code enforcement.

Socrata (works, free, no login, SODA API; 50k rows per request in about 5 s without an app token):
- Assessor - Parcel Addresses `https://datacatalog.cookcountyil.gov/resource/3723-97qp.json`: 50.7M rows across all years, `year=2025` is
  1,863,808. Fields `pin` (14 digits, no dashes), `prop_address_full`, `prop_address_city_name`, `prop_address_zipcode_1`, `mail_address_name`
  (the taxpayer, this is our owner), `mail_address_full`, `mail_address_city_name`, `mail_address_state`, `mail_address_zipcode_1`, plus
  `owner_address_*`. Server-side absentee works: `$where=year=2025 AND mail_address_zipcode_1 != prop_address_zipcode_1`.
- Assessor - Parcel Universe (Current) `pabr-t5kh`: 1,864,469 rows (year 2026), `class`, `township_name`, `cook_municipality_name`, `zip_code`,
  lat/lon. Single family classes 202-210, 234, 278, 295 (203 alone is 343,900; 202 107k; 205 81k; 234 96k; 278 89k; 204 54k; 295 53k; 206 44k).
  299 is condos (457k), 211 is 2 to 6 units (150k).
- Assessor - Assessed Values `uzyt-m557`: `year=2025` 1,863,801 rows, `mailed_tot`, `certified_tot`, `board_tot`. Cook County assesses
  residential at 10% of market value, so market value = assessed total x 10; apply `min_value` to that.
- Assessor - Residential Single and Multi-Family Improvement Characteristics `x54s-btds`: `char_yrblt`, `char_bldg_sf`, `char_repair_cnd`
  (condition, a derived signal candidate), `char_cnst_qlty`, `cdu`.
- Assessor - Parcel Sales `wvhk-k5uv`: 165,516 sales since 2024-05; `buyer_name`, `seller_name`, `sale_price`, `sale_date`, `deed_type`,
  `mydec_deed_type`, `is_multisale`, `sale_filter_less_than_10k`. This is the cash buyer list.

## Distress signals

- City of Chicago Building Violations `https://data.cityofchicago.org/resource/22u3-xenr.json`: 1.16M open rows total, 102,166 open with
  `violation_date > 2024-01-01`. By bureau: CONSERVATION 77,350 (the housing code cases), ELEVATOR 9.5k, DEMOLITION 218, SPECIAL TASK FORCE 693.
  Address only (`address`, `street_number`, `street_direction`, `street_name`, `street_type`), no PIN, so join by normalized address like
  `score.py` already does for signals without a tag. Vacant building codes CN193xxx (register/secure/board) are a few dozen.
- Vacant and Abandoned Buildings - Violations `kc9i-wq85`: 5,012 rows, bank-owned buildings only, `property_address`, fines owed. Small but clean.
- Everything else on `gis.cookcountyil.gov` and `gisapps.chicago.gov` is boundaries, transit, zoning.

## Dead ends

- Treasurer - Annual Tax Sale `55ju-2fs9` stops at tax sale year 2014; Scavenger Sale `ydgz-vkrp` stops at 2007. Not refreshed.
- cookcountytreasurer.com has only a per-PIN delinquent search (`delinquentpropertytaxsearch.aspx`), no bulk list.
- 311 Vacant and Abandoned Buildings Reported `7nii-7srd` is historical, last record 2018-12.
- ArcGIS Hub has no Cook County owner or mailing layer, and no Chicago code enforcement feature service.

## What it takes to ship

A Socrata puller, either a `sfdeals/chi/` module like `sfdeals/stl/` or a `source: "socrata"` switch in `metro/parcels.py` and
`metro/signals.py` with a `socrata(url, where, select, page=50000)` generator (`$limit`/`$offset`/`$order=pin`). Parcels = Parcel Addresses
(year 2025, absentee filter) joined by `pin` to Parcel Universe (class in the single family list) and Assessed Values (x10), optionally
Improvement Characteristics for year built, sqft and condition. Buyers from Parcel Sales since 18 months ago. Signals = Building Violations
(open, CONSERVATION and DEMOLITION bureaus, since 2024) joined by address, plus the vacant building violations. Expected pull: about 1M
single family parcels before the absentee filter, well under 10 minutes at 50k rows per 5 s.

UI notes for when it ships: Illinois is a judicial foreclosure state and an attorney state by custom (both sides use lawyers at closing).
Since 2020 Illinois requires a broker license to wholesale more than once in 12 months (Real Estate License Act, 225 ILCS 454/1-10);
disclose the assignment in writing. Lookup: `https://www.cookcountyassessor.com/pin/{tag}`. SOS: `https://apps.ilsos.gov/businessentitysearch/`.

Next: Chicago 311 current dataset `v6vf-nfxy` (type "Vacant/Abandoned Building Complaint"), Cook County Sheriff foreclosure sale list,
Cook County Clerk of Court foreclosure filings (judicial state), suburban code enforcement (Cicero, Harvey, Chicago Heights via SSMMA hub).
