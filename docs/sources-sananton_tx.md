# San Antonio (Bexar County) sources

Working, free, unattended:
- Bexar County parcel layer `maps.bexar.org/arcgis/rest/services/Parcels/MapServer/0` (729k parcels, Bexar Appraisal District data; `PropID`, `AcctNumb` (12 digit GEO id with dashes), `Situs`, `Owner`, `AddrLn1..3`, `AddrCity`, `AddrSt`, `Zip`, `Exempts` (text, e.g. `HS, OV65`), `State_cd` state class code, `PropUse`, `TotVal`, `GBA` living area, `YrBlt`, `Houses`, `Stories`). Single family is `State_cd = 'A1'` (588k). Pull is A1 and (no `HS` homestead code or mailing state not TX): 194k rows, about 4 minutes. The service description says the layer was last refreshed in 2021 but `YrBlt` runs through 2025 and values match the current BCAD site, so it is current.
- City of San Antonio 311 service calls `services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services/311_All_Service_Calls/FeatureServer/0` (510k cases, 25k open). Code enforcement is `Department = 'Development Services'`; we pull open cases by `TypeName`: Dangerous Premise BSB Processed / DP Emergency Demolition (305, weight 40), Property Structure Concerns (635, 25), Vacant/Overgrown Property (1,631, 25), Overgrown Yard/Trash and Junk Vehicle (4,155, 15), Absentee Property Owner Registration Required (1,085, 10). Address only (`ObjectDescription`, format `123 MAIN ST, SAN ANTONIO, TX 78201`), no parcel id. About 900 open cases have a blank address and are dropped.
- City vacant building registry `services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services/OHP_Vacant_Buildings_Parcels_Public/FeatureServer/0` (987 parcels; `PropID`, `Situs`, `RegistrationStatus`, `TIER_VBP_Status`, `DelinquentTaxAmount`). Used twice: on the registry (weight 30) and `DelinquentTaxAmount > 0` (223, weight 30), the only tax delinquency source we found.

Last run: 128,672 parcels in the pull, 2,022 hot, median hot value $158k. Hot by signal: nuisance 671, vacant registry 524, vacant case 473, absentee registration 375, back taxes 136, structure case 92, dangerous premises 53.

Gotchas:
- `PropID` is a double in the parcel layer. The signal id fetch quotes ids as strings and ArcGIS rejects that on a numeric field, so the parcel tag is `AcctNumb` (text) and every signal matches on address. The vacant registry carries `PropID` but we still match it by `Situs`.
- `Situs` carries a trailing `\r\nCITY, TX ZIP`. We leave it on so situs, 311 and registry addresses all normalize to the same `123 MAIN ST SAN ANTONIO TX` form (`norm_addr` strips the zip). `mail` is `AddrLn2 + AddrCity + AddrSt` for the same reason, so owner occupied homes without a homestead code compare equal and are not flagged absentee. `AddrLn2` is the street line for nearly every record; 13 rows use `AddrLn1` only and 86 also have `AddrLn3`.
- `Exempts` is text, so `occ_field` cannot be used; no homestead is handled in the `where`, and absentee is the mail vs situs compare.
- Texas is a non-disclosure state: no sale date or price in any public layer, so `buyers.json` is empty. The UI says so.
- The parcel layer has no zip or city field of its own; the zip is inside `Situs`.

Lookups: BCAD record page is `bexar.trueautomation.com/clientdb/Property.aspx?cid=110&prop_id=<PropID>` (integer only, `175728.0` fails); our tag is the GEO id so the UI links to the tax office search (`bexar.acttax.com/act_webdev/bexar/index.jsp`, Account Number, no dashes) and the BCAD search page. `esearch.bcad.org` returns 404. The tax office search is POST only, no deep link by account.

Dead ends:
- `gis.bexar.org` and `gis.bcad.org` do not resolve; the county server is `maps.bexar.org`.
- BCAD Hub layer `BCAD_Parcels/FeatureServer/0` is updated weekly but lacks the value and exemption fields, so the county layer is used.
- Bexar County Clerk foreclosure layers `maps.bexar.org/arcgis/rest/services/CC/ForeclosuresProd/MapServer` (0 mortgage, 337; 1 tax, 19) have address, city, zip and sale month but no parcel id and no street type, so they did not match situs reliably. Worth a `derived` style address match later.
- `DemolitionLocations/FeatureServer/0` (5,351 permits) and `Risk_of_Demolition` (census tract level) have no parcel id.
- `311_Cases_WFL1` and `311_Open_Service_Calls` overlap with `311_All_Service_Calls` and have blank `LOCATION` on many rows.

Next: Bexar tax office delinquent roll (no public layer found), County Clerk trustee sale notices as an address matched signal, Guadalupe County (Seguin, Schertz) parcels at the Guadalupe Appraisal District, and a PropID lookup once the signal fetch handles numeric ids.
