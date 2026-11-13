// Haalt het linkgebruik op bij de site en maakt er een tabel van (voor de GitHub Actions-samenvatting).
// Gebruik: ADMIN_SECRET=... node scripts/toon-gebruik.mjs [https://framework.benable.nl]
import { readFileSync, existsSync } from 'node:fs';
const basis = (process.argv[2] || 'https://framework.benable.nl').replace(/\/$/, '');
const res = await fetch(basis + '/_beheer/gebruik', { headers: { Authorization: 'Bearer ' + process.env.ADMIN_SECRET } });
if (!res.ok) { console.log(`Ophalen mislukt (${res.status}): ${await res.text()}`); process.exit(1); }
const data = await res.json();
const per = Object.fromEntries(data.map((r) => [r.i, r]));
// Uitgegeven links uit het overzicht, zodat ook ongebruikte links zichtbaar zijn
const links = [];
if (existsSync('toegang/links.md')) {
  for (const regel of readFileSync('toegang/links.md', 'utf8').split('\n')) {
    const c = regel.split('|').map((x) => x.trim());
    if (c.length >= 7 && /^[0-9a-f]{8}$/.test(c[5])) links.push({ aangemaakt: c[1], n: c[2], p: c[3], tot: c[4], i: c[5], status: c[6] });
  }
}
for (const r of data) if (!links.find((l) => l.i === r.i)) links.push({ aangemaakt: '', n: r.n, p: r.p, tot: new Date(r.e * 1000).toLocaleDateString('nl-NL'), i: r.i, status: '' });
const fmt = (s) => (s ? new Date(s).toLocaleString('nl-NL', { timeZone: 'Europe/Amsterdam', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '–');
const rij = (l) => {
  const r = per[l.i];
  const regio = r ? Object.entries(r.regio || {}).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} (${v})`).join(', ') : '–';
  return `| ${l.n} | ${l.p} | ${l.tot} | ${l.status || '–'} | ${r ? fmt(r.eerste) : 'nog niet gebruikt'} | ${r ? fmt(r.laatste) : '–'} | ${r ? r.aantal : 0} | ${regio} | ${r && r.pin ? 'ja, ' + fmt(r.pin) : 'nee'} | ${l.i} |`;
};
links.sort((a, b) => ((per[b.i]?.laatste || '') > (per[a.i]?.laatste || '') ? 1 : -1));
console.log('## Gebruik van toegangslinks\n');
console.log(`Opgehaald op ${new Date().toLocaleString('nl-NL', { timeZone: 'Europe/Amsterdam' })}. Een bezoek telt elke keer dat de pagina wordt geopend of ververst. Regio is bij benadering (geen IP-adressen).\n`);
console.log('| Naam | Pagina | Geldig tot | Status | Eerste bezoek | Laatste bezoek | Bezoeken | Regio | Pincode gebruikt | Id |');
console.log('|---|---|---|---|---|---|---|---|---|---|');
for (const l of links) console.log(rij(l));
