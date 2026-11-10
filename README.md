# sfdeals

Off-market deal finder for Sioux Falls, SD and St. Louis, MO (city and county). Pulls public distress data every night, scores every 1-4 unit residential parcel, and gives you a phone-first CRM to work the list. Switch markets with the dropdown at the top of the app; call notes are kept per market.

Sioux Falls signals: absentee owner (city parcel layer), sheriff mortgage foreclosures (Minnehaha, Lincoln), code enforcement citations (city), delinquent property taxes (Minnehaha, December list).

St. Louis signals: absentee owner (city mailing address, county TENURE flag), city tax balance, city vacant building registry (year listed, open violations, unpaid fees), city building division inspections (condemnations, notices to secure, violation letters, accumulated nightly), sheriff land tax sale list when posted, county 2022 vacancy survey.

## Run
    pip install -r requirements.txt
    python -m sfdeals.run all        # both markets
    python -m sfdeals.run sf all     # or: sf parcels citations sheriff delinquent lincoln score
    python -m sfdeals.run stl all    # or: stl city_parcels county_parcels inspections vacant landtax county_vacant score
    python -m pytest tests

Data lands in `data/sf/` and `data/stl/` (committed by the nightly workflow, parcel dumps excluded). Open `index.html` over any static host (Vercel) to use the CRM. Call notes stay in the phone's browser; use Backup in the app.

## Law
Assigning your own purchase contract is not brokerage in SD (SDCL 36-21A-6, 36-21A-29) or MO (RSMo 339.010). Do not use option agreements in SD. Get the drafts in `docs/contracts/` reviewed by a local attorney before the first signature. Details in `docs/sources.md`, `docs/sources-stl.md` and `docs/contracts/README.md`.
