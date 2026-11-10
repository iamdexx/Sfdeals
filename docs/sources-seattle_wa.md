# Seattle (King County, Pierce County) sources

Working, free, unattended:
- King County `services.arcgis.com/Ej0PsM5Aw677QF1W/.../PARCEL_ADDRESS_PUB_AREA_3069/FeatureServer/0` ("Parcels with Address, Property and Ownership Information (Public)", 637k, refreshed weekly). Fields: `PIN`, `ADDR_FULL`, `ZIP5`, `CTYNAME`, taxpayer mailing address `KCTP_ADDR` / `KCTP_CITY` / `KCTP_STATE` / `KCTP_ZIP` (space padded, sometimes zip+4), `PREUSE_CODE` / `PREUSE_DESC` (single family is code 2, `LIKE 'Single Family%'`, 484k), `APPRLNDVAL` and `APPR_IMPR` (no total value field), `ACCNT_NUM`. Absentee pulled server side as `KCTP_ZIP NOT LIKE ZIP5 || '%' OR KCTP_STATE <> 'WA'` (76k, about 2 minutes at 1000 a page). No year built, living area or sale fields on this layer, so the "real house" test is the street number plus the building value floor.
- King County `Residential_Parcels_with_Building_Age/FeatureServer/2` (523k residential buildings, assessor survey snapshot from Feb 2021: `YrBuilt`, `SqFtTotLiv`, `BldgGrade`, `Condition` 1 Poor to 5 Very Good). Used as a signal layer: `Condition = 1` (555). Fair (2) is 3.9k more if wanted.
- King County `PARCEL_SALES3YR_AREA_287/FeatureServer/0` (114k sales in the last 3 years, refreshed weekly; `buyername`, `SaleDate`, `SalePrice`, `Principal_Use`). Listed as the first King County parcel entry, filtered to residential company buyers over $10k, so the cash buyer list has real names. Buyer mailing address columns are blank on this layer.
- Pierce County `services2.arcgis.com/1UvBaQ5y1ubjUPmd/.../Tax_Parcels/FeatureServer/0` (340k, refreshed weekly). `TaxParcelNumber` (10 digits), `Site_Address`, mailing `Delivery_Address` / `City_State` ("TACOMA, WA") / `Zipcode` (zip+4), `Use_Code` (1101 single family 235k, 1152 and 1155 manufactured homes), `Taxable_Value`, `Tax_Senior_Exemption`. No site zip or city, so absentee is `Delivery_Address <> Site_Address` server side (61k) and the normalised address compare client side. About 5 to 10 percent of those are formatting differences (AVENUE vs AVE, O'BRIEN vs OBRIEN), so a few owner occupied Pierce houses carry the absentee tag.
- City of Tacoma `services3.arcgis.com/SCwJH1pD8WSn5T5y/.../Code%20Violations/FeatureServer/0` (22.9k cases back to 2016, refreshed daily; `parcelnumber` matches the Pierce parcel number, `casetype`, `casestatus`, `currentstatus`). Open cases: Derelict Building 156, Substandard or Unfit Building 31, Nuisance 665.

Gotchas:
- Neither King nor Pierce County puts the taxpayer name in any public GIS layer (King removed it years ago; the "Ownership" layer only carries the mailing address, plus an attention line `KCTP_ATTN` that is filled 2 percent of the time). The config maps `owner` to that attention line plus the tax account number so leads are not dropped, and the lookup links (King eRealProperty, Pierce ATIP) show the name. The King County Assessor's "Real Property Account" extract (CSV zip on the assessor data download page) does have `TaxpayerName`; a small loader for it would fix the owner line and the investor-owned flag for 484k houses.
- King County has no total value field; `value` is the building value (`APPR_IMPR`), the UI copy says so. Seattle land is often worth more than the house.
- Pierce `City_State` is one field, so `mail_state` is not mapped and Pierce leads never get the out of state tag.
- The Tacoma layer's `casestatus` values have trailing spaces; filter on `currentstatus = 'Open'` instead.

Dead ends:
- City of Seattle code complaints and violations (SDCI) exist only on Socrata (`data.seattle.gov/resource/ez4a-iug7`), not ArcGIS; the generic puller only speaks ArcGIS. Same for the Seattle vacant building monitoring list. Worth a Socrata adapter later (clean data, parcel address keyed).
- King County Treasury tax foreclosure list is an annual PDF, no layer. King County Recorder (trustee sale notices) has no public bulk API.
- Seattle `ADUniverse_parcels` has `TAXPAYER` but is a 2020 snapshot, Seattle only.
- Snohomish County not started.

Next: Socrata adapter for Seattle SDCI cases and vacant buildings, King County assessor extract for taxpayer names, Pierce County Assessor-Treasurer foreclosure list, Snohomish County parcels.
