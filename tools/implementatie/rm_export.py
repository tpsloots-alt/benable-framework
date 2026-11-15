"""Voegt aan de module Vastleggen → Verbeterroadmap een functie RM.export() toe,
zodat het implementatieplan (tabblad 12, eigen bestand in dezelfde klantmap) de roadmap kan lezen.
Gebruik: python3 tools/implementatie/rm_export.py pagina.html [uit.html]
Werkt op elke framework-pagina met de roadmap-module (InWarmte, Projectorganisaties, casus). Idempotent."""
import sys
src=sys.argv[1];dst=sys.argv[2] if len(sys.argv)>2 else src
h=open(src).read()
MARK='/* RM:EXPORT */'
if MARK in h: print('al aanwezig',dst);open(dst,'w').write(h);sys.exit()
old='window.RM={refresh(){'
assert h.count(old)==1,'roadmap-module niet gevonden'
api=MARK+r"""
/* Levert de roadmap aan het implementatieplan. Alleen lezen: het plan verandert niets in het framework. */
function rmExport(){const crit=window.__scanCrit||[],its=items();
  return{versie:1,naam:C.naam,key:K,demo:!!D.demo,lagen:C.lagen.slice(),fases:C.fases.map(f=>f.slice()),
   open:its.filter(x=>!st(x.id)).length,beoordeeld:its.filter(x=>st(x.id)).length,
   niveaus:niveaus().map(n=>({laag:n.i+1,naam:C.lagen[n.i],eff:n.eff,afg:n.afg,man:n.man||null,b:n.b,crit:((crit[n.i]||[])[1]||[]).slice()})),
   acties:acties().map(a=>({id:a.id,tekst:a.tekst,laag:a.laag,fase:+a.fase||0,eig:a.eig||'',prio:+a.prio||0,stat:+a.stat||0,s:a.s,eigen:!!a.eigen,norm:a.it?a.it.norm:'',groep:a.it?a.it.groep:'',tab:a.tab||'',tabNaam:a.tab?tabNaam(a.tab):'',o:a.o||''}))}}
"""
h=h.replace(old,api+'window.RM={export:rmExport,refresh(){',1)
open(dst,'w').write(h);print('ok',dst)
