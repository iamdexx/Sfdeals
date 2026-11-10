# Las Vegas, NV (Clark County) sources

Metro key `lasvegas_nv`, config `sfdeals/metro/configs/lasvegas_nv.json`. One county (Clark) and one city (Las Vegas) for now.

## Parcels: Clark County Assessor extract (county GIS)

`https://maps.clarkcountynv.gov/arcgis/rest/services/GISMO/Address/MapServer/2` (layer `AOEXT_V`, Clark County GIS Management Office).
867,384 rows county wide, `maxRecordCount` 1000 (config sets `page: 1000`), supports pagination, statistics and standardized SQL expressions.

- `landuse = '110'` is single family residential: 596,439 parcels. Las Vegas 170,852, Henderson 103,903, North Las Vegas 74,950,
  Enterprise 74,886, Spring Valley 50,066, Sunrise Manor 37,651, Paradise 30,526, the rest in Summerlin, Whitney, Mesquite, Boulder City...
  Other codes seen: 160 condo/townhouse (53,760), 100 vacant residential (22,124), 150 mobile home, 140 fourplex, 185 PUD. Not pulled yet.
- Fields used: `APN` (11 digits, no dashes, same as the assessor web site), `strno strdir strname strtype` (situs, padded with spaces, `pick()`
  strips them), `City` (full name, e.g. `LAS VEGAS`, `HENDERSON`, `SUNRISE MANOR`), `owner`, `owner2` (second owner or trustee line, kept in
  `extra`), `MAIL_ADDRESS1` (mailing street line only), `TOTVAL`, `CONSTYR`, `DOCDATE` (`YYYY-MM-DD`), `SALEPRICE`, `CAPACITY` (units),
  `DOCVEST` (vesting code NS/JT/RS...), `STATELANDUSE` (`20.110` built house, `26.110` lot under construction).
- Absentee filter is a server side SQL expression, the layer has no mailing zip or homestead flag:
  `MAIL_ADDRESS1 NOT LIKE CONCAT(CAST(strno AS VARCHAR(10)), ' %')` keeps parcels whose mailing street number differs from the situs number.
  158,965 rows (27% of houses). Checked 20 rows on both sides: owner occupied homes have `MAIL_ADDRESS1` equal to the situs line, so the
  `mail != addr` test in `score.py` agrees with the filter. Owners whose mailing house number happens to match on a different street are missed
  (rare). The expression works with POST + `resultOffset` paging as `stl.arcgis()` sends it; it fails on `returnDistinctValues` queries.
- `TOTVAL` is Nevada assessed value, 35% of taxable value, so a 100k TOTVAL house is worth roughly 285k on the tax roll. `min_value` 30000
  (about 85k taxable) drops lots, shells and the `26.110` under construction rows that have `TOTVAL` under 3000 and no `CONSTYR`.
- No situs zip, mailing city, state or zip in this layer, so `zip`, `mail_city`, `mail_state`, `mail_zip` are blank and "out of state" never fires.
  `MAIL_ADDRESS2` and `MAIL_ADDRESS3` are blank on 99.9% of houses.
- Values with living area are not published; `CONSTYR` is the "real house" test.

### Parcel layers checked and not used

- `https://services1.arcgis.com/F1v0ufATbBQScMtY/arcgis/rest/services/CC_PARCELS_SHP/FeatureServer/1` (City of Las Vegas copy of the county
  roll, 841,426 rows, updated 2026-11-05, `maxRecordCount` 2000). Has `ZIP` (situs) and `ZIPCODE`/`ZIPMAIN` (mailing) so a
  `ZIPCODE/10000 <> ZIP` filter works (150,337 houses), and `ADDRESS2` carries "CITY ST ZIP". Rejected because `ADDRESS1` is the second
  owner or trustee name on 242,233 of 595,912 houses (the mailing street is then in `ADDRESS2`), which would mark 40% of owner occupied
  homes absentee; it has no total value (`IMPVAL` + `LANDVAL1` only), and `SALEDATE`/`DOCDATE` are `YYYYMMDD` strings that `parcels.sale_date()`
  does not parse, so cash buyers would be empty. `SALETYPE` here looks useful: `T` rows are trustee (foreclosure) sales to banks and flippers,
  `F` looks like a normal financed sale. Worth a `derived` rule if `parcels.py` learns `YYYYMMDD` dates.
- `https://services1.arcgis.com/F1v0ufATbBQScMtY/arcgis/rest/services/parcels/FeatureServer/0`: same schema, City of Las Vegas only (302,403).
- `https://maps.clarkcountynv.gov/arcgis/rest/services/GISMO/...` other folders are zoning, addresses and points of interest, no assessor fields.

## Signals: City of Las Vegas code enforcement

`https://services1.arcgis.com/F1v0ufATbBQScMtY/arcgis/rest/services/Code_Enforcement_Open_Data/FeatureServer/0` (City of Las Vegas Office of GIS).
28,505 rows, 9,357 with `STAT = 'Open'` on 1,290 distinct parcels, data edited 2026-11-09. Fields: `Event_Date` (epoch ms), `STAT`, `WARD`,
`DESCRIPT` (code section + short text), `ADDRESS`, `Parcel_Number` (11 digit integer, matches `APN` once stringified), `LAT`, `LONG`.
One row per violation, so a parcel with 5 violations is 5 rows. City of Las Vegas limits only (Henderson, North Las Vegas and
unincorporated Clark County are not in it).

Gotcha: `maxRecordCount` is 1000 and `signals.py` asks for 2000 per page, so any signal with more than 1000 rows is silently cut at 1000.
Every signal below is kept under 1000 rows by splitting on description and date. Re-check the counts when the layer grows.

| signal | weight | where | rows | parcels |
|---|---|---|---|---|
| danger | 40 | Open and DANGEROUS BUILDING, VACATE, DEMOLI, UNSAFE, IMMINENT HAZARD, CONDEMN | 874 | 176 |
| housing | 25 | Open and `HC-%` housing code sections, DILAPIDAT, SUBSTANDARD (minus the danger terms) | 867 | 190 |
| junk | 15 | Open since 2024-01-01 and REFUSE, STORED MATERIALS, VEGETATION, LITTER, WEEDS | 860 | 158 |
| nuisance | 15 | Open since 2024-01-01 and GENERAL NUISANCE, ATTRACTIVE NUISANCE, GRAFFITI, INOP, JUNK, ABANDONED VEH | 486 | 106 |

Most common open descriptions: `UAC 301.1 PERMITS REQUIRED` (not used, permit paperwork), `9.04.010 (4) REFUSE & WASTE` 791,
`9.12.030 STORED MATERIALS` 422, `9.04.010 (9) GENERAL NUISANCE` 320, `9.04.010(9)(A) HIGH VEGETATION` 280, `9.04.010 (9)(D) DILAPIDATED` 255,
`9.04.010 (5) ZONING VIOLATION` 243 (not used), `HC-1001.2 GEN DILAPIDATION` 177, `9.04.010 IMMINENT HAZARD` 145,
`HC-SEC 1103 VACATE ORDER` 120, `LVMC 16.08.010 2022 DANGEROUS BUILDING CODE SECTION 403` 106. Open cases run from 2015 to late 2024;
nothing dated 2025 or later carries `STAT = 'Open'`, so the layer may lag a year behind the city's Accela system.

## Parked (found, not wired)

- `.../Parcel_Foreclosures/FeatureServer/0` (City of Las Vegas): 1,925 recorder notices (`NOTICE OF TRUSTEE SALE` 745, `BREACH & ELECTION TO SELL`
  535, `BREACH` 358, `DEFAULT & ELECTION TO SELL` 287) with `ParcelNumber`, `RecordDate`, `DocTypeDescription`. All records are 2020-01-02 to
  2020-09-11, a one time extract. Would be a 45 weight pre-foreclosure signal if the city refreshes it.
- `.../ABANDONED_PROPERTY_REGISTRY/FeatureServer/0` (413 rows, `PRCLID`, `ADDRESS`, `OWNERNAME`, `APNO` like `FR21-...`) and
  `.../ABANDONED_PROPERTY_UNREGISTERED_LOCATIONS/FeatureServer/0` (466 rows): city abandoned property registrations, last edited 2022-09.
  `.../AbandonedPropertySurvey/FeatureServer/0` (255 rows, `Vacant`, `Secure`, `FireDmg`, `Resolved`) mixes resolved and test rows.
  All three are 3 to 4 years stale; add the registry as a 20 weight vacant signal if it gets a refresh.
- Clark County Treasurer: property tax search is a web form at `https://trweb.co.clark.nv.us/` with no public layer or bulk file found.
  The annual tax sale (trustee auction of tax delinquent parcels, usually April) is published as a PDF list on the treasurer page;
  no ArcGIS Hub dataset for Clark County NV delinquent tax exists (Hub search returns other states' Clark counties).
- Clark County Recorder: document search is a web application, no REST layer.

## Dead ends

- `gis.clarkcountynv.gov`, `gisgate.co.clark.nv.us`: no REST endpoints. `maps.clarkcountynv.gov/arcgis/rest/services` is the live server.
- Henderson (`maps.cityofhenderson.com/arcgis/rest/services`, `gis-hendersonnv.opendata.arcgis.com`): public folder has zoning, boundaries,
  master plans; no code enforcement or vacant property layer. North Las Vegas has no public ArcGIS server found and no Hub datasets beyond
  city limits and zoning. Unincorporated Clark County code enforcement (Enterprise, Spring Valley, Sunrise Manor, Paradise) not published.
- ArcGIS Hub searches for "Clark County Nevada code enforcement" and "... tax delinquent" return nothing for Nevada.

## Look for next

1. Henderson and North Las Vegas code enforcement (Accela or Socrata exports) to cover 180k more houses.
2. Clark County Treasurer tax sale list (PDF) parsed to parcel numbers, weight 45.
3. A refreshed `Parcel_Foreclosures` or a Recorder notice of default feed (Nevada trustee sales move fast, 4 months from NOD to sale).
4. Add `landuse` 160 (condo/townhouse) and 150 (mobile home) once the single family list is working.
5. If `parcels.py` learns `YYYYMMDD` dates, switch to `CC_PARCELS_SHP` for `ZIP`, mailing zip and `SALETYPE = 'T'` trustee sale derived signal,
   using `ADDRESS2`/`ADDRESS3` rules for the c/o rows.

## First run (2026-11-10)

`python -m sfdeals.run lasvegas_nv all`: 8m50s. 3,086 signal rows (danger 874, housing 866, junk 860, nuisance 486), 159,291 parcels pulled
(158,965 absentee filter + signal parcels fetched by id), `score (334, 157870)`. Hot leads by signal: housing 160, danger 148, junk 101,
nuisance 75; 121 of the 334 hot leads are owner occupied (mail equals situs, no absentee tag), the rest absentee. Median hot `value` (assessed)
80,985, about 230k taxable. All hot leads are inside the City of Las Vegas because that is where the only signal layer lives.
Cash buyers: 150 entities with 2+ buys in 18 months (Opendoor, Better Assets, Neighbor to Neighbor Homes, Alpha Investment Group...).
