# Sacramento, CA (sacramen_ca) sources

Metro: Sacramento-Roseville-Folsom. Shipped county: Sacramento County only. Signals are all `derived` rules on the parcel layer (no separate distress layer is pullable yet). Placer and El Dorado are parked (see bottom).

## Working

### Sacramento County GIS parcel base (parcels)
- `https://mapservices.gis.saccounty.gov/arcgis/rest/services/PARCELS/MapServer/8` ("Active GIS Parcel Base", county-run ArcGIS, no key, 2000 rows a page).
- 509,292 parcels. `LANDUSE LIKE 'A1%'` (single family, A1xxxx codes) = 423,806. With the absentee filter
  `MAILING_ZIP <> SITUS_ZIP OR MAIL_STATE <> 'CA'` = 75,804. The config also pulls estate / deceased / recent distress deed parcels, so the
  pull is about 85k rows and takes a few minutes.
- Fields used: `PARCEL_NUMBER` (14 digits, our tag), `APN_DASH` (xxx-xxxx-xxx-xxxx, what the county sites want), `SITUS_ADD1`, `SITUS_ZIP`,
  `CITY`, `JURISDICTION`, `MAIL1`, `MAIL_CITY`, `MAIL_STATE`, `MAILING_ZIP`, `LANDUSE`, `TAX_ROLL_STATUS`, `OWNER_STATUS`
  (`Est Of` / `Deceased` / null), `DOCUMENT_TYPE_DESCRIPTION` + `DOCUMENT_DATE` (last recorded document on the parcel).
- Gotchas:
  - `OWNER` is the literal string `OWNER OF RECORD` on every row; the county does not publish owner names online. So no entity owners,
    no cash buyer list (`buyers.json` is empty), and the absentee test is mailing address vs situs only.
  - No value, year built, living area or sale price fields. `min_value` is 0 and the scorer's house test falls back to "has a street address".
    `res_sqft`/`value` are blank on every card.
  - `DOCUMENT_DATE` is the last recorded document, not necessarily a sale. It feeds `sale_date` and the `derived` rules only.
  - `STREET_NBR <> ''` drops about 340 parcels with no situs number.
- Derived signals from the last document: estate (DEATH OF OWNER, AFFIDAVIT OF DEATH, probate orders, executor / administrator deeds, about 3.5k
  in the last two years), deceased (`OWNER_STATUS` Est Of / Deceased, about 1,050), foreclosure (TRUSTEES DEED UPON SALE, TRUSTEES DEED,
  DEED IN LIEU, SHERIFF DEED, about 200), tax deed (about 50 all time), quit claim (about 5k in the last two years).

### Sacramento County land use classification (reference only)
- `https://services1.arcgis.com/5NARefyPVtAeuJPU/arcgis/rest/services/Parcels/FeatureServer/0` (502,449 rows). Has `LANDUSE`, `LU_GENERAL`,
  `LU_SPECIF`, `LU_DETAIL` which decode the A1 codes (Residential / Single Family). No owner or mailing fields, so not used as the parcel layer.

### City of Sacramento Vacant Lot Program (tried, dropped)
- `https://services5.arcgis.com/54falWtcpty3V47Z/arcgis/rest/services/Vacant_Lot_Program/FeatureServer/0`, 4,822 cases (open and closed).
- `APN` is the 14 digit parcel number (matches `PARCEL_NUMBER`), `ADDRESS`, `CASE_NUMBER`, `CASE_STATUS`. Wired it first as a weight 15
  signal: 655 of the top 2,500 leads became bare lots (many with no street number, since parcels with a signal are fetched by id and skip
  the `STREET_NBR` filter) and the county layer has no year built or sqft to tell a lot from a house. Dropped. Useful again once the
  assessor sales layer below gives us a living area field.

### Sacramento County Assessor sales (not wired yet)
- `https://mapservices.gis.saccounty.gov/arcgis/rest/services/ASSESSOR/MapServer/1` ("Sales by Property Type", 56,883 rows):
  `PARCEL_NUMBER`, `INDICATED_SALES_PRICE`, `DOCUMENT_DATE`, `EFFECTIVE_YEAR_BUILT`, `TOTAL_LIVING_AREA`, `Property_Type`. Would give year built,
  sqft and sale price for recently sold houses only. Needs a join by parcel number that the generic puller does not do yet.

## Parked (real signal, needs a small code change)

### City of Sacramento 311 / code enforcement
- `https://services5.arcgis.com/54falWtcpty3V47Z/arcgis/rest/services/SalesForce311_View/FeatureServer/0`. Fields `ReferenceNumber`,
  `CategoryLevel1` (Code Enforcement), `CategoryName`, `Address`, `ZIP`, `DateCreated`, `DateClosed`, `PublicStatus`.
- Open code cases right now: Housing - Complaint 438, Housing - Boardup 51, Junk & Debris 245, Combo 168, Emergency Housing Repair 9.
- Why parked: no APN, and `Address` is `2130 P ST, SACRAMENTO 95816`. `norm_addr` only strips the zip, leaving `2130 P ST SACRAMENTO`,
  which never matches the parcel situs `2130 P ST`. Fix is an `addr_strip` option on signal layers in `signals.py` (one line), then add
  `where: CategoryLevel1 = 'Code Enforcement' AND PublicStatus IN ('Open','In Progress') AND CategoryName IN ('Housing - Complaint','Housing - Boardup','Combo','Junk & Debris')`
  with weights 25 (housing), 30 (boardup), 15 (junk).

## Dead ends
- `https://eproptax.saccounty.gov/` redirects to `https://county-taxes.net/sacramento/property-tax` which is behind a Cloudflare challenge
  (HTTP 403 to scripts). Tax delinquency is not pullable. The county tax sale list is a PDF on `finance.saccounty.gov` (not parsed).
- `https://mapservices.gis.saccounty.gov/arcgis/rest/services/ACCELA_ACTIVITIES/MapServer`: layer 0 is a group layer, sublayers 1, 3, 4
  (Application Status, This year, Last Year) return 0 rows. County (unincorporated) code enforcement is not published here.
- Assessor Parcel Viewer `https://assessorparcelviewer.saccounty.gov/JSViewer/assessor.html` has no deep link by APN that I could find; the
  lookup link opens the viewer and shows the parcel number to type in.

## Look for next
- An owner name source: the county recorder index is not online for free; the assessor roll with names is a paid extract.
- Placer County: `https://gis.placer.ca.gov/` (ArcGIS) parcels with owner names are likely; Roseville code enforcement on the city's open data.
- El Dorado County: `https://see-eldorado.edcgov.us/` parcel layers.
