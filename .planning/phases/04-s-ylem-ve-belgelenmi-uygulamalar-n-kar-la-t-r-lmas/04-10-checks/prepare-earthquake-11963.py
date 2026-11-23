import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent;read=lambda p:json.loads(Path(p).read_text())
package=read(D/'constitution-meeting-20240605-union-draft.json');previous=read(D/'constitution-meeting-20240605-union-review-draft.json');base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries,records=package['entries'],package['practice_records'];entries.extend(read(D/'earthquake-11963-source-draft.json')['entries']);now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='barinma-konut' and x['research_kind']=='event')
def add(k,**v):entries.append(dict(kind=k,values=v))
eid,rid,fid='0410-earthquake-11963-event','0410-earthquake-11963-relation','0410-earthquake-11963-explanation';stem='0410-emep-earthquake-11963-detail-'
add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Program sağlıklı ve güvenli konut hakkını savunur. Sevda Karaca Demir hasar tespitlerine itiraz davalarını Adalet Bakanına yazılı soruyla sordu; TBMM kaydı yanıtın bildirildiğini gösterir.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program, TBMM ayrıntısı, imzalı soru ve bakanlık yanıtı okundu; tarih farkı ve sonuç sınırı korundu.')
pids=['0309-emep-program-057-0-passage']+[stem+k+'-p' for k in ('number','date','reply','owner','topic')]
for p in pids:
 add('finding_evidence',finding_id=fid,passage_id=p,role='support');add('verification',finding_id=fid,passage_id=p,checked_at=now,result='confirmed',reason='Program veya TBMM soru kaydı okundu.')
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-2-7-11963-deprem-hasar-itirazlari',event_at='2024-05-17',date_precision='day',date_unknown_reason=None,scope_context='TBMM deprem hasar tespiti itiraz davaları hakkında yazılı soru',title='Deprem hasar tespitlerine itirazlar hakkında yazılı soru',occurrence_basis='TBMM soru kaydı sahibi, konuyu ve başkanlığa geliş gününü bildirir.'))
for key,point in [('number','TBMM 7/11963 sayılı yazılı soru kaydıdır.'),('date','Soru 17 Mayıs 2024 tarihinde başkanlığa geldi.'),('owner','Soru sahibi Gaziantep Milletvekili Sevda Karaca Demirdir.'),('topic','TBMM özeti 6 Şubat 2023 depremi sonrası hasar itiraz davalarını belirtir.'),('reply','TBMM kaydına göre yanıt 15 Ağustos 2024te bildirildi.')]:
 p=stem+key+'-p';records['practice_event_evidence'].append(dict(event_id=eid,passage_id=p,supported_point=point,stage='action',concrete_basis='TBMM resmi soru kaydı.',limitation='İmzalı soru ve bakanlık yanıtında deprem yılı 2024 yazıyor; bildirim davaların çözüldüğünü göstermez.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=p,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0410-earthquake-housing-statement',event_id=eid,party_id='emep',topic_id='barinma-konut',scope_id=scope,comparability_reason='Program güvenli konut hakkını savunur; soru hasar itirazları nedeniyle geçici barınma yaşayanları konu alır.',target_finding_id='0309-emep-program-057-0-summary',result_finding_id=None,explanation_finding_id=fid,temporal_context='Programın 2019 yayını ve 2024 soru ve yanıt bildirimi ayrı tarihlerdir.',authority_context='Soru Karaca Demire, yanıt Adalet Bakanlığına aittir.',uncertainty_reason='TBMM özeti 2023 derken imzalı soru ve yanıtta 2024 yazılı; sayıların hangi depreme ait olduğu kesinleştirilmedi. Programın olay tarihinde kesintisiz yürürlüğü de bilinmiyor.'))
records['practice_candidate'].append(dict(id='0410-earthquake-11963-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='TBMM soru ve yanıt kayıtları okundu.',passage_ids=json.dumps(pids[1:])))
for role in ('detail','question','answer'):
 v='0410-emep-earthquake-11963-'+role+'-v1';version=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==v);aid='0410-earthquake-11963-'+role+'-attempt';section={'detail':'Soru ve yanıt bildirimi','question':'İmzalı soru','answer':'Adalet Bakanlığı yanıtı'}[role]
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=version['original_url'],relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=version['original_url'],url=version['original_url'],result='examined',reason='TBMM soru ve yanıtı okundu; tarih farkı ve karar sonuçları açık.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='emep');passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
 if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
 inspected=[passages[x] for x in sorted(ids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program ve TBMM kayıt pasajları okundu.',limitations='Soru ve yanıt davaların çözüldüğünü göstermez; soru ve yanıttaki deprem yılı dizinle farklı.',result='reviewed',reason=kind+' / '+identity+' kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('earthquake-11963-union-draft.json',package),('earthquake-11963-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('EARTHQUAKE_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
