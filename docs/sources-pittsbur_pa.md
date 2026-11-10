# Pittsburgh (Allegheny County) sources

Coverage today: City of Pittsburgh only (about a quarter of the county's parcels). The rest of Allegheny County is parked, see "Dead ends".

Working, free, unattended (all ArcGIS Online, no login):
- Parcels: City of Pittsburgh org `services1.arcgis.com/YZCmUqbcsUpOKfj7/.../Housing_Density/FeatureServer/0` (96,954 residential parcels inside the city). It is the county assessment file joined to city parcels by City Planning: `parid` (16 char PIN, e.g. `0046B00242000000`), situs (`propertyho` + `propertyad`, `propertyzi`), owner `propertyow`, mailing address (`changenoti` street, `changeno12` city, `changeno13` state, `changeno21` zip), `usedesc`, `fairmarke3` (fair market total), `yearblt`, `finishedli` (living area), `saledate` (epoch ms), `saleprice` (string), `homesteadf` ('HOM' or null), `cdudesc` (assessor condition). Field names are shapefile-truncated.
  - Filter: `usedesc IN (SINGLE FAMILY, ROWHOUSE, TOWNHOUSE, TWO/THREE/FOUR FAMILY) AND homesteadf IS NULL` = 43,704 rows. No homestead exclusion is the server-side absentee filter; the absentee flag itself still comes from mailing vs situs address, so a non-homestead owner occupant is not flagged.
  - Gotcha: this is a snapshot, not a live feed. `asofdate` is 5-Dec-25, newest sale 2025-11-25, layer last edited 2026-03. Owners and sales after that are missing, and the cash buyer window is short on recent months. Check `asofdate` before trusting it and swap the source when a fresher one exists.
  - `homesteadf` is text, so `occ_field` (numeric test) is not used.
- Condemned and dead end: `YZCmUqbcsUpOKfj7/.../condemned_dead_end/FeatureServer/0` (3,236 active: 1,933 Condemned Property, 1,303 Dead End Property). `parc_num` is the same 16 char PIN. Address carries ", Pittsburgh, 15233-" so joins are by PIN.
- Code enforcement (PLI): `YZCmUqbcsUpOKfj7/.../code_enforcement2/FeatureServer/0` (157,866 cases, 146k Closed). Used: `status IN ('In Violation','In Court')` (8,033) as open code violation, `status = 'Clean & Lien'` (2,238) as nuisance. `workflows` is a large JSON blob with violation text and court dates; not pulled. Layer last edited 2026-01.
- City tax delinquency: `services1.arcgis.com/0DMNBNaacQNEfN4H/.../city_tax_delinquent_3yr/FeatureServer/0` (12,317 parcels three or more years behind on city and school taxes; `pin`, `prior_years`, `total_owed`). Updated daily. About half are vacant lots and do not match a house.
- Derived: `cdudesc` in POOR, VERY POOR, UNSOUND (3,378 citywide).

Test run: 25,824 signal rows, 47,007 parcels, 6,133 hot of 34,586 leads, about 1 minute.

Looked at, not used:
- `YZCmUqbcsUpOKfj7/.../ParcelsPublic/FeatureServer/0` (142,615, refreshed daily): use, building value, vacant flag, owner category, but no owner name, mailing address or sale.
- `0DMNBNaacQNEfN4H/.../onetoFourunitresidential` (94,742, 2023): owner and one-line mailing address, no value or sale.
- `YZCmUqbcsUpOKfj7/.../Tax_delinquent_properties` (26,485, any delinquency including current year only): too broad; `Tax_Delinquent` (13,796, undated, full assessment fields): older copy.
- `0DMNBNaacQNEfN4H/.../gisdb_gis_condemned_property` (1,939): same condemned list as above.
- `0DMNBNaacQNEfN4H/.../USPS_Vacancy` (4,427) and `vacant_land_points` (33,803): small or land only.

Dead ends:
- Allegheny County's own server `gisdata.alleghenycounty.us/arcgis/rest/services/OPENDATA/Parcels/MapServer/0` and PASDA `AlleghenyCounty/MapServer/25` have parcel geometry and PIN only, no owner or assessment fields.
- `services1.arcgis.com/vdNDkVykv9vEWFX4/.../AlCoParcels` has the full assessment schema but only 1,574 rows. `services6.arcgis.com/drkDXByy6E3bYW3a/.../allegheny` needs a token. Many small municipal layers (Moon, North Fayette, QVCOG...) exist but are stale and piecemeal.
- The complete, current county file is on WPRDC (CKAN, CC0, scripts allowed): Property Assessments resource `65855e14-549e-4992-b5be-d629afc676fa` (584,995 parcels, weekly, has HOMESTEADFLAG, CHANGENOTICEADDRESS1-4, FAIRMARKETTOTAL, CDUDESC, SALEDATE). It is not ArcGIS, so the generic puller cannot read it.

Next:
- Add a small CKAN datastore reader (`data.wprdc.org/api/3/action/datastore_search_sql`) so parcels come from the weekly WPRDC assessment file; that makes the whole county live and fixes the stale snapshot. WPRDC also has Sheriff Sales (`adffb94b-...`, `21b22189-...`), tax liens and Property Sales Transactions (`5bbe6c55-...`) for a better buyer list.
- Buyer list: multi-parcel deeds repeat the full price on every parcel (e.g. one LLC with 53 "buys" at 3.75M); filter `saledesc` MULTI-PARCEL when the reader supports it.
- Westmoreland, Washington, Butler, Beaver counties: not searched.
