import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text())
package=read(D/'tpi-26431-union-draft.json'); previous=read(D/'tpi-26431-union-review-draft.json')
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries,records=package['entries'],package['practice_records'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
entries.extend(read(D/'gaziantep2026-source-draft.json')['entries'])
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='orgut-il-kongre' and x['research_kind']=='event')
charter='0410-emep-kocaeli-charter-selected-p'; historic='0410-emep-kocaeli-charter-202305-p'; news='0410-emep-gaziantep2026-news-p'; party='0410-emep-gaziantep2026-party-p'
eid='0410-gaziantep-2026-congress-event';rid='0410-gaziantep-2026-congress-relation';rf='0410-gaziantep-2026-congress-result';fid='0410-gaziantep-2026-congress-explanation'
def add(k,**v):entries.append(dict(kind=k,values=v))
for f,text,pids in [(rf,'Yeni Çizgi Haber, EMEP Gaziantep 11. Olağan İl Kongresi’nde Mecit Bozkurt’un il başkanı seçildiğini bildirdi.',[news]),(fid,'Tüzük il kongresine il başkanını seçme görevi verir. Yeni Çizgi Haber, Gaziantep il kongresinde Mecit Bozkurt’un seçildiğini bildirdi.',[charter,historic,news,party])]:
 add('finding',id=f,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=f,text=text,provenance='summary',epistemic_type='claim');add('review',id='review-'+f,kind='finding',subject_id=f,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Tüzük, parti ve yerel haber ayrı okundu.')
 for pid in pids:add('finding_evidence',finding_id=f,passage_id=pid,role='support');add('verification',finding_id=f,passage_id=pid,checked_at=now,result='confirmed',reason='İlgili tüzük veya haber pasajı okundu.')
records['practice_event'].append(dict(id=eid,common_event_key='emep-gaziantep-11-il-kongresi-2026',event_at=None,date_precision='unknown',date_unknown_reason='Yerel haber 8 Kasım 2026’da yayımlanmıştır; kongrenin kesin günü metinde açık değildir.',scope_context='EMEP Gaziantep 11. Olağan İl Kongresi',title='Gaziantep il başkanlığı seçimi',occurrence_basis='8 Kasım 2026 yerel haber ve 10 Kasım parti yayını kongre ve seçimi bildirir.'))
for stage in ('action','result'):
 records['practice_event_evidence'].append(dict(event_id=eid,passage_id=news,supported_point='Yeni Çizgi Haber, Mecit Bozkurt’un Gaziantep il başkanı seçildiğini bildirdi.',stage=stage,concrete_basis='8 Kasım 2026 yerel haber.',limitation='Kongre günü ve oy sayısı açık değildir; seçim tutanağı görülmedi.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=news,stage=stage,basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0410-kocaeli-charter-statement',event_id=eid,party_id='emep',topic_id='orgut-il-kongre',scope_id=scope,comparability_reason='Tüzükte il kongresinin başkan seçme yetkisi ile Gaziantep il başkanlığı seçimi aynı konudadır.',target_finding_id='0410-kocaeli-charter-finding',result_finding_id=rf,explanation_finding_id=fid,temporal_context='2019/2020 tüzük yayını, 2023 arşivi, 8 ve 10 Kasım 2026 yayınları ayrıdır; olay günü kesin değil.',authority_context='Seçim il kongresine atfedilir; parti ve yerel haber ayrı kaynaklardır.',uncertainty_reason='Tüzüğün 2026 ara sürümü ve seçim tutanağı görülmedi; yayın günü kongre günü olarak alınmadı.'))
records['practice_candidate'].append(dict(id='0410-gaziantep-2026-congress-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='Yerel haber il kongresi başkan seçimini bildirir.',passage_ids=json.dumps([news])))
for i,role in enumerate(('party','news')):
 v='0410-emep-gaziantep2026-'+role+'-v1';doc=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==v);url=doc['original_url'];section='Gaziantep il kongresi ve başkan seçimi';aid='0410-gaziantep-2026-attempt-'+str(i)
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='Yayın okundu; kongre günü ve tutanak açık.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='emep');passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
 if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
 inspected=[passages[x] for x in sorted(pids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='İl kongresi başkan seçimi tüzüğü ve haber kaynakları okundu.',limitations='Kongre günü, oy sayısı ve 2026 tüzük ara sürümü bilinmiyor.',result='reviewed',reason=kind+' / '+identity+' için kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for n,obj in [('gaziantep2026-union-draft.json',package),('gaziantep2026-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/n).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('GAZIANTEP_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
