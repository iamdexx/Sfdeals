# Metro playbook: adding one metro to Sfdeals

You are adding ONE metro to https://github.com/iamdexx/Sfdeals, a public-records deal finder for real estate wholesalers.
Adding a metro means adding ONE file, `sfdeals/metro/configs/<key>.json`, plus `docs/sources-<key>.md`. Do not edit any other file
(no `index.html`, no `metros.py`, no workflow). Open a PR from branch `metro/<key>`. Do not commit anything under `data/`.

## 1. Read these first (5 minutes)
- `sfdeals/metro/metros.py` docstring (config shape), `sfdeals/metro/configs/phx.json`, `tpa.json`, `clt.json` (three working examples:
  separate signal layers, derived signals from parcel fields, city code enforcement layers).
- `sfdeals/metro/parcels.py` (`row()` field mapping, `addr_strip`, `occ_field`, `extra`), `signals.py`, `score.py` (`derived()` rules, `cash_buyers()`).
- `docs/sources-phx.md`, `docs/sources-tpa.md`, `docs/sources-clt.md` for how to write the source notes.

## 2. Find the sources (most of the work). Free, public, no login, no CAPTCHA, terms allow automated use.
Order of search for the principal county (and the biggest city):
1. County's own ArcGIS server: try `https://gis.<county>.gov/arcgis/rest/services`, `.../server/rest/services`, `maps.<county>...`, and the
   ArcGIS Hub API `https://hub.arcgis.com/api/v3/datasets?q=<county> parcels&filter[type]=Feature Service`. Also the county's open data portal
   (`data.<county>.gov`, `opendata-<county>.hub.arcgis.com`). You need a PARCEL layer with: parcel id, situs address, owner name, owner mailing
   address (street, city, state, zip), land use / property class, value, ideally year built or living area and last sale date/price.
   Residential single family is usually a land use code (Ohio 510, Florida DOR 01, Maricopa PUC 01xx, NC "SINGLE FAMILY RESIDENTIAL").
2. Distress signal layers keyed by parcel id or address, any of: treasurer delinquent tax or tax lien or tax sale lists, code enforcement cases
   (city folders named HNS, Accela, Code, DMD, Neighborhood Services), condemnations / unsafe structures / orders to demolish, vacant building
   registry, sheriff or trustee foreclosure sales, lis pendens. Also check the parcel layer itself for signal FIELDS (homestead flag, building
   condition, deed type, taxes owed, rental registration) and use `derived` rules for those.
3. Query every candidate with `?f=pjson` for fields and `/query?where=1%3D1&returnCountOnly=true&f=json` for counts, and pull 2 sample rows.
   Verify the parcel id in the signal layer matches the parcel layer's id format (strip spaces, dashes).
Do NOT scrape sites that block scripts or forbid it in their terms (Cloudflare challenges, CAPTCHA, "no automated access"). Note them as dead ends.
If after a real search no distress layer exists, ship the metro with parcels only (absentee + cash buyers) and say so in the notes.

## 3. Write the config
- `where`: residential land use AND a server-side absentee filter (mailing zip differs, or state differs, or no homestead) so the pull stays under
  ~300k rows / 10 minutes. Parcels that carry a signal are fetched by id afterwards, so the filter never hides them.
- `map`: tag, addr (may be a list of fields), zip, muni, owner, mail, mail_city, mail_state, mail_zip, landuse, units, year, res_sqft, value,
  sale_date, sale_price. Use `addr_strip` if the situs address carries a trailing city/state. Use `occ_field` for a homestead/owner-occupied field.
- `signals`: name, weight (demolish/condemned 40-45, tax sale 45, tax delinquent 30-35, housing code case 25, nuisance 15, vacant 15-30), label
  (short, plain English, no jargon), url, optional `where`, `map` with tag and addr plus any extra fields you want on the card.
- `derived`: rules on parcel fields (see tpa.json). `min_value`: a value floor that drops lots and shells (40000-80000 depending on the market).
- `ui`: copy the shape from an existing config. Keep the copy short, plain, no em dashes, no hype. `lookup` is an HTML snippet with `{tag}` or `{addr}`
  placeholders pointing at the county property record page. `sigs` lists filter words that appear in the signal labels, plus "absentee","out of state".
  `law` is one or two sentences on the state's wholesaling/assignment rules (judicial vs non-judicial foreclosure, attorney closing states, disclosure).
  `title_cos`, `groups`, `repairs`, `sos` (state business entity search link) are real local names and links. `contracts` is "mo" for now.

## 4. Test
`pip install -r requirements.txt`, then `python -m sfdeals.run <key> all`. It must finish in under 15 minutes and print `<key> score (hot, total)`
with hot > 0 (unless parcels-only). Check `data/<key>/leads.json`: the top 10 must be real houses with sensible values, correct absentee
flags (owner-occupied homes must not be flagged absentee: compare `mail` vs `addr` on a few), and readable `why` labels. Check
`data/<key>/buyers.json` has plausible LLC buyers. Run `python -m pytest -q tests`. Then `python -m sfdeals.site x` must still build.

## 5. Deliver
- `docs/sources-<key>.md`: working sources with URLs, counts, field notes, gotchas, dead ends, and what to look for next.
- Commit only the two files. Branch `metro/<key>`, PR title `metro: <City>, <ST> (<county>)`, body: sources used, hot lead count, median value,
  signal counts, anything parked. Do not commit `data/`.
- Report in your structured output: key, status (live / parcels-only / blocked), pr_url, hot, total, signals list, notes.
