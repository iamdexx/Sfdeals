# Portland, OR sources (Multnomah County)

Metro key `portland_or`. Principal county Multnomah; principal city Portland. Config: `sfdeals/metro/configs/portland_or.json`.

## Working sources

### Parcels: Multnomah County Taxlot Parcels (assessor roll)
- URL: `https://services5.arcgis.com/x7DNZL1YqNQVNykA/arcgis/rest/services/Multnomah_County_Taxlot_Parcels_DEV/FeatureServer/0`
- Public hosted FeatureServer on Multnomah County's ArcGIS Online org (also the source of the county's ArcGIS Hub "Multnomah County Taxlot Parcels" item). 284,463 rows total, 180,484 with `IMPTYPE='SFR'`.
- Pull where: `IMPTYPE IN ('SFR','DPX','TPX','FPX','ROW','MFG') AND (STATE <> 'OR' OR SUBSTRING(ZIP,1,5) <> SITUSZIP OR ZIP IS NULL OR ZIP = '')` = 34,473 rows, about 20 seconds.
- Fields: `PROPID` (tag, "R186993"), `ALTACCTNUM` (long account "R512005550", what the city and county code lists use), `NAME`/`NAME2` owner, `ADDR1`/`ADDR2`/`CITY`/`STATE`/`ZIP` mailing (zip is ZIP+4, handled by `SUBSTRING`), `SITUSADDR`/`SITUSCITY`/`SITUSZIP` situs, `IMPTYPE` improvement type (SFR, DPX, TPX, FPX, ROW, MFG, CONDO, APT, COMM...), `PROPCLASS` (101 = residential improved), `UNITS`, `ACTYEARBUILT`, `MAIN_SQFT`, `ROLLLAND`/`ROLLIMP` (real market value split), `ROLLM50` (Measure 50 assessed value), `SALE_DATE`/`SALE_PRICE` (epoch ms, 0 when none), `DEED_TYPE`/`DEED_DATE` (last deed), `EXEMPTION`.
- Gotchas:
  - The non-DEV twin `Multnomah_County_Taxlot_Parcels/FeatureServer/0` has the same data but its object id field is `OBJECTID_1`, so our pager's `orderByFields=OBJECTID` fails on it. The DEV layer has `OBJECTID` and the same 284k rows; if it disappears, switch the url to the non-DEV layer and fix the pager's order field.
  - `value` is `ROLLM50`, the Measure 50 assessed value, which runs well under market (median hot lead 227k vs typical Portland RMV 450k+). RMV is split across `ROLLLAND` + `ROLLIMP` and the mapper takes one field. `min_value` 80000 on M50 still drops lots and shells.
  - The query parser rejects `LEFT()` and `TRIM()`; `SUBSTRING()` works.
  - No homestead or owner-occupied flag in Oregon (no homestead exemption), so absentee is mail vs situs only.
  - `SITUSADDR` has a trailing space; our normalizer strips it.

### Derived signals from the parcel row (deed type)
- `DEED_TYPE` on SFR-type parcels, deeds since 2023-11: PRD/PR/AFFD (estate) 1,946 on all SFR, QCD/QC/QD (quit claim) 2,340, TRD/SHD/TD/JUD (trustee, sheriff, judgment) 497. On the absentee pull: estate 189, quit claim 470, foreclosure deed 59.
- Distribution of all deed types on the layer: WD 176k, BSD 50k, INST 13.5k, QCD 11.8k, SWD 10.5k, PRD 5.6k, TOD 2.8k, DECR 2.3k. `TOD` is a transfer on death deed recorded by a living owner (estate planning), not a death event, so it is not used.

### Signal: Multnomah County Code Compliance Backlog
- URL: `https://services5.arcgis.com/x7DNZL1YqNQVNykA/arcgis/rest/services/CodeComplianceBacklog/FeatureServer/0`
- 172 open county (unincorporated) code cases. Fields `CASE_`, `ALTACCNUMBER` (long R account, matches `ALTACCTNUM` not `PROPID`, so the scorer joins by address), `SITEADDRESS`, `CITY`, `PRIMARYCOMPLAINT` (NP- DWELL 64, NP- DEV 51, COMM 26, GEC 16, MISC 8), `COMPLAINTPRIORITY`, `COMPLAINTRECEIVEDDATE`, `STATUS_1`, `TOTALYEARSMONTHS`.
- Cases are old (some from 2001-2004) and many are commercial or non-permitted development; 32 landed on residential absentee parcels. Weight 15.

### Lookup
- `https://www.portlandmaps.com/detail/property/{PROPID}_did/` works for every Multnomah parcel (city or not).

## Results (first run)
- `portland_or score (750, 33958)`, 22 seconds. Median hot lead value (M50) 226,715. Signals: quit claim 470, estate 189, foreclosure deed 59, county code case 32.
- Buyers: 80 repeat buyers; Rose City Fund LLC, Opendoor entities, LCRE Holdings, Platinum Group LLC.

## Parked: Portland city code enforcement (PDF, not ArcGIS)
- `https://www.portland.gov/ppd/code-enforcement/open-code-enforcement-cases` publishes "Current open housing and dangerous building cases" as a PDF (`https://www.portland.gov/ppd/documents/current-open-housing-and-dangerous-building-cases/download`), refreshed monthly. 767 cases (about 751 HS housing, 55 DB dangerous building), columns NUM PREFIX STREET PARCEL CASENO STARTDATE, parcel is the long R account (`R056801290` = `ALTACCTNUM`). Public, no login.
- Not wired because `signals.py` only pulls ArcGIS layers and the playbook forbids shared code changes. Best next signal for this metro: a 20 line PDF to signals step (pypdf, regex `R\d{9}`), weight 25 for HS and 45 for DB, joined on `ALTACCTNUM`.
- `CodeComplianceBacklog` above is the county's, not the city's.

## Dead ends
- `https://gis.multco.us/arcgis/rest/services` returns nothing public.
- `multcoproptax.com` property detail (`/Property-Detail/PropertyQuickRefID/R...`) redirects to an error page without a session; use PortlandMaps for lookup.
- Multnomah tax foreclosure pages on multco.us returned 520/404 during this run; the county only publishes the foreclosure list as a yearly web page anyway.
- PortlandMaps `Public/Taxlots/MapServer/0` (regional, 607k rows, Multnomah 243k) has owner and situs but Multnomah rows carry `LANDUSE='RP R'` (no building type), `PRPCD_DESC` mixed, no deed type. Washington County rows (`COUNTY='W'`, `LANDUSE='SFR'`) have `TOTALVAL3=0` and owner names prefixed `zzzz`, so not usable for values or buyers.
- PortlandMaps `BDS_Property` and `COP_OpenData_Property` services: no better parcel source; `FeatureServer` variants of portlandmaps MapServers are not enabled.
- Portland residential demolition permits exist at `https://www.portlandmaps.com/od/rest/services/COP_OpenData_PlanningDevelopment/MapServer/126` but are permits pulled by developers after purchase, not distress.

## Next
1. Portland HS/DB open cases PDF (above) once a PDF signal step exists.
2. Portland Housing Bureau rental registration and the city's vacant/derelict building list (Chapter 29 enforcement) if an open data layer appears on `portlandmaps.com/od`.
3. Second county: Clackamas (`https://gis.clackamas.us/arcgis/rest/services` or ArcGIS Hub) and Washington County GIS (`https://gisportal.washingtoncountyor.gov/`), both have their own ArcGIS servers worth probing. Clark County WA (`gis.clark.wa.gov`) would need a WA-specific absentee filter.
4. Multnomah tax foreclosure list (annual) is a web page only.
