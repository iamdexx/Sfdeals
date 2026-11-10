# Tampa (Hillsborough County) sources

Working, free, unattended:
- Property Appraiser daily parcel layer `services.arcgis.com/apTfC6SUmnNfnxuF/.../HCPA_Parcels_Daily/FeatureServer/0` (531k parcels; owner, mailing address, `HX_YEAR` homestead year, `B1_COND_DSC` building condition from the appraiser's inspection, `SALE1_DEED_DSC` deed type and date, `JUST` value, permits). Single family is `DOR_C LIKE '01%'` (396k). Pull is non-homestead or out of state or condition Poor (128k, about 1 minute).
- Signals are derived from the parcel record (no separate layer): condition Poor (4k), estate / guardian deed, quit claim, tax deed or sheriff sale within 2 years. No homestead exemption sets the absentee flag.

Zip compare does not work on this layer (fields are space padded), so absentee is computed client side.
Confidential owners (2,961, mostly law enforcement) are excluded by the `where`.

Next: Hillsborough Clerk lis pendens and tax deed sale calendars (realtaxdeed), Tampa and county code enforcement (Accela), Tax Collector delinquent list.
