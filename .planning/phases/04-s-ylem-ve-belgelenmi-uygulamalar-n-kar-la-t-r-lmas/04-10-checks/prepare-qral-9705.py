import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent;read=lambda p:json.loads(Path(p).read_text())
package=read(D/'ilic-complaint-20240315-union-draft.json');previous=read(D/'ilic-complaint-20240315-union-review-draft.json');base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries,records=package['entries'],package['practice_records'];entries.extend(read(D/'qral-9705-source-draft.json')['entries']);now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='kurt-sorunu' and x['research_kind']=='event')
def add(k,**v):entries.append(dict(kind=k,values=v))
eid,rid,fid='0410-qral-9705-event','0410-qral-9705-relation','0410-qral-9705-explanation';stem='0410-emep-qral-9705-detail-'
add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Program ulusal toplulukların kamu hizmetlerinden ana dilinde yararlanmasını savunur. Sevda Karaca Demir Kürtçe tiyatro oyunu gösteriminin iptalini Kültür ve Turizm Bakanına yazılı soruyla sordu; TBMM kaydı yanıtın bildirildiğini gösterir.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program, TBMM ayrıntısı, imzalı soru ve bakanlık yanıtı okundu; yanıtın kurum sınırı korundu.')
pids=['0309-emep-program-007-0-passage']+[stem+k+'-p' for k in ('number','date','reply','owner','topic')]
for p in pids:
 add('finding_evidence',finding_id=fid,passage_id=p,role='support');add('verification',finding_id=fid,passage_id=p,checked_at=now,result='confirmed',reason='Program veya TBMM soru kaydı okundu.')
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-2-7-9705-kurtce-tiyatro',event_at='2024-02-12',date_precision='day',date_unknown_reason=None,scope_context='TBMM Kürtçe tiyatro gösteriminin iptal iddiası hakkında yazılı soru',title='Kürtçe tiyatro gösterimi hakkında yazılı soru',occurrence_basis='TBMM soru kaydı sahibi, konuyu ve başkanlığa geliş gününü bildirir.'))
for key,point in [('number','TBMM 7/9705 sayılı yazılı soru kaydıdır.'),('date','Soru 12 Şubat 2024 tarihinde başkanlığa geldi.'),('owner','Soru sahibi Gaziantep Milletvekili Sevda Karaca Demirdir.'),('topic','TBMM özeti Kürtçe tiyatro gösterimine izin verilmediği iddiasını belirtir.'),('reply','TBMM kaydına göre yanıt 7 Haziran 2024te bildirildi.')]:
 p=stem+key+'-p';records['practice_event_evidence'].append(dict(event_id=eid,passage_id=p,supported_point=point,stage='action',concrete_basis='TBMM resmi soru kaydı.',limitation='İptal nedeni soru ve yanıt bildiriminden bağımsız olarak çözümlenmez.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=p,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0410-kurdish-rights-statement',event_id=eid,party_id='emep',topic_id='kurt-sorunu',scope_id=scope,comparability_reason='Program kamu hizmetlerinden ana dilinde yararlanmayı savunur; soru kamuya bağlı merkezde Kürtçe tiyatro gösteriminin iptal iddiasını konu alır.',target_finding_id='0309-emep-program-007-0-summary',result_finding_id=None,explanation_finding_id=fid,temporal_context='Programın 2019 yayını ve 2024 soru ve yanıt bildirimi ayrı tarihlerdir.',authority_context='Soru Karaca Demire, yanıt Kültür ve Turizm Bakanlığına aittir.',uncertainty_reason='Bakanlık yanıtı Devlet Tiyatroları Genel Müdürlüğü işlemleriyle sınırlıdır; tüm kurumların işlemleri hakkında genel sonuç vermez. Programın olay tarihinde kesintisiz yürürlüğü bilinmiyor.'))
records['practice_candidate'].append(dict(id='0410-qral-9705-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='TBMM soru ve yanıt kayıtları okundu.',passage_ids=json.dumps(pids[1:])))
for role in ('detail','question','answer'):
 v='0410-emep-qral-9705-'+role+'-v1';version=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==v);aid='0410-qral-9705-'+role+'-attempt';section={'detail':'Soru ve yanıt bildirimi','question':'İmzalı soru','answer':'Kültür ve Turizm Bakanlığı yanıtı'}[role]
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=version['original_url'],relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=version['original_url'],url=version['original_url'],result='examined',reason='TBMM soru ve yanıtı okundu; yanıtın kurum sınırı açık.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='emep');passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
 if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
 inspected=[passages[x] for x in sorted(ids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program ve TBMM kayıt pasajları okundu.',limitations='Bakanlık yanıtı Genel Müdürlük işlemleriyle sınırlıdır; iptalin tüm idari nedenleri açıklanmış değildir.',result='reviewed',reason=kind+' / '+identity+' kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('qral-9705-union-draft.json',package),('qral-9705-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('QRAL_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
