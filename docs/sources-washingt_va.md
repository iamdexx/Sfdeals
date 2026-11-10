# Washington (District of Columbia) sources

The metro's principal county is Fairfax County, VA, but Fairfax publishes no owner names or mailing addresses in bulk, so the metro
runs on the District of Columbia, which does. Config `state` is `DC` so in-District owners are not flagged out of state; `ui.st` stays `VA` as the metro list has it.

Working, free, unattended:
- DC Office of Tax and Revenue public extract (ITSPE), `maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Property_and_Land_WebMercator/MapServer/53`
  (221,699 rows, refreshed about weekly, max 2000 per page). Owner (`OWNERNAME`), billing address (`ADDRESS1`, `CITYSTZIP`), homestead (`HSTDCODE`),
  tax class (`CLASSTYPE`), assessed value (`ASSESSMENT`), last sale (`SALEPRICE`, `SALEDATE`), balances per year (`PY1BAL`.., `TOTBALAMT`) and tax sale flags (`PY1TXSALE`, `CY1TXSALE`).
  - Single family is `USECODE IN ('011','012','013')` (row, detached, semi-detached), `DELCODE = 'N'` for live lots: 94,171.
  - Absentee pull: `HSTDCODE IS NULL` (no homestead), 29,881 rows, about 20 seconds. Rows whose billing street equals the house address are dropped by the scorer, leaving about 14k absentee.
  - Signals are queries on the same layer, joined by `SSL` (square and lot, space padded like `0784    0026`):
    blighted `CLASSTYPE = '4'` (148), vacant `CLASSTYPE = '3'` (1,082), tax sale flag on last or this year (about 330), last year's balance `PY1BAL >= 1000` (882).
- Test run: 2,444 signal rows, 30,534 parcels, 1,963 hot of 13,985 leads, median assessed value of hot leads $589,510, 61 cash buyers.

Gotchas:
- `PREMISEADD` carries a trailing `WASHINGTON DC 20020-6920`; removed with `addr_strip`. There is no separate situs zip field.
- Billing city, state and zip are one field (`CITYSTZIP`, `SILVER SPRING MD 20910-1253`). It is mapped to `mail_city`, so the card shows the whole line and
  `mail_state` is empty: the "out of state" tag never fires for this metro. A splitter in `parcels.row()` would fix it.
- No year built or living area on this layer (`RESIDENTIAL (CAMA)`, layer 25, has `AYB`, `GBA`, `CNDTN_D` by SSL but is a separate table), so the house test is the street number plus the use code.
- Tax sale flag values (`RS`, `RR`, `3Y`, `4Y`) are not defined in the layer's data dictionary (layer 66); the label only says a flag is on the record.
- Homestead codes `1` and `5` are the common ones; `3` and `7` also appear on owner-occupied homes.
- MyTax DC has no deep link by lot, so the lookup link opens the portal and the card shows the square and lot to type in. DC CorpOnline needs a free login.

Dead ends:
- Fairfax County, VA: `Tax_Administration_Real_Estate_*` tables on `services1.arcgis.com/ioennV6PpG5Xodq0` (parcels, legal, dwelling, sales, assessed values, keyed by `PARID`)
  and `www.fairfaxcounty.gov/mercator` and `/euclid` servers carry address, land use, year built, condition (`CDU_DESC`), sales and values, but no owner or mailing address anywhere.
- Loudoun County, VA `logis.loudoun.gov/gis/rest/services/COL/LandRecords`: parcel geometry only, no owner.
- No DC code enforcement or notice of infraction layer found on `maps2.dcgis.dc.gov` `DCGIS_DATA`.

Next:
- Prince William County, VA `gisweb.pwcva.gov/arcgis/rest/services/CountyMapper/LandRecords/MapServer/4` (157k) has owner, mailing address split into city, state, zip,
  use code and living area, but no value, sale price or distress field. Needs a per-county `state` in the config before it can share a metro with DC.
- Maryland (Montgomery, Prince George's): the state iMAP parcel service did not answer during this search; SDAT data has owner, mailing address and owner-occupied code.
- Fairfax `PLUS/PLUSGISRecords/FeatureServer/3` (enforcement records) and `CDU_DESC` condition are usable signals if an owner source for Fairfax turns up.
- DC: join CAMA layer 25 for year built, size and condition; flats and conversions are use codes `023` and `024`; DOB vacant building list and Recorder of Deeds foreclosure notices.
