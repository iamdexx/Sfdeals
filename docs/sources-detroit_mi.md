# Detroit (Wayne County) sources

Working, free, unattended. All on the City of Detroit open data org `services2.arcgis.com/qvkbeam7Wirps6zC` (data.detroitmi.gov, public domain). Every layer caps at 1,000 rows per page.
- `parcel_file_current/FeatureServer/0` (378k parcels; `parcel_id` like `10001178.`, situs `address` with no street type, `taxpayer_1` owner, taxpayer mailing address, `pct_pre_claimed` = principal residence exemption (Michigan homestead), `amt_assessed_value` (half of market by state law), `year_built`, `total_floor_area`, `sale_date`, `amt_sale_price`, `use_code_description`). Residential improved is `property_class = '401'` (213k; 180k single family, 15k two family). Pull is taxable, no PRE, and mail address not starting with the situs address or out of state (`taxpayer_address NOT LIKE CONCAT(address, '%')`, 58k, about 2 minutes at 1,000 a page).
- `city_demolition_pipeline/FeatureServer/0` (292 houses on the city demolition list, 24 emergency).
- `Fire_Escrow_Properties/FeatureServer/0` (1.1k; fire insurance money the city holds until the house is fixed or razed). Used as `Property_Class = 'Residential-Structure' AND Updated_Balance > 0` (792). Many are DLBA owned and drop out as government owners. Losses date back to 2008.
- `bseed_vacant_property_registrations/FeatureServer/0` (1.5k, rolling 12 months of vacant building registrations).
- `blight_tickets/FeatureServer/0` (913k tickets since 2004). Used: in collections, balance $100 or more, issued 2025 or later, and only the building-condition ordinances (`ordinance_law IN` 8-15-113 vacant not maintained, 8-17-21 dangerous building, 8-15-37 / 8-15-39 unsafe, 8-15-201(b) exterior, 8-15-205 walls, 8-15-206 roof, 8-15-209 porch), 4.1k tickets on 2.4k parcels. Filter on `ordinance_law` codes, not `LIKE` on the description: the LIKE version took 10 to 55 seconds a query and the server returns a 400 when it times out.

Result (2026-11-10): 62k parcels pulled, 6.7k signal rows, 3,056 hot of 60,177 leads; median assessed value of the top 2,500 is 43k (about 86k market). Signals on the top 2,500: blight 1,243, vacant 907, fire 409, demolish 37; 311 out of state. Pull plus score takes about 3 minutes.

Gotchas:
- `signals.py` pages at 2,000 and stops when a page comes back short, so a 1,000-row layer is truncated after the first page. Signals over 1,000 rows (vacant, blight) are split into several entries with the same `name` and a `where` on parcel id ranges (`parcel_id < '1602'`, ...), each kept under about 700 rows so the lists can grow. If the shared code ever takes a `page` key for signals, collapse them.
- Situs addresses have no street type (`2627 HOGARTH`) while mailing addresses do (`2627 HOGARTH ST`), so a plain mail vs situs compare calls owner-occupants absentee. The server-side `NOT LIKE CONCAT(address, '%')` handles the main pull; parcels fetched by id because they carry a signal can still be mislabelled absentee when the only difference is the street type.
- `util.norm_addr` strips `LOT<anything>` as a unit, so streets starting with LOT (Lothrop, Lotus, 496 parcels) lose the street name and show as a bare house number.
- Ticket dates include typos (years 3016, 2521), so bound both ends of the date range.
- Assessed value is 50% of market: `min_value` 20000 is a 40k house.

Dead ends:
- Wayne County has no public parcel service: `gis.`, `maps.`, `www.waynecounty.com/arcgis` all redirect to an interactive portal; county parcel data is sold through the Register of Deeds. The Treasurer's delinquent and foreclosure data is only behind the pay-taxes search (`pta.waynecounty.com`), no list or API.
- `Residential_Inspections_(combined)` ends in 2024. `bseed_rental_registrations` and the rental compliance tickets (27k in collections) only say landlord, parked.
- `assessor_property_sales_view` has deed types (`SD` sheriff deed 855 in two years, `QC` quit claim 13.5k) but quit claims are the normal Detroit transfer, so not used as a signal.

Next: Wayne County Treasurer foreclosure auction list (each year's list is a PDF on the auction vendor's site), blight tickets for the other 26k rental/compliance ordinances, the suburbs (Oakland and Macomb counties each have their own GIS; Oakland sells parcel data).
