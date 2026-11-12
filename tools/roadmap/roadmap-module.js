/* B.Enable · module Vastleggen → Verbeterroadmap (generiek, voor alle frameworks)
   Verwacht window.RM_CFG = {
     naam:'inwarmte', key:()=>'opslagsleutel', items:()=>[{id,tab,laag,groep,norm,actie,eig,fase}],
     fases:[['Snelle verbeteringen','0–3 maanden'],...], lagen:['Financiële basis',...], demo:()=>({id:'ok'|'deels'|'niet'}) }
   Zet per tabblad (section#v-<tab>) een kaart "Vastleggen" en bouwt in #rmRoad de roadmap. */
(function(){
const C=window.RM_CFG;if(!C)return;
const $=s=>document.querySelector(s);
const LS={get(k,d){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const LAB={ok:'Op orde',deels:'Deels',niet:'Niet op orde'};
const PRIO=['Hoog','Midden','Laag'],STAT=['Niet gestart','Loopt','Gereed'];
function fresh(demo){const d={st:{},act:{},extra:[],demo:!!demo};if(demo&&C.demo)Object.entries(C.demo()).forEach(([id,s])=>d.st[id]={s,o:''});return d}
let K=C.key(),D=LS.get(K,null)||fresh(true);
const save=()=>LS.set(K,D);
const items=()=>C.items().filter(it=>document.getElementById('v-'+it.tab));
const tabNaam=t=>{const a=document.querySelector('#nav a[href="#'+t+'"]');if(!a)return t;const sp=a.querySelector('span');return a.textContent.slice(sp?sp.textContent.length:0).trim()};
const st=id=>(D.st[id]&&D.st[id].s)||'';
const act=(id,it)=>Object.assign({fase:it.fase||0,prio:1,stat:0,eig:it.eig||''},D.act[id]||{});

function panel(tab){const sec=document.getElementById('v-'+tab);if(!sec)return;const its=items().filter(i=>i.tab===tab);if(!its.length)return;
  let card=sec.querySelector(':scope>.rmPanel');if(!card){card=document.createElement('div');card.className='card rmPanel';sec.appendChild(card)}
  const n=its.filter(i=>st(i.id)).length,ok=its.filter(i=>st(i.id)==='ok').length;const groepen=[...new Set(its.map(i=>i.groep))];
  card.innerHTML=`<div class="row" style="justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:6px"><h2 style="margin:0">Vastleggen: hoe staat het bij jullie?</h2><span class="note">${n} van ${its.length} beoordeeld · ${ok} op orde</span></div>
   <p class="note" style="margin:4px 0 6px">Beoordeel per punt de huidige situatie. Wat niet of deels op orde is, wordt een actie in de <a href="#roadmap">verbeterroadmap</a>.${D.demo?' <span class="badge-ex">voorbeeldinvulling</span>':''}</p>`+
   groepen.map(g=>`<h3 class="rmG">${esc(g)}</h3>`+its.filter(i=>i.groep===g).map(it=>{const s=st(it.id),o=(D.st[it.id]||{}).o||'';
    return `<div class="rmRow"><div><div class="rmT">${esc(it.norm)}</div><div class="note">Laag ${it.laag}${s&&s!=='ok'?' · actie: '+esc(it.actie):''}</div></div>
     <div class="seg rmSeg" role="group" aria-label="Beoordeling">${['ok','deels','niet'].map(k=>`<button type="button" class="${s===k?'on rm-'+k:''}" data-id="${it.id}" data-s="${k}" aria-pressed="${s===k}">${LAB[k]}</button>`).join('')}</div>
     <input class="rmO" data-id="${it.id}" value="${esc(o)}" placeholder="Toelichting" aria-label="Toelichting"></div>`}).join('')).join('');
  card.querySelectorAll('.rmSeg button').forEach(b=>b.onclick=()=>{const id=b.dataset.id,cur=st(id);D.st[id]=Object.assign(D.st[id]||{o:''},{s:cur===b.dataset.s?'':b.dataset.s});save();all()});
  card.querySelectorAll('.rmO').forEach(el=>el.onchange=()=>{const id=el.dataset.id;D.st[id]=Object.assign(D.st[id]||{s:''},{o:el.value});save();road()});
}
function acties(){const out=[];items().forEach(it=>{const s=st(it.id);if(s==='deels'||s==='niet')out.push(Object.assign({it,s,o:(D.st[it.id]||{}).o||''},act(it.id,it),{id:it.id,tekst:it.actie,laag:it.laag,tab:it.tab}))});
  D.extra.forEach(x=>out.push(Object.assign({s:'eigen',o:'',tab:''},act(x.id,x),{id:x.id,tekst:x.tekst,laag:x.laag,eigen:1})));
  return out.sort((a,b)=>a.laag-b.laag||a.prio-b.prio)}
function road(){const host=$('#rmRoad');if(!host)return;const its=items(),A=acties();
  const lagen=C.lagen.map((l,i)=>{const li=its.filter(x=>x.laag===i+1),b=li.filter(x=>st(x.id)),ok=b.filter(x=>st(x.id)==='ok').length,de=b.filter(x=>st(x.id)==='deels').length;const pct=b.length?(ok+de*0.5)/b.length:null;return{l,n:li.length,b:b.length,ok,de,pct,score:pct==null?null:1+Math.round(pct*4)}});
  const open=its.filter(x=>!st(x.id)),gereed=A.filter(a=>a.stat===2).length;
  host.innerHTML=`<div class="card" style="margin-top:16px"><div class="row" style="justify-content:space-between;flex-wrap:wrap;gap:8px"><div><h2 style="margin:0">Roadmap uit de vastleggingen</h2><p class="note" style="margin:2px 0 0">${A.length} acties · ${gereed} gereed · ${open.length} punten nog niet beoordeeld${D.demo?' · <span class="badge-ex">voorbeeldinvulling</span>':''}</p></div>
    <div class="row" style="gap:6px;flex-wrap:wrap"><button class="btn" id="rmCsv">Exporteer roadmap (Excel)</button><button class="btn" id="rmCsv2">Exporteer vastleggingen</button><button class="btn" id="rmCopy">Kopieer roadmap</button><button class="btn" id="rmNieuw">Begin nulmeting (alles leeg)</button>${D.demo?'':'<button class="btn" id="rmDemo">Voorbeeld terugzetten</button>'}</div></div>
    <p class="note rmMsg" id="rmMsg" role="status"></p>
    <div class="grid g4" style="margin-top:8px">${lagen.map((x,i)=>`<div class="tile"><div class="lbl">Laag ${i+1} · ${esc(x.l)}</div><div class="val">${x.pct==null?'–':Math.round(x.pct*100)+'%'}</div><div class="sub">${x.ok} op orde · ${x.de} deels · ${x.b-x.ok-x.de} niet · ${x.n-x.b} open${x.score?` · indicatie niveau ${x.score}`:''}</div><div class="bar" style="margin-top:6px"><i style="width:${(x.pct||0)*100}%;background:${x.pct==null?'var(--line)':x.pct>=0.6?'var(--good)':x.pct>=0.35?'var(--warn)':'var(--bad)'}"></i></div></div>`).join('')}</div></div>
   <div class="grid g3" style="margin-top:16px">${C.fases.map((f,fi)=>{const L=A.filter(a=>a.fase===fi);return `<div class="phase"><div><h2 style="margin:0">${esc(f[0])}</h2><span class="note">${esc(f[1])} · ${L.length} acties</span></div>${L.map(card).join('')||'<p class="note">Geen acties.</p>'}</div>`}).join('')}</div>
   <div class="grid" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;margin-top:16px">
    <div class="card"><h2>Eigen actie toevoegen</h2><div class="stack" style="gap:8px"><input id="rmNT" placeholder="Omschrijving van de actie" aria-label="Omschrijving"><div class="row" style="gap:8px"><select id="rmNL" aria-label="Laag">${C.lagen.map((l,i)=>`<option value="${i+1}">Laag ${i+1} · ${esc(l)}</option>`).join('')}</select><select id="rmNF" aria-label="Fase">${C.fases.map((f,i)=>`<option value="${i}">${esc(f[0])}</option>`).join('')}</select><button class="btn pri" id="rmAdd">Toevoegen</button></div></div></div>
    <div class="card"><h2>Nog te beoordelen (${open.length})</h2>${open.length?[...new Set(open.map(x=>x.tab))].map(t=>`<p style="margin:4px 0"><a href="#${t}">${esc(tabNaam(t))}</a> <span class="note">· ${open.filter(x=>x.tab===t).length} punten</span></p>`).join(''):'<p class="note">Alles is beoordeeld.</p>'}</div>
   </div>`;
  host.querySelectorAll('[data-a]').forEach(el=>el.onchange=()=>{const id=el.dataset.id;D.act[id]=Object.assign(D.act[id]||{},{[el.dataset.a]:el.dataset.a==='eig'?el.value:+el.value});save();road()});
  host.querySelectorAll('.rmDel').forEach(b=>b.onclick=()=>{D.extra=D.extra.filter(x=>x.id!==b.dataset.id);delete D.act[b.dataset.id];save();road()});
  $('#rmAdd').onclick=()=>{const t=$('#rmNT').value.trim();if(!t)return;const id='x'+Date.now().toString(36);D.extra.push({id,tekst:t,laag:+$('#rmNL').value,fase:+$('#rmNF').value});D.act[id]={fase:+$('#rmNF').value};save();road()};
  $('#rmCsv').onclick=()=>download(csvRoad(),C.naam+'-verbeterroadmap.csv');
  $('#rmCsv2').onclick=()=>download(csvVast(),C.naam+'-vastleggingen.csv');
  $('#rmCopy').onclick=()=>{const t=rowsRoad().map(r=>r.join('\t')).join('\n');(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(()=>msg('Gekopieerd. Plak in Excel.'),()=>msg('Kopiëren lukt hier niet; gebruik de export.'))};
  $('#rmNieuw').onclick=()=>{if(!host.dataset.sure){host.dataset.sure=1;msg('Klik nogmaals om alle vastleggingen en acties te wissen.');setTimeout(()=>delete host.dataset.sure,4000);return}delete host.dataset.sure;D=fresh(false);save();all();msg('Alles is leeg. Beoordeel per tabblad wat op orde is.')};
  const dm=$('#rmDemo');if(dm)dm.onclick=()=>{D=fresh(true);save();all()};
}
function card(a){const lagL=C.lagen[a.laag-1]||'';return `<div class="rmAct ${a.s} ${a.stat===2?'done':''}"><div class="rmT">${esc(a.tekst)}</div>
  <div class="row" style="gap:6px;margin-top:4px;flex-wrap:wrap"><span class="pill p-cool">Laag ${a.laag}</span>${a.eigen?'<span class="pill p-mut">eigen actie</span>':`<span class="pill ${a.s==='niet'?'p-bad':'p-warn'}">${LAB[a.s]}</span><a class="note" href="#${a.tab}">${esc(tabNaam(a.tab))}</a>`}</div>
  ${a.o?`<p class="note" style="margin:6px 0 0">${esc(a.o)}</p>`:''}
  <div class="rmCtl"><select data-a="fase" data-id="${a.id}" aria-label="Fase">${C.fases.map((f,i)=>`<option value="${i}"${i===a.fase?' selected':''}>${esc(f[1])}</option>`).join('')}</select>
   <select data-a="prio" data-id="${a.id}" aria-label="Prioriteit">${PRIO.map((p,i)=>`<option value="${i}"${i===a.prio?' selected':''}>Prio ${p.toLowerCase()}</option>`).join('')}</select>
   <select data-a="stat" data-id="${a.id}" aria-label="Status">${STAT.map((p,i)=>`<option value="${i}"${i===a.stat?' selected':''}>${p}</option>`).join('')}</select>
   <input data-a="eig" data-id="${a.id}" value="${esc(a.eig)}" placeholder="Eigenaar" aria-label="Eigenaar"></div>
  ${a.eigen?`<button class="btn rmDel" data-id="${a.id}" style="margin-top:6px">Verwijderen</button>`:''}</div>`}
function rowsRoad(){return [['Fase','Periode','Laag','Actie','Bevinding','Toelichting','Eigenaar','Prioriteit','Status','Tabblad']].concat(acties().sort((a,b)=>a.fase-b.fase||a.laag-b.laag||a.prio-b.prio).map(a=>[C.fases[a.fase][0],C.fases[a.fase][1],a.laag+' · '+(C.lagen[a.laag-1]||''),a.tekst,a.eigen?'eigen actie':LAB[a.s],a.o,a.eig,PRIO[a.prio],STAT[a.stat],a.tab?tabNaam(a.tab):'']))}
function rowsVast(){return [['Tabblad','Laag','Onderwerp','Doelsituatie','Beoordeling','Toelichting','Actie bij afwijking']].concat(items().map(it=>[tabNaam(it.tab),it.laag,it.groep,it.norm,LAB[st(it.id)]||'Nog niet beoordeeld',(D.st[it.id]||{}).o||'',it.actie]))}
const toCsv=rows=>'﻿'+rows.map(r=>r.map(v=>{v=String(v==null?'':v);return /[;"\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v}).join(';')).join('\r\n');
const csvRoad=()=>toCsv(rowsRoad()),csvVast=()=>toCsv(rowsVast());
let DL=null;try{if(window.claude&&window.claude.use)window.claude.use('downloads').then(d=>{DL=d}).catch(()=>{})}catch(e){}
async function download(txt,name){
  if(DL){try{await DL.save({filename:name,data:txt});msg('Bestand '+name+' opgeslagen.')}catch(e){msg(e&&e.code==='declined'?'Opslaan geannuleerd.':'Opslaan lukt hier niet; gebruik Kopieer roadmap.')}return}
  if(window.claude){msg('Opslaan lukt in deze weergave niet; gebruik Kopieer roadmap en plak in Excel.');return}
  try{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([txt],{type:'text/csv;charset=utf-8'}));a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},500);msg('Bestand '+name+' gedownload.')}catch(e){msg('Downloaden lukt hier niet; gebruik Kopieer roadmap.')}}
function msg(t){const m=$('#rmMsg');if(m)m.textContent=t}
function all(){[...new Set(items().map(i=>i.tab))].forEach(panel);road()}
window.RM={refresh(){const k=C.key();if(k!==K){K=k;D=LS.get(K,null)||fresh(true)}document.querySelectorAll('.rmPanel').forEach(c=>c.remove());all()}};
all();
})();
