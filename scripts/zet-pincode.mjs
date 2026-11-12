// Zet de pincode voor het presentatie-slot in een pagina.
// Gebruik: node scripts/zet-pincode.mjs 482913 public/inwarmte/index.html
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
const [pin, file = 'public/inwarmte/index.html'] = process.argv.slice(2);
if (!pin || !/^\d{4,12}$/.test(pin)) { console.error('Geef een pincode van 4 tot 12 cijfers.'); process.exit(1); }
const hash = createHash('sha256').update('benable:' + pin).digest('hex');
const html = readFileSync(file, 'utf8');
const nieuw = html.replace(/const LOCK_HASH="[^"]*";/, `const LOCK_HASH="${hash}";`);
if (nieuw === html && !html.includes(hash)) { console.error('Geen slot gevonden in ' + file); process.exit(1); }
writeFileSync(file, nieuw);
console.log(`Pincode gezet in ${file}. Commit en push om hem online te zetten.`);
