// Toegang via persoonlijke link met vervaldatum (Cloudflare Pages Functions).
// Een link ziet eruit als https://framework.benable.nl/inwarmte/?t=<token>
// Token = base64url(JSON {n: naam, p: pad, e: vervaltijd (unix), i: id}) + "." + HMAC-SHA256 met LINK_SECRET.
// Na de eerste klik zet de server een cookie, zodat de link niet in de adresbalk blijft staan.
import INGETROKKEN from './ingetrokken.js';

// Paden die een persoonlijke link vereisen. Voeg hier later bijv. '/algemeen/' toe.
const BESCHERMD = ['/inwarmte/', '/projectorganisaties/', '/warmtebedrijf/'];

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
