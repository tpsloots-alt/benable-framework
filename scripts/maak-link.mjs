// Maakt een persoonlijke link met vervaldatum.
// Gebruik: node scripts/maak-link.mjs --naam "Jan Jansen" --dagen 14 [--pad /inwarmte/] [--domein https://framework.benable.nl]
// LINK_SECRET komt uit de omgeving of uit het bestand .env (staat niet in git).
import { createHmac, randomBytes } from 'node:crypto';
import { readFileSync, existsSync, appendFileSync } from 'node:fs';

const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > -1 ? process.argv[i + 1] : d; };
let secret = process.env.LINK_SECRET;
if (!secret && existsSync('.env')) secret = (readFileSync('.env', 'utf8').match(/^LINK_SECRET=(.+)$/m) || [])[1]?.trim();
if (!secret) { console.error('LINK_SECRET ontbreekt. Zet hem in .env (LINK_SECRET=...) of als omgevingsvariabele.'); process.exit(1); }

const naam = arg('naam');
if (!naam) { console.error('Geef een naam op: --naam "Jan Jansen"'); process.exit(1); }
const dagen = Number(arg('dagen', '14'));
const pad = arg('pad', '/inwarmte/');
const domein = arg('domein', 'https://framework.benable.nl').replace(/\/$/, '');
const e = Math.floor(Date.now() / 1000) + Math.round(dagen * 86400);
const i = randomBytes(4).toString('hex');
const b64u = (b) => Buffer.from(b).toString('base64url');
const body = b64u(JSON.stringify({ n: naam, p: pad, e, i }));
const sig = createHmac('sha256', secret).update(body).digest('base64url');
const link = `${domein}${pad}?t=${body}.${sig}`;
const tot = new Date(e * 1000).toLocaleString('nl-NL', { dateStyle: 'long', timeStyle: 'short' });
console.log(`\nLink voor ${naam} (geldig tot ${tot}, id ${i}):\n\n${link}\n`);
appendFileSync('links-log.csv', `${new Date().toISOString()};${naam};${pad};${tot};${i}\n`);
