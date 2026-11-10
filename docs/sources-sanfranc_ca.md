# San Francisco-Oakland (Alameda County) sources

Working, free, unattended:
- City of Oakland ArcGIS org `services.arcgis.com/9tC74aDHuml0x5Yz/arcgis/rest/services/AC_Parcels2020/FeatureServer/0`: a copy of the
  Alameda County assessor roll with `OWNER_NAME`, mailing address (`MAILING_ADDRESS`, `MAILING_ADDRESS_CITY_STATE`, `MAILING_ADDRESS_ZIP_5`),
  `HOME_OWNER_EXEMPTION` (7000 = owner lives there), `USE_CODE`, `SHP_BLDG_YEARBUILT`, `BLDG_AREA_SQFT`, `SHP_NO_BEDROOMS`, `ASSESSED_VALUE`,
  `LAST_DOCUMENT_DATE`. 224k rows, of which 112k are City of Oakland parcels with data (the other half are empty geometry rows: no APN,
  no owner); the `OWNER_NAME <> ''` clause drops them. Roll date 2020-04 (max `LAST_DOCUMENT_DATE`), layer last edited 2021-05.
  `maxRecordCount` is 1000, so `page` is 1000 (2000 stops after the first page). Tag is `PRINTPARCEL` (`1-115-20`), same format as the
  county's `Print_Parcel`. Single family use codes: 1100 (SFR), 1200/1201 (SFR with ADU), 1400 (duet), 1600 (site condo), 1800 (PD tract),
  1900/1901 (manufactured/modular). Where clause: SFR codes, owner present, and (no homeowner exemption OR heirs/estate owner) = 22.8k rows,
  20 seconds. 11.1k are absentee (mailing address differs from the house).
- Derived signals off the same roll: `OWNER_NAME` contains `HEIRS` (245, "SMITH JOHN HEIRS OF EST" = deceased owner, heirs hold title) and
  `EST OF` (7). Weight 30 each. Those rows are pulled even when the homeowner exemption is still on the roll.
- Use code list: `services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/Assessor_Office_Use_Codes/FeatureServer/0` (198 codes).

Run: 252 hot (245 heirs, 7 estate), 11,351 leads total, median assessed value of hot leads 89k (Prop 13 basis, not market).
No sale prices anywhere in Alameda County data, so `buyers.json` is empty.

Gotchas:
- Alameda County's own open data (data.acgov.org, `services5.arcgis.com/ROBnTHSNjoZ2Wm1P`) is fresh (Secured Tax Roll 2025 to 2026, 472k;
  `Parcels`, 489k) and has mailing address, `HOEX`, value, use code and latest document date, but NO owner name (`Attention_Name` is empty on
  every row). `metro/score.py` drops parcels with an empty owner, so that roll alone yields zero leads. A config-only metro therefore has to
  use the Oakland copy. If the scorer ever allows nameless parcels (or a `owner_optional` flag), switch `parcels.url` to
  `Assessor_Office_Secured_Tax_Roll_2025_to_2026/FeatureServer/0` with `Print_Parcel`, `Situs_Street_Number`+`Situs_Street_Name`, `HOEX` as
  `occ_field`, `Total_Net_Value`, `Latest_Document_Date` (DateOnly string) for the whole county, current year.
- Oakland `Parcels21/FeatureServer/0` is the same roll one year later (2020-12) and covers Oakland, Berkeley, Alameda, San Leandro, San
  Lorenzo, Castro Valley, Emeryville (219k with owner names), but its object id field is `FID`, and `stl.arcgis` orders by `OBJECTID`, so the
  query fails with "'OBJECTID' parameter is invalid". An `order` key in the parcels config would unlock it (field names are the 10 character
  shapefile versions: `PRINTPARCE`, `SITUS_HOUS`, `SITUS_STRE`, `MAILING__2` street, `MAILING__4` city state, `MAILING__5` zip, `HOME_OWNER`,
  `SHP_BLDG_Y`, `BLDG_AREA_`, `ASSESSED_V`, `LAST_DOC_2`).
- Mailing city and state are one field (`OAKLAND CA`), so `mail_state` is not mapped and the "out of state" flag never fires; the card shows
  the city and state together (`Houston Tx`).
- Assessed value is the Prop 13 base, often 30k to 100k for houses worth 600k+; `min_value` is 25000 so long time owners are not dropped.
- Owner names are as of 2020: about one house in six has changed hands since. The county tax portal has the current mailing address.

Dead ends (do not retry):
- Oakland code enforcement: Accela Citizen Access only, nothing on data.oaklandca.gov or the city ArcGIS org. The only AGOL layer is
  `Housing_Habitability_Complaints_20182020` (3.1k complaints, 2018 to 2020, no APN, address field carries ", Oakland, CA 94606" so it does not
  join). `Oakland_Code_Complaints_2013` is a 2013 one off. OAK 311 (`data.oaklandca.gov/resource/quth-gb8e`, Socrata) has 81k BLDGMAINT
  requests by address but is not ArcGIS.
- Alameda County Treasurer: tax defaulted land page (treasurer.acgov.org/tax-defaulted-land) has only the Bid4Assets auction results PDF; no
  delinquent or power to sell list is posted. The "Secured Top 10/25" hub layers are the largest taxpayers, not delinquents.
- Alameda County Recorder: no free index (notices of default are paid search only).
- `Assessor_Office_Ownership_Transfer_List` (197k, 2 rows per transfer, has transfer tax value but no names) could give sale prices for the
  buyer list if a join by APN is ever added.
- San Mateo County: no public parcel attribute service (`Parcels_DA` is 14 rows, `gis.smcgov.org` returns 404). Marin County `Parcels` layer
  has only the APN. San Francisco publishes its roll on Socrata (data.sfgov.org) without owner names. Nothing usable for a second county yet.

Next: ask the City of Oakland GIS team whether a current year copy of the roll with owner names exists; add an `order` option to the parcels
config to use `Parcels21` (half the county); Socrata adapter for OAK 311 building maintenance complaints; County Recorder notice of default
feed if one ever becomes free.
