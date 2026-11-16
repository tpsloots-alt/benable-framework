"""Voegt aan de module Vastleggen → Verbeterroadmap een functie RM.export() toe,
zodat het implementatieplan (tabblad 12, eigen bestand in dezelfde klantmap) de roadmap kan lezen.
Gebruik: python3 tools/implementatie/rm_export.py pagina.html [uit.html]
Werkt op elke framework-pagina met de roadmap-module (InWarmte, Projectorganisaties, casus). Idempotent."""
import sys
src=sys.argv[1];dst=sys.argv[2] if len(sys.argv)>2 else src
h=open(src).read()
MARK='/* RM:EXPORT */'
if MARK in h:  # oudere versie van dit blok vervangen
    a=h.index(MARK);b=h.index('window.RM={export:rmExport',a);e=h.index('refresh(){',b)
    h=h[:a]+'window.RM={refresh(){'+h[e+len('refresh(){'):]
old='window.RM={refresh(){'
assert h.count(old)==1,'roadmap-module niet gevonden'
api=MARK+r"""
/* Levert de roadmap aan het implementatieplan. Alleen lezen: het plan verandert niets in het framework. */
/* Rollen uit het tabblad Organisatie (het implementatieplan kent alleen deze rollen). */
const rmEigKey='be_rollen_'+K;
const rmEigen=()=>{const v=LS.get(rmEigKey,[]);return Array.isArray(v)?v.filter(r=>r&&r.naam&&(r.groep==='finance'||r.groep==='business')):[]};
const rmStd=()=>[['rolesFin','finance'],['rolesBus','business']].flatMap(([id,g])=>[...document.querySelectorAll('#'+id+'>div:not(.rolEigen)')].map(d=>({naam:((d.querySelector('h3')||{}).textContent||'').trim(),groep:g,omschr:((d.querySelector('.note')||{}).textContent||'').trim()}))).filter(r=>r.naam);
const rmRollen=()=>rmStd().concat(rmEigen().map(r=>({naam:r.naam,groep:r.groep,omschr:r.omschr||'',eigen:true})));
/* Eigen rollen toevoegen in tabblad Organisatie (alleen toevoegen; de standaardrollen blijven staan). */
(function(){const e=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 let bezig=false;
 function teken(){if(bezig)return;bezig=true;try{
  [['rolesFin','finance','finance'],['rolesBus','business','de business']].forEach(([id,g,lab])=>{const st=document.getElementById(id);if(!st)return;const card=st.parentElement;
   st.querySelectorAll('.rolEigen').forEach(x=>x.remove());const f0=card.querySelector('.rolForm');if(f0)f0.remove();
   rmEigen().filter(r=>r.groep===g).forEach(r=>{const d=document.createElement('div');d.className='rolEigen';
    d.innerHTML='<h3>'+e(r.naam)+' <span class="note" style="font-weight:400">(eigen rol)</span></h3><p class="note" style="margin:0">'+e(r.omschr||'Eigen rol, toegevoegd door de adviseur.')+'</p><button class="btn rolDel" style="margin-top:6px" aria-label="Rol '+e(r.naam)+' verwijderen">Verwijderen</button>';
    d.querySelector('.rolDel').onclick=()=>{LS.set(rmEigKey,rmEigen().filter(x=>!(x.naam===r.naam&&x.groep===g)));teken()};st.appendChild(d)});
   const f=document.createElement('div');f.className='rolForm stack';f.style.cssText='gap:8px;margin-top:12px';
   f.innerHTML='<h3>Eigen rol toevoegen</h3><input type="text" class="rolN" placeholder="Naam van de rol, bijvoorbeeld Projectmanagement" aria-label="Naam van de rol"><input type="text" class="rolO" placeholder="Korte omschrijving (optioneel)" aria-label="Omschrijving van de rol"><div class="row" style="gap:8px;align-items:center"><button class="btn pri rolAdd">Rol toevoegen</button><span class="note rolMsg" role="status"></span></div>';
   card.appendChild(f);
   f.querySelector('.rolAdd').onclick=()=>{const n=f.querySelector('.rolN').value.replace(/\s+/g,' ').trim(),o=f.querySelector('.rolO').value.trim(),m=f.querySelector('.rolMsg');
    if(!n){m.textContent='Vul een naam in.';return}
    if(rmRollen().some(r=>r.naam.toLowerCase()===n.toLowerCase())){m.textContent='Deze rol bestaat al.';return}
    LS.set(rmEigKey,rmEigen().concat([{naam:n,groep:g,omschr:o}]));teken()}});
 }finally{bezig=false}}
 const start=()=>{teken();['rolesFin','rolesBus'].forEach(id=>{const st=document.getElementById(id);if(st)new MutationObserver(()=>{if(!bezig&&!st.querySelector('.rolEigen')&&rmEigen().length||!bezig&&!st.parentElement.querySelector('.rolForm'))teken()}).observe(st,{childList:true})})};
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
 window.__rolTeken=teken;})();
function rmExport(){const crit=window.__scanCrit||[],its=items();
  return{versie:1,naam:C.naam,key:K,demo:!!D.demo,lagen:C.lagen.slice(),fases:C.fases.map(f=>f.slice()),
   rollen:rmRollen(),
   open:its.filter(x=>!st(x.id)).length,beoordeeld:its.filter(x=>st(x.id)).length,
   niveaus:niveaus().map(n=>({laag:n.i+1,naam:C.lagen[n.i],eff:n.eff,afg:n.afg,man:n.man||null,b:n.b,crit:((crit[n.i]||[])[1]||[]).slice()})),
   acties:acties().map(a=>({id:a.id,tekst:a.tekst,laag:a.laag,fase:+a.fase||0,eig:a.eig||'',prio:+a.prio||0,stat:+a.stat||0,s:a.s,eigen:!!a.eigen,norm:a.it?a.it.norm:'',groep:a.it?a.it.groep:'',tab:a.tab||'',tabNaam:a.tab?tabNaam(a.tab):'',o:a.o||''})),
   vast:its.map(it=>({id:it.id,tabNaam:tabNaam(it.tab),laag:it.laag,groep:it.groep,norm:it.norm,s:st(it.id),o:(D.st[it.id]||{}).o||'',actie:it.actie}))}}
/* Volledige stand van de vastleggingen, voor het versiebestand; laad() zet een opgeslagen stand terug. */
const rmStaat=()=>JSON.parse(JSON.stringify(D));
function rmLaad(d){if(!d||typeof d!=='object')return;D=Object.assign({st:{},act:{},extra:[]},d);save();document.querySelectorAll('.rmPanel').forEach(c=>c.remove());all()}
"""
h=h.replace(old,api+'window.RM={export:rmExport,staat:rmStaat,laad:rmLaad,refresh(){',1)
open(dst,'w').write(h);print('ok',dst)
