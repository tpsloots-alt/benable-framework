// Toegang via persoonlijke link met vervaldatum (Cloudflare Pages Functions).
// Een link ziet eruit als https://framework.benable.nl/inwarmte/?t=<token>
// Token = base64url(JSON {n: naam, p: pad, e: vervaltijd (unix), i: id}) + "." + HMAC-SHA256 met LINK_SECRET.
// Na de eerste klik zet de server een cookie, zodat de link niet in de adresbalk blijft staan.
import INGETROKKEN from './ingetrokken.js';

// Paden die een persoonlijke link vereisen. Voeg hier later bijv. '/algemeen/' toe.
const BESCHERMD = ['/inwarmte/', '/projectorganisaties/', '/warmtebedrijf/']; // '/implementatieplan/' tijdelijk openbaar (op verzoek, 14-11-2026); later weer toevoegen

const enc = new TextEncoder();
const b64u = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64u = (s) => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4)), (c) => c.charCodeAt(0));

async function controleer(token, secret) {
  if (!token || !secret || !token.includes('.')) return null;
  const [body, sig] = token.split('.');
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['verify']);
  let ok = false;
  try { ok = await crypto.subtle.verify('HMAC', key, unb64u(sig), enc.encode(body)); } catch { return null; }
  if (!ok) return null;
  try { return JSON.parse(new TextDecoder().decode(unb64u(body))); } catch { return null; }
}

const cookie = (req, naam) => {
  const m = (req.headers.get('Cookie') || '').match(new RegExp('(?:^|; )' + naam + '=([^;]*)'));
  return m ? decodeURIComponent(m[1]) : null;
};

// Gebruik per link bijhouden in Cloudflare KV (binding TOEGANG). Geen IP-adressen, alleen regio bij benadering.
async function registreer(env, p, request, soort) {
  if (!env.TOEGANG) return;
  const key = 'u:' + p.i;
  let r = null;
  try { r = await env.TOEGANG.get(key, 'json'); } catch {}
  r = r || { i: p.i, n: p.n, p: p.p, e: p.e, eerste: null, laatste: null, aantal: 0, regio: {}, pin: null };
  const nu = new Date().toISOString();
  if (soort === 'pin') { r.pin = r.pin || nu; r.pinLaatst = nu; }
  else if (soort === 'pin2') { r.pin2 = r.pin2 || nu; r.pin2Laatst = nu; r.pin2Aantal = (r.pin2Aantal || 0) + 1; }
  else {
    const cf = request.cf || {};
    const regio = [cf.country, cf.region || cf.city].filter(Boolean).join(' · ') || 'onbekend';
    r.eerste = r.eerste || nu; r.laatste = nu; r.aantal = (r.aantal || 0) + 1;
    r.regio[regio] = (r.regio[regio] || 0) + 1;
  }
  await env.TOEGANG.put(key, JSON.stringify(r));
}

async function beheer(request, env) {
  const auth = request.headers.get('Authorization') || '';
  if (!env.ADMIN_SECRET || auth !== 'Bearer ' + env.ADMIN_SECRET) return new Response('Geen toegang', { status: 401 });
  if (!env.TOEGANG) return Response.json({ fout: 'KV-binding TOEGANG ontbreekt' }, { status: 500 });
  const uit = []; let cursor;
  do {
    const l = await env.TOEGANG.list({ prefix: 'u:', cursor });
    for (const k of l.keys) { const v = await env.TOEGANG.get(k.name, 'json'); if (v) uit.push(v); }
    cursor = l.list_complete ? null : l.cursor;
  } while (cursor);
  return Response.json(uit, { headers: { 'Cache-Control': 'no-store' } });
}

// ---------- Pincode 2: volledig invullen van het implementatieplan ----------
// De pincode staat per klant als geheime instelling in Cloudflare: PIN2_<MAP>, bijv. PIN2_INWARMTE voor /inwarmte/.
// Na een juiste pincode zet de server een cookie (gebonden aan de link en de map, geldig PIN2_UREN uur of tot de link verloopt).
// Met dat cookie levert de server onder <map>implementatie/ de bewerkversie (bewerken.html), anders de leesversie (index.html).
const PIN2_UREN = 10, PIN2_MAX = 5, PIN2_WACHT = 15 * 60; // pogingen per link, wachttijd in seconden
const pin2Naam = (pad) => 'PIN2_' + pad.replace(/\//g, '').toUpperCase().replace(/[^A-Z0-9]/g, '_');
async function hmac(secret, tekst) {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return b64u(await crypto.subtle.sign('HMAC', key, enc.encode(tekst)));
}
function gelijk(a, b) { if (a.length !== b.length) return false; let x = 0; for (let i = 0; i < a.length; i++) x |= a.charCodeAt(i) ^ b.charCodeAt(i); return x === 0; }
async function pin2Cookie(env, p, pad, exp) { return exp + '.' + await hmac(env.LINK_SECRET, 'pin2|' + p.i + '|' + pad + '|' + exp); }
async function pin2Geldig(request, env, p, pad) {
  const c = cookie(request, 'be_pin2'); if (!c || !c.includes('.')) return false;
  const exp = +c.split('.')[0]; if (!(exp > Math.floor(Date.now() / 1000))) return false;
  return gelijk(c, await pin2Cookie(env, p, pad, exp));
}
async function pin2Inloggen(request, env, p, pad, waitUntil) {
  const geheim = env[pin2Naam(pad)];
  if (!geheim) return new Response('Pincode 2 is niet ingesteld', { status: 404, headers: { 'Cache-Control': 'no-store' } });
  const sleutel = 'p2:' + p.i, nu = Math.floor(Date.now() / 1000);
  let st = null; if (env.TOEGANG) { try { st = await env.TOEGANG.get(sleutel, 'json'); } catch {} }
  st = st || { n: 0, tot: 0 };
  if (st.tot > nu) return new Response('Te vaak onjuist', { status: 429, headers: { 'Retry-After': String(st.tot - nu), 'Cache-Control': 'no-store' } });
  const pin = (await request.text()).trim().slice(0, 32);
  const ok = gelijk(await hmac(env.LINK_SECRET, 'pin|' + pin), await hmac(env.LINK_SECRET, 'pin|' + String(geheim).trim()));
  if (!ok) {
    st.n = (st.n || 0) + 1; if (st.n >= PIN2_MAX) { st.tot = nu + PIN2_WACHT; st.n = 0; }
    if (env.TOEGANG) waitUntil(env.TOEGANG.put(sleutel, JSON.stringify(st), { expirationTtl: 86400 }).catch(() => {}));
    return new Response('Onjuiste pincode', { status: st.tot > nu ? 429 : 401, headers: st.tot > nu ? { 'Retry-After': String(PIN2_WACHT), 'Cache-Control': 'no-store' } : { 'Cache-Control': 'no-store' } });
  }
  if (env.TOEGANG && st.n) waitUntil(env.TOEGANG.delete(sleutel).catch(() => {}));
  waitUntil(registreer(env, p, request, 'pin2').catch(() => {}));
  const exp = Math.min(p.e, nu + PIN2_UREN * 3600);
  const h = new Headers({ 'Cache-Control': 'no-store' });
  h.append('Set-Cookie', `be_pin2=${await pin2Cookie(env, p, pad, exp)}; Path=${pad}; Max-Age=${exp - nu}; HttpOnly; Secure; SameSite=Strict`);
  return new Response(null, { status: 204, headers: h });
}

function geweigerd(reden) {
  const html = `<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><title>B.Enable · Control Framework</title>
<style>body{font-family:'IBM Plex Sans','Helvetica Neue',Arial,sans-serif;background:#F3F5F8;color:#14263A;display:grid;place-items:center;min-height:100vh;margin:0}main{max-width:460px;padding:32px;background:#fff;border:1px solid #D5DBE2;border-top:4px solid #1E3A5F;border-radius:12px}h1{font-size:20px;margin:0 0 10px}p{color:#566577;line-height:1.5}</style></head>
<body><main><h1>B.Enable · Control Framework</h1><p>${reden}</p><p>Neem contact op met B.Enable voor een nieuwe link.</p></main></body></html>`;
  return new Response(html, { status: 403, headers: { 'Content-Type': 'text/html; charset=utf-8', 'X-Robots-Tag': 'noindex, nofollow', 'Cache-Control': 'no-store' } });
}

export async function onRequest({ request, env, next, waitUntil }) {
  const url = new URL(request.url);
  if (url.pathname === '/_beheer/gebruik') return beheer(request, env);
  const pad = BESCHERMD.find((p) => url.pathname.startsWith(p) || url.pathname === p.slice(0, -1));
  if (!pad) {
    const res = await next();
    const out = new Response(res.body, res);
    out.headers.set('X-Robots-Tag', 'noindex, nofollow');
    return out;
  }
  const uitLink = url.searchParams.get('t');
  const token = uitLink || cookie(request, 'be_access');
  const p = await controleer(token, env.LINK_SECRET);
  const nu = Math.floor(Date.now() / 1000);
  if (!p) return geweigerd(token ? 'Deze link is niet geldig.' : 'Deze pagina is alleen toegankelijk via een persoonlijke link.');
  if (p.p !== pad) return geweigerd('Deze link geeft geen toegang tot deze pagina.');
  if (p.e <= nu) return geweigerd('Deze link is verlopen.');
  if (INGETROKKEN.includes(p.i)) return geweigerd('Deze link is ingetrokken.');

  // Melding van het presentatie-slot: pincode is gebruikt.
  if (url.pathname === pad + '_pin' && request.method === 'POST') {
    waitUntil(registreer(env, p, request, 'pin').catch(() => {}));
    return new Response(null, { status: 204 });
  }
  // Pincode 2 (implementatieplan volledig invullen)
  if (url.pathname === pad + '_pin2' && request.method === 'POST') return pin2Inloggen(request, env, p, pad, waitUntil);
  if (url.pathname === pad + '_pin2uit' && request.method === 'POST') {
    return new Response(null, { status: 204, headers: { 'Cache-Control': 'no-store', 'Set-Cookie': `be_pin2=; Path=${pad}; Max-Age=0; HttpOnly; Secure; SameSite=Strict` } });
  }
  const impl = pad + 'implementatie/';
  if (url.pathname.startsWith(impl + 'bewerken')) return geweigerd('Deze pagina is niet rechtstreeks te openen.');
  if ((url.pathname === impl || url.pathname === impl + 'index.html') && await pin2Geldig(request, env, p, pad)) {
    let res = await env.ASSETS.fetch(new Request(new URL(impl + 'bewerken', url), request));
    if (res.status >= 300 && res.status < 400 && res.headers.get('Location')) res = await env.ASSETS.fetch(new Request(new URL(res.headers.get('Location'), url), request));
    const out = new Response(res.body, res);
    out.headers.set('X-Robots-Tag', 'noindex, nofollow'); out.headers.set('Cache-Control', 'private, no-store'); out.headers.set('Referrer-Policy', 'no-referrer');
    return out;
  }
  const isPagina = url.pathname === pad || url.pathname === pad + 'index.html';
  if (isPagina) waitUntil(registreer(env, p, request, 'bezoek').catch(() => {}));

  const maxAge = p.e - nu;
  if (uitLink) {
    // Cookie zetten en doorsturen naar het adres zonder token.
    url.searchParams.delete('t');
    const h = new Headers({ Location: url.pathname + url.search + url.hash, 'Cache-Control': 'no-store' });
    h.append('Set-Cookie', `be_access=${encodeURIComponent(token)}; Path=${pad}; Max-Age=${maxAge}; HttpOnly; Secure; SameSite=Lax`);
    h.append('Set-Cookie', `be_who=${encodeURIComponent(p.n + '|' + p.e)}; Path=${pad}; Max-Age=${maxAge}; Secure; SameSite=Lax`);
    return new Response(null, { status: 302, headers: h });
  }
  const res = await next();
  const out = new Response(res.body, res);
  out.headers.set('X-Robots-Tag', 'noindex, nofollow');
  out.headers.set('Cache-Control', 'private, no-store');
  out.headers.set('Referrer-Policy', 'no-referrer');
  return out;
}
