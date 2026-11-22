import copy
import datetime
import json
from pathlib import Path
import uygulamalar

D=Path(__file__).parent
load=lambda n:json.loads((D/n).read_text())
p=load('package-sdd-106-union-draft.json'); r=load('sdd-106-union-review-draft.json')
before=copy.deepcopy(p); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
sources=[]
for filename in ('kirikkale-preselection-source-records-draft.json','kirikkale-scope-source-records-draft.json'):
 sources.extend(load(filename)['entries'])
for e in sources:
 if e not in p['entries']:p['entries'].append(e)
summary='0303-epm-uyelik-secme-secilme-summary'; quote='0303-epm-uyelik-secme-secilme-quote'; cp='0303-epm-uyelik-secme-secilme-p'
key='0404-kirikkale-onsecim'; event=key+'-event'; relation=key+'-relation'; finding=key+'-explanation'; statement=key+'-statement'
scope_statement='practice-80e95aa6bab6692e2ebe42140046c60610656b8a1172ef5a55d94491f5e2eec7'
scope_event='practice-37e1bd3479872aa927f96519c1e8d1a1bee951eb055ced90f53e59b0deac5fd3'
news=['0404-kirikkale-haberler-p','0404-kirikkale-haber-p','0404-kirikkale-scope-city-p','0404-kirikkale-scope-center-p']
entries=[{'kind':'finding','values':{'id':finding,'party_id':'yeni-parti','heading':'Söylem ve uygulama','pair_id':finding,
 'text':'Tüzük, üyelerin tüzük ve yönetmelikler çerçevesinde seçme ve seçilme hakkını düzenler. Haberler ve Kırıkkale Haber, Kırıkkale il başkanlığı önseçiminde üyelerin oy kullandığını bildirir. Yeni Ankara, 928–221 oylarını il geneline, 467–171 oylarını merkez ilçeye atfeder. Resmî tutanak ve il kongresi sonucu görülmedi.',
 'provenance':'summary','epistemic_type':'claim'}},
 {'kind':'review','values':{'id':'review-'+finding,'kind':'finding','subject_id':finding,'reviewer_kind':'agent','reviewed_at':now,'result':'reviewed',
 'reason':'Kurucu tüzük ve üç önseçim haberi okundu; Yeni Ankara il geneli ile merkez ilçeyi ayırıyor, tutanak görülmedi.'}}]
for fid,pids in ((summary,[cp]),(quote,[cp]),(finding,[cp]+news)):
 for pid in pids:
  if fid==finding:entries.append({'kind':'finding_evidence','values':{'finding_id':fid,'passage_id':pid,'role':'support'}})
  entries.append({'kind':'verification','values':{'finding_id':fid,'passage_id':pid,'checked_at':now,'result':'confirmed',
   'reason':'Üyelik hükmü ve Kırıkkale önseçim haberinin ilgili pasajı ayrı incelendi.'}})
for e in entries:
 if e not in p['entries']:p['entries'].append(e)
records={k:[] for k in p['practice_records']}
records['practice_statement'].append({'id':statement,'party_id':'yeni-parti','topic_id':'uyelik-secme-secilme','taxonomy_version':4,
 'summary_finding_id':summary,'quote_finding_id':quote,'statement_at':None,'date_precision':'unknown','version_id':'epm-charter-v1',
 'period_basis':'22 Temmuz tarihli kurucu tüzük ve 24 Temmuz kuruluş ayrı; hükmün kesin kabul anı belirlenmedi.',
 'uncertainty_reason':'Genel üyelik hükmü her somut seçimdeki uygulamayı tek başına kanıtlamaz.',
 'comparison_row_id':'04-03-v3-0303-epm-uyelik-secme-secilme-row'})
records['practice_scope_v2'].append({'id':scope_statement,'party_id':'yeni-parti','topic_id':'uyelik-secme-secilme','taxonomy_version':4,
 'period_start':'2026-07-24','cutoff_at':'2026-11-10T14:38:46.154751+00:00','research_kind':'statement',
 'boundary_reason':'Kırıkkale önseçimi kaynak okuması; diğer üyelik uygulamaları ve tutanaklar açık.'})
records['practice_event'].append({'id':event,'common_event_key':'yeni-parti-kirikkale-il-baskani-onsecim-2026-10-18',
 'event_at':'2026-10-18','date_precision':'day','date_unknown_reason':None,'scope_context':'Kırıkkale il başkanlığı üyeler önseçimi',
 'title':'Kırıkkale il başkanlığı önseçimi','occurrence_basis':'18 ve 19 Ekim tarihli haberlerde üye önseçimi aktarılır.'})
for pid in news:
 records['practice_event_evidence'].append({'event_id':event,'passage_id':pid,'stage':'action',
  'supported_point':'Kırıkkale üye önseçimindeki il geneli veya merkez ilçe oylarının ilgili kaynakta aktarılması.',
  'concrete_basis':'Yerel basın ilgili adayların oylarını bildiriyor; Yeni Ankara il ile merkez kapsamını ayırıyor.',
  'limitation':'Asıl seçim tutanağı görülmedi; sonuçlar haberlere atıflıdır, il kongresi ayrıdır.','epistemic_type':'claim'})
 records['practice_evidence_assessment'].append({'event_id':event,'passage_id':pid,'stage':'action','basis_kind':'document'})
records['practice_relation'].append({'id':relation,'statement_id':statement,'event_id':event,'party_id':'yeni-parti',
 'topic_id':'uyelik-secme-secilme','scope_id':scope_event,'comparability_reason':'Her ikisi parti üyelerinin oy kullanmasıyla ilgilidir.',
 'target_finding_id':summary,'result_finding_id':None,'explanation_finding_id':finding,
 'temporal_context':'Kurucu tüzükten sonra 18 Ekim üye önseçimi.','authority_context':'Tüzük üyelik hakkını düzenler; basın üyelerin önseçimini bildirir.',
 'uncertainty_reason':'Seçim tutanağı görülmedi; haberlerde il geneli ve merkez kapsamı Yeni Ankara tarafından ayrılıyor, il kongresi ayrıdır.'})
records['practice_candidate'].append({'id':key+'-candidate','scope_id':scope_event,'event_id':event,'relation_id':relation,'state':'eligible',
 'reason':'Parti üyelerinin önseçimde oy kullanması üyelik hakkı hükmüyle ilgilidir.','passage_ids':json.dumps(news)})
for scope,version,url,section in [(scope_statement,'epm-charter-v1','https://yenipartiyiz.biz/parti-tuzugu','Üyelerin seçme ve seçilme hakkı')]+[
 (scope_event,e['values']['id'],e['values']['original_url'],'Kırıkkale önseçimi haberi') for e in sources if e['kind']=='document_version']:
 aid=key+'-reading-'+str(len(records['practice_attempt_v2'])+1); reason=section+' özgün kaynakta incelendi.'
 records['practice_scope_source'].append({'scope_id':scope,'version_id':version,'inspected_sections':json.dumps([section],ensure_ascii=False),'inspected_at':now})
 records['practice_lead'].append({'id':'lead-'+aid,'scope_id':scope,'url':url,'relevance_reason':reason,'state':'examined','attempt_ids':json.dumps([aid])})
 records['practice_attempt_v2'].append({'id':aid,'scope_id':scope,'attempted_at':now,'query':url,'url':url,'result':'examined','reason':reason,'source_version_id':version})
for k,rows in records.items():
 for x in rows:
  if x not in p['practice_records'][k]:p['practice_records'][k].append(x)
assert p['entries'][:len(before['entries'])]==before['entries']
for k,rows in before['practice_records'].items():assert p['practice_records'][k][:len(rows)]==rows
data=json.loads(Path('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json').read_text())
for e in p['entries']:
 arr=data.setdefault(e['kind'],[])
 if e['values'] not in arr:arr.append(e['values'])
for k,rows in p['practice_records'].items():
 arr=data.setdefault(k,[])
 for x in rows:
  if x not in arr:arr.append(x)
targets=uygulamalar.practice_review_targets(data,records); passages={x['id']:x for x in data['passage']}; fresh=[]
for (kind,identity),(pids,_) in targets.items():
 ids=sorted(pids); fresh.append({'subject_kind':kind,'subject_id':identity,'reviewer_kind':'agent','reviewed_at':now,
  'source_version_ids':json.dumps(sorted({passages[x]['version_id'] for x in ids}),ensure_ascii=False),
  'passage_ids':json.dumps(ids,ensure_ascii=False),'inspected_sections':json.dumps(['Kırıkkale önseçim haberleri ve üyelik hükmü: '+kind],ensure_ascii=False),
  'supported_claim':identity+' için üyelik hükmü veya önseçim haberinde ilgili pasajlar incelendi.',
  'limitations':'Asıl tutanak ve il kongresi sonucu görülmedi; il geneli ile merkez kapsamı habere atfedilir.',
  'result':'reviewed','reason':identity+' hedefi için tüzük ve Kırıkkale kaynak pasajları ayrı okundu.'})
uygulamalar.validate_practice_source_review(data,fresh,require_coverage=False,party_id='yeni-parti')
r['practice_source_review'].extend(fresh); r['source_review_refs'].extend({'subject_kind':x['subject_kind'],'subject_id':x['subject_id']} for x in fresh)
uygulamalar.validate_practice_source_review(data,r['practice_source_review'],party_id='yeni-parti')
for n,obj in [('package-kirikkale-107-union-draft.json',p),('kirikkale-107-union-review-draft.json',r)]:
 (D/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('SEMANTIC_PASS',len(r['practice_source_review']),len(p['practice_records']['practice_event']),len(p['practice_records']['practice_relation']))
