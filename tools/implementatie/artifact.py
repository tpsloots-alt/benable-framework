"""Maakt van een framework-pagina met tabblad Implementatieplan (tabblad.py) een zelfstandig artifact.
In het artifact bestaat geen map implementatie/; het plan (de bewerkversie, zonder pincode) wordt daarom in de pagina
meegeleverd en in het tabblad als ingebed venster (srcdoc) getoond. Het venster hoort bij dezelfde oorsprong als de pagina,
dus RM.export() en de downloads-capability van het artifact blijven bereikbaar.
Gebruik: python3 tools/implementatie/artifact.py framework.html implementatieplan.html uit.html
Volgorde: rm_export.py -> tabblad.py -> artifact.py (niet lock.py). Idempotent."""
import sys,re,base64
src,plan,dst=sys.argv[1:4]
h=open(src).read();p=open(plan).read()
assert 'IMPL:START' in h,'eerst tabblad.py draaien'
h=re.sub(r'\n?<script type="text/plain" id="implSrc">.*?</script>','',h,flags=re.S)
# plan: bewerkversie als frameworkmodus; downloads via het artifact; geen pincode-2-knop
p=p.replace('<meta charset="utf-8">','<meta charset="utf-8">\n<meta name="be-bron" content="framework">\n<meta name="be-modus" content="bewerken">',1)
p=p.replace('<script>\nconst $=','<script>\ntry{if(!window.claude&&parent.claude)window.claude=parent.claude}catch(e){}\nconst $=',1)
assert 'parent.claude' in p
p=p.replace('</style>','#bPin2{display:none!important}\n</style>',1)
b=base64.b64encode(p.encode()).decode()
blk='\n<script type="text/plain" id="implSrc">'+b+'</script>'
# plaats het blok vlak voor het eerste <script> na de sectie
j=h.index('<script',h.index('<!-- /IMPL:SECTIE -->'))
h=h[:j]+blk.lstrip('\n')+'\n'+h[j:]
old="fr.src='implementatie/';"
if old in h:
    h=h.replace(old,"fr.srcdoc=new TextDecoder().decode(Uint8Array.from(atob(document.getElementById('implSrc').textContent),c=>c.charCodeAt(0)));",1)
assert 'fr.srcdoc=' in h
open(dst,'w').write(h);print('ok',dst,len(h))
