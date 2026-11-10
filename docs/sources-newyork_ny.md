# New York, NY (newyork_ny) sources

Metro: New York-Newark-Jersey City, NY-NJ. Principal county is Kings County (Brooklyn), but no public layer there carries owner
mailing addresses, so this metro ships on Suffolk County (Town of Brookhaven first, rest of the county second) plus Westchester County.
See "Dead ends" for why Kings / NYC and New Jersey are parked.

## Working sources

### Town of Brookhaven assessor property layer (parcels + derived signals)
- `https://gis.brookhavenny.gov/server/rest/services/Town_Website_Map/MapServer/54` ("Assessor Property Information"), ArcGIS Server, POST queries fine, 2,000 rows/page, ~1.3 s per page.
- Residential: `PROPERTY_TYPE IN ('210','220','230')` = 122,185 rows (NYS property class codes; 210 one family, 220 two family, 230 three family). `MARKET_VALUE > 0` on 122,159 of them.
- Fields used: `SCTM` (tag, Suffolk tax map id e.g. `0200 12300 0100 001000`), `PHYS_STREET`, `PHYS_CITY`, `PHYS_ZIP`, `OWNER_NAME`, `OWNER_ADDRESS`, `CITY`, `STATE`, `OWN_ZIP`, `MARKET_VALUE`, `LAST_SALE_DATE`, `LAST_SALE_PRICE`, `TOTAL_TAX`, `EXEMPTION1`.
- Signal fields on the parcel itself (used as `derived` rules):
  - `ARREARS` = 'ARREARS' when the current tax bill is unpaid: 1,185 residential rows.
  - `PRIORARREARS` = 'PRIOR ARREARS' when a prior year is still unpaid (lien now with Suffolk County): 1,563 residential rows.
  - `ON_VACANT_REGISTRY` = registration year ('2023' 176, '2024' 216, '2025' 143) or 'No' (121,650).
- Absentee filter: `STATE <> 'NY' OR TRIM(BOTH ' ' FROM OWNER_ADDRESS) <> TRIM(BOTH ' ' FROM PHYS_STREET)` (19,115 rows), plus the arrears / vacant rows so owner-occupied distressed houses are not hidden. Gotcha: `RTRIM()` and long OR chains with LIKE return ArcGIS "Unable to complete operation"; `TRIM(BOTH ' ' FROM x)` works.
- No year built or living area on this layer; those live in layer 55 below. `score.py` treats a county without building fields as "all houses are real", and the `where` only pulls residential classes, so that is fine.

### Town of Brookhaven building inventory (condition signal)
- `https://gis.brookhavenny.gov/server/rest/services/Town_Website_Map/MapServer/55` ("Assessor Building Inventory"), same `SCTM` key so the join is exact.
- `EXTERIOR_CONDITION = 'INFERIOR' OR INTERIOR_CONDITION = 'INFERIOR'` = 1,522 rows. Other values: NORMAL, GOOD, EXCELLENT. Also has `YEAR_BLT`, `TOTAL_LIVING`, `BLDG_STYLE`, its own `ON_VACANT_REGISTRY`.

### New York State tax parcels (rest of Suffolk, and Westchester)
- `https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Tax_Parcels_Public/MapServer/1`, NYS ITS GIS Program Office, statewide annual roll, 10,000 rows/page (~10 s per page).
- Fields used: `SWIS_SBL_ID` (tag), `PARCEL_ADDR`, `LOC_ZIP`, `MUNI_NAME`, `CITYTOWN_NAME`, `PRIMARY_OWNER`, `MAIL_ADDR`, `PO_BOX`, `MAIL_CITY`, `MAIL_STATE`, `MAIL_ZIP`, `PROP_CLASS`, `YR_BLT`, `SQFT_LIVING`, `FULL_MARKET_VAL`, `TOTAL_AV`, `BLDG_STYLE_DESC`, `PRINT_KEY`. No sale date / price.
- Suffolk: 210 = 425,472, 220 = 10,710, 215 = 7,672, 211 = 7,626. Residential absentee (`MAIL_STATE <> 'NY' OR MAIL_ZIP <> LOC_ZIP OR (LOC_ZIP IS NULL AND MAIL_ADDR <> PARCEL_ADDR)`) = 164,295; excluding Brookhaven (`CITYTOWN_NAME <> 'Brookhaven'`) = 91,268.
- Westchester: same filter = 70,961. Gotcha: many Westchester rows have `FULL_MARKET_VAL` = 0 with `TOTAL_AV` populated (towns assess at a fraction); those rows get `value = None` and drop out of hot, `TOTAL_AV` is kept in `extra`.
- Gotcha: `LOC_ZIP` is often null, hence the `MAIL_ADDR <> PARCEL_ADDR` fallback. `MAIL_ADDR IS NOT NULL` returns 0 for NYC counties (mailing fields are not supplied by NYC).
- Suffolk tags differ between the two layers (Brookhaven `SCTM` vs state `SWIS_SBL_ID`), which is why Brookhaven is its own county entry; the state entry excludes Brookhaven so nothing is double counted.

### Lookups
- Both lookups are the layer's own `f=html` record page by tag (no public per-parcel web page exists without a form: Brookhaven's assessor site returns 403 to scripts, Suffolk's RPTS site is search-form only).
- NY Department of State entity search: `https://apps.dos.ny.gov/publicInquiry/`.

## Results (first run, 2026-11-10)
- `python -m sfdeals.run newyork_ny all`: 4 min 14 s. 1,522 signal rows, 184,719 parcel rows pulled, 127,678 kept (min_value 150,000), 4,445 hot. Median value of the top 2,500 leads 503k.
- Signal counts in the top 2,500: prior_arrears 1,423, arrears 755, condition 324, vacant 125. 1,065 absentee, 1,435 owner-occupied with a signal (mail = situs, correctly not flagged absentee).
- 23 cash buyers (2+ buys in 18 months) from the Brookhaven sale fields, e.g. CLEAR HOUSES LLC, JD PROPERTY SOLUTIONS LLC, SELL HOUSE HOMEBUYERS LLC.
- Known quirk: `norm_addr` keeps the direction word where the town puts it, so "167 VILLAGE W CIR" vs mail "167 VILLAGE CIR W" shows as absentee. Rare.

## Dead ends
- Kings County / NYC: `MAPPLUTO` (`services5.arcgis.com/GfwWNkhOj9bNBqoJ/.../MAPPLUTO/FeatureServer/0`) has owner name, class, year built, assessed value, but no owner mailing address. The NYS layer for Kings (275,680 rows) has `PROP_CLASS` in the NYC `01`..`04` format and null mailing fields. So no absentee flag is possible for the five boroughs from ArcGIS. HPD violations, DOB violations / complaints, ECB, and the DOF tax lien sale list are Socrata only (`data.cityofnewyork.us`), which `signals.py` does not read. Park until the shared code gets a Socrata puller or NYC publishes mailing addresses.
- New Jersey counties (Bergen, Middlesex, Essex, Hudson, Ocean, Monmouth, Union, Morris, Passaic, Somerset): NJOGIS `Parcels_Composite_NJ_WM` (`services2.arcgis.com/XVOqAjTOJ5P6ngMu/.../FeatureServer/0`) has `OWNER_NAME`, `ST_ADDRESS`, `CITY_STATE`, `ZIP_CODE`, `NET_VALUE`, `YR_CONSTR`, `DEED_DATE`, `SALE_PRICE`, but `OWNER_NAME` is blank on most rows (Bergen 252,657 blanks) and `CITY_STATE` is a free text blob ("N.J.", " NJ", "FOREST HILLS, NY"), so the state field cannot be mapped cleanly. NJ MOD-IV is downloadable by county but not an ArcGIS service.
- Nassau County: Land Records Viewer is a form-driven ASP site, no REST service found; the NYS layer covers Nassau parcels but with no distress fields (add it as a parcels-only entry later if wanted).
- Suffolk County Comptroller tax sale list and Clerk foreclosure index: PDF / form search only.
- Town of Brookhaven assessor web pages (`brookhavenny.gov/...`) return HTTP 403 to scripts; the ArcGIS server is open.

## Next
- Westchester county GIS (`https://giswww.westchestergov.com/arcgis/rest/services`, `MunicipalTaxParcels`, Yonkers = layer 483) has per-municipality parcel layers with owner mailing address and may carry condition / sale fields; check Yonkers, Mount Vernon, New Rochelle code enforcement.
- Towns of Islip, Babylon, Huntington, Smithtown: look for their own ArcGIS servers with assessor layers like Brookhaven's.
- Nassau and Rockland as parcels-only entries from the NYS layer.
