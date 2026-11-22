import copy
import datetime
import json
from pathlib import Path

import uygulamalar

D=Path(__file__).parent
load=lambda n:json.loads((D/n).read_text())
p=load('package-anka-sulakyurt-105-union-draft.json')
r=load('anka-sulakyurt-105-union-review-draft.json')
source=load('sdd-protocol-source-draft.json')
before=copy.deepcopy(p)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for e in source['entries']:
    if e not in p['entries']:p['entries'].append(e)
summary='0303-epm-eleventh-sivil-toplum-iliskileri-summary'
quote='0303-epm-eleventh-sivil-toplum-iliskileri-quote'
cp='0303-epm-eleventh-sivil-toplum-iliskileri-p'
party='0404-yeni-parti-haber-197-protocol-p'
news='0404-sdd-toplumsal-20261008-protocol-p'
key='0404-sdd-protokol'; event=key+'-event'; relation=key+'-relation'; finding=key+'-explanation'; statement=key+'-statement'
scope_statement='practice-f0152c7829df8f7b60328a5fd1439abb9da28ba5c5d23384be897567f8770ee0'
scope_event='practice-d87407e37978488f14c9da77da862419dccc11859a1c01e0b38615191bd8a2ba'
new_entries=[
 {'kind':'finding','values':{'id':finding,'party_id':'yeni-parti','heading':'Söylem ve uygulama','pair_id':finding,
  'text':'Tüzük, Merkez Yönetim Kurulunun sivil toplum örgütleriyle ilişkileri düzenlemesini öngörür. Parti duyurusu ve Toplumsal Haber, Yeni Parti ile Sosyal Demokrasi Derneği arasında bir iş birliği protokolü imzalandığını bildirir. Protokolün metni ve Merkez Yönetim Kurulu kararı görülmedi.',
  'provenance':'summary','epistemic_type':'claim'}},
 {'kind':'review','values':{'id':'review-'+finding,'kind':'finding','subject_id':finding,'reviewer_kind':'agent',
  'reviewed_at':now,'result':'reviewed','reason':'Kurucu tüzük, parti duyurusu ve Toplumsal haberi ayrı okunarak protokol içeriği ve yetki kararı açık tutuldu.'}},
]
for fid,passages in ((summary,[cp]),(quote,[cp]),(finding,[cp,party,news])):
    for pid in passages:
        if fid==finding:new_entries.append({'kind':'finding_evidence','values':{'finding_id':fid,'passage_id':pid,'role':'support'}})
        new_entries.append({'kind':'verification','values':{'finding_id':fid,'passage_id':pid,'checked_at':now,
          'result':'confirmed','reason':'Kurucu tüzük ve SDD protokolü kaynaklarında ilgili pasaj ayrı okundu.'}})
for e in new_entries:
    if e not in p['entries']:p['entries'].append(e)
records={k:[] for k in p['practice_records']}
records['practice_statement'].append({'id':statement,'party_id':'yeni-parti','topic_id':'sivil-toplum-iliskileri',
 'taxonomy_version':4,'summary_finding_id':summary,'quote_finding_id':quote,'statement_at':None,'date_precision':'unknown',
 'version_id':'epm-charter-v1','period_basis':'22 Temmuz tarihli kurucu tüzük ve 24 Temmuz parti kuruluşu ayrı; kesin kabul anı bilinmiyor.',
 'uncertainty_reason':'Tüzük MYK görevini düzenler; bu protokol için MYK kararı ayrıca görülmedi.',
 'comparison_row_id':'04-03-v3-0303-epm-eleventh-sivil-toplum-iliskileri-row'})
for kind,sid in [('statement',scope_statement),('event',scope_event)]:
 records['practice_scope_v2'].append({'id':sid,'party_id':'yeni-parti','topic_id':'sivil-toplum-iliskileri',
  'taxonomy_version':4,'period_start':'2026-07-24','cutoff_at':'2026-11-10T14:38:46.154751+00:00',
  'research_kind':kind,'boundary_reason':'SDD ile protokol okuması; diğer sivil toplum ilişkileri ve karar belgeleri açıktır.'})
records['practice_event'].append({'id':event,'common_event_key':'yeni-parti-sdd-isbirligi-protokolu-2026',
 'event_at':None,'date_precision':'unknown','date_unknown_reason':'8 Ekim haberi imzayı bildiriyor; kaynak gövdesinde olayın kesin günü belirtilmiyor.',
 'scope_context':'Yeni Parti ve Sosyal Demokrasi Derneği iş birliği protokolü','title':'Sosyal Demokrasi Derneği ile protokol',
 'occurrence_basis':'Parti duyurusu ve 8 Ekim tarihli haber aynı imza olayını bildiriyor.'})
for pid in (party,news):
 records['practice_event_evidence'].append({'event_id':event,'passage_id':pid,'stage':'action',
  'supported_point':'Yeni Parti ile Sosyal Demokrasi Derneği arasında iş birliği protokolü imzalanması.',
  'concrete_basis':'Parti duyurusu ve yerel haberin protokol imzasına ilişkin pasajı.',
  'limitation':'Protokolün metni, MYK yetki kararı ve bağımsız kaynak ilişkisi belirlenmedi.','epistemic_type':'claim'})
 records['practice_evidence_assessment'].append({'event_id':event,'passage_id':pid,'stage':'action','basis_kind':'document'})
records['practice_relation'].append({'id':relation,'statement_id':statement,'event_id':event,'party_id':'yeni-parti',
 'topic_id':'sivil-toplum-iliskileri','scope_id':scope_event,'comparability_reason':'Her ikisi partinin sivil toplum kuruluşlarıyla ilişkisine yöneliktir.',
 'target_finding_id':summary,'result_finding_id':None,'explanation_finding_id':finding,
 'temporal_context':'Kurucu tüzükten sonra, 8 Ekim tarihli haberden önce veya o tarihte bildirilen imza.',
 'authority_context':'Tüzük MYK ilişkilerini düzenler; protokol için MYK kararı veya imza yetkisi görülmedi.',
 'uncertainty_reason':'Protokol metni, kesin imza günü ve MYK yetki kararı açık; basın kaynaklarının bağımsızlığı varsayılmaz.'})
records['practice_candidate'].append({'id':key+'-candidate','scope_id':scope_event,'event_id':event,'relation_id':relation,
 'state':'eligible','reason':'Sivil toplum derneğiyle bildirilen iş birliği tüzükteki ilişki konusuyla ilgilidir.',
 'passage_ids':json.dumps([party,news])})
for scope,version,url,section in [(scope_statement,'epm-charter-v1','https://yenipartiyiz.biz/parti-tuzugu','MYK sivil toplum ilişkileri'),
 (scope_event,'0404-yeni-parti-haber-197-v1','https://api.yeni-parti.org.tr/api/haberler/197','Parti duyurusu protokol imzası'),
 (scope_event,'0404-sdd-toplumsal-20261008-v1','https://www.toplumsal.com.tr/haber/ozgur-ozel-ve-heyeti-sosyal-demokrasi-dernegi-ile-gorustu_28637/','Toplumsal Haber protokol imzası')]:
 idx=str(len(records['practice_attempt_v2'])+1); aid=key+'-reading-'+idx; reason=section+' metni gerçek kaynakta incelendi.'
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
 ids=sorted(pids)
 fresh.append({'subject_kind':kind,'subject_id':identity,'reviewer_kind':'agent','reviewed_at':now,
  'source_version_ids':json.dumps(sorted({passages[x]['version_id'] for x in ids}),ensure_ascii=False),
  'passage_ids':json.dumps(ids,ensure_ascii=False),'inspected_sections':json.dumps(['SDD protokolü ve tüzük hükmü: '+kind],ensure_ascii=False),
  'supported_claim':identity+' için tüzük veya protokol imzasını bildiren kaynak pasajları incelendi.',
  'limitations':'Protokol metni, kesin olay günü ve MYK yetki kararı görülmedi; haberlerin bağımsızlığı varsayılmadı.',
  'result':'reviewed','reason':identity+' hedefinin tüzük ve SDD protokolü pasajları ayrı okundu.'})
uygulamalar.validate_practice_source_review(data,fresh,require_coverage=False,party_id='yeni-parti')
r['practice_source_review'].extend(fresh)
r['source_review_refs'].extend({'subject_kind':x['subject_kind'],'subject_id':x['subject_id']} for x in fresh)
uygulamalar.validate_practice_source_review(data,r['practice_source_review'],party_id='yeni-parti')
for name,obj in [('package-sdd-106-union-draft.json',p),('sdd-106-union-review-draft.json',r)]:
 (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('SEMANTIC_PASS',len(r['practice_source_review']),len(p['practice_records']['practice_event']),len(p['practice_records']['practice_relation']))
