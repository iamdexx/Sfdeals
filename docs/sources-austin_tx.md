# Austin (Travis County) sources

Working, free, unattended:
- Travis County GIS, TCAD parcel layer `gis.traviscountytx.gov/server1/rest/services/Boundaries_and_Jurisdictions/TCAD/MapServer/0` (389,622 parcels, max 1000 per page; `PROP_ID`, `geo_id`, situs parts, `py_owner_name`, `py_address`, `land_state_cd` / `land_type_desc`, `market_value`, `F1year_imprv` year built, `deed_date`, `hyperlink` to the appraisal district record). Single family is `land_state_cd = 'A1'` (291,309). Other codes: A2 mobile home 6k, B2 duplex 9.7k, C1 vacant lot 36k.
- Absentee is pulled server side: `py_address NOT LIKE CONCAT(situs_num,' %')` (mailing address does not start with the house number), 58,896 of the A1 parcels. The `+` concat and `CHARINDEX` return 400; `CONCAT()` works. Full pull is 57.5k rows in about 70 seconds.
- Signals are derived from the owner name (no separate layer): `ESTATE OF` (102 single family, pulled even when the mail still goes to the house, since the owner has died) and `LIFE ESTATE` with mail going elsewhere (about 250). `REAL ESTATE` and `ESTATES LLC` names do not match either rule.
- Tag is `PROP_ID` because the appraisal district record link needs it (`travis.prodigycad.com/property-detail/{PROP_ID}`).

Gotchas:
- `py_address` is one string, `street , city , state , zip , `. There are no separate mailing city, state or zip fields, so `mail` on the card reads `1217 PORTERFIELD DR AUSTIN TX` (zip dropped by the address normaliser) and the out of state flag is never set. 12,158 of the absentee A1 parcels have a mailing state other than TX (`py_address NOT LIKE '%, TX ,%'`); splitting `py_address` on ` , ` in `parcels.row()` would recover city, state and zip.
- Texas does not disclose sale prices, the layer has `deed_date` only, so `buyers.json` is empty (the buyer list needs a price of 10k or more).
- No living area on the layer; the real house test uses the year built.
- `situs_city` is blank on many rows; `situs_zip` is reliable. Blank `situs_num` rows (1.4k) are excluded with `situs_num > '0'`.
- `imprv_homesite_val` is not a homestead flag (only 12.8k A1 parcels have 0), and `land_homesite_val` is filled on commercial parcels too. Do not use them for owner occupancy.
- The sibling layers `TCAD_public/MapServer/0` and AGOL `TCAD_Parcels_Dec_2025` have no owner or value fields. City of Austin `EXTERNAL_tcad_parcel` has geometry and land value only.

Parked, best next step:
- City of Austin code complaint cases are on Socrata, not ArcGIS: `https://data.austintexas.gov/resource/6wtj-zbtb.json` (82,530 cases, updated daily, newest opened 2026-11-09; `status`, `description` such as Property Abatement / Structure Condition / Work Without Permit, `address`, `parcelid`, `repeatoffenderrelated`, `violationcasenumber`). `parcelid` is the 10 digit TCAD `geo_id` (for example `0219380702`), not `PROP_ID`, so join on `geo_id` or on the address. The generic signal puller only speaks ArcGIS REST, so this needs a small Socrata reader in `signals.py`. It would be the main distress signal for this metro.
- The ArcGIS copy `services.arcgis.com/0L95CJ0VTaxqcmED/.../Austin_Code_Complaint_Cases/FeatureServer/0` is stale (2,762 rows, 2009 to 2020, last edit 2020-11) and its `PARCELID` has the leading zero stripped. Not used.

Dead ends:
- Texas statewide StratMap parcels `feature.geographic.texas.gov/arcgis/rest/services/Parcels/stratmap_land_parcels_48_most_recent/MapServer/0` has split mailing fields and `stat_land_use`, but every `/query` returns 400 "Requested operation is not supported" (map display only).
- No delinquent tax, tax sale, foreclosure or vacant building layer found on the Travis County server, the county AGOL org (`services1.arcgis.com/HGcSYZ5bvjRswoCb`) or the City of Austin AGOL org and `maps.austintexas.gov`. `Shared/Permits` has demolition permits, which in Austin mean a teardown for a new build, not distress.

Next:
- Socrata reader for the code cases above (and the repeat offender flag).
- Travis County Tax Office tax sale lists and County Clerk foreclosure notices (posted for the first Tuesday sale); not checked for format or terms yet.
- Williamson County: `publicdata.wcad.org/arcgis/rest/services/Sidwell/WCADTXCadastral/MapServer/49` (WCAD parcels, found on ArcGIS Hub, fields not checked). Hays County not searched. City of Austin `EXTERNAL_wcad_parcel` and `EXTERNAL_hcad_parcels` carry no owner data.
