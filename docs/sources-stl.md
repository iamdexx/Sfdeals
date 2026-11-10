# St. Louis distress data sources (probed 2026-11-10)

Repo: https://github.com/iamdexx/Sfdeals (main). Vercel project "sfdeals" (team team_qoj8KCEJXcaB8GNp3bMJmM4D), prod alias sfdeals.vercel.app, deploy via CLI from repo root (static: index.html + data/).

## St. Louis City
| Source | URL | Notes | Status |
|---|---|---|---|
| Parcels (assessor, live) | https://maps6.stlouis-mo.gov/arcgis/rest/services/St_Louis_Parcels/MapServer/0/query | 134,305 rows, maxRecordCount 2000, pagination OK. Residential = AsrClassCode=100 (106k; land use 1110 SF 67k, 1120 2-fam 12.7k, 1010 vacant lot 10k, 1140 4-fam 4.5k, 1115/1114 condo-ish). Filter: AsrClassCode=100 AND VacantLot=0 AND NbrOfUnits BETWEEN 1 AND 4 -> 93,988. Fields: ParcelId, HANDLE, SITEADDR ('5860   MAFFITT AV ' with extra spaces), OWNERNAME/2, OWNERADDR/CITY/STATE/ZIP, OWNEROCC ('1' owner occ 48k, None 47.6k, '2','4','5','C','X'), VacBldgYear (>0 = on vacant building list; 16k res), TaxBalance (delinquent $; 11.5k res >0), LendingAgcy, AsdTotal, AprLand, CostAprImprove, ResSalePrice, ResSaleDate (epoch ms), FirstYearBuilt, NBRHD, ZIP, LRMSParcel (-1 default), IsAbatedProperty | WORKS |
| Parcel basic CSV | https://static.stlouis-mo.gov/open-data/PLANNING/parcels/parcels-basic-info.csv | 15 MB, no owner | n/a |
| Vacant buildings API | https://www.stlcitypermits.com/API/VacantBuilding/GetAllVacantBuildings (slow, >60s) and GetVacantBuildingOverview (keyed by HANDLE: {mo (months?), vmin, vmaj (minor/major violations), csb, unpd (unpaid $)}) | overview works fast | WORKS |
| Existing structure inspections (code enforcement) | https://www.stlcitypermits.com/API/HCES/GetExistingStructureInspections | 3.4 MB, ~1,100 rows, ONLY last 30 days (accumulate nightly). Fields: InspectionType (ES - Complaint...), ProjectAddress, ProjectASRParcelID (= ParcelId), ProjectHandle, CurrentResult (Violation Letter 617, Notice to Secure 95, Structural Condemnation 47, Condemned for Occupancy 19, Emergency CFO...), CurrentResultDate, OwnerName/Address, Violations[{ViolationType, ViolationSeverity Minor/Major, ViolationText}] | WORKS |
| 87/88 nuisance inspections | https://stlcitypermits.com/API/HCES/GetAllInspectionsReporting | probe | TBD |
| Sheriff land tax sale list | https://www.stlouis-mo.gov/government/departments/sheriff/documents/current-land-tax-sale-properties.cfm | PDF only posted 2 weeks before each sale (currently placeholder PDF). Parse when present. | PARTIAL |
| LRA inventory | https://static.stlouis-mo.gov/open-data/SLDC/REAL-ESTATE/LRA_INVENTORY.csv | 10k city-owned lots/buildings; exclude from leads (owner = LRA) | WORKS |
| Forestry service records (grass cuts by city) | https://www.stlouis-mo.gov/data/upload/data-files/forestry-service-records.csv | 294 MB, too big for nightly; skip | SKIP |
| CSB 311 | csb.zip 128 MB | skip v1 | SKIP |

## St. Louis County
| Source | URL | Notes | Status |
|---|---|---|---|
| Parcels | https://maps.stlouisco.com/hosting/rest/services/Maps/AGS_Parcels/MapServer/0/query | 401,620 rows, maxRecordCount 6000, pagination OK (0.4s/page). PROPCLASS 'R' 381k; LUCODE Single Family 351k, Duplex/Townhome 3.3k, Multi-Family 3k; TENURE 'OWNER' 284k / 'NOT OWNER' 117k (absentee flag!). Fields: LOCATOR (parcel id), OWNER_NAME, PROP_ADD, PROP_ZIP, OWN_ADD/CITY/STATE/ZIP, MUNICIPALITY, LIVUNIT, YEARBLT, RESQFT, TOTAPVAL, APPIMPVAL, DEEDTYPE, RECDATEDAILY, CAREOF, TAXYR. Filter: PROPCLASS='R' AND LIVUNIT BETWEEN 1 AND 4 -> 356,342. No tax balance field. | WORKS |
| Same data on AGOL | https://services2.arcgis.com/w657bnjzrjguNyOy/arcgis/rest/services/Pardata_Juris/FeatureServer/1 | 656k (incl. history?), maxRecordCount 2000 | backup |
| County vacant parcels 2022 | https://services2.arcgis.com/w657bnjzrjguNyOy/arcgis/rest/services/Vacany_Parcels_2022/FeatureServer/0 | static 2022 survey, fields USER_STATU, OWNER_NAME, PROP_ADD | maybe |
| Collector tax sale list (Aug) | stlouiscountymo.gov is behind Cloudflare (403 for curl and for Chrome over CDP after 30s), no archived PDF URL found. Used instead: Combined_Trustee_and_Post_Third FeatureServer/42 (AGOL, 1,557 rows, 304 with 1-4 living units, edited monthly): STATUS Post Third = failed 3 tax sales, still owned by taxpayer, offers via Collector; Trustee = deeded to County trustee | `stl/county_taxsale.py` | done |
| Trustee's sale notices (MO foreclosure = non-judicial) | mopublicnotices.com search works (ASP.NET AJAX: county postback then btnGo, follow pageRedirect) but every Details.aspx is CAPTCHA gated and the Terms of Use forbid automated collection, so not used. SouthLaw public report https://www.southlaw.com/app/uploads/report/Sales_Report_MO.pdf (statewide, county headers, 13-14 St. Louis rows) is parsed by `stl/trustee.py`. Millsap & Singer (bot check), Martin Leigh / mllfpc.com, Kozeny McCubbin / kmlegal.com, LOGS: no public sale list found | partial |

## Probe notes (cont.)
- GetAllVacantBuildings API: connection drops (000) after 60-170s; do NOT use. Use parcel VacBldgYear + GetVacantBuildingOverview (fast JSON keyed by HANDLE).
- GetAllInspectionsReporting: 16.8 MB, 8,502 rows, last 90 days (2026-08-12..), types Housing Conservation 5,172 (occupancy inspections, not distress), ES - Complaint 2,919, ES - HCD 196, Tornado 108, Emergency 51, TR-ROE-DEMO 18. Same schema as GetExistingStructureInspections. Use GetExistingStructureInspections nightly (30 days, 3.4 MB) and accumulate; dedupe on InspectionID.
- mopublicnotices.com: St. Louis = lstCounty$102 (covers city+county). Flow that returns results: GET Search.aspx (session in URL), AJAX postback of the county checkbox (X-MicrosoftAjax: Delta=true, ctl00$ToolkitScriptManager1=...upSearch|target, __ASYNCPOST=true), then btnGo, then GET the pageRedirect URL. Detail pages are CAPTCHA gated and ToS bans scraping: do not automate.
- County collector: website unreachable for scripts; the AGOL post-third/trustee layer is the only machine-readable tax sale data. The annual August sale list itself is only in the Countian.
