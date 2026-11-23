"""Ortak 10/4961 sicilini ve DEM grup katkısını ayrı kaynak kimlikleriyle hazırlar."""
import json
from pathlib import Path
from arsiv import html_source_text
c = Path(__file__).resolve().parent
root = c.parents[3]
source = json.loads((c.parent/'04-08-checks/nov03-4961-source-records.json').read_text())
old, new = '0408-nov03-4961-', '0406-nov03-4961-'
keep_passages = {'floor-call','floor-vote','register-number','register-date','register-status','signed-number'}
entries=[]
for entry in source['entries']:
    v=entry['values']; ident=v.get('id',v.get('version_id',v.get('passage_id','')))
    suffix=ident.removeprefix(old)
    if not ident.startswith(old): continue
    if entry['kind']=='passage' and suffix not in keep_passages: continue
    if entry['kind']=='manual_passage' or any(suffix==x or suffix.startswith(x+'-') for x in ('tursg','deadline')): continue
    item=json.loads(json.dumps(entry,ensure_ascii=False).replace(old,new).replace('0408-nov03-genelgorusme-floor-v1','0406-nov03-genelgorusme-floor-v1'))
    if item['kind']=='document': item['values']['party_id']='dem'
    entries.append(item)
text=html_source_text((root/'data/practices/sources/dem/objects/43f76c014493808d974aed00ce23152667132f1862f387bde6f788524a17357b/original.html.bin').read_bytes())
for suffix,exact,section in (
 ('floor-dem-role','DEM PARTİ GRUBU ADINA ZÜLKÜF UÇAR (Van)','Zülküf Uçar’ın DEM Grup sıfatı'),
 ('floor-dem-critique','Bakanın bugünkü açıklamaları da adaleti sağlamaya değil, suçluyu korumaya odaklanmış vaziyette.','Zülküf Uçar’ın bakan açıklamasına atıflı eleştirisi'),
):
 assert exact in text
 entries.append({'kind':'passage','values':{'id':new+suffix,'version_id':'0406-nov03-genelgorusme-floor-v1','exact':exact,'prefix':None,'suffix':None,'article':None,'section':section,'pdf_page_index':None,'printed_page':None}})
(c/'nov03-4961-dem-source-records.json').write_text(json.dumps({'party_id':'dem','entries':entries},ensure_ascii=False,indent=2)+'\n')
print('NOV03_4961_DEM_SOURCES_OK',len(entries))
