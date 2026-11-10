# Denver, CO sources (denver_co)

Covers the City and County of Denver only (one government, one assessor). All layers are on Denver's public ArcGIS Online org,
`https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services` (Denver Open Data Catalog, `ODC_*` services). No login.

## Working sources

### Parcels: `ODC_PROP_PARCELS_A/FeatureServer/245`
- 240,580 parcels, max 2,000 rows per page. 168,364 match `PROP_CLASS IN ('1212','1215') AND SITUS_ADDR_NBR IS NOT NULL`.
- Fields used: `SCHEDNUM` (13 digit schedule number, the parcel id), `SITUS_ADDRESS_LINE1`, `SITUS_CITY`, `SITUS_ZIP`, `OWNER_NAME`,
  `OWNER_ADDRESS_LINE1`, `OWNER_CITY`, `OWNER_STATE`, `OWNER_ZIP`, `D_CLASS_CN` (class text), `TOT_UNITS`, `RES_ORIG_YEAR_BUILT`,
  `RES_ABOVE_GRADE_AREA`, `APPRAISED_TOTAL_VALUE`, `SALE_DATE` (ms epoch), `SALE_PRICE`, `ASAL_INSTR` (deed type of the last sale).
- `PROP_CLASS` 1212 and 1215 are the residential improved classes. `D_CLASS_CN` shows what is inside: SFR grades, rowhouse, duplex,
  and condominium (43,816 condos). Condos are kept; filter on `D_CLASS_CN` if they turn out to be noise.
- No homestead or owner-occupied field. Absentee is mailing address vs situs address.
- Gotcha: owner mailing addresses often drop the street direction that the situs carries (`1035 JASMINE ST` vs `1035 N JASMINE ST`) or
  add a unit. A plain string compare flagged about 50,000 owner-occupied homes as absentee. Fix in the config: the county is listed
  twice. The first entry pulls parcels whose mailing address starts with the situs number + street + type (with or without the
  direction), 134,948 rows, and maps `mail` to the situs address so they score as owner-occupied. The second entry pulls all 168,364
  residential parcels; rows already seen are skipped, so what is left is the real absentee set (33,132). Remaining false absentees
  in a spot check: 163 (0.5%), mostly `N BROADWAY` vs `BROADWAY` and corner lots.
- Because of that there is no absentee-only server filter; the full residential pull is 168k rows and the whole run takes under 4 minutes.
- Derived signals from `ASAL_INSTR` + `SALE_DATE` within 730 days: estate (`PR: PERSONAL REP`, `CS: CONSERVATORS`, `AD: ADMINISTRATORS`,
  `PB: PROBATE COURT`), quit claim (`QC: QUIT CLAIM`), foreclosure (`PT: PUBLIC TRUSTEE`, `SF: SHERIFFS`, `DF: DEED/LIEU OF FRCLSR`).

### City complaints: `ODC_service_requests_311/FeatureServer/53` (table)
- 395,626 rows, rolling 12 months of Denver 311 cases. Filter `Agency = 'Community Planning & Development'`, address not null,
  `Case_Status NOT LIKE 'Closed%'`, then by `Case_Summary`.
- Pulled 4,705 open cases: weeds 3,387, trash 1,091, vacant 129, neglect 98. About 78% match a residential parcel
  (weeds 2,772, trash 746, vacant 85, neglect 74); the rest are commercial, apartments, or intersections.
- No parcel id. `Incident_Address_1` is matched to the situs address after normalizing; both carry the street direction.
- These are complaints sent to inspectors, not confirmed violations. Weights are set low for weeds (10) and trash (15), 20 vacant, 25 neglect.

## Results (last run)
- 168,364 parcels, 4,705 signals, 37,323 scored, 6,651 hot. Median value of the top 2,500: $560,700.
- Top 2,500 by signal: quit claim 1,007, estate 644, weeds 574, trash 279, vacant 71, neglect 69, foreclosure 44.
- Cash buyers: 100 entities from assessor sales.

## Parked
- Delinquent tax list: `https://www.denvergov.org/files/assets/public/v/1/finance/documents/treasury/delinquent-real-property-tax-list.xlsx`
  (linked from the Real Estate Delinquent Taxes and Tax Lien Sale page). It is a spreadsheet, and the signal puller only reads ArcGIS
  layers, so it needs an xlsx reader in shared code. This is the best next signal (tax delinquent, weight 30-35).
- Property record link: Denver's Real Property page redirects to `https://property.spatialest.com/co/denver#/`. The config links to
  `#/property/{tag}`. That deep link was not confirmed in a browser; if it does not open the record, link to the search page instead.

## Dead ends
- No county ArcGIS server answers at `gis.denvergov.org`, `maps.denvergov.org`, `geospatial.denvergov.org`, `gisservices.denvergov.org`
  or `www.denvergov.org/arcgis`. Everything public is on ArcGIS Online.
- `denvergov.org/property/realproperty/summary/<schednum>` returns 404. The Spatialest API returns 403 to scripts; not used.
- No public layer found for code violations with a parcel id, condemned or unsafe buildings, or a neglected and derelict building list.

## Next
- Tax delinquent xlsx (above). Denver Public Trustee foreclosure sale list. Denver's neglected and derelict building list if it is published.
- Other counties, each with its own assessor: Arapahoe (Aurora, Centennial), Jefferson (Lakewood), Adams, Douglas, Broomfield. Not started.
