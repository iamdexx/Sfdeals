# Miami (Miami-Dade County) sources

Working, free, unattended, all ArcGIS hosted layers on Miami-Dade's open data org `services.arcgis.com/8Pc9XBTAsYuxx9Ny`:

- Property Appraiser point layer `PaGISView_gdb/FeatureServer/0` (944k folios, 2000 per page, nightly refresh). Fields: `FOLIO` (13 digits),
  `TRUE_SITE_ADDR_NO_UNIT`, `TRUE_SITE_CITY`, `TRUE_SITE_ZIP_CODE` (padded `33136-0000`, we keep 5), `TRUE_MAILING_ADDR1/CITY/STATE/ZIP_CODE/COUNTRY`,
  `TRUE_OWNER1..3`, `DOR_CODE_CUR`, `UNIT_COUNT`, `BUILDING_HEATED_AREA`, `YEAR_BUILT`, `ASSESSED_VAL_CUR`, `DOS_1` (string `YYYYMMDD`),
  `DATEOFSALE_UTC` (ms epoch, what we use), `PRICE_1`. Single family is `DOR_CODE_CUR LIKE '01%'` (385k).
  Pull: single family and (mailing state not FL, or mailing zip differs from site zip, or mailing street differs from site street), 170k rows,
  about 4 minutes. Site and mailing street lines are both in the appraiser's own format (`460 NW 10 ST`) so the client side mail vs addr
  compare is clean.
- Building department open cases `Open_Building_Violations/FeatureServer/0` (25k open, keyed by `FOLIO`): `CASE_TYPE = 'Unsafe Structure'` (3.1k)
  and `All Other Code Violations` opened 2020 or later (11k). Also has `Expired Permit` (7k, not used) and `Boilers`.
- Code compliance cases `CCVIOL_gdb/FeatureServer/0` (179k cases since 1996, `FOLIO` padded with trailing spaces, stripped on load). `STAT_DESC`:
  Open 9.4k, Lien 7k, Referred to Internal Compliance (unpaid fines in collections) 15k, Civil, Active LP, Closed 147k. Used: Lien since 2015 (3k),
  Referred since 2022 (3.6k), Open foreclosure registry cases (`PROBLEM_DESC LIKE '%Foreclos%'`, 260), Open Minimum Housing / Structure
  Maintenance (150), Open Junk/Trash/Overgrowth and Abandoned Property (1.5k). Filtered views of the same table exist
  (`CodeComplianceViolation_Open_View`, `_Lien_View`, `_ReferredtoFinance_View`, `_Civil_View`).

Gotchas:
- The hosted appraiser view has no homestead or just value fields. The county's own server `gisweb.miamidade.gov/arcgis/rest/services/MD_EAMSCodeEnforcement/MapServer/2`
  (PaGis) has everything (`HSTEAD_EX_VAL_CUR`, `TOTAL_VAL_CUR`, `QU_FLG_1`, grantor and grantee, 1000 per page, 93k non homestead single family) but
  its only sale date is the `YYYYMMDD` string, which `parcels.sale_date` does not parse, so cash buyers would be empty. We use the hosted view;
  value shown is the assessed value (capped at 10 percent a year for non homestead, so long held rentals show under market).
- The hosted view accepts standardized SQL in `where` (`SUBSTRING`, field to field compares, `DATE '2015-01-01'`).
- Code compliance and building cases cover unincorporated Miami-Dade plus the cities the county inspects for. City of Miami folios (prefix `01`)
  barely appear (36 unsafe structure cases, 251 open code cases); Hialeah, Miami Beach, Coral Gables run their own code departments.
- Hub also lists `EnergovCodeCasePublicView` (13.6k county EnerGov cases): mostly consumer protection (towing, licensing), not property distress. Skipped.
- Miami-Dade has no deed type on the parcel record, so no estate / quit claim derived rules like Tampa.

Dead ends:
- City of Miami code compliance cases are in Accela (iBuild / Code Compliance portal); no open layer. `maps.miamigov.com/arcgis01` does not answer.
  The city's AGOL org (`services1.arcgis.com/CvuPhqcTQpZPT9qY`) only has code enforcement zones, offices and sectors.
- Tax Collector delinquent list is on `miamidade.county-taxes.com` (Grant Street), no public export. Tax deed sales are on RealAuction.
- Clerk lis pendens search is session based, no API.

Next: City of Miami code cases if the city ever publishes them, Clerk lis pendens, tax certificate list, Broward County (second county) which has
a BCPA parcel layer and Fort Lauderdale code compliance on `gis.fortlauderdale.gov`.
