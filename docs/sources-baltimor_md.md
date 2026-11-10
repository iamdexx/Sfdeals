# Baltimore (Baltimore County + Baltimore City) sources

Working, free, unattended:
- Baltimore County tax parcels: `bcgis.baltimorecountymd.gov/arcgis/rest/services/Property/Property/MapServer/1` (375k rows, maxRecordCount 1000
  so the config sets `page: 1000`). Fields: TAXPIN (10 digit SDAT account, the parcel id), PREMISE_ADDRESS, CITY, ZIP_CODE, OWNER_NA1/OWNER_NA2,
  ADDRESS_1/ADDRESS_2 + OWNER_CITY/OWNERSTATE/OWNER_ZIP (mailing), GIS_LU_CODE, YEAR_BUILT, TOTAL_VALUE, URL (per parcel SDAT link).
  Residential is `GIS_LU_CODE IN ('SFD','SFA','SFSD','RURAL RESIDENTIAL SFD')` (SFD 165k, SFA 69k, rural SFD 30k, SFSD 7k).
  Absentee pulled server-side with `ADDRESS_1<>PREMISE_ADDRESS OR OWNERSTATE<>'MD' OR OWNER_ZIP<>ZIP_CODE OR ADDRESS_1 IS NULL` (69.8k).
  The layer carries no sale date, no sale price, no homestead flag and no condition fields; the same TAXPIN can appear on several polygons
  (parcels.run dedupes by tag). MULTIFAMILY (19.6k, mostly apartment complexes) is left out.
- Baltimore County vacant property registry: `bcgisdata.baltimorecountymd.gov/arcgis/rest/services/Facilities/Facilities/MapServer/2`
  (673 rows, all APP_STATUS Active, filed 2023 to now, from code enforcement sweeps). TAXPIN matches the parcel layer. PROPERTY_TIER is
  "Tier 1 - No Violations" / "Tier 2 - Has Violations" / "Tier 3 - Dilapidated State, Structural Issues". PROPERTY_ADDR has an embedded
  newline and city line so it is not mapped as addr; the join is by TAXPIN only. Signal `where` drops `TAXPIN = 'NOT LOCATED'`.
- Baltimore City real property: `baltegis.baltimorecity.gov/mapping/rest/services/CityView/RealProperty_OB/FeatureServer/0` (237k).
  Parcel id is BLOCKLOT, an 8 character fixed width string: 5 char block padded with a space plus 3 char lot ("0001 003", "3836A010").
  PERMHOME is the SDAT principal residence flag (H = owner occupied 110k, N 127k, D 0.5k), USEGROUP 'R ' is residential (194k),
  NO_IMPRV = 'Y' marks vacant lots (22k). Pull: `USEGROUP LIKE 'R%' AND PERMHOME<>'H' AND NO_IMPRV IS NULL` (80.9k).
  MAILTOADD is one string "9726 MENDOZA RD RANDALLSTOWN, MD, 21133" or "2019 W NORTH AVE, 21217"; norm_addr strips the trailing zip and
  commas so owner occupied rows compare equal to FULLADDR, but mail_city / mail_state cannot be split out (no "out of state" flag for city
  rows). Value is TAXBASE (FULLCASH is 0 on 92% of rows). SALEDATE is a MMDDYYYY string, SALEPRIC is numeric, STRUCTAREA and YEAR_BUILD are often 0.
- Baltimore City DHCD open data, `.../Housing/DHCD_Open_Baltimore_Datasets/FeatureServer`: layer 1 Vacant Building Notice - Open (11.4k,
  OWNER_ABBR MCC/HABC/USA marks city, housing authority and federal owners, filtered out with `OWNER_ABBR IS NULL`, 10.2k left),
  layer 4 Receivership - Filed and Open (768, DateFiled 2001 to 2026, only 2 filed since 2023 so most are long running cases),
  layer 9 Open Work Orders (501, WorkOrderType Cleaning 478 / Boarding 23). All keyed by BLOCKLOT; 150 of 150 sampled ids matched the parcel layer.
- Baltimore City tax sale: `.../Housing/Tax_Sale_2026/FeatureServer/0` (4,342, Blocklot, Address, Owner, LIEN_AMOUNT). 24 city owned rows
  dropped with `Owner NOT LIKE 'MAYOR AND CITY%'`. `Tax_Sale_2025` (15.7k) is the prior year list and was not used.
- Baltimore City in rem: `.../Housing/In_Rem_Eligibility/FeatureServer/0` (32.6k eligible rows; InREM='Yes' 4.9k are properties the city is
  taking through in rem tax foreclosure; InRemStatu tells vacant lot vs VBN). Keyed by blocklot.
- Baltimore City code enforcement: `.../Housing/NoticesInspections/MapServer/0` "Open Inspection" (18.7k open or unfinished inspections,
  BlockLot, Address, CataDesc, DateInspection; 2.2k inspected in the last 10 days so it is live). Slow layer (5 to 10 s per page).
  The config keeps the housing categories (HCD Sanitation Property, Vacant Building, Maintenance Structure, General Inspection, Rodents,
  Systems, Trees and Shrubs, Space and Occupancy, CCE Violation Notice, Insects; 13.3k) and drops SEO signs / flyers / abandoned vehicle,
  extensions, re-inspections and receivership follow ups. 96 of 150 sampled BlockLots matched the parcel layer (the rest are lots or commercial).
- Property lookup: SDAT real property search `sdat.dat.maryland.gov/RealProperty/Pages/default.aspx`. Baltimore County is county 04, search
  by account with district = first two digits of TAXPIN and the full 10 digits as account number. Baltimore City is county 03, search by ward /
  section / block / lot. Deep links (`viewdetails.aspx?County=04&SearchType=ACCT&District=13&AccountNumber=...`) redirect scripts to a login
  page, so the UI links to the search page and shows the account.

Dead ends and gotchas:
- Maryland iMAP statewide parcels `mdgeodata.md.gov/imap/rest/services/PlanningCadastre/MD_ParcelBoundaries/MapServer/0` (2.29M, JURSCODE='BACO'
  303k) has OOI (owner occupied), RESITYP, YEARBLT, SQFTSTRC, TRADATE, CONSIDR1, NFMTTLVL and the owner mailing address, but NO owner name
  field, so it cannot drive lead cards or the cash buyer list. `geodata.md.gov` (no "md" prefix) returned a 503 maintenance page.
- Cash buyers: both parcel layers store the sale date as an 8 digit string (county has none at all), which `parcels.sale_date()` does not
  parse, so `buyers.json` is empty for this metro until that helper learns YYYYMMDD / MMDDYYYY. Parked, not a config fix.
- Baltimore County tax sale list (`baltimorecountymd.gov/departments/budfin/taxsale`) returns 403 to scripts; county code enforcement cases
  live in Accela "Code Enforcement Online" with no bulk layer. `Apps/RentalLicenses` and `Apps/MyNeighborhood` on bcgis have no violation layers.
- City Foreclosure Filings (DHCD layer 11, 14.1k) stops at Dec 2020; legacy `services1.arcgis.com/UWYHeuuJISiGmgXx` Tax_Sale (11.6k) is the
  2021 list; `V2Vreceiverships` uses an unpadded block lot ("3454010") that only matches 37 of 150 parcels. `911/Fire_CODEX_XRAY_UNSAFE_Building`
  (7.7k) is CAD premise hazards keyed by address text only, back to 2015. All skipped.
- `dmxPermitsCodeEnforcement/MapServer` has 30+ sublayers (citations, injunctions, illegal dumping) but the service metadata call failed; worth
  a retry for citation and litigation layers.

Next, not yet wired: Anne Arundel and Howard County parcels (both have ArcGIS servers, not checked), Baltimore County tax sale list,
city Tax_Sale_2027 when it is published (rename the layer in the config each spring), RPDELTAG codes on the city parcel layer (A/R/D/S, 148 rows).
