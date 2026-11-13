"""Ontwerplaag (kopbalk, zijbalk, componentstijlen, print) op basis van een huisstijl-JSON.
Gebruik: python3 design.py brand.json target.html          (toepassen of vervangen; idempotent)
         python3 design.py --undo target.html               (terugzetten naar het ontwerp zonder laag)
Werkt na theme.py. Alleen presentatie; de logica van het framework wordt niet gewijzigd."""
import json,sys,re
def hx(c):c=c.lstrip('#');return [int(c[i:i+2],16) for i in (0,2,4)]
def mix(a,b,t):A,Bc=hx(a),hx(b);return '#%02X%02X%02X'%tuple(round(A[i]*(1-t)+Bc[i]*t) for i in range(3))
CSS_TAIL=r'''/* 2 · BASIS EN ZIJBALK */
body{font-size:14.5px;background:var(--be-bg);color:var(--be-ink)}
h1,h2,h3{color:var(--be-navy);letter-spacing:-.01em}
.app{grid-template-columns:248px 1fr}
nav.side{background:var(--be-navy);border-right:0;padding:18px 12px 20px}
nav.side .brand{border-left:0;display:flex;align-items:center;gap:12px;padding:2px 8px 14px;margin-bottom:2px;border-bottom:1px solid rgba(255,255,255,.14);color:#fff}
.logo{width:36px;height:36px;border-radius:9px;background:rgba(255,255,255,.12);display:grid;place-items:center;flex:none;position:relative;font:800 20px var(--display);color:#fff}
.logo::after{content:"";position:absolute;right:6px;bottom:7px;width:6px;height:6px;border-radius:50%;background:var(--be-orange-lt)}
.brand-t{line-height:1.15}.brand-t b{font:800 16px var(--display);color:#fff}.brand-t span{display:block;font:500 12px var(--body);color:#B9C7D8}
nav.side .demo-flag{margin:10px 8px 0;color:#FBE7C5;background:color-mix(in srgb,var(--be-orange-lt) 24%,transparent);border:1px solid color-mix(in srgb,var(--be-orange-lt) 65%,transparent);border-radius:99px;padding:3px 10px}
.brand-var{margin:10px 8px 0;font:500 12px var(--body);color:#B9C7D8}
.navlist{margin-top:10px}
.navgrp{color:#8FA5BD;padding:14px 10px 4px}
.navlist a{color:#D5DFEA;font-weight:500;font-size:13.5px;padding:7px 10px;border-radius:var(--r-sm);border-left:3px solid transparent;transition:background .12s}
.navlist a span{color:#8FA5BD}
.navlist a:hover{background:rgba(255,255,255,.08);color:#fff}
.navlist a.on{background:rgba(255,255,255,.13);color:#fff;border-left-color:var(--be-orange-lt)}
.navlist a.on span{color:var(--be-orange-lt)}
.sidenote{color:#9FB0C4;border-top-color:rgba(255,255,255,.14)}
main{padding:0 32px 56px}
.view{max-width:1220px}
/* 3 · KOPBALK */
.top{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:16px;flex-wrap:wrap;background:color-mix(in srgb,var(--be-bg) 94%,transparent);backdrop-filter:blur(6px);margin:0 -32px 22px;padding:11px 32px;border-bottom:1px solid var(--be-line)}
.crumb{line-height:1.25;min-width:0;flex:1}
.crumb small{display:block;font:600 10.5px var(--body);letter-spacing:.08em;text-transform:uppercase;color:var(--be-ink-3)}
.crumb b{font:700 15px var(--display);color:var(--be-navy)}
.top-client{display:flex;align-items:center;gap:8px}
.top-client label{font:600 10.5px var(--body);letter-spacing:.08em;text-transform:uppercase;color:var(--be-ink-3)}
.top-client input{width:200px}
.pr{display:none}
/* 4 · COMPONENTEN */
.card{border-radius:var(--r-md);box-shadow:var(--shadow);border-color:var(--be-line)}
.tile{display:flex;flex-direction:column;gap:2px}
.tile .lbl{font-size:12.5px;color:var(--be-ink-2);font-weight:500}
.tile .val{font:800 26px/1.15 var(--display);color:var(--be-navy);letter-spacing:-.01em;margin-top:2px}
.tile .val.neg,.tile .val .neg{color:var(--be-bad)}.tile .val.pos{color:var(--be-good)}
.tile .sub{font-size:12.5px;color:var(--be-ink-3)}
.tile{border-top:3px solid var(--be-navy-100)}
.btn{border-radius:var(--r-sm);color:var(--be-navy);transition:background .12s,border-color .12s}
.btn:hover{border-color:var(--be-navy);background:var(--be-navy-50);color:var(--be-navy)}
.btn.pri{background:var(--be-navy);border-color:var(--be-navy);color:#fff}.btn.pri:hover{background:var(--be-navy-700);filter:none;color:#fff}
.seg{background:var(--be-surface)}.seg button{color:var(--be-navy);background:transparent}.seg button:hover{background:var(--be-navy-50)}
.seg button.on{background:var(--be-navy);color:#fff}
input[type=number],input[type=text],input[type=search],select,textarea,.rmO,.rmCtl select,.rmCtl input,#rmNT,#rmNL,#rmNF{background:var(--be-surface);border-color:var(--be-line)}
input:hover,select:hover,textarea:hover{border-color:#B9C4D0}
input:focus-visible,select:focus-visible,button:focus-visible,a:focus-visible,textarea:focus-visible{outline:none;box-shadow:var(--focus)}
nav.side a:focus-visible{box-shadow:0 0 0 3px rgba(255,255,255,.35)}
th{background:var(--be-bg);color:var(--be-ink-3);font-size:11.5px;letter-spacing:.05em;border-bottom:1px solid var(--be-line)}
td{border-bottom-color:var(--be-line-soft)}
tbody tr:hover td{background:#FAFBFD}
tr.sum td{border-top:2px solid var(--be-navy)}
.layer,.item,.tl,.mgr,.kpitile,.rmAct{border-radius:var(--r-md);box-shadow:var(--shadow);border-color:var(--be-line)}
.layer{border-left-color:var(--be-navy)}.layer.on{border-left-color:var(--be-orange);box-shadow:0 0 0 1px var(--be-orange)}
.kpitile{border-left-width:4px}
.pill,.p-cool{font-weight:500}
.demo-banner{border-radius:var(--r-sm)}
/* overzicht: compactere, rustigere kop */
#v-overzicht>.card:first-child{padding:20px 26px!important;border-left:4px solid var(--be-orange)!important}
#v-overzicht>.card:first-child div[style*="clamp"]{font-size:clamp(1.45rem,2.6vw,2rem)!important;line-height:1.12!important;color:var(--be-navy)!important}
#v-overzicht>.card:first-child p{font-size:1rem!important}
#v-overzicht>h1{margin-top:6px}
/* 5 · RESPONSIVE */
@media (max-width:1000px){.app{grid-template-columns:210px 1fr}main{padding:0 20px 48px}.top{margin:0 -20px 18px;padding:10px 20px}.top-client input{width:150px}}
@media (max-width:760px){.app{grid-template-columns:1fr}nav.side{padding:12px 14px}.navlist a{white-space:nowrap}main{padding:0 16px 40px}.top{margin:0 -16px 16px;padding:10px 16px;position:static}.top-client{width:100%}.top-client input{flex:1;width:auto}}
/* 6 · PRINT (A4 liggend: de actieve sectie, zonder navigatie en bediening) */
@page{size:A4 landscape;margin:11mm}
@media print{
  *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  body{background:#fff;font-size:12px}
  .app{display:block}nav.side,.noprint,.btn,.seg,.top-client input,.rmSeg,.linkbtn{display:none!important}
  main{padding:0}.view{max-width:none}
  .top{position:static;margin:0 0 10px;padding:0 0 8px;background:#fff;border-bottom:2px solid var(--be-navy);backdrop-filter:none}
  .top-client .pr{display:inline!important;font:700 13px var(--display);color:var(--be-navy)}
  .card,.layer,.item,.tl,.mgr,.kpitile,.rmAct{box-shadow:none}
  .layer,.item,.tl,.mgr,.kpitile,.rmAct,.tile,tr{break-inside:avoid}
  .top-client label{display:none}
  h1,h2,h3{break-after:avoid}
  .scrolly{max-height:none;overflow:visible}.tablewrap{overflow:visible}
  .grid{gap:10px}
}
'''
def tokens(B):
    L=B['colors']['light'];S=B['colors']['status']['light']
    nv,ac=L['primary'],L['accent']
    return f""":root:root:root{{
  --be-navy:{nv}; --be-navy-700:{mix(nv,'#000000',.25)}; --be-navy-100:{mix(nv,'#FFFFFF',.84)}; --be-navy-50:{L['primary_soft']};
  --be-orange:{ac}; --be-orange-700:{mix(ac,'#000000',.2)}; --be-orange-50:{L['accent_soft']}; --be-orange-lt:{mix(ac,'#FFFFFF',.28)};
  --be-bg:{L['background']}; --be-surface:{L['surface']}; --be-ink:{L['text']}; --be-ink-2:{L['text_muted']}; --be-ink-3:{mix(L['text_muted'],L['background'],.3)};
  --be-line:{L['border']}; --be-line-soft:{mix(L['border'],'#FFFFFF',.55)};
  --be-good:{S['good']}; --be-good-50:{S['good_soft']}; --be-warn:{S['warning']}; --be-warn-50:{S['warning_soft']}; --be-bad:{S['critical']}; --be-bad-50:{S['critical_soft']};
  --r-sm:6px; --r-md:10px; --shadow:0 1px 2px color-mix(in srgb,var(--be-navy) 8%,transparent); --focus:0 0 0 3px color-mix(in srgb,var(--be-navy) 28%,transparent);
  --bg:var(--be-bg); --panel:var(--be-surface); --ink:var(--be-ink); --muted:var(--be-ink-2); --line:var(--be-line);
  --accent:var(--be-orange); --accent-soft:var(--be-orange-50); --cool:var(--be-navy); --cool-soft:var(--be-navy-50); --primary:var(--be-navy);
  --good:var(--be-good); --good-soft:var(--be-good-50); --warn:var(--be-warn); --warn-soft:var(--be-warn-50); --bad:var(--be-bad); --bad-soft:var(--be-bad-50);
  --radius:var(--r-md); color-scheme:light;
}}
"""
TOP='''<!-- DESIGN:TOP:START -->
<header class="top">
  <div class="crumb"><small id="tbGrp">Framework</small><b id="tbSec">Overzicht en context</b></div>
  <div class="top-client"><label for="tbKlant">Klant</label><input type="text" id="tbKlant" placeholder="Klantnaam" autocomplete="off" aria-label="Klantnaam"><span class="pr" id="tbKlantPr"></span></div>
  <button class="btn noprint" id="tbPrint" title="Druk de huidige sectie af of sla op als pdf">Afdrukken</button><span class="note noprint" id="tbMsg" aria-live="polite"></span>
</header>
<!-- DESIGN:TOP:END -->
'''
JS='''<!-- DESIGN:JS:START -->
<script>
/* === ONTWERPLAAG: kopbalk (broodkruimel, klantnaam, afdrukken); geen invloed op de berekeningen === */
(function(){const $=s=>document.querySelector(s);let kl='';try{kl=localStorage.getItem('be_klant')||''}catch(e){}
  const inp=$('#tbKlant'),pr=$('#tbKlantPr');inp.value=kl;pr.textContent=kl;
  inp.addEventListener('input',()=>{kl=inp.value;pr.textContent=kl;try{localStorage.setItem('be_klant',kl)}catch(e){}});
  function crumb(){const a=document.querySelector('#nav a.on');if(!a)return;let g='';for(let n=a.previousElementSibling;n;n=n.previousElementSibling){if(n.classList.contains('navgrp')){g=n.textContent;break}}
    $('#tbGrp').textContent=g||'Framework';$('#tbSec').textContent=(a.lastChild.textContent||'').trim()}
  window.addEventListener('hashchange',()=>setTimeout(crumb,0));crumb();
  $('#tbPrint').onclick=()=>{try{window.print()}catch(e){$('#tbMsg').textContent='Gebruik Ctrl+P (Cmd+P) om af te drukken of als pdf op te slaan.'}};
})();
</script>
<!-- DESIGN:JS:END -->
'''
def undo(h):
    # herstel zijbalkmerk
    m=re.search(r'<!-- DESIGN:BRAND:START -->.*?<!-- DESIGN:BRAND:END -->',h,re.S)
    if m:
        orig=re.search(r'<!-- DESIGN:ORIG (.*?) -->',m.group(0),re.S).group(1).replace('- -','--')
        h=h.replace(m.group(0),orig)
    h=re.sub(r'/\* DESIGN:START.*?/\* DESIGN:END \*/\n?','',h,flags=re.S)
    h=re.sub(r'<!-- DESIGN:TOP:START -->.*?<!-- DESIGN:TOP:END -->\n?','',h,flags=re.S)
    h=re.sub(r'<!-- DESIGN:JS:START -->.*?<!-- DESIGN:JS:END -->\n?','',h,flags=re.S)
    return h
def apply(h,B):
    h=undo(h)
    # zijbalkmerk
    m=re.search(r'<div class="brand">(.*?)</div>',h,re.S)
    assert m,'brand-blok niet gevonden'
    orig=m.group(0);inner=m.group(1)
    sm=re.search(r'<small[^>]*>(.*?)</small>',inner,re.S);var=sm.group(1).strip() if sm else ''
    dm=re.search(r'<span class="demo-flag">(.*?)</span>',inner,re.S);demo=dm.group(1) if dm else ''
    new=('<!-- DESIGN:BRAND:START --><!-- DESIGN:ORIG '+orig.replace('--','- -')+' -->'
         '<div class="brand"><div class="logo" aria-hidden="true">B</div><div class="brand-t"><b>B.Enable</b><span>Control Framework</span></div></div>'
         +(f'\n  <div class="brand-var">{var}</div>' if var else '')
         +(f'\n  <span class="demo-flag">{demo}</span>' if demo else '')+'<!-- DESIGN:BRAND:END -->')
    h=h.replace(orig,new,1)
    # css
    css='/* DESIGN:START · ontwerplaag uit '+B['brand']['name']+' huisstijl v'+B['version']+' · niet met de hand wijzigen */\n'+tokens(B)+CSS_TAIL+'/* DESIGN:END */\n'
    i=h.index('</style>');h=h[:i]+css+h[i:]
    # kopbalk
    h=h.replace('<main>\n','<main>\n'+TOP,1);assert 'DESIGN:TOP:START' in h
    j=h.rindex('</body>');h=h[:j]+JS+h[j:]
    return h
if __name__=='__main__':
    if sys.argv[1]=='--undo':
        p=sys.argv[2];h=undo(open(p).read());open(p,'w').write(h);print('undo ok')
    else:
        B=json.load(open(sys.argv[1]));p=sys.argv[2];h=apply(open(p).read(),B);open(p,'w').write(h);print('design ok',B['brand']['name'])
