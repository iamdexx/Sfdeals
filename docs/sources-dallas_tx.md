# Dallas (Dallas County) sources

Working, free, unattended:
- Parcels: City of Dallas hosted DCAD account points `services2.arcgis.com/rwnOSbfKSwyTBcwN/arcgis/rest/services/CRMHostedLayers/FeatureServer/0` ("Tax Account Points", 548k accounts, appraisal year 2026, refreshed by the city from the five appraisal districts). Fields: `AccountID` (17 digit DCAD account, same id DCAD's `AcctDetail.aspx?ID=` takes), `SiteAddrNum` + `SiteStreetname`, `CityJuris`, `CountyJuris`, `PropClass`, `BldgClass`, `Owner1`, `OwnAddr1-4`, `OwnerCity`, `OwnerState`, `OwnerZip`, `ImpVal`, `LandVal`, `TotalVal`. Single family is `PropClass = 'SINGLE FAMILY RESIDENCES'` (322k in Dallas County). The pull takes the whole class (no server-side absentee filter: there is no situs zip or homestead field, and hosted services reject `CONCAT` in `where`), about 3 minutes at 2000 rows a page. Absentee is mailing street vs situs street client side.
- Coverage is the City of Dallas plus a one-mile buffer, not all of Dallas County (Garland, Irving, Mesquite, Grand Prairie outside the buffer are missing). DCAD itself publishes no ArcGIS service, only 171 MB zip exports (`dallascad.org/DataProducts.aspx`), and the Dallas County GIS `DCAD_PARCELS` layer (`services3.arcgis.com/zqe2kwz79KUqUvxC`, 685k) is a 2023 snapshot with owner and deed date but no value or land use.
- Signals: City of Dallas 311 cases, rolling 90 days, `services2.arcgis.com/rwnOSbfKSwyTBcwN/arcgis/rest/services/CRM_90Days/FeatureServer/0` (130k rows, refreshed daily). Code Compliance subjects end in `- CCS`. Used: `Demolition Property - CCS` (7), `Intensive Case Resolution - CCS` (64, chronic problem properties), nuisance abatement (`Nuisance Abatement Tracking`, `Mow Clean Request`, `Heavy Clean Request`, `Mow Clean Tire Removal`, `Litter Removal Request`, `Vegetation Removal Request`, residential only, 4.3k), `Code Concern - CCS` open and residential (2.1k), `Single Family Rental Needs Registration - CCS` (484). No parcel id on the layer; matched by `Address_c` ("10211 RIDGE OAK ST, DALLAS, TX, 75227") after stripping the city, state and zip with the signal `addr_strip`. About 60 percent of the 4.6k distinct case addresses land on a single family account (the rest are apartments, commercial, lots or outside the buffer).
- `CRM_FY23` on the same server has every 311 case since October 2022 (2.2M rows) if a longer window is wanted later.

Gotchas:
- `OwnerState` is spelled out ("TEXAS"); `parcels.py` now maps full state names to two letters, otherwise everything looks out of state.
- `Owner1` ending in `&` means `OwnAddr1` is the second owner's name and `OwnAddr2` is the street; `OwnAddr2` is the mailing street in every record (OwnAddr3/4 are always empty). 878 accounts have no owner at all and are dropped by the `where`.
- Texas is a non-disclosure state: no sale price anywhere, so `buyers.json` is empty. Deed date is only inside `Legal4` ("INT202000314166 DD11102020 CO-DC"), not a field.
- No year built, living area or homestead flag on this layer, so the "real house" test is the street number plus `TotalVal >= 70000`.

Result on first run: 320,902 parcels, 6,949 signal rows, 72,410 leads, 2,761 hot, median hot value $246k.

Dead ends: `gis.dallascounty.org`, `maps.dallascounty.org`, `gis.dallascad.org` (no response); Dallas Open Data (Socrata) `Code Violations` datasets stop in 2017 and 2021; `Vacant_Properties` hosted layer is a 2022 snapshot of improved value under $100 (lots).

Next: Dallas County Clerk foreclosure (trustee sale) notices, Dallas County tax office delinquent and sheriff tax sale lists (Linebarger), Dallas Habitual Nuisance Property list, DCAD zip for exemptions and year built, code enforcement for Garland, Irving and Mesquite.
