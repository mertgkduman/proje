import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent;read=lambda p:json.loads(Path(p).read_text())
package=read(D/'qral-9705-union-draft.json');previous=read(D/'qral-9705-union-review-draft.json');base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries,records=package['entries'],package['practice_records'];entries.extend(read(D/'karinca-9093-source-draft.json')['entries']);now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='sendika-grev' and x['research_kind']=='event')
def add(k,**v):entries.append(dict(kind=k,values=v))
eid,rid,fid='0410-karinca-9093-event','0410-karinca-9093-relation','0410-karinca-9093-explanation';stem='0410-emep-karinca-9093-detail-'
add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Program sendikalaşma ve grev haklarını savunur. İskender Bayhan Karınca Lojistikte işkolu değişikliğinin sendikalaşmaya etkisini Çalışma ve Sosyal Güvenlik Bakanına yazılı soruyla sordu; TBMM kaydı yanıtın bildirildiğini gösterir.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program, TBMM ayrıntısı, imzalı soru ve bakanlık yanıtı okundu; yanıtın kurum sınırı korundu.')
pids=['0309-emep-program-006-1-passage']+[stem+k+'-p' for k in ('number','date','reply','owner','topic')]
for p in pids:
 add('finding_evidence',finding_id=fid,passage_id=p,role='support');add('verification',finding_id=fid,passage_id=p,checked_at=now,result='confirmed',reason='Program veya TBMM soru kaydı okundu.')
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-2-7-9093-karinca-sendika',event_at='2024-02-02',date_precision='day',date_unknown_reason=None,scope_context='TBMM işkolu değişikliğinin sendikalaşmaya etkisi hakkında yazılı soru',title='İşkolu değişikliğinin sendikalaşmaya etkisi hakkında yazılı soru',occurrence_basis='TBMM soru kaydı sahibi, konuyu ve başkanlığa geliş gününü bildirir.'))
for key,point in [('number','TBMM 7/9093 sayılı yazılı soru kaydıdır.'),('date','Soru 2 Şubat 2024 tarihinde başkanlığa geldi.'),('owner','Soru sahibi İstanbul Milletvekili İskender Bayhandır.'),('topic','TBMM özeti işkolu değişikliklerinin sendikalaşmaya etkisini belirtir.'),('reply','TBMM kaydına göre yanıt 7 Kasım 2024te bildirildi.')]:
 p=stem+key+'-p';records['practice_event_evidence'].append(dict(event_id=eid,passage_id=p,supported_point=point,stage='action',concrete_basis='TBMM resmi soru kaydı.',limitation='Bakanlık bildirimi davanın sonraki sonucunu göstermez.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=p,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0410-labor-statement',event_id=eid,party_id='emep',topic_id='sendika-grev',scope_id=scope,comparability_reason='Program sendikalaşma hakkını savunur; soru işkolu değişikliğinin sendika yetkisine etkisini konu alır.',target_finding_id='0410-labor-statement-finding',result_finding_id=None,explanation_finding_id=fid,temporal_context='Programın 2019 yayını ve 2024 soru ve yanıt bildirimi ayrı tarihlerdir.',authority_context='Soru Bayhana, yanıt Çalışma ve Sosyal Güvenlik Bakanlığına aittir.',uncertainty_reason='Bayhan işin niteliğinin değişmediğini, Bakanlık ise değişiklik gerekçesiyle başvuru yapıldığını bildirir; Bakanlık yanıtında o tarihte dava derdesttir, sonraki sonucu bilinmez. Programın olay tarihinde kesintisiz yürürlüğü bilinmiyor.'))
records['practice_candidate'].append(dict(id='0410-karinca-9093-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='TBMM soru ve yanıt kayıtları okundu.',passage_ids=json.dumps(pids[1:])))
for role in ('detail','question','answer'):
 v='0410-emep-karinca-9093-'+role+'-v1';version=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==v);aid='0410-karinca-9093-'+role+'-attempt';section={'detail':'Soru ve yanıt bildirimi','question':'İmzalı soru','answer':'Çalışma ve Sosyal Güvenlik Bakanlığı yanıtı'}[role]
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=version['original_url'],relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=version['original_url'],url=version['original_url'],result='examined',reason='TBMM soru ve yanıtı okundu; yanıtın kurum sınırı açık.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='emep');passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
 if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
 inspected=[passages[x] for x in sorted(ids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program ve TBMM kayıt pasajları okundu.',limitations='Soru ve bakanlık yanıtının işin niteliğine ilişkin farklı anlatımları ve yanıt anında derdest dava ayrı tutulur.',result='reviewed',reason=kind+' / '+identity+' kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('karinca-9093-union-draft.json',package),('karinca-9093-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('KARINCA_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
