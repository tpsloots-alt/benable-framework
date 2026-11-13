"""Maakt van de InWarmte-build een geanonimiseerde casus 'Warmtebedrijf'."""
import re,json,random,sys
src,dst=sys.argv[1],sys.argv[2]
h=open(src).read()
def R(a,b,cnt=None):
    global h
    n=h.count(a)
    assert n>=1,('niet gevonden',a[:90])
    if cnt: assert n==cnt,(n,a[:90])
    h=h.replace(a,b)
random.seed(7)
PRE=["Akker","Beek","Berken","Bloemen","Boom","Bron","Dijk","Duin","Eiken","Esch","Gaarde","Haven","Heide","Kade","Lind","Meer","Molen","Oever","Park","Polder","Riet","Singel","Spoor","Veld","Vijver","Water","Weide","Wilg","Zon","Klaver","Hazel","Esdoorn","Kastanje","Iepen","Dennen"]
SUF=["hof","park","kwartier","weide","zicht","rijk","veld","haven","hoek","laan","tuinen","staete","erf"]
CITIES=[("Amersfoort","UT"),("Apeldoorn","GE"),("Arnhem","GE"),("Breda","NB"),("Den Bosch","NB"),("Deventer","OV"),("Dordrecht","ZH"),("Ede","GE"),("Enschede","OV"),("Gouda","ZH"),("Groningen","GR"),("Haarlem","NH"),("Helmond","NB"),("Hengelo","OV"),("Leeuwarden","FR"),("Lelystad","FL"),("Maastricht","LI"),("Nijmegen","GE"),("Oss","NB"),("Purmerend","NH"),("Roosendaal","NB"),("Schiedam","ZH"),("Venlo","LI"),("Zaandam","NH"),("Zwolle","OV"),("Alkmaar","NH"),("Almere","FL"),("Houten","UT"),("Zeist","UT"),("Veenendaal","UT"),("Hoorn","NH"),("Assen","DR"),("Emmen","DR"),("Middelburg","ZE"),("Rotterdam","ZH"),("Utrecht","UT")]
names=set();
def nieuw():
    while True:
        n=random.choice(PRE)+random.choice(SUF)
        if n not in names: names.add(n);return n
# PROJ_RAW
i=h.index('const PROJ_RAW=')+len('const PROJ_RAW=');j=h.index(';\n',i)
rows=json.loads(h[i:j]);mp={}
for r in rows:
    nn=nieuw();mp[r[1]]=nn;c=random.choice(CITIES);r[0],r[1],r[2]=c[0],nn,c[1];r[17]=0
h=h[:i]+json.dumps(rows,ensure_ascii=False)+h[j:]
# RPROJ echte namen
for old,(nm,pl) in {'Acaciaschool':('Brede school De Klimop','Zwolle'),'Fruitpark Hotel':('Hotel Waterrijk','Ede'),'Langen Linden':('Lindenkwartier','Oss')}.items():
    a=f"naam:'{old}',plaats:'"
    k=h.index(a);e=h.index("',",k+len(a))
    h=h[:k]+f"naam:'{nm}',plaats:'{pl}"+h[e:]
h=h.replace(",echt:1,",",echt:0,")
R("x.naam==='Conrad'",f"x.naam==='{mp['Conrad']}'",1)
# teksten
T=[("<title>B.Enable · Control Framework · InWarmte</title>","<title>B.Enable · Control Framework · Warmtebedrijf (casus)</title>"),
 ("<small>voor InWarmte · werkversie</small>","<small>casus warmtebedrijf · ter feedback</small>"),
 ('<h1 style="font-size:1.35rem">Waar InWarmte op moet sturen</h1>','<h1 style="font-size:1.35rem">Waar het warmtebedrijf op moet sturen</h1>'),
 ("De omzet van InWarmte komt uit","De omzet van het warmtebedrijf komt uit"),
 ("Het resultaat van InWarmte hangt af van drie dingen","Het resultaat van het warmtebedrijf hangt af van drie dingen"),
 ("Dit framework maakt die stappen concreet voor InWarmte:","Dit framework maakt die stappen concreet voor een warmtebedrijf:"),
 ("Een uitgave van B.Enable · werkversie voor InWarmte","Een uitgave van B.Enable · casus voor feedback"),
 ("<b>Werkversie om samen te toetsen.</b> Projectnamen, plaatsen, techniek en fase komen van inwarmte.nl; alle aantallen en bedragen zijn fictief.","<b>Casus om het framework en de aanpak te toetsen.</b> Een fictief warmtebedrijf: alle namen, plaatsen, aantallen en bedragen zijn verzonnen."),
 ("InWarmte in het kort (openbare bronnen)","De casus in het kort (fictief)"),
 ("Bij InWarmte bestaat","Bij dit warmtebedrijf bestaat"),
 ("De projecten van InWarmte zoals vermeld op de website, met techniek en fase.","De projecten van het warmtebedrijf, met techniek en fase."),
 ("namen echt · aantallen, bedragen en entiteiten fictief","fictieve casus"),
 ("Fase: eigen ontwikkeling of later ingestapt is afgeleid uit de fasetags op de website (aanname).","Herkomst: eigen ontwikkeling of later ingestapt (overgenomen)."),
 ("${pr.tonb?' (techniek niet vermeld op website; aangenomen)':''}",""),
 ("Energiekosten van InWarmte per geleverde GJ","Energiekosten van het warmtebedrijf per geleverde GJ"),
 ("voor InWarmte resteert","voor het warmtebedrijf resteert"),
 ("InWarmte ontvangt vaste bedragen","Het warmtebedrijf ontvangt vaste bedragen"),
 ("drie projectnamen echt · pijplijnprojecten en alle bedragen fictief","fictieve casus"),
 ("InWarmte Projecten B.V.","Warmtebedrijf Projecten B.V."),("InWarmte B.V.","Warmtebedrijf B.V."),
 ("Bijvoorbeeld (vgl. website): ","Bijvoorbeeld: "),
 ("'Tijdelijke noodlevering: aparte verantwoording en kostendekking',",""),
 ("['Noodleverancier','Partij die door de minister wordt aangewezen om tijdelijk warmte te leveren als de oorspronkelijke leverancier wegvalt.'],",""),
 ("groep:'Omzetketen en Exact Online'","groep:'Omzetketen en administratie'"),
 ("Exact Online","het financieel pakket"),
 ("/* InWarmte: branchepunten","/* Casus warmtebedrijf: branchepunten"),
 ("naam:'inwarmte',key:()=>'inw_rm_v1'","naam:'warmtebedrijf',key:()=>'wbc_rm_v1'"),
 ("vbBron:239, vbKoude:217, wpHuur:600,","vbBron:250, vbKoude:200, wpHuur:575,"),
]
for a,b in T: R(a,b)
h=h.replace("'inw_","'wbc_")
h=re.sub(r'<div class="sidenote">.*?</div>','<div class="sidenote">Fictieve casus van een warmtebedrijf, bedoeld om het framework en de aanpak te toetsen. Alle namen en cijfers zijn verzonnen.</div>',h,count=1,flags=re.S)
h=re.sub(r'\s*<p class="note">Bronnen: <a href="https://inwarmte\.nl.*?</p>','',h,count=1,flags=re.S)
h=re.sub(r" \{id:'I-S2'.*?\},\n","",h,count=1)
i=h.index('function renderFacts(){');j=h.index('function renderChallenges(){')
h=h[:i]+r"""function renderFacts(){const c={};S.proj.forEach(x=>c[x.tech]=(c[x.tech]||0)+1);const n=S.proj.length;
  $('#inwFacts').innerHTML=[`${n} projecten in ontwikkeling, exploitatie of alleen dienstverlening, in wijken van enkele tientallen tot ruim duizend aansluitingen.`,`Techniek: ${c.bod_ind} bodemenergie met warmtepompen, ${c.wko_bron} alleen WKO, ${c.lw_ind} lucht/water-warmtepompen, ${(c.net||0)+(c.aqua||0)} collectieve netten of aquathermie, ${c.dv} alleen dienstverlening.`,`Opbrengsten vooral vaste bedragen per aansluiting (bronwarmte, koude, huur warmtepomp); de klant betaalt de stroom van de warmtepomp.`,`Levering via aparte project-BV's, deels samen met een woningcorporatie of VvE.`,`Groei door eigen ontwikkeling én door overname van bestaande portefeuilles.`,`Technische dienst, onderhoud en storingen via onderaanneming; eigen mensen in ontwikkeling, projectmanagement en exploitatiemanagement.`].map(x=>`<li>${x}</li>`).join('')}
"""+h[j:]
# InWarmte-specifieke stijlregels eruit
h=h.replace('.brand{border-left:5px solid #FF6200;padding-left:10px}\nh1{color:var(--accent)}\n','')
h=h.replace("k:'Warmtenet',wp:true,c:'#FF6200'","k:'Warmtenet',wp:true,c:'#C2410C'")
h=h.replace("naam:'inwarmte', key:()=>'opslagsleutel'","naam:'framework', key:()=>'opslagsleutel'")
open(dst,'w').write(h)
# controle
bad=['InWarmte','inwarmte','InEnergie','Conrad','DBH','DEEM','Exact','oodle','Dubotechniek','vorm.nl','Hibi','Acaciaschool','Fruitpark','Langen Linden','#FF6200']
real=[l.split('|')[0] for l in open('/home/claude/inw/data.py').read().split('P="""')[1].split('"""')[0].split('\n')]
rest=[w for w in bad if w in h]+[w for w in real if re.search(r'["\']'+re.escape(w)+r'["\']',h)]
print('resterend:',rest)
