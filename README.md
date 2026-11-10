# sfdeals

Off-market deal finder for Sioux Falls, SD and St. Louis, MO (city and county). Pulls public distress data every night, scores every 1-4 unit residential parcel, and gives you a phone-first CRM to work the list. Switch markets with the dropdown at the top of the app; call notes are kept per market.

Sioux Falls signals: absentee owner (city parcel layer), sheriff mortgage foreclosures (Minnehaha, Lincoln), code enforcement citations (city), delinquent property taxes (Minnehaha, December list).

St. Louis signals: absentee owner (city mailing address, county TENURE flag), city tax balance, city vacant building registry (year listed, open violations, unpaid fees), city building division inspections (condemnations, notices to secure, violation letters, accumulated each run), sheriff land tax sale list when posted, county 2022 vacancy survey, county tax sale leftovers (post third sale and trustee parcels, official ArcGIS layer), trustee foreclosure sales from SouthLaw's public Missouri sale report, and city pre-foreclosures from the Recorder of Deeds index (successor trustee appointments and notices of sale, recorded weeks before the newspaper notice).

## Run
    pip install -r requirements.txt
    python -m sfdeals.run all        # both markets
    python -m sfdeals.run sf all     # or: sf parcels citations sheriff delinquent lincoln score
    python -m sfdeals.run stl all    # or: stl city_parcels county_parcels inspections vacant landtax county_vacant score
    python -m pytest tests

Data lands in `data/<market>/` (committed by the heartbeat workflow, one job per market in parallel, every 2 hours 6am to 10pm Central, parcel dumps excluded). Open `index.html` over any static host (Vercel) to use the CRM. Call notes stay in the phone's browser; use Backup in the app.

## Law
Assigning your own purchase contract is not brokerage in SD (SDCL 36-21A-6, 36-21A-29) or MO (RSMo 339.010). Do not use option agreements in SD. Get the drafts in `docs/contracts/` reviewed by a local attorney before the first signature. Details in `docs/sources.md`, `docs/sources-stl.md` and `docs/contracts/README.md`.

## Adding a metro

Metros other than Sioux Falls and St. Louis are config, not code: one entry in `sfdeals/metro/metros.py`
naming the county's ArcGIS parcel layer (field map, residential + absentee `where`) and any signal layers
keyed by parcel number (tax liens, tax sale, code cases, vacancy). Then add the market block in `index.html`.
`python -m sfdeals.run <key> all` pulls signals, parcels (absentee filter plus every parcel with a signal) and scores.
Phoenix (`phx`, Maricopa County: assessor parcels, delinquent tax and state held lien lists) and Tampa (`tpa`, Hillsborough County: appraiser parcels with homestead, condition and deed type signals) are the first config-driven metros. Signals can come from separate layers (`signals`) or from fields on the parcel record (`derived`).

## Public site (SEO)

`python -m sfdeals.site <site-url>` writes a static marketing site into `site/` (gitignored): home, metros index, one page per metro and per signal with live counts and a sitemap. The heartbeat `site` job rebuilds it after every pull and deploys to Cloudflare Pages (`deals-site`) when the `CLOUDFLARE_API_TOKEN` repo secret exists.
