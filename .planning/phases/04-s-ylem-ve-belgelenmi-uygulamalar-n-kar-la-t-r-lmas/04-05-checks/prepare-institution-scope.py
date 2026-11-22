import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,'src')
from arsiv import html_source_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); inv=json.loads(Path('data/practices/04-inventory.json').read_text()); now=datetime.now(timezone.utc).isoformat()
charter=Path('data/objects/e86237895eda1cec2e66ac388ce7b9cd7096e86dfc9f1cccdd93ab1a298e4a60/original.pdf');assert hashlib.sha256(charter.read_bytes()).hexdigest()=='e86237895eda1cec2e66ac388ce7b9cd7096e86dfc9f1cccdd93ab1a298e4a60'
checks=[('institution-istifa-capture.json','Bu sebeplerle Türkiye İşçi Partisi'),('institution-gazeteci-capture.json','Parti bizi kesinlikle ihraç etmedi')]
for name,fragment in checks:
 cap=json.loads((p/name).read_text()); text=html_source_text((Path('data/practices/sources/tip/objects')/cap['sha256']/'original.html.bin').read_bytes());assert fragment in text
items={'statement':[('0203-tip-charter2022-v1','https://tip.org.tr/wp-content/uploads/2022/06/Tu%CC%88rkiye-I%CC%87s%CC%A7c%CC%A7i-Partisi-Tu%CC%88zu%CC%88k-2022.pdf','Tüzük PDF basılı 18–19. sayfalarda organlarda tartışma, karar uygulaması ve kamusal açıklama sınırı görsel okundu.')], 'event':[('0405-tip-istifa-cumhuriyet-v1','https://www.cumhuriyet.com.tr/siyaset/tipin-uc-il-yonetimi-istifa-etti-statukocu-bir-anlayisla-yol-2229384','Açıklama, eleştiriler ve partinin üyelik ve görev durumuna karşı cevabı okundu.'),('0405-tip-gazeteci-yanit-v1','https://cagdassamsun.com/kose-yazilari/umit_ozcelik_tipnin_seni_26_haziranda_ihrac_etmedigini_ispatla_-238','Gazetecinin sonraki yazısı ve kişinin ihraç edilmediği yönündeki cevabı okundu.')]}
r={'practice_scope_v2':[],'practice_attempt_v2':[],'practice_scope_source':[],'practice_lead':[]}
for kind,sources in items.items():
 cell=next(c for c in inv['cells'] if c['party_id']=='tip' and c['topic_id']=='ic-tartisma-elestiri' and c['research_kind']==kind);sid=cell['cell_id'];r['practice_scope_v2'].append(dict(id=sid,party_id='tip',topic_id=cell['topic_id'],taxonomy_version=cell['taxonomy_version'],period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=kind,boundary_reason='Seçili tüzük ve çekişmeli olay kaynakları okundu; bütün dönem ve kalan ilgili uçlar araştırılacak.'))
 for n,(version,url,reason) in enumerate(sources,1):
  aid=f'0405-tartisma-{kind}-okuma-{n}';r['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=now,query=url,url=url,result='examined',reason=reason,source_version_id=version));r['practice_scope_source'].append(dict(scope_id=sid,version_id=version,inspected_sections=json.dumps([reason],ensure_ascii=False),inspected_at=now));r['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,relevance_reason=reason,state='examined',attempt_ids=json.dumps([aid])))
(p/'institution-scope-delta.json').write_text(json.dumps(dict(status='draft_unvalidated',practice_records=r),ensure_ascii=False,indent=2)+'\n');print('DRAFT ONLY',sum(map(len,r.values())))
