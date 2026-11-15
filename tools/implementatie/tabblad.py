"""Zet het tabblad Implementatieplan in een framework-pagina (vóór lock.py). Idempotent.
Gebruik: python3 tools/implementatie/tabblad.py bron.html [uit.html] [nummer]
- menu-item na Verbeterroadmap, sectie v-implementatie, en een lader die implementatie/ als ingebed venster toont
  (pas na het laden van de pagina, zodat de roadmap-module RM.export() klaar is) met automatische hoogte.
Zet daarna ook de module-export (rm_export.py) en neem 'implementatie' op in de lijst van lock.py."""
import sys,re
src=sys.argv[1];dst=sys.argv[2] if len(sys.argv)>2 else src;nr=sys.argv[3] if len(sys.argv)>3 else '12'
h=open(src).read()
if 'IMPL:START' in h:
    h=re.sub(r'\n?<!-- IMPL:NAV -->.*?<!-- /IMPL:NAV -->','',h,flags=re.S)
    h=re.sub(r'\n?<!-- IMPL:SECTIE -->.*?<!-- /IMPL:SECTIE -->\n','\n',h,flags=re.S)
    h=re.sub(r'\n?/\* IMPL:START.*?/\* IMPL:END \*/\n','\n',h,flags=re.S)
    h=h.replace(",'implementatie'",'')
nav=re.search(r'\n(\s*)<a href="#roadmap">[^\n]*</a>',h);assert nav,'menu-item Verbeterroadmap niet gevonden'
h=h[:nav.end()]+'\n%s<!-- IMPL:NAV --><a href="#implementatie"><span>%s</span>Implementatieplan</a><!-- /IMPL:NAV -->'%(nav.group(1),nr)+h[nav.end():]
sec='''<!-- IMPL:SECTIE -->
<section class="view" id="v-implementatie">
  <h1>Implementatieplan</h1>
  <p class="lede">Van verbeterroadmap naar uitvoering: wie doet wat en wanneer, wat dat vraagt aan capaciteit en welke besluiten nodig zijn. Het plan gebruikt de acties uit de verbeterroadmap (tabblad 11).</p>
  <div id="implHost"><p class="note">Het implementatieplan wordt geladen…</p></div>
</section>
<!-- /IMPL:SECTIE -->
'''
m=re.search(r'\n<!-- [A-Z0-9]+ BEGRIPPEN -->',h) or re.search(r'\n<section class="view" id="v-begrippen"',h)
assert m,'sectie Begrippen niet gevonden';h=h[:m.start()+1]+sec+h[m.start()+1:]
v=re.search(r"const views=\[([^\]]*)'roadmap'",h);assert v,'routering niet gevonden'
h=h[:v.end()]+",'implementatie'"+h[v.end():]
css='\n#v-implementatie{max-width:1360px}\n#implHost iframe{width:100%;border:0;display:block;min-height:640px;background:transparent}\n'
i=h.index('</style>');h=h[:i]+'/* IMPL:CSS */'+css+h[i:] if '/* IMPL:CSS */' not in h else h
js=r'''/* IMPL:START tabblad Implementatieplan: eigen bestand in implementatie/ (lees- of bewerkversie, de server kiest); leest tabblad 11 via RM.export() */
(function(){let fr=null;
  function fit(){try{const d=fr.contentDocument;if(!d||!d.body)return;const w=d.querySelector('.wrap')||d.body,h=Math.ceil(w.getBoundingClientRect().bottom+(d.defaultView.scrollY||0))+8;if(Math.abs(fr.offsetHeight-h)>4)fr.style.height=h+'px'}catch(e){}}
  function laad(){if(fr||location.hash!=='#implementatie'||!window.RM||document.readyState!=='complete')return;const host=document.getElementById('implHost');if(!host)return;
    fr=document.createElement('iframe');fr.src='implementatie/';fr.title='Implementatieplan';fr.setAttribute('allow','fullscreen');fr.allowFullscreen=true;
    host.innerHTML='';host.appendChild(fr);
    fr.addEventListener('load',()=>{fit();try{new ResizeObserver(fit).observe(fr.contentDocument.body)}catch(e){}});setInterval(fit,1000)}
  window.addEventListener('hashchange',laad);window.addEventListener('load',laad);laad();
})();
/* IMPL:END */
'''
i=h.rindex('</script>');h=h[:i]+js+h[i:]
open(dst,'w').write(h);print('ok',dst)
