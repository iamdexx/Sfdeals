# Orlando (Orange County) sources

Working, free, unattended:
- Orange County GIS parcel layer `ocgis4.ocfl.net/arcgis/rest/services/AGOL_Open_Data/MapServer/56` (498k parcels, Property Appraiser data: `PARCEL` 15 digit id, `SITUS`/`SITUS_ZIP`/`SITUS_CITY`, `NAME1`/`NAME2` owners, `ADD1`-`ADD4`/`CITY`/`STATE`/`ZIP` mailing, `DOR_CODE`, `LIVING_AREA`, `AYB` year built, `BEDS`/`BATH`, `TOTAL_MKT` market value, `SALE_DATE` (ms epoch, 1900 placeholder when none), `SALE_ADJ_VALUE` sale price, `EXEMPT_CODE` homestead flag ('HX' or null), `TAXES`). Single family is `DOR_CODE LIKE '01%'` (352k: 0103 250k, 0104 42k, 0121 26k, 0100 15k). Pull is non-homestead or out of state, with a street number and not confidential (116k rows, about 2 minutes at 2000/page).
- Orange County Code Enforcement "Active Violations and Open Incidents" `AGOL_Open_Data/MapServer/53` (2,049 rows, unincorporated county only). `CE_OFFICIAL_PARCEL_ID` matches `PARCEL` exactly. `INCI_TYP`: Z zoning 1,050 (trailers, fences, pavers), H housing 592 (unsafe structure, burnout, roof, mold, unsecured), LOT 300 (grass, junk, trash), DMV 87 derelict vehicles, ONSS 27. We use H (weight 25) and LOT (15); Z and DMV are not distress. `INCI_ST_CD` A/E/I are all open; E cases go back to 2005. `INCI_DESC` is free text from the complaint and can be a paragraph, it is carried as `kind` on the card. Same data also at `InfoMap_Public_Layers/MapServer/2` (query errors 500, use layer 53).

Absentee is mail address vs situs (no `occ_field`: `EXEMPT_CODE` is a text flag and `occ_field` needs a number). 9k homestead parcels have a PO box or other mailing address and would read as absentee, but the `where` keeps homestead parcels out unless they carry a signal. `ADD1` is a "C/O" or trustee line on about 400 homestead parcels (then `ADD2` is the street), kept in `extra`.
Confidential owners (2,586) are excluded by the `where`.

Result on first run: 116k parcels, 884 signal rows, 592 hot (399 housing, 227 lot), 73k leads total, median hot value 272k, 2.5 minutes.

Links: Property Appraiser search `ocpaweb.ocpafl.org/parcelsearch` (Angular app, state is not in the URL, so the card links to the search page), Tax Collector `county-taxes.net/fl-orange?search_query=<parcel>` (Grant Street, 403 to scripts, fine as a browser link).

Dead ends:
- City of Orlando code enforcement is Socrata only: `data.cityoforlando.net/resource/k6e8-nw6w.json` (262k cases since 1990s, `parcel_id` 15 digit, `casetype` H/LOT/Z, `caseinfostatus` Open/Lien/ENF/CEB; today 609 open H, 384 H with lien, 535 open LOT, 3,014 LOT liens). No ArcGIS copy anywhere (`gis.orlando.gov/server`, cityoforlando.maps.arcgis.com, Hub). Needs a Socrata reader in `signals.py` to use; it would be the best signal in the metro.
- `InfoMap_Public_Layers/MapServer/30` Foreclosures: 71k rows but 2006-2013 only, dead data.
- OCPA own servers (`gis.ocpafl.org`, `maps.ocpafl.org`) return 503; the OCPA app API (`ocpa-mainsite-afd-standard.azurefd.net`) is behind a WAF.
- Orange County Tax Collector delinquent list and Comptroller tax deed sales (realtaxdeed) are not published as layers.

Next: Socrata reader for Orlando city cases (open H + lien), Orange County Comptroller lis pendens, Seminole County (second central county, scpafl.org) once a parcel service is found.
