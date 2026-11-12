"""Maakt de sitebuild van een framework-pagina met een presentatie-slot (blur + pincode).
Gebruik: python3 tools/lock.py bron.html doel.html sturing,organisatie,cyclus,datamodel,roadmap
De pincode zet je daarna met: node scripts/zet-pincode.mjs <pincode> <doel.html>"""
import sys
src,dst,views=sys.argv[1],sys.argv[2],sys.argv[3].split(',')
h=open(src).read()
css='''
/* LOCK:START presentatie-slot */
section.view.locked{position:relative}
section.view.locked>*:not(.lockbox){filter:blur(7px);pointer-events:none;user-select:none}
.lockbox{display:none}
section.view.locked>.lockbox{display:block;position:sticky;top:28vh;z-index:5;max-width:420px;margin:0 auto 24px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:22px 24px;box-shadow:0 10px 40px rgba(0,0,0,.18)}
.lockbox h2{margin:0 0 6px}.lockbox p{margin:0 0 12px;color:var(--muted)}
.lockbox form{display:flex;gap:8px}.lockbox input{flex:1;font:inherit;font-size:20px;letter-spacing:.3em;text-align:center;padding:8px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink)}
.lockbox .msg{min-height:1.2em;margin-top:8px;font-size:13px;color:var(--bad)}
#nav a.lk::after{content:"🔒";font-size:11px;margin-left:6px;opacity:.7}
.who{margin-top:10px;font-size:12px;color:var(--muted)}
/* LOCK:END */
'''
i=h.index('</style>');h=h[:i]+css+h[i:]
js='''
/* LOCK:START presentatie-slot: geen beveiliging, alleen voor de presentatie */
(function(){
const LOCK_VIEWS=%s;
const LOCK_HASH="__PIN_HASH__";
const KEY='be_unlock_'+location.pathname;
let fails=0,waitUntil=0;
const isOpen=()=>{try{return sessionStorage.getItem(KEY)===LOCK_HASH}catch(e){return false}};
async function sha(t){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode('benable:'+t));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('')}
function apply(){const open=isOpen();
  LOCK_VIEWS.forEach(v=>{const s=document.getElementById('v-'+v);if(!s)return;s.classList.toggle('locked',!open);
    [...s.children].forEach(c=>{if(!c.classList.contains('lockbox')){if(open)c.removeAttribute('aria-hidden');else c.setAttribute('aria-hidden','true')}});
    const a=document.querySelector('#nav a[href="#'+v+'"]');if(a)a.classList.toggle('lk',!open)});}
LOCK_VIEWS.forEach(v=>{const s=document.getElementById('v-'+v);if(!s)return;const box=document.createElement('div');box.className='lockbox';
  box.innerHTML='<h2>Bespreken we samen</h2><p>Dit onderdeel lichten we toe in de sessie. Vul de pincode in om het te openen.</p><form><input type="password" inputmode="numeric" autocomplete="off" aria-label="Pincode" maxlength="12"><button class="btn pri" type="submit">Open</button></form><div class="msg" role="status"></div>';
  s.insertBefore(box,s.firstChild);
  box.querySelector('form').onsubmit=async e=>{e.preventDefault();const inp=box.querySelector('input'),msg=box.querySelector('.msg');
    if(Date.now()<waitUntil){msg.textContent='Even wachten en opnieuw proberen.';return}
    if(await sha(inp.value.trim())===LOCK_HASH){try{sessionStorage.setItem(KEY,LOCK_HASH)}catch(err){}msg.textContent='';inp.value='';apply()}
    else{fails++;inp.value='';msg.textContent='Onjuiste pincode.';if(fails>=5){waitUntil=Date.now()+30000;fails=0;msg.textContent='Te vaak onjuist. Probeer het over 30 seconden opnieuw.'}}};});
apply();
// bezoeker en vervaldatum uit de toegangslink (cookie gezet door de server)
try{const m=document.cookie.match(/(?:^|; )be_who=([^;]*)/);if(m){const [n,e]=decodeURIComponent(m[1]).split('|');const d=new Date(+e*1000);const el=document.createElement('div');el.className='who';el.textContent='Toegang voor '+n+' tot '+d.toLocaleDateString('nl-NL',{day:'numeric',month:'long',year:'numeric'});const sn=document.querySelector('.sidenote');if(sn)sn.after(el)}}catch(e){}
})();
/* LOCK:END */
''' % repr(views).replace("'",'"')
i=h.rindex('</script>');h=h[:i]+js+h[i:]
h=h.replace('<head>','<head>\n<meta name="robots" content="noindex,nofollow">',1)
open(dst,'w').write(h);print('ok',dst)
