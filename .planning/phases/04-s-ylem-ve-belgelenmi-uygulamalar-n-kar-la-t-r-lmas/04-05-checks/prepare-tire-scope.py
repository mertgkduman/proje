import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,'src')
from arsiv import html_source_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); inv=json.loads(Path('data/practices/04-inventory.json').read_text()); now=datetime.now(timezone.utc).isoformat()
charter=Path('data/objects/e86237895eda1cec2e66ac388ce7b9cd7096e86dfc9f1cccdd93ab1a298e4a60/original.pdf');assert hashlib.sha256(charter.read_bytes()).hexdigest()=='e86237895eda1cec2e66ac388ce7b9cd7096e86dfc9f1cccdd93ab1a298e4a60'
items={'statement':[('0203-tip-charter2022-v1','https://tip.org.tr/wp-content/uploads/2022/06/Tu%CC%88rkiye-I%CC%87s%CC%A7c%CC%A7i-Partisi-Tu%CC%88zu%CC%88k-2022.pdf','Tüzük PDF basılı 18. sayfada organ kararına üst organa itiraz hükmü görsel okundu.')], 'event':[]}
for name,version,fragment,reason in [('sevk','0405-tip-tire-sevk-v1','nihai karar alınıncaya kadar','İlçe açıklamasında disipline sevk ve geçici tedbir okundu.'),('yanit','0405-tip-tire-yanit-v1','kendisinin istifa ettiğini söylese de','İlçe açıklamasında istifa ve sevk zamanlamasına ilişkin karşı beyan okundu.'),('ozturk','0405-tip-tire-ozturk-v1','Ve istifa ettim.','Kişinin ayrı istifa beyanı ve siyasi gerekçesi okundu.')]:
 cap=json.loads((p/('tire-'+name+'-capture.json')).read_text()); raw=(Path('data/practices/sources/tip/objects')/cap['sha256']/'original.html.bin').read_bytes();assert fragment in html_source_text(raw);items['event'].append((version,cap['url'],reason))
r={'practice_scope_v2':[],'practice_attempt_v2':[],'practice_scope_source':[],'practice_lead':[]}
for kind,sources in items.items():
 cell=next(c for c in inv['cells'] if c['party_id']=='tip' and c['topic_id']=='parti-ici-itiraz' and c['research_kind']==kind);sid=cell['cell_id'];r['practice_scope_v2'].append(dict(id=sid,party_id='tip',topic_id=cell['topic_id'],taxonomy_version=cell['taxonomy_version'],period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=kind,boundary_reason='Tüzük hükmü ve Tire açıklamaları okundu; somut itiraz, nihai karar ve bütün dönem uçları araştırılacak.'))
 for n,(version,url,reason) in enumerate(sources,1):
  aid=f'0405-itiraz-{kind}-okuma-{n}';r['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=now,query=url,url=url,result='examined',reason=reason,source_version_id=version));r['practice_scope_source'].append(dict(scope_id=sid,version_id=version,inspected_sections=json.dumps([reason],ensure_ascii=False),inspected_at=now));r['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,relevance_reason=reason,state='examined',attempt_ids=json.dumps([aid])))
(p/'tire-scope-delta.json').write_text(json.dumps(dict(status='draft_unvalidated',practice_records=r),ensure_ascii=False,indent=2)+'\n');print('DRAFT ONLY',sum(map(len,r.values())))
