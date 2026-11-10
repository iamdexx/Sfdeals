# San Diego (San Diego County) sources

Status: parcels only. No public distress layer (tax, code, foreclosure) that joins to parcels was found, and California does not publish owner names. Hot leads come from two rules on the parcel record itself: single family house, no homeowner exemption, and no deed recorded since before 1990 (weight 30) or since the 1990s (weight 20).

Working, free, unattended:
- SanGIS parcels (County Assessor MPR/PAR data), countywide, 1,088,564 rows. Used copy: City of San Diego `webmaps.sandiego.gov/arcgis/rest/services/DoIT_Public/DoIT_Public/MapServer/4` ("Parcels All", 2000 per page, pagination works). Fields: `APN` (10 digits, no dashes), `PARCELID`, situs parts (`SITUS_ADDRESS` number, `SITUS_PRE_DIR`, `SITUS_STREET`, `SITUS_SUFFIX`, `SITUS_POST_DIR`, `SITUS_ZIP`, `SITUS_COMMUNITY`), `OWNEROCC` ('Y' = homeowner exemption on file, otherwise null), `TAXSTAT` (T taxable, N not), `ASR_LANDUSE` (11 = single family, 12 duplex, 13 = 2-4 units, 17 condo, 10 vacant residential), `NUCLEUS_USE_CD` (finer 3 digit use), `UNITQTY`, `TOTAL_LVG_AREA`, `BEDROOMS`, `BATHS`, `ASR_LAND`, `ASR_IMPR`, `ASR_TOTAL`, `DOCTYPE`, `DOCNMBR`, `DOCDATE` (last recorded deed, text `MMDDYY`), `YEAR_EFFECTIVE` (2 digits).
- Counts: single family 571k; single family with no exemption, taxable, with a street number and living area 206,114; of those, last deed in the 1950s-1980s 1,889 and in the 1990s 5,009. Full run takes about 10 seconds; result 6,880 hot of 6,898, median assessed value about 198k.

Gotchas:
- No owner name, no mailing address, no sale price anywhere in the public layers (SanGIS strips them). The engine drops parcels with an empty owner, so `owner` is mapped to `APN`: the card shows the parcel number where the owner name would be. The cash buyer list is empty for the same reason. A real fix needs an engine change (allow a missing owner) or a paid owner source.
- `occ_field` in the engine only understands numbers, so `OWNEROCC` ('Y'/null) always reads as not owner occupied. That is correct here only because the `where` already keeps `OWNEROCC IS NULL` and there are no signal layers that fetch other parcels by id. If a signal layer is added later, the engine must learn 'Y'/'N' first or owner occupied homes will be flagged absentee.
- No exemption is not proof of absentee: some owners who live in the house never filed. Expect some owner occupied homes in the list.
- The derived rules can only test a field for presence, so the config lists the county twice with different `where` clauses (1950s-80s, 1990s) and a different `extra` field each (`DOCDATE`, `DOCNMBR`) to tell the two groups apart. The signal `value` on 1990s leads is therefore the document number, not a date.
- `ASR_TOTAL` is the Prop 13 assessed value. For long-held houses it is far below market (28k to 300k on houses worth 700k+), so `min_value` is 20000 rather than the usual 40000+; 18 of 6,898 fall under it.
- SANDAG's own copy `geo.sandag.org/server/rest/services/Hosted/Parcels/FeatureServer/0` has the same data with lowercase field names, but the engine orders by `OBJECTID` and that server answers "Field name 'OBJECTID' does not exist. Did you mean 'objectid'?". Do not use it until the engine's order field is configurable.
- County copy `gis-public.sandiegocounty.gov/arcgis/rest/services/cosd_warehouse/parcels_all_for_public_use/MapServer/0` has only APN, situs and acreage.
- No verified deep link to a parcel on the Assessor or Tax Collector sites, so `lookup` shows the APN and links to both search pages.

Dead ends:
- County tax sale `gis-public.sandiegocounty.gov/arcgis/rest/services/Hosted/taxsalepointsVIEW/FeatureServer/0` (401 rows, APN matches): 388 timeshares and 13 unimproved lots, no houses.
- City code enforcement `webmaps.sandiego.gov/arcgis/rest/services/DSD/Operational/MapServer/1` (18,329 polygons): only `PARCEL_POL` and `JOB_LOC_ID`, `CASE_RECORD` always null, no address, type, status or date. `PARCEL_POL` does not match SanGIS `PARCELID` (checked coordinates on three).
- City open data CSV `seshat.datasd.org/code_enforcement_violations/code_enf_past_3_yr_datasd.csv` (22k rows with APN): legacy system, newest case opened 2018-01-09. Also a CSV, which the engine cannot read.
- City `GetItDone`, `GetItDone311`, `PandA`, `CoSD_Parcel_Changes` folders need a token.
- ArcGIS Hub and ArcGIS Online searches for code enforcement, vacant, notice of default and tax defaulted layers for San Diego, Chula Vista, Oceanside, Escondido and El Cajon returned nothing usable.

Next:
- Notices of default and trustee sales (non-judicial state): County Recorder index has no free API found yet; check trustee sale posting sites whose terms allow it.
- County Treasurer-Tax Collector tax defaulted list beyond the auction layer (a PDF or CSV may be posted before each sale).
- City of San Diego current code cases (Accela): ask for an open data export or find a public layer.
- Engine: owner optional, 'Y'/'N' `occ_field`, configurable order field, numeric and date rules in `derived` (would let one county entry score by years held and add 2-4 unit houses).
