"""Build the public marketing/SEO site into site/: one page per metro and per signal, with live counts
from data/<market>/leads.json. Static, no framework. python -m sfdeals.site"""
import datetime as dt
import html
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from .markets import MARKETS
from .util import ROOT

OUT = ROOT / "site"
APP = "https://sfdeals.vercel.app"
BRAND = "Deals"
SIGNAL_COPY = {
    "pre-foreclosure": ("Pre-foreclosure", "The lender has recorded a successor trustee or a notice of sale. The newspaper notice and auction usually follow in 3 to 8 weeks. The owner can still sell."),
    "trustee sale": ("Trustee sale scheduled", "A foreclosure auction date is set. Two to four weeks of lead time to reach the owner."),
    "tax sale": ("Tax sale", "The county has already offered the parcel at tax sale, or it is headed there. Years of unpaid taxes."),
    "tax delinquent": ("Tax delinquent", "Property tax balance more than a year behind."),
    "delinquent tax": ("Delinquent tax, lien list", "On the county treasurer's delinquent list; the lien was or will be sold at auction."),
    "tax lien unsold": ("Tax lien unsold, state held", "Nobody bought the lien at auction. The most distressed parcels on the list."),
    "vacant": ("Vacant building", "On the city's vacant building registry or the county vacancy survey."),
    "condemned": ("Condemned", "The building division has condemned the structure."),
    "code violation": ("Code violations", "Open building code violation letters in the last 18 months."),
    "sheriff": ("Sheriff sale", "Mortgage foreclosure sale scheduled with the sheriff."),
    "citation": ("Code citations", "City code enforcement citations on the property."),
    "condition poor": ("Condition poor", "The appraiser's own field inspection rated the building Poor."),
    "estate": ("Estate transfer", "Personal representative or guardian deed in the last 2 years. Heirs who may want out."),
    "quit claim": ("Quit claim transfer", "Quit claim deed in the last 2 years, often a family or distress transfer."),
    "absentee": ("Absentee owner", "The tax bill goes somewhere other than the house."),
    "out of state": ("Out of state owner", "The owner's mailing address is in another state."),
}
STATE = {"sf": ("Sioux Falls", "SD"), "stl": ("St. Louis", "MO"), "phx": ("Phoenix", "AZ"), "tpa": ("Tampa", "FL")}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def page(title, desc, body, path, canonical):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<style>body{{margin:0;background:#0f1115;color:#f2f4f8;font:17px/1.5 -apple-system,system-ui,sans-serif}}main{{max-width:760px;margin:0 auto;padding:24px 16px 60px}}a{{color:#3ddc84}}
h1{{font-size:30px;line-height:1.2;margin:8px 0}}h2{{font-size:22px;margin:28px 0 8px}}.big{{font-size:44px;font-weight:700;color:#3ddc84}}.mut{{color:#8b93a3}}
.card{{background:#1a1d24;border:1px solid #2a2f3a;border-radius:12px;padding:14px 16px;margin:10px 0}}.cta{{display:inline-block;background:#3ddc84;color:#000;font-weight:700;padding:12px 18px;border-radius:10px;text-decoration:none;margin:10px 0}}
table{{width:100%;border-collapse:collapse}}td,th{{text-align:left;padding:8px 4px;border-bottom:1px solid #2a2f3a}}nav a{{margin-right:14px}}</style></head>
<body><main><nav><a href="/">Home</a><a href="/metros/">Metros</a><a href="{APP}">Open the app</a></nav>{body}
<p class="mut" style="margin-top:40px">Public records only. Not a consumer report, not for credit, tenant or employment screening. Call rules: honor Do Not Call requests.</p></main></body></html>"""


def signal_counts(leads):
    c = Counter()
    for l in leads:
        seen = set()
        for w in l.get("why", []):
            for key in SIGNAL_COPY:
                if key in w and key not in seen:
                    seen.add(key); c[key] += 1
    return c


def build():
    OUT.mkdir(exist_ok=True)
    (OUT / "metros").mkdir(exist_ok=True)
    urls, metro_rows = [], []
    today = dt.date.today().isoformat()
    for key, m in MARKETS.items():
        f = ROOT / "data" / key / "leads.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        leads = d.get("leads", [])
        city, st = STATE.get(key, (m["name"], ""))
        counts = signal_counts(leads)
        mslug = slug(f"{city} {st}")
        mdir = OUT / "metros" / mslug
        mdir.mkdir(parents=True, exist_ok=True)
        updated = d.get("updated", "")[:16].replace("T", " ") + " UTC"
        rows = "".join(f'<tr><td><a href="/metros/{mslug}/{slug(k)}/">{html.escape(SIGNAL_COPY[k][0])}</a></td><td>{v:,}</td></tr>' for k, v in counts.most_common())
        body = f"""<p class="mut">{city}, {st}</p><h1>Distressed property leads in {city}, {st}</h1>
<div class="card"><div class="big">{d.get('hot', 0):,}</div><div>houses with a real distress signal right now<br><span class="mut">updated {updated}, refreshed every 2 hours from public records</span></div></div>
<a class="cta" href="{APP}/?m={key}">Open the {city} list</a>
<h2>By signal</h2><table>{rows}</table>
<h2>Where the data comes from</h2><p class="mut">{html.escape(m.get('sources', ''))}</p>
<h2>How wholesalers use it</h2><p>Call the owners most likely to sell, agree on a price in writing, assign the contract to a cash buyer. The app holds your call list steady, logs every call, and gives you the follow-up date. Phone numbers are added on demand with prepaid skip trace credits.</p>"""
        title = f"{city} {st} distressed property leads: {d.get('hot', 0):,} houses, updated every 2 hours"
        desc = f"Pre-foreclosure, tax sale, vacant and absentee owner leads in {city}, {st} from public records, refreshed every 2 hours. {d.get('hot', 0):,} houses with a distress signal today."
        (mdir / "index.html").write_text(page(title, desc, body, f"/metros/{mslug}/", f"{{SITE}}/metros/{mslug}/"))
        urls.append(f"/metros/{mslug}/")
        metro_rows.append((city, st, mslug, d.get("hot", 0)))
        for k, v in counts.items():
            name, blurb = SIGNAL_COPY[k]
            sdir = mdir / slug(k)
            sdir.mkdir(exist_ok=True)
            sample = [l for l in leads if any(k in w for w in l.get("why", []))][:5]
            ex = "".join(f'<tr><td>{html.escape(l["addr"].title())}</td><td>{html.escape((l.get("muni") or "").title())}</td><td>{l["score"]}</td></tr>' for l in sample)
            body = f"""<p class="mut"><a href="/metros/{mslug}/">{city}, {st}</a></p><h1>{html.escape(name)} properties in {city}, {st}</h1>
<div class="card"><div class="big">{v:,}</div><div>houses tagged "{html.escape(name.lower())}" right now<br><span class="mut">updated {updated}</span></div></div>
<p>{html.escape(blurb)}</p><a class="cta" href="{APP}/?m={key}">See the full list in the app</a>
<h2>Examples from the list</h2><table><tr><th>Address</th><th>City</th><th>Score</th></tr>{ex}</table>
<p class="mut">Owner names, mailing addresses and the full ranked list are in the app.</p>"""
            title = f"{name} properties in {city}, {st}: {v:,} today"
            desc = f"{v:,} {name.lower()} houses in {city}, {st} from public records, updated every 2 hours. {blurb}"
            (sdir / "index.html").write_text(page(title, desc, body, f"/metros/{mslug}/{slug(k)}/", f"{{SITE}}/metros/{mslug}/{slug(k)}/"))
            urls.append(f"/metros/{mslug}/{slug(k)}/")
        # seller landing page per metro
        sdir = OUT / "sell" / mslug
        sdir.mkdir(parents=True, exist_ok=True)
        sell = f"""<p class="mut">{city}, {st}</p><h1>Sell your {city} house as is, for cash, on your timeline</h1>
<p>No repairs, no showings, no agent fees. Tell us about the house and a local buyer calls you back the same day with a fair cash offer. Behind on taxes, inherited a house, tired of tenants, facing foreclosure: we have seen it all and we can close in as little as 2 weeks or on the date you pick.</p>
<form class="card" method="post" action="/api/inbound" onsubmit="return send(event)">
<input type="hidden" name="market" value="{key}"><input type="text" name="website" style="display:none" tabindex="-1" autocomplete="off">
<label>Property address<br><input name="address" required placeholder="123 Main St, {city}"></label><br>
<label>Your name<br><input name="name" placeholder="First and last"></label><br>
<label>Phone<br><input name="phone" type="tel" required placeholder="(555) 555-5555"></label><br>
<label>Email (optional)<br><input name="email" type="email"></label><br>
<label>What is going on with the house? (optional)<br><textarea name="situation" rows="3"></textarea></label><br>
<label style="font-size:14px"><input type="checkbox" name="consent" value="1" required> You may call or text me about my property. Message and data rates may apply. Reply STOP to opt out.</label><br>
<button class="cta" type="submit">Get my cash offer</button><div id="msg" class="mut"></div></form>
<h2>How it works</h2><ol><li>You send the address.</li><li>We call within a few hours, ask a few questions, and make an as-is cash offer.</li><li>You pick the closing date. A local title company handles the paperwork and pays you.</li></ol>
<style>input,textarea{{width:100%;box-sizing:border-box;background:#0f1115;color:#f2f4f8;border:1px solid #2a2f3a;border-radius:8px;padding:10px;font-size:16px;margin:4px 0 10px}}label{{display:block}}</style>
<script>async function send(e){{e.preventDefault();const f=e.target,b=Object.fromEntries(new FormData(f).entries());b.consent=!!b.consent;const m=document.getElementById('msg');m.textContent='Sending...';
const r=await fetch('/api/inbound',{{method:'POST',headers:{{'content-type':'application/json'}},body:JSON.stringify(b)}});m.textContent=r.ok?'Got it. Expect a call shortly.':'Something went wrong, call or text us instead.';if(r.ok)f.reset();return false}}</script>"""
        (sdir / "index.html").write_text(page(f"Sell my house fast in {city}, {st}: cash offer, as is, close in 2 weeks", f"Sell your {city} house as is for cash. No repairs, no fees, close on your date. Get a cash offer today.", sell, f"/sell/{mslug}/", f"{{SITE}}/sell/{mslug}/"))
        urls.append(f"/sell/{mslug}/")
    fn = Path(__file__).parent / "pages_functions"
    if fn.exists():
        shutil.copytree(fn, OUT / "functions", dirs_exist_ok=True)
    metro_list = "".join(f'<div class="card"><a href="/metros/{s}/"><b>{c}, {st}</b></a> · {h:,} distressed houses</div>' for c, st, s, h in metro_rows)
    (OUT / "metros" / "index.html").write_text(page(f"{BRAND}: metros", "Every metro we cover, with live counts.", f"<h1>Metros</h1>{metro_list}<p class='mut'>Want your metro? Request it in the app.</p>", "/metros/", "{SITE}/metros/"))
    total = sum(h for *_, h in metro_rows)
    home = f"""<h1>Today's distressed owners, before anyone else calls them</h1>
<p>Public records in each metro, pulled every 2 hours: pre-foreclosure filings, tax liens, condemnations, vacant buildings, estate transfers. Ranked, with a phone-first call list that never reshuffles under you.</p>
<div class="card"><div class="big">{total:,}</div><div>houses with a distress signal across {len(metro_rows)} metros right now</div></div>
<a class="cta" href="{APP}">Open the app, free</a>
<h2>Metros</h2>{metro_list}
<h2>Why it beats a monthly list</h2><p>PropStream and the national list sellers refresh weekly or monthly from aggregators. We read the county's own records every 2 hours, so a successor trustee filed this morning is on your list this afternoon, weeks before the newspaper notice.</p>"""
    (OUT / "index.html").write_text(page(f"{BRAND}: distressed property leads updated every 2 hours", f"{total:,} distressed houses across {len(metro_rows)} metros, from public records, refreshed every 2 hours. Phone-first CRM for wholesalers.", home, "/", "{SITE}/"))
    urls.insert(0, "/")
    urls.insert(1, "/metros/")
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{{SITE}}{u}</loc><lastmod>{today}</lastmod></url>" for u in urls) + "</urlset>")
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    return len(urls)


def finalize(site_url):
    """Replace the {SITE} placeholder once the deploy URL is known."""
    for f in OUT.rglob("*"):
        if f.is_file() and f.suffix in (".html", ".xml", ".txt"):
            f.write_text(f.read_text().replace("{SITE}", site_url.rstrip("/")))


if __name__ == "__main__":
    import sys
    n = build()
    finalize(sys.argv[1] if len(sys.argv) > 1 else APP)
    print(n, "pages ->", OUT)
