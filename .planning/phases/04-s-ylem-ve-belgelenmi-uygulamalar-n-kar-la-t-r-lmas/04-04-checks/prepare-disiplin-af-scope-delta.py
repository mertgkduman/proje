import datetime
import json
from pathlib import Path
import uygulamalar

D=Path(__file__).parent
research=json.loads((D/'disiplin-af-scope-341-research.json').read_text())
base=json.loads(Path('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json').read_text())
live=json.loads(Path('data/practices/04-yeni-parti.json').read_text())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
scope=research['scope_id']; pids=research['charter']['passage_ids']
prefixes=['0303-epm-third-disiplin-af','0303-epm-detail13-disiplin-af-bag-slama-basvurusu-',
          '0303-epm-detail14-disiplin-af-bag-slama-karar-nda-gizli-oy-',
          '0303-epm-detail15-disiplin-af-bag-slama-isteminin-sunulmas-']
keys=['yetki','basvuru','gizli-oy','sunum']
records={k:[] for k in live['practice_records']}; entries=[]
records['practice_scope_v2'].append({'id':scope,'party_id':'yeni-parti','topic_id':'disiplin-af','taxonomy_version':4,
 'period_start':'2026-07-24','cutoff_at':'2026-11-10T14:38:46.154751+00:00','research_kind':'statement',
 'boundary_reason':'Kurucu tüzük madde 52 bağışlama söylemi; kesim içi sonraki değişiklik kararı ve diğer söylemler açık.'})
for key,pre,pid in zip(keys,prefixes,pids):
 summary=pre+'-summary' if not pre.endswith('-') else pre+'-summary'
 quote=pre+'-quote' if not pre.endswith('-') else pre+'-quote'
 row='04-03-v3-'+pre+'-row' if not pre.endswith('-') else '04-03-v3-'+pre+'-row'
 for identity in (summary,quote):
  assert any(x['id']==identity for x in base['finding'])
  assert any(x['finding_id']==identity and x['passage_id']==pid for x in base['finding_evidence'])
  entries.append({'kind':'verification','values':{'finding_id':identity,'passage_id':pid,'checked_at':now,
   'result':'confirmed','reason':'22 Temmuz kurucu tüzük madde 52 ve bu fıkranın exact özgün pasajı yeniden okundu.'}})
 assert any(x['id']==row for x in base['comparison_row'])
 records['practice_statement'].append({'id':'0404-disiplin-af-'+key+'-statement','party_id':'yeni-parti',
  'topic_id':'disiplin-af','taxonomy_version':4,'summary_finding_id':summary,'quote_finding_id':quote,
  'statement_at':None,'date_precision':'unknown','version_id':'epm-charter-v1',
  'period_basis':'22 Temmuz tüzük tarihi ile 24 Temmuz parti kuruluşu ayrıdır; hükmün kesin kabul anı bilinmiyor.',
  'uncertainty_reason':'Kesim içi 9 Kasım değişiklik kararının tam metni ve ara sürüm henüz görülmedi.',
  'comparison_row_id':row})
url=research['charter']['url']; aid='0404-disiplin-af-charter-reading'
records['practice_scope_source'].append({'scope_id':scope,'version_id':'epm-charter-v1',
 'inspected_sections':json.dumps(['Madde 52: dört bağışlama fıkrası'],ensure_ascii=False),'inspected_at':now})
records['practice_lead'].append({'id':'lead-'+aid,'scope_id':scope,'url':url,
 'relevance_reason':'Kurucu tüzüğün bağışlama maddesinin dört fıkrası özgün bayttan okundu.',
 'state':'examined','attempt_ids':json.dumps([aid])})
records['practice_attempt_v2'].append({'id':aid,'scope_id':scope,'attempted_at':now,'query':url,'url':url,
 'result':'examined','reason':'22 Temmuz tüzüğünün madde 52 dört fıkrası ve Faz 3 pasajları incelendi.','source_version_id':'epm-charter-v1'})
records['practice_lead'].append({'id':'lead-0404-disiplin-af-9kasim-decision','scope_id':scope,
 'url':'https://api.yeni-parti.org.tr/api/haberler/295',
 'relevance_reason':'9 Kasım kurul değişikliklerinin tamamına ve madde 52 durumuna ait karar aslı ayrıca araştırılacak.',
 'state':'pending','attempt_ids':'[]'})
for e in live['entries']+entries:
 arr=base.setdefault(e['kind'],[])
 if e['values'] not in arr:arr.append(e['values'])
for k,rows in live['practice_records'].items():
 arr=base.setdefault(k,[])
 for x in rows:
  if x not in arr:arr.append(x)
for k,rows in records.items():
 arr=base.setdefault(k,[])
 for x in rows:
  if x not in arr:arr.append(x)
targets=uygulamalar.practice_review_targets(base,records); passages={x['id']:x for x in base['passage']}; reviews=[]
for (kind,identity),(references,_) in targets.items():
 ids=sorted(references)
 reviews.append({'subject_kind':kind,'subject_id':identity,'reviewer_kind':'agent','reviewed_at':now,
  'source_version_ids':json.dumps(sorted({passages[x]['version_id'] for x in ids}),ensure_ascii=False),
  'passage_ids':json.dumps(ids,ensure_ascii=False),'inspected_sections':json.dumps(['Madde 52 bağışlama: '+kind],ensure_ascii=False),
  'supported_claim':identity+' için kurucu tüzüğün ilgili bağışlama hükmü ve Faz 3 bulgusu karşılaştırıldı.',
  'limitations':'9 Kasım değişiklik kararının tamamı ve kesim içi ara sürüm henüz görülmedi.',
  'result':'reviewed','reason':identity+' hedefinin özgün tüzük pasajı ve eşleşen bulgusu okundu.'})
uygulamalar.validate_practice_source_review(base,reviews,require_coverage=False,party_id='yeni-parti')
result={'status':'draft_open','party_id':'yeni-parti','scope_id':scope,'additional_entries':entries,'practice_records':records,
 'practice_source_review':reviews,'source_review_refs':[{'subject_kind':x['subject_kind'],'subject_id':x['subject_id']} for x in reviews],
 'note':'Dört kurucu tüzük bulgusu; 9 Kasım karar ve ara sürüm açık, closure yok. Gerçek corpus ve dış aramalar ayrı research makbuzunda.'}
(D/'disiplin-af-scope-341-delta.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('SEMANTIC_PASS',len(reviews),'statements',len(records['practice_statement']))
