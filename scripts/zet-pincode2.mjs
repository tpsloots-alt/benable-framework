// Pincode 2 (volledig invullen van het implementatieplan) per klantmap.
// De pincode staat NIET in de repo, maar als geheime instelling in Cloudflare Pages: PIN2_<MAP>.
// Gebruik: node scripts/zet-pincode2.mjs /inwarmte/ 482913
//  - controleert de pincode (6 tot 12 cijfers) en toont de naam van de instelling;
//  - met wrangler geïnstalleerd en ingelogd kun je hem direct zetten met de getoonde opdracht.
const [pad, pin] = process.argv.slice(2);
if (!pad || !/^\/[a-z0-9-]+\/$/.test(pad)) { console.error('Geef de map op, bijv. /inwarmte/'); process.exit(1); }
if (!pin || !/^\d{6,12}$/.test(pin)) { console.error('Kies een pincode van 6 tot 12 cijfers.'); process.exit(1); }
const naam = 'PIN2_' + pad.replace(/\//g, '').toUpperCase().replace(/[^A-Z0-9]/g, '_');
console.log(`
Pincode 2 voor ${pad}

Cloudflare-dashboard: Workers & Pages → benable-framework → Settings → Variables and Secrets
  → Add → type Secret, naam ${naam}, waarde ${pin} (Production). Daarna opnieuw deployen
  (Deployments → laatste deployment → Retry), anders werkt de nieuwe pincode nog niet.

Of met wrangler:
  echo ${pin} | npx wrangler pages secret put ${naam} --project-name benable-framework

Geef de pincode alleen aan de adviseur en de projectleider. Na een wijziging blijft een geopend
bewerkscherm werken tot het cookie verloopt (maximaal 10 uur); daarna is de nieuwe pincode nodig.
`);
