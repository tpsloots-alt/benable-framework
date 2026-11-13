# B.Enable · Control Framework — online omgeving

Statische site voor de framework-pagina's per organisatie, met:

- **Persoonlijke links met vervaldatum.** Zonder geldige link krijgt een bezoeker een nette weigerpagina.
- **Presentatie-slot.** Gekozen tabbladen zijn geblurd en gaan open met een pincode die je in de sessie geeft.
- **Niet vindbaar.** Zoekmachines worden overal geweerd (`noindex`, `robots.txt`).

Hosting via **Cloudflare Pages**, gekoppeld aan deze GitHub-repo. Elke push zet een nieuwe versie online.

```
public/                 de site zelf
  index.html            startpagina (openbaar, zonder inhoud)
  inwarmte/index.html   framework InWarmte (alleen met link)
  projectorganisaties/index.html   framework Projectorganisaties (alleen met link)
  warmtebedrijf/index.html   geanonimiseerde warmtecasus voor feedback, zonder pincode (alleen met link)
  implementatieplan/index.html   losse tool: roadmap inlezen en omzetten naar implementatieplan (tijdelijk openbaar, zonder link of pincode; niet vindbaar voor zoekmachines)
functions/
  _middleware.js        controleert de links; hier staan ook de beschermde paden
  ingetrokken.js        id's van links die niet meer mogen werken
scripts/
  maak-link.mjs         maakt een persoonlijke link
  zet-pincode.mjs       zet de pincode van het presentatie-slot
tools/
  lock.py               maakt van een framework-pagina een sitepagina met slot
```

## Eenmalig inrichten

1. **GitHub.** Maak een *private* repo (bijv. `benable-framework`) en zet deze bestanden erin.
2. **Cloudflare Pages.** Maak een gratis account op cloudflare.com. Ga naar *Workers & Pages → Create → Pages → Connect to Git* en kies de repo. Vul in:
   - Build command: leeg laten
   - Build output directory: `public`
3. **Geheime sleutel.** Maak een lange willekeurige sleutel:
   ```
   node -e "console.log(require('crypto').randomBytes(32).toString('base64url'))"
   ```
   Zet die in Cloudflare onder *Settings → Variables and Secrets* als **secret** met de naam `LINK_SECRET` (Production). Deploy daarna opnieuw.
4. **Domein.** Kies in Cloudflare Pages *Custom domains → framework.benable.nl*. Cloudflare geeft een CNAME-record (naar `<project>.pages.dev`). Zet dat record bij de partij waar het DNS van benable.nl wordt beheerd.
5. **Lokaal.** Maak in de map van de repo een bestand `.env` met dezelfde sleutel:
   ```
   LINK_SECRET=<dezelfde sleutel>
   ```
   Dit bestand staat in `.gitignore` en komt nooit in GitHub.

## Een link maken voor iemand

**Via GitHub (geen installatie nodig):**

1. Eenmalig: zet in GitHub onder *Settings → Secrets and variables → Actions → New repository secret* de sleutel als `LINK_SECRET`. Gebruik dezelfde waarde als in Cloudflare.
2. Ga naar het tabblad **Actions → Maak toegangslink → Run workflow**.
3. Vul naam en aantal dagen in en klik op **Run workflow**.
4. Open na een halve minuut de run. De link staat in de samenvatting.

**Of lokaal, als je Node hebt:**

```
node scripts/maak-link.mjs --naam "Jan Jansen" --dagen 14
```

Je krijgt een link die 14 dagen geldig is, plus een **id**. De link is gekoppeld aan één pagina; standaard is dat `/inwarmte/`, met `--pad /algemeen/` kies je een andere.

Bij de eerste klik zet de server een cookie en haalt de link uit de adresbalk. In het menu ziet de bezoeker voor wie de toegang is en tot wanneer.

Elke link wordt lokaal bijgehouden in `links-log.csv` (niet in git): datum, naam, pagina, vervaldatum en id.

## Overzicht en intrekken

- **Overzicht:** `toegang/links.md` toont alle uitgegeven links: naam, pagina, geldig tot, id en status. De knop *Maak toegangslink* werkt het bij.
- **Intrekken:** Actions → **Trek toegangslink in** → Run workflow → vul het id in. Het id komt in `functions/ingetrokken.js` en de status in het overzicht wordt bijgewerkt. Na de deploy (1 à 2 minuten) werkt de link niet meer.

## Gebruik van links bekijken

Bij elk bezoek houdt de site per link bij: eerste en laatste bezoek, aantal bezoeken, regio (bij benadering, geen IP-adressen) en of de pincode is gebruikt. Op de pagina staat dat het gebruik wordt bijgehouden.

- **Bekijken:** Actions → **Toon linkgebruik** → Run workflow. De tabel staat in de samenvatting van de run, inclusief links die nog niet gebruikt zijn.
- **Eenmalig inrichten:**
  1. Cloudflare → *Storage & Databases → KV* → namespace `benable-toegang` aanmaken.
  2. Pages-project → *Settings → Bindings* → KV namespace toevoegen met variabelenaam `TOEGANG`.
  3. Een tweede geheime sleutel `ADMIN_SECRET` in Cloudflare (*Variables and Secrets*, type Secret) én in GitHub (*Settings → Secrets → Actions*). Daarna opnieuw deployen.
- Zonder de KV-koppeling werkt de site gewoon; er wordt dan niets bijgehouden.

## De pincode

Wijzigen:

```
node scripts/zet-pincode.mjs 482913 public/inwarmte/index.html
```

Commit en push daarna. In de sessie geef je de pincode mondeling of in de chat. Een geopend tabblad blijft open tot de bezoeker het browsertabblad sluit.

## Een nieuwe versie van het framework plaatsen

Exporteer de bijgewerkte pagina als HTML. Maak er dan een sitepagina met slot van:

```
python3 tools/lock.py inwarmte.html public/inwarmte/index.html sturing,organisatie,cyclus,datamodel,roadmap
node scripts/zet-pincode.mjs <pincode> public/inwarmte/index.html
```

Het laatste argument van `lock.py` bepaalt welke tabbladen geblurd zijn. Na `lock.py` moet je de pincode altijd opnieuw zetten.

## Later: het algemene model of een andere klant

1. Zet de pagina in een nieuwe map, bijv. `public/algemeen/index.html` (met `tools/lock.py`).
2. Voeg het pad toe aan `BESCHERMD` in `functions/_middleware.js`, bijv. `['/inwarmte/', '/algemeen/']`.
3. Maak links met `--pad /algemeen/`.

## Wat dit wel en niet beschermt

- **De link is echte toegangscontrole.** De server controleert handtekening, pagina en vervaldatum. Zonder geldige link komt niemand bij de pagina.
- **Het pincode-slot is een presentatiemiddel.** Het slot werkt in de browser van iemand die al toegang heeft. Een technisch handige bezoeker kan de geblurde inhoud via de broncode zien. Dat is acceptabel zolang de data fictief is. Bij echte klantcijfers kunnen de afgeschermde onderdelen pas na de pincode van de server worden geladen.
- **Een link is overdraagbaar.** Wie een link doorstuurt, geeft toegang tot de vervaldatum. Houd de looptijd daarom kort, en trek een link in als dat nodig is.
