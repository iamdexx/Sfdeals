# Houston (Harris County) sources

Working, free, unattended:
- Harris County / HCAD parcels `www.gis.hctx.net/arcgishcpid/rest/services/HCAD/Parcels/FeatureServer/0` (1.55M; `HCAD_NUM` 13 digit account, owner, mailing address, situs parts, `state_class`, `bld_value`, `total_market_val`, `new_owner_date`). Single family is `state_class = 'A1'` (1.16M). Absentee pulled server side as mailing state not TX, or mailing zip differs from `site_zip`, or mailing street does not start with the situs street number; with `site_str_num > 0 AND bld_value > 0` that is about 250k rows and the whole run takes about 8.5 minutes. Use `site_str_num`, not `SiteNumber` (null on 329k houses). No year built, living area, homestead flag or sale price on this layer, so the real house test uses the street number and building value filter only.
- Harris County Tax Office `services.arcgis.com/su8ic9KbA7PYVxPS/arcgis/rest/services/Delinquent_Parcels_2025/FeatureServer/0` (52.9k, April 2026 snapshot; `HCAD_NUM` matches the parcel layer exactly). `tax_suit` = `CAUSENO` filled (5.7k), `tax_delinquent` = `LEVYDUE >= 500` (36.7k). Both skip rows with `TAXDEFSTRT` set (2.9k, over 65 or disabled tax deferral, not distress). The service name carries the tax year, so the URL has to be bumped when the 2026 list is published.
- City of Houston 311 `mycity2.houstontx.gov/gisweb01/rest/services/311/HOUSTON311_RECENT_SR_SNOW/FeatureServer/0` (52.8k recent service requests). Used with `STATE_CODE = 'Active'`: `Dangerous Buildings` (1.2k), `Building Code Violation` (0.3k), `Weeds/Trash/Stagnant Water on Property` (19.8k). `TAXID` is the HCAD account with the leading zero dropped (12 digits for most), so only accounts that do not start with 0 match by id; the rest match by address. About half of dangerous building reports land on a parcel; the others are apartments, commercial or lots.

Gotchas:
- These are 311 complaints, not adjudicated violations. Labels say "report" and "complaint" on purpose.
- About 0.6% of pulled parcels are owner occupied homes whose mailing address is a typo or abbreviation of the situs address with a different zip. They show as absentee.
- Texas is a non-disclosure state: no sale price anywhere in the county data, so `buyers.json` is empty. `new_owner_date` is mapped as `sale_date` and defaults to 1988-01-02 for old records.
- Signal parcels fetched by id can be non A1 (Z, A3, C1 classes); the value floor and street number test keep most lots out.

Dead ends:
- `search.hcad.org` and `hcad.org/property-search` sit behind a Cloudflare challenge (403 to scripts). Not scraped. The lookup link uses the HCAD parcel viewer `arcweb.hcad.org/parcel-viewer-v2.0/?account={tag}` instead.
- `arcweb.hcad.org/server/rest/services/public/public_query/MapServer/0` (1.55M) works but has fewer fields than the layer above.
- City `Dangerous_Building` item on `services.arcgis.com/NummVBqZSIJKUeVR` (493 rows) is a stale 2017 extract.
- Harris County Clerk foreclosure postings (`cclerk.hctx.net/applications/websearch/FRCL_R.aspx`) is an ASP.NET form search with no bulk feed; parked.
- Tax office top delinquent list is a subset of the layer above.

Next: HCAD bulk download (real_acct, building_res) for year built, living area and homestead exemption to add `occ_field`, `year`, `res_sqft`; County Clerk foreclosure postings; tax sale list from the constables; Fort Bend (FBCAD), Brazoria and Waller parcels; Pasadena and Baytown code cases.
