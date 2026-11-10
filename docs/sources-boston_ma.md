# Boston (Middlesex County towns + City of Boston) sources

Working, free, unattended:
- MassGIS statewide assessor table `arcgisserver.digital.mass.gov/arcgisserver/rest/services/AGOL/MassachusettsPropertyTaxParcels/FeatureServer/4` (`GISDATA.L3_ASSESS`, 2,553,985 rows statewide; owner, mailing address, `USE_CODE`, `TOTAL_VAL`, `YEAR_BUILT`, `RES_AREA`, `LS_DATE`, `LS_PRICE`). Filter to Middlesex County with `TOWN_ID IN (...)` (54 towns; ids come from the MassGIS municipalities layer). Single family is `USE_CODE LIKE '101%'` (towns write 101, 1010, 1013...). The pull is out of state mailing, or estate / heirs in the owner name, or a mailing street that differs from the situs street: 19,491 rows, about 15 seconds. Parcel id is `MA_PROP_ID` (`M<town>_<local id>`).
- City of Boston FY26 assessing layer `gisportal.boston.gov/arcgis/rest/services/Assessing/PROPERTY_ASSESSMENT_PARCEL_JOIN_FY26/FeatureServer/0` (184,548 rows; `PID`, `LU`, `OWN_OCC`, `OVERALL_COND`, mailing address, `TOTAL_VALUE`, `YR_BUILT`, `LIVING_AREA`). Listed as "Suffolk County" in the config; it is Boston only. `LU IN ('R1','R2','R3')` is 1 to 3 family houses. The pull is not owner occupied, or out of state, or condition Poor / Fair: 14,431 rows.
- Boston 311 cases opened in the last 30 days `gisportal.boston.gov/arcgis/rest/services/Live/lagan_311_cases_opened_past_30_days/FeatureServer/0` (about 2,700 rows; `parcel_num` is the same 10 digit id as the assessor `PID`, `land_usage` matches `LU`). This is the city's code enforcement intake (Inspectional Services). Used for three signals: abandoned building, unsafe building, housing complaint. 127 cases on 1 to 3 family parcels on the test day.

Signals in the leads on the test run (680 hot of 32,625): condition fair 509, housing complaint 73, estate 32, condition poor 27, heirs 26, unsafe 11, abandoned 5. Median value of hot leads $701,650.

Gotchas:
- MassGIS `LS_DATE` is a text field in `YYYYMMDD` form on every MassGIS parcel service. `parcels.sale_date()` does not read that form, so sale dates are blank and the cash buyer list is empty. Reading 8 digit dates in `sale_date()` would turn buyers on for every Massachusetts metro. Boston's layer has no sale fields at all.
- MassGIS has no owner occupied flag. Absentee is mailing street vs situs street. The `where` drops rows where the mailing address starts with the same house number in the same town, which removes spelling variants (`62 SECOND ST` vs `62 2ND ST`). A few owner occupants who use a PO box still come through as absentee.
- Boston mailing addresses often drop the street suffix (`41 NIXON` for `41 NIXON ST`). The `where` handles this for the main pull, but an owner occupied house fetched because it has a 311 case can still show as absentee (6 of 680 on the test run). `OWN_OCC` is Y/N text, so `occ_field` (numeric) cannot use it.
- `OWN_OCC = 'N'` means no residential exemption, the closest thing to a homestead flag here.
- The 311 layer is a rolling 30 day window, so the signals are fresh but thin. Many cases are tenant complaints about a landlord, which is the point.
- MassGIS town data is 1 to 3 years old depending on the town (see `FY`).
- The MassGIS server returns a 400 if the `where` nests too many expressions. Keep it flat.

Dead ends:
- Middlesex County has no county government, assessor or GIS. Everything is town by town or MassGIS.
- Boston structure violations `services.arcgis.com/sFnw0xNflSi8J0uh/.../Structure_Violations_Map_WFL1/FeatureServer/0` (26,239 rows): last edited 2023, keyed by address and `sam_id`, not parcel. Too old.
- Boston tax title `.../TaxTitleNewDATA/FeatureServer/0` (5,227 rows, has `ParcelID`): last edited 2016. Too old.
- Cambridge Housing Code Violations (Socrata `f8su-kv88` on data.cambridgema.gov, updated daily): good data, but Socrata, not ArcGIS, and address only. Needs a Socrata signal loader.
- Lowell, Somerville, Newton, Framingham ArcGIS servers: no public code enforcement or tax layers found.
- masslandrecords.com (registry of deeds, lis pendens, foreclosure deeds) blocks scripts.

Next:
- Teach `sale_date()` the `YYYYMMDD` form to get cash buyers.
- A Socrata / CKAN signal loader would add Cambridge housing violations and Boston's CKAN sets on data.boston.gov (code enforcement building and property violations, updated daily).
- Add Essex, Norfolk and Plymouth towns: same MassGIS table, just more `TOWN_ID`s. Add 2 and 3 family (`USE_CODE` 104, 105) for the towns.
- Town tax title lists (Lowell, Cambridge) are PDFs published once a year.
