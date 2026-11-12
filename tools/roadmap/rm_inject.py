"""Voegt de module Vastleggen → Roadmap toe aan een framework-pagina.
Gebruik: python3 rm_inject.py pagina.html items-config.js [uit.html]"""
import sys,os
src,cfg=sys.argv[1],sys.argv[2];dst=sys.argv[3] if len(sys.argv)>3 else src
here=os.path.dirname(os.path.abspath(__file__))
h=open(src).read()
assert 'RM:START' not in h,'module zit er al in'
h=h.replace('</style>',open(os.path.join(here,'rm.css')).read()+'</style>',1)
a='<div class="grid g3" id="roadmapCols"></div>'
assert h.count(a)==1
h=h.replace(a,'<div class="grid g3" id="roadmapCols" style="display:none"></div>\n  <div id="rmRoad"></div>')
# oude voortgangsbalk verbergen
i=h.index('<b id="progTxt"></b>');j=h.rindex('<div class="card"',0,i)
h=h[:j]+'<div class="card" style="display:none"'+h[j+len('<div class="card"'):]
js='<script>\n/* RM:START */\n'+open(os.path.join(here,'items-core.js')).read()+'\n'+open(cfg).read()+'\n'+open(os.path.join(here,'roadmap-module.js')).read()+'\n/* RM:END */\n</script>\n'
k=h.rindex('</body>');h=h[:k]+js+h[k:]
open(dst,'w').write(h);print('ok',dst)
