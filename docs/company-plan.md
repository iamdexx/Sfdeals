# Company plan: off-market deal intelligence, nationwide, at $0 infrastructure

Working names (pick one, all .com checks needed): **Parcelhawk**, **Distress Signal**, **Deedline**.
This document is written as if we are building a multi-million dollar company. Short sentences, real numbers, no hand-waving.

## 1. What the company is

A subscription data product for real estate wholesalers, flippers and small landlords. It watches public records in every US metro, finds owners who are about to lose or dump a house (pre-foreclosure filings, tax sales, condemnations, vacancy, probate), ranks them, and gives the user a phone-first CRM to work the list. The edge is **time**: we surface the owner 2 to 8 weeks before the competition sees the newspaper notice or the MLS.

Proof point from St. Louis: the City Recorder feed flagged 5037 Steffens Ave on Oct 13; it hit the trustee sale list on Nov 19. Five weeks of lead time, from free public data, refreshed every 2 hours.

Who pays: 150k to 200k active wholesalers and small investors in the US. Incumbents (PropStream $99, DealMachine $99 to $299, BatchLeads $77 to $299, Propelio, REISift) sell national lists refreshed weekly or monthly, on desktop, with no early-signal feeds and a learning curve. We sell: same-day signals, phone-first, one tap to call, a playbook for beginners.

## 2. Product

Three tiers, one codebase.

| | Starter $49/mo | Pro $99/mo | Team $249/mo |
|---|---|---|---|
| Metros | 1 | 3 | 10 |
| Heartbeat | daily | every 2 hours | every 2 hours |
| Signals | all public signals | all + pre-foreclosure recorder feeds | all |
| CRM seats | 1 | 1 | 5 |
| Skip trace | pay as you go, $0.15/hit | $0.12/hit | $0.10/hit |
| Exports | 500 rows/mo | 5,000 | unlimited |
| Alerts | daily email | push + SMS on new pre-foreclosure | push + SMS, shared inbox |

Annual plans at 2 months free. 7-day trial, card required. Skip trace is pass-through with margin (we pay about $0.02 to $0.10 per hit).

Core product surfaces:
1. **Today**: held call list, follow-ups due, new pre-foreclosures since yesterday. Nothing moves until the user taps Refresh.
2. **Leads**: ranked list with filters by signal, value band, equity, owner type, map view, saved searches.
3. **Lead card**: owner, mailing address, phones with DNC flags, every signal with the source document, comps link, offer calculator, one-tap call, text, log.
4. **Pipeline**: called, talking, offer, contract, closed, dead. Shared on Team.
5. **Buyers**: cash buyer list per metro, seeded from recorder cash sales (deeds with no deed of trust) which we already parse.
6. **Playbook**: the 6-step script and contract drafts per state (attorney reviewed before sale, see Legal).

Mobile: installable PWA on day one (home screen icon, push), native wrappers via Capacitor for App Store and Google Play in month 4. Same code.

## 3. Architecture at $0

Design rule: no server we pay for until revenue pays for it. Everything below has a free tier that carries us to roughly 1,000 paying users.

```
GitHub Actions (public repo, free, unlimited)      -> pulls + scoring per metro, every 2h
  writes data/<metro>/leads.json + signals          -> committed to repo (history = audit trail)
Cloudflare Pages (free, commercial OK)              -> app + SEO site, static + edge functions
Cloudflare R2 (10 GB free)                           -> leads.json per metro served to the app (moves off git when > 1 GB)
Supabase free (Postgres 500 MB, Auth, Realtime)      -> users, subscriptions, notes, held lists, buyers, call logs
Stripe (no fixed fee)                                -> billing, metered skip trace credits
Resend (3k emails/mo free), Web Push (free)          -> alerts
Tracerfy API (user-funded credits)                   -> skip trace
Plausible CE on Cloudflare or GA4 (free)             -> analytics
```

Why this holds up:
- Data is read-mostly and public. Static JSON on a CDN beats a database for it. One file per metro per signal, 1 to 3 MB gzipped, cached at the edge.
- User data is tiny: notes, statuses, held lists. 500 MB in Supabase is years of it.
- Compute is the scrapers. A metro costs 3 to 6 minutes of Actions time per run. Public repo makes that free at any scale; at 50 metros and 9 runs a day that is about 45 hours a day of runner time, still free. If GitHub ever pushes back, the same containers run on Oracle Cloud's always-free ARM VMs (4 cores, 24 GB) at $0.
- Public repo means open code. Accept it: the moat is the adapter library, the data history, the brand and the SEO footprint, not the Python. Keep scoring weights and the skip-trace margin logic in a private config repo if it ever matters.

Breakpoints and the next step when hit:
- Supabase > 500 MB or > 50k MAU: Supabase Pro $25/mo.
- Repo > 1 GB of data: move leads.json to R2 (still free to 10 GB), keep code history clean.
- Need sub-hour latency on recorder feeds: Cloudflare Workers cron (free, 100k requests/day) for the light JSON APIs like Fidlar.

## 4. Data strategy: every metro without hand-building every county

The St. Louis build taught the pattern: counties do not build their own systems, they buy from a short list of vendors. We build **one adapter per vendor**, then each county is a config entry (URL, layer id, field map). Target: 80% of US population from about 15 adapters.

| Record type | Vendors covering most of the US | Adapter status |
|---|---|---|
| Parcels, owner, mailing address, owner-occupied | Esri ArcGIS REST (thousands of counties), Schneider Beacon/qPublic, Tyler iasWorld, Patriot, Vision | ArcGIS done (SF, STL city, STL county). Beacon next. |
| Tax delinquency, tax sale lists | DEVNET wEdge, Tyler, GovTech, county PDFs | PDF parser done (SD, STL city). DEVNET blocked by Cloudflare in STL; works elsewhere. |
| Recorder (pre-foreclosure, lis pendens, deeds) | Fidlar Direct Search/Laredo, Landmark Web, Tyler Eagle, Cott, GovOS/Kofile, Avenu | Fidlar done (STL city). Landmark next (huge share of the Midwest and South). |
| Code enforcement, vacant buildings, condemnations | Accela Citizen Access, Tyler EnerGov, OpenGov, Socrata/open data portals, ArcGIS | Custom done for STL; Accela and Socrata adapters next (cover most big cities). |
| Foreclosure sales | Judicial states: court dockets (Tyler Odyssey, sheriff sale pages). Non-judicial: trustee firm reports, recorder notices | Sheriff PDF (SD), SouthLaw report (MO) done. Odyssey and Xome/Auction.com public calendars next. |
| Probate, eviction, divorce | State court portals (Odyssey, re:SearchTX, eCourts) | Later; ToS review per state. |
| Utility shutoffs, water liens | City open data where published | Opportunistic. |

Rollout order by wholesaler demand and data openness: Phoenix, Dallas-Fort Worth, Houston, Atlanta, Tampa, Orlando, Jacksonville, Charlotte, Indianapolis, Columbus, Kansas City, Memphis, Birmingham, Cleveland, Detroit, Chicago, Philadelphia, Baltimore, St. Louis (done), Sioux Falls (done). Texas, Florida, Georgia and Arizona are open-records states with excellent portals; start there.

Coverage promise to customers: every metro ships with parcels + owner + absentee + tax status. Recorder and code feeds are listed per metro with a green/yellow/red badge so nobody is surprised. Users can request a metro; 100 requests triggers a build.

Paid data later, not now: Regrid (parcels nationwide, from $0 for the API trial to roughly $1k/mo) or ATTOM once ARR > $50k/mo, to fill gaps and add mortgage and equity. Priced into Pro.

Quality rules (learned the hard way in St. Louis): a lead needs a real distress signal, not just absentee; current-year tax bills are not delinquency; value floors to drop shells; vacancy weighted by age; investor owners down-ranked; the user's working list is frozen until they ask for new leads.

## 5. Go-to-market

1. **Programmatic SEO** (month 1 onward, $0): one page per metro per signal, generated from live data with real counts: "Pre-foreclosures in St. Louis, MO: 178 filed in the last 120 days", "Tax sale properties in Jackson County". Sitemap, schema.org Dataset markup, internal links, weekly auto-updated. 50 metros × 8 signals = 400 pages that nobody else has with live numbers. This is the cheapest acquisition channel in the category.
2. **Founder content**: the St. Louis story, the week-one interested sellers, YouTube shorts and TikTok of real calls (with consent) using the existing autoclipper pipeline. Wholesaling content is a huge niche on both platforms.
3. **Communities**: BiggerPockets, local REIA meetups (St. Louis and Sioux Falls first), wholesaling Facebook groups and Discords. Offer a free metro report PDF generated from the data as the lead magnet.
4. **Partnerships**: title companies and hard money lenders in each metro (they want deal flow), skip-trace vendor co-marketing, REIA sponsorships at $200 to $500.
5. **Referral**: one month free per paying referral, built into the app.
6. **Paid ads**: only after SEO and content show CAC under $150. Search ads on "pre-foreclosure list <city>" convert well in this niche.

Targets: 100 trials in month 2, 25% trial to paid, 5% monthly churn by month 6, LTV about $1,500 at $79 blended ARPU.

### Affiliate program (built into Phase 1 with billing)

Influencers and REIA leaders drive most new wholesalers, so paying them is the cheapest channel we have.
- 30% recurring commission for the first 12 months of every referred subscription (industry standard; DealMachine and BatchLeads pay in this range). Flat $20 per skip trace credit pack referred.
- Referral link (`?ref=code`, 60-day cookie) plus a code the influencer can say on camera; code wins if both exist.
- Attribution stored as Stripe customer metadata; commissions computed from paid invoices only, 30 days after payment (refund window), so trials and chargebacks never pay out.
- Affiliate dashboard: clicks, trials, paid, churned, pending and paid commissions, downloadable W-9 flow at $600 a year (IRS requirement).
- Payouts monthly through Stripe Connect Express (or PayPal for those who prefer it), $50 minimum.
- Co-marketing kit: metro report PDFs, screenshots, a 60-second demo, their own free Pro account.
- Fraud rules: no self-referral, no coupon-site listings, commission clawback on refunds.
- Tiering later: 35% at 50 active referrals, 40% at 200. White-label option for REIAs in Phase 5.

## 6. Financial model (conservative)

| Month | Paying users | MRR | Infra cost |
|---|---|---|---|
| 3 | 40 | $3k | $0 |
| 6 | 250 | $20k | $25 (Supabase Pro) |
| 12 | 1,000 | $85k | $300 |
| 18 | 2,500 | $210k | $1,500 (paid parcel data, support tooling) |
| 24 | 4,500 | $380k | $3k |

$4.5M ARR at month 24 with 4,500 users is 2 to 3% of the addressable wholesaler base. Skip trace margin adds roughly 10% on top. Gross margin stays above 90% because the data is public and the infra is free or near free. The model is sensitive to churn: wholesalers quit the business often, so onboarding to a first contract fast (the playbook) is a retention feature, not a nicety.

Funding: none needed to reach $20k MRR. Optional seed of $500k to $1M at month 6 to hire ahead on data adapters and sales, or stay bootstrapped.

## 7. Legal and compliance (non-negotiable for a company)

- **TCPA, DNC, TCPA litigator flags**: show flags on every number, block one-tap calling of DNC numbers by default with an override that logs consent basis, no built-in SMS blasting. Terms require users to comply; we log what we showed them.
- **Terms of service and data licensing**: we redistribute public records and derived scores. Keep every source documented with its public URL and terms (we already do in docs/sources-*.md). Do not scrape sites whose terms forbid it (we dropped mopublicnotices.com for exactly this). No CAPTCHA bypass, ever.
- **FCRA**: never market this for tenant, employment or credit screening. Say so in the terms, like every skip-trace vendor does.
- **State wholesaling rules**: contract drafts per state reviewed by a licensed attorney before they ship inside a paid product; flag states that require disclosure or a license to market contracts (Oklahoma, Illinois, Pennsylvania, South Carolina, Kansas, Arkansas and others changing yearly).
- **Privacy**: CCPA/CPRA applies once revenue or data volume crosses thresholds; opt-out page for property owners who ask to be removed, honored across all metros within 10 days.
- **Entity**: Delaware C-corp if raising, otherwise an LLC in the home state. Trademark the name once chosen.

## 8. Team and hiring order

Month 0 to 6: founder (sales, content, product calls) plus Devin for engineering. Month 6: part-time support/success person (onboarding calls are the retention lever). Month 9: data engineer for adapters and QA across metros. Month 12: growth marketer for SEO and content. Month 15: account exec for Team plans and partnerships. Keep headcount under 6 through $2M ARR.

## 9. Roadmap

**Phase 1, weeks 1 to 3: sellable v1.** Name and domain. Supabase auth with magic links. Notes, statuses, held lists and buyers saved to the cloud per user, synced across devices. Stripe checkout, trial, metering for skip trace. Landing page. Cloudflare Pages deploy. Terms, privacy, DNC handling. Sioux Falls and St. Louis live.

**Phase 2, weeks 4 to 8: metros and SEO.** ArcGIS and Beacon parcel adapters as config. Fidlar and Landmark recorder adapters. Accela and Socrata code enforcement adapters. 10 metros live (TX, FL, GA, AZ, IN, OH first). SEO site generated from data, 80+ pages. Metro request queue.

**Phase 3, weeks 9 to 12: product depth.** Redesign on a design system (two directions mocked first). Map view, saved searches, equity estimate from last sale and assessed value, push alerts on new pre-foreclosures, Capacitor builds to both stores, referral program.

**Phase 4, months 4 to 6: scale.** 25 metros. Team plans with shared pipeline. Cash buyer lists from recorder deed data. Weekly metro email reports. Partnerships program.

**Phase 5, months 7 to 12: 50 metros, paid data layer, API for power users, white-label for REIAs and title companies.**

## 10. Metrics that run the company

Activation: user logs 5 calls in the first 7 days. Retention: percent of users with a call log in the last 14 days. Data: freshness per metro (hours since last successful pull, red if over 8), signal coverage per metro, lead quality score (percent of called leads marked "talking" or better). Revenue: trial to paid, churn, ARPU, skip trace attach rate. Unit cost: Actions minutes per metro per day, support hours per 100 users.

## 11. Decisions needed now

1. Name (Parcelhawk / Distress Signal / Deedline / your own) and domain.
2. Entity type (LLC now, convert later, is the cheap default).
3. Launch metro order beyond St. Louis and Sioux Falls (my pick: Phoenix, Dallas, Atlanta, Tampa, Indianapolis).
4. Go for Phase 1 this week.
