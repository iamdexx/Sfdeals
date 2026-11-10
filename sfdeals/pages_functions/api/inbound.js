// Seller form intake. POST stores a lead in KV; GET with the owner's token lists and clears them.
const cors = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "content-type", "Access-Control-Allow-Methods": "GET,POST,OPTIONS" };
const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json", ...cors } });
export async function onRequestOptions() { return new Response(null, { headers: cors }); }
export async function onRequestPost({ request, env }) {
  let b; try { b = await request.json(); } catch { const f = await request.formData(); b = Object.fromEntries(f.entries()); }
  if (b.website) return json({ ok: true });                       // honeypot
  const addr = String(b.address || "").trim(), phone = String(b.phone || "").replace(/\D/g, "");
  if (addr.length < 5 || phone.length < 10) return json({ ok: false, error: "address and phone required" }, 400);
  const id = Date.now() + "-" + Math.random().toString(36).slice(2, 8);
  await env.INBOUND.put("lead:" + id, JSON.stringify({ id, at: new Date().toISOString(), market: String(b.market || "").slice(0, 8), address: addr.slice(0, 120),
    name: String(b.name || "").slice(0, 80), phone, email: String(b.email || "").slice(0, 120), situation: String(b.situation || "").slice(0, 600), consent: !!b.consent }), { expirationTtl: 60 * 60 * 24 * 90 });
  return json({ ok: true });
}
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url);
  if (u.searchParams.get("token") !== env.INBOUND_TOKEN) return json({ error: "no" }, 403);
  const list = await env.INBOUND.list({ prefix: "lead:" });
  const out = [];
  for (const k of list.keys) { const v = await env.INBOUND.get(k.name); if (v) out.push(JSON.parse(v)); }
  if (u.searchParams.get("ack") === "1") await Promise.all(list.keys.map(k => env.INBOUND.delete(k.name)));
  return json({ leads: out.sort((a, b) => a.at < b.at ? 1 : -1) });
}
