"""Genereert het huisstijlblok (CSS-variabelen + fonts) uit een brand-JSON en zet het tussen de markers in een artefact.
Gebruik: python3 theme.py brand.json target.html [cf|scan]"""
import json,sys,re,urllib.parse
# Standaard B.Enable-pictogram: ook klantvarianten blijven een B.Enable-product.
DEFAULT_ICON='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#193657"/><text x="27" y="48" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-weight="700" font-size="46" fill="#fff">B</text><circle cx="49" cy="43" r="5.5" fill="#F0773A"/></svg>'
def iconlink(B):
    svg=(B.get('brand',{}).get('pictogram') or {}).get('svg') or DEFAULT_ICON
    return '<link rel="icon" type="image/svg+xml" data-brand="1" href="data:image/svg+xml,'+urllib.parse.quote(svg)+'">'
MAP={
 'cf':{'bg':'background','panel':'surface','ink':'text','muted':'text_muted','line':'border','accent':'accent','accent-soft':'accent_soft','cool':'primary','cool-soft':'primary_soft','primary':'primary',
       'good':'S.good','good-soft':'S.good_soft','warn':'S.warning','warn-soft':'S.warning_soft','bad':'S.critical','bad-soft':'S.critical_soft'},
 'scan':{'paper':'background','surface':'surface','ink':'text','muted':'text_muted','line':'border','cold':'primary','hot':'accent','mid':'C.5','soft':'primary_soft',
       'good':'S.good','warn':'S.warning','bad':'S.critical'}
}
def val(B,mode,ref):
    if ref.startswith('S.'):return B['colors']['status'][mode][ref[2:]]
    if ref.startswith('C.'):return B['colors']['chart']['categorical'][int(ref[2:])]
    return B['colors'][mode][ref]
def block(B,kind):
    t=B['typography'];m=MAP[kind]
    fam=lambda k:f"\"{t[k]['family']}\", {t[k]['fallback']}"
    fonts={'cf':f"--display:{fam('display')}; --body:{fam('body')}; --mono:{fam('mono')};",'scan':f"--display:{fam('display')}; --body:{fam('body')}; --mono:{fam('mono')};"}[kind]
    v=lambda mode:' '.join(f"--{k}:{val(B,mode,r)};" for k,r in m.items())
    return ("/* BRAND:START · gegenereerd uit "+B['brand']['name']+" huisstijl v"+B['version']+" · niet met de hand wijzigen */\n"
      f":root{{\n  {v('light')}\n  {fonts}\n  --radius:{B['shape']['radius_px']['default']}px;\n  color-scheme:light;\n}}\n"
      f"@media (prefers-color-scheme: dark){{\n  :root:not([data-theme=\"light\"]){{\n    {v('dark')}\n    color-scheme:dark;\n  }}\n}}\n"
      f":root[data-theme=\"dark\"]{{\n  {v('dark')}\n  color-scheme:dark;\n}}\n/* BRAND:END */")
def fontlink(B):
    t=B['typography'];fams=[]
    for k in ('display','body','mono'):
        f=t[k]['family'];w=';'.join(str(x) for x in sorted(t[k]['weights']))
        fams.append('family='+f.replace(' ','+')+':wght@'+w)
    return '<link href="https://fonts.googleapis.com/css2?'+'&'.join(fams)+'&display=swap" rel="stylesheet">'
if __name__=='__main__':
    B=json.load(open(sys.argv[1]));h=open(sys.argv[2]).read();kind=sys.argv[3]
    h=re.sub(r'/\* BRAND:START.*?/\* BRAND:END \*/',lambda _:block(B,kind),h,flags=re.S)
    h=re.sub(r'<link href="https://fonts.googleapis.com/css2\?[^"]*" rel="stylesheet">',lambda _:fontlink(B),h)
    h=re.sub(r'<link rel="icon"[^>]*data-brand="1"[^>]*>\n?','',h)
    h=h.replace('<head>','<head>\n'+iconlink(B),1)
    open(sys.argv[2],'w').write(h);print('ok',kind)
