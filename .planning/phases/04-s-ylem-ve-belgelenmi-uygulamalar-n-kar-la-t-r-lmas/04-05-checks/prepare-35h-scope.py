import json,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,'src')
from arsiv import html_source_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); inv=json.loads(Path('data/practices/04-inventory.json').read_text());cap=json.loads((p/'institution-nisan-capture.json').read_text()); raw=(Path('data/practices/sources/tip/objects')/cap['sha256']/'original.html.bin').read_bytes(); text=html_source_text(raw)
assert 'Çalışma Süresi Haftalık 35 Saate Düşürülsün' in text and '2024-04-09T11:16:00+03:00' in text
now=datetime.now(timezone.utc).isoformat(); cell=next(c for c in inv['cells'] if c['party_id']=='tip' and c['topic_id']=='calisma-sureleri' and c['research_kind']=='statement'); sid=cell['cell_id']; aid='0405-pm35-statement-okuma'; url=cap['url'];version='0405-tip-pm-nisan-v1'; reason='9 Nisan 2024 tarihli PM değerlendirmesinin 1 Mayıs için 35 saat hedefi ve tarih künyesi özgün HTML içinde okundu.'
r={'practice_scope_v2':[dict(id=sid,party_id='tip',topic_id='calisma-sureleri',taxonomy_version=cell['taxonomy_version'],period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind='statement',boundary_reason='Tarihli PM açıklaması okundu; tüm dönem ve söylem uçları açık, kapsam kapanmadı.')], 'practice_attempt_v2':[dict(id=aid,scope_id=sid,attempted_at=now,query=url,url=url,result='examined',reason=reason,source_version_id=version)], 'practice_scope_source':[dict(scope_id=sid,version_id=version,inspected_sections=json.dumps(['Öncelikli somut hedeflerimiz ve takvimimiz; sayfa yayın tarihi'],ensure_ascii=False),inspected_at=now)], 'practice_lead':[dict(id='lead-'+aid,scope_id=sid,url=url,relevance_reason=reason,state='examined',attempt_ids=json.dumps([aid]))]}
(p/'policy-35h-scope-delta.json').write_text(json.dumps(dict(status='draft_unvalidated',practice_records=r),ensure_ascii=False,indent=2)+'\n');print('DRAFT ONLY',sum(map(len,r.values())))
