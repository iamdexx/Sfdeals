# sfdeals

Off-market deal finder for Sioux Falls, SD. Pulls public distress data every night, scores every residential parcel, and gives you a phone-first CRM to work the list.

Signals: absentee owner (city parcel layer), sheriff mortgage foreclosures (Minnehaha, Lincoln), code enforcement citations (city), delinquent property taxes (Minnehaha, December list).

## Run
    pip install -r requirements.txt
    python -m sfdeals.run all        # or: parcels citations sheriff delinquent lincoln score
    python -m pytest tests

Data lands in `data/` (committed by the nightly workflow). Open `index.html` over any static host (Vercel) to use the CRM. Call notes stay in the phone's browser; use Backup in the app.

## Law
Assigning your own purchase contract is not brokerage in SD (SDCL 36-21A-6, 36-21A-29). Do not use option agreements. Get the two drafts in `docs/contracts/` reviewed by a local attorney before the first signature. Details in `docs/sources.md`.
