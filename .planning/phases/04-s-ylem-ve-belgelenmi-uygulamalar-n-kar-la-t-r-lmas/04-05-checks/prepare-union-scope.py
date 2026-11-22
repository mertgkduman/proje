import json,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); inv=json.loads(Path('data/practices/04-inventory.json').read_text()); now=datetime.now(timezone.utc).isoformat()
program=Path('data/objects/6aa8a0087e2426e808defbc8e427281f08862b1206fdad2ae847fd294854c7e0/original.html.bin'); assert 'sendikal örgütlenme ve toplu sözleşme hakları' in html_source_text(program.read_bytes())
pdf=Path('data/practices/sources/tip/objects/c679a7e811b5815bb95508e5dd11952768209064d89f8883b30540c93fb2f58c/original.pdf'); assert 'Sigortasız çalıştırılan işçiler' in pdf_page_text(pdf,6)
outcome=Path('data/practices/sources/tip/objects/ba2883e38fed0a4a930fb66c3d51b7e72248196ebffb8df52e6688fef57a75ed/original.pdf'); assert '4115 2/4390' in pdf_page_text(outcome,232)
items={'statement':[('0203-tip-program-v1','https://tip.org.tr/parti-programi','İşçi sınıfı mücadelesi bölümünde sendikal örgütlenme ve toplu sözleşme hakları okundu.')], 'event':[('0405-tip-sendika-274390-pdf-v1','https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y5/T2/WebOnergeMetni/9c60b46f-6665-479a-aa0f-9025c059f4e9.pdf','İmzalı 2/4390 teklifinin 1. maddesi ve gerekçesi okundu.'),('0405-tip-sendika-hukumsuz-v1','https://www5.tbmm.gov.tr/tutanaklar/TUTANAK/TBMM/d28/c001/tbmm28001001.pdf','2 Haziran 2023 tutanak basılı 200. sayfada 2/4390 hükümsüz listesi okundu.')]}
r={'practice_scope_v2':[],'practice_attempt_v2':[],'practice_scope_source':[],'practice_lead':[]}
for kind,sources in items.items():
 cell=next(c for c in inv['cells'] if c['party_id']=='tip' and c['topic_id']=='sendika-grev' and c['research_kind']==kind); scope=cell['cell_id']
 r['practice_scope_v2'].append(dict(id=scope,party_id='tip',topic_id='sendika-grev',taxonomy_version=cell['taxonomy_version'],period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=kind,boundary_reason='Seçili kaynaklar incelendi; bütün dönem ve diğer ilgili uçlar açık, kapanış yapılmadı.'))
 for n,(version,url,reason) in enumerate(sources,1):
  aid=f'0405-sendika-{kind}-okuma-{n}';r['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=reason,source_version_id=version));r['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps([reason],ensure_ascii=False),inspected_at=now));r['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=reason,state='examined',attempt_ids=json.dumps([aid])))
(p/'union-scope-delta.json').write_text(json.dumps(dict(status='draft_unvalidated',practice_records=r),ensure_ascii=False,indent=2)+'\n'); print('DRAFT ONLY',sum(map(len,r.values())))
