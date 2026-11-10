# Philadelphia (Philadelphia County) sources

All on the City of Philadelphia's ArcGIS Online org `services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services` (2,300 services, open data, no key). Parcel id everywhere is the 9 digit OPA account number (`parcel_number`, `opa_account_num`, `opa_id`, `OPA_NUMBER`), no padding, so signals join by id directly.

Working, free, unattended:
- Parcels: `OPA_Properties_Public/FeatureServer/0` (584k; Office of Property Assessment). Single family is `category_code = '1'` (463k). Fields: `location` is the situs address, `mailing_street` / `mailing_city_state` ("PHILADELPHIA PA" in one field) / `mailing_zip`, `state_code` is the mailing state, `market_value`, `sale_date` and `sale_price`, `year_built`, `total_livable_area`, `exterior_condition` (0 n/a, 1 other, 2 newer, 3 above average, 4 average, 5 below average, 6 vacant, 7 sealed or structurally compromised), `homestead_exemption` (0 or 100000). Pull is `mailing_street <> location OR state_code <> 'PA' OR exterior_condition IN ('6','7')` (145k, about 3 minutes at 2000 a page). Homestead is NOT used for absentee: 228k of 463k houses have no exemption and most of those are owner occupied who never applied.
- `UNSAFE/FeatureServer/0` (3.1k, L&I unsafe structure cases; `violationresolutiondate IS NULL` is the open set, 2k opened since 2024). Weight 40.
- `DEMOLITIONS/FeatureServer/0` (14k demolition permits and cases). Only `city_demo = 'YES'` and not COMPLETED/CANCELLED (36) is a signal; private permits are owners redeveloping. Weight 45.
- `VIOLATIONS/FeatureServer/0` (2.0M L&I violations, updated daily). Two signals: `casestatus = 'IN VIOLATION - COURT'` with `violationstatus = 'OPEN'` (10k rows, L&I suing the owner, weight 30) and open vacant property codes `9-3905, PM15-301, PM15-901.1, 9-3904, PM15-108.2, PM15-901.2` (vacant structure license, vacant structure and land, vacant and open, 10k rows, weight 25). `publicnov` is a link to the notice PDF.
- `Vacant_Indicators_Bldg/FeatureServer/0` (9.6k, city's likely-vacant building model, refreshed monthly, `opa_id`). Weight 20.
- `REAL_ESTATE_TAX_DELINQUENCIES/FeatureServer/0` (54k) is a frozen June 2022 snapshot (`YEAR_MONTH` is 202206 for every row). Kept at weight 20, narrowed to residential, actionable, no payment agreement, 3+ years owed (20k) and labeled with the date so callers know. The live monthly list is only on Carto (`phl.carto.com/api/v2/sql`, table `real_estate_tax_delinquencies`), which the generic puller does not speak yet.
- Derived from the parcel record: exterior condition 7 sealed/compromised (2.4k, weight 35) and 6 vacant (1.9k, weight 25).

Gotchas:
- `LI_VIOLATIONS` (1.45M) and `ImminentlyDangerousViolations`, `UnsafeViolations` are dead copies last edited 2016 to 2021; use `VIOLATIONS` and `UNSAFE` instead.
- `violationresolutiondate IS NULL` on `VIOLATIONS` still includes closed cases (CLIP notices); filter on `violationstatus` and `casestatus`.
- `mailing_city_state` is one field, so mail_city shows as "Philadelphia Pa" on the card.
- Lookup: `property.phila.gov/?p={opa}`, `atlas.phila.gov/{address}/property`, `li.phila.gov/property-history/search?address={address}`.

Dead ends: `Foreclosure_Filings` is a 2022 census tract count, not parcels. `City_Demolitions` is a hex grid. Sheriff sale listings (phillysheriff.com, Bid4Assets) have no open API. Philadelphia requires a Wholesale Residential Real Property license from L&I (Bill 210791, 2022) plus a written seller disclosure; this is in the `law` copy.

Next: Carto live tax delinquency and `rtt_summary` (deed and mortgage transfers, including sheriff deeds and estate transfers) once the puller can read a Carto SQL endpoint; `RENTAL_LICENSES_` (292k, `OWNEROCCUPIED` flag) for a cleaner absentee test; the suburban counties (Montgomery, Bucks, Delaware, Chester are on PA county GIS, Camden and Burlington on NJ MOD-IV).
