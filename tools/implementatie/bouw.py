"""Maakt het implementatieplan voor een klantmap: een leesversie en een bewerkversie.
Gebruik: python3 tools/implementatie/bouw.py implementatieplan.html public/inwarmte/implementatie/

- index.html     leesversie (pincode 1): alleen het managementoverzicht, zonder bewerkscherm, inlezen of versies.
- bewerken.html  bewerkversie (pincode 2): het volledige plan. De server levert dit bestand alleen
                 met een geldige pincode-2-cookie, onder hetzelfde adres als index.html (zie functions/_middleware.js).
Bron is de planningstool (implementatieplan.html, dezelfde als het artifact); de modus volgt uit <meta name="be-modus">."""
import sys,os,re
src,out=sys.argv[1],sys.argv[2]
h=open(src).read()
os.makedirs(out,exist_ok=True)
def meta(x,modus):
    return x.replace('<meta charset="utf-8">','<meta charset="utf-8">\n<meta name="robots" content="noindex,nofollow">\n<meta name="be-bron" content="framework">\n<meta name="be-modus" content="%s">'%modus,1)
def cut(x,a,b,keep_b=False):
    i=x.index(a);j=x.index(b,i)
    return x[:i]+(x[j:] if keep_b else x[j+len(b):])

# bewerkversie: volledig
open(os.path.join(out,'bewerken.html'),'w').write(meta(h,'bewerken'))

# leesversie: bewerkscherm, inlezen en versieknoppen worden niet meegeleverd
l=h
l=cut(l,'  <div id="app"','</div>\n</div>\n\n<script>',keep_b=True)          # bewerkscherm (tabbladen, actielijst, instellingen)
l=l.replace('</div>\n</div>\n\n<script>','</div>\n\n<script>',1)             # sluit de wrap zonder #app
l=cut(l,'    <div id="impBody"','  </section>\n\n  <main id="mg"',keep_b=True)  # roadmap inlezen
for bid in ['bSave','bOpen','bDemo','bClear','bTog']:
    l=re.sub(r'\s*<button class="btn[^"]*" id="%s"[^>]*>.*?</button>'%bid,'',l,count=1,flags=re.S)
l=re.sub(r'<input type="file" id="fPlan"[^>]*>','',l,count=1)
l=l.replace('<button data-mode="edit" id="mEdit" class="on">Plan bewerken</button>','',1)
# ontbrekende elementen worden een los, onzichtbaar element, zodat de gedeelde code blijft werken
l=l.replace("const $=s=>document.querySelector(s),","const $=s=>document.querySelector(s)||(window.__leeg||(window.__leeg=document.createElement('div'))),",1)
for must in ['id="mg"','id="impCard"','id="saveBox"','id="verMsg"','be-modus']:
    pass
l=meta(l,'lezen')
assert 'id="tabs"' not in l and 'id="tPaste"' not in l and 'id="bSave"' not in l, 'bewerkdeel niet volledig verwijderd'
open(os.path.join(out,'index.html'),'w').write(l)
print('ok',out,len(l),'/',len(h))
