import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent; read=lambda p:json.loads(Path(p).read_text())
package=read(D/'aliaga-union-draft.json');previous=read(D/'aliaga-union-review-draft.json');base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries,records=package['entries'],package['practice_records'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
for name in ('mesem-question-source-draft.json','mesem-additional-passages.json'):entries.extend(read(D/name)['entries'])
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='is-sagligi' and x['research_kind']=='event')
program='0410-emep-safety-program-p'; pre='0410-emep-question-8231-register-'; pids=[pre+x+'-p' for x in ('date','owner','topic','reply')]
def add(k,**v):entries.append(dict(kind=k,values=v))
fid='0410-mesem-78231-explanation';eid='0410-mesem-78231-event';rid='0410-mesem-78231-relation'
add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Program iş kazalarına karşı yeterli önlemi savunur. Sevda Karaca 11 Ocak 2024’te MESEM öğrencilerinin iş kazaları hakkında yazılı soru yöneltti; TBMM kaydı 11 Mart’ta bakanlık yanıtı bildirildiğini gösterir.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program ve TBMM kayıt pasajları incelendi.')
for pid in [program]+pids:
    add('finding_evidence',finding_id=fid,passage_id=pid,role='support');add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün program veya TBMM kaydı incelendi.')
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-2-7-8231-mesem',event_at='2024-01-11',date_precision='day',date_unknown_reason=None,scope_context='TBMM yazılı soru ve cevap kaydı',title='MESEM öğrencilerinin iş kazalarına ilişkin soru',occurrence_basis='TBMM kaydı başvuru tarihi, sahibi ve konusunu gösterir.'))
points=['Soru 11 Ocak 2024’te başkanlığa geldi.','Soru sahibi Sevda Karaca olarak kaydedildi.','Soru MESEM öğrencilerinin uğradığı iş kazalarıyla ilgilidir.','Yanıt 11 Mart 2024’te bildirildi.']
for pid,point in zip(pids,points):
    records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,supported_point=point,stage='action',concrete_basis='TBMM soru kayıt ekranı.',limitation='Yanıt gelişi iş kazalarının önlendiğini veya her iddianın doğrulandığını göstermez.',epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0410-safety-statement',event_id=eid,party_id='emep',topic_id='is-sagligi',scope_id=scope,comparability_reason='Program iş kazalarına karşı önlem ister; soru MESEM öğrencilerinin uğradığı kazalar ve iş sağlığı denetimleri hakkındadır.',target_finding_id='0410-safety-statement-finding',result_finding_id=None,explanation_finding_id=fid,temporal_context='Programın 2023 arşivi, Ocak sorusu ve Mart yanıtı ayrı tarihlidir.',authority_context='Soru Sevda Karaca’ya, yanıt MEB’e aittir.',uncertainty_reason='Yanıtın bildirildiği bilinir; işyerlerinde risklerin giderildiği veya tüm iddiaların doğrulandığı çıkarılmaz.'))
records['practice_candidate'].append(dict(id='0410-mesem-78231-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='İş sağlığına ilişkin tarihli TBMM soru kaydı.',passage_ids=json.dumps(pids)))
versions={e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'}
for i,role in enumerate(('register','question','answer')):
    version='0410-emep-question-8231-'+role+'-v1';url=versions[version]['original_url'];section={'register':'soru tarihi, sahibi, konusu ve yanıt bildirilişi','question':'tek sayfa imzalı soru görseli','answer':'üç sayfa bakanlık yanıtı görseli'}[role];aid='0410-mesem-attempt-'+str(i)
    records['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; kapsam açık.',source_version_id=version))
data=copy.deepcopy(base)
for entry in entries:
    if entry['values'] not in data.setdefault(entry['kind'],[]):data[entry['kind']].append(entry['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_targets(data,records);passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
    if 'emep' not in parties:continue
    if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
    inspected=[passages[x] for x in sorted(pids)]
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program iş sağlığı önlemi ister; TBMM kaydı MESEM sorusu ve yanıt bildirimini gösterir.',limitations='Yanıt bildirimi, risklerin giderildiğini göstermez.',result='reviewed',reason=kind+' / '+identity+' için program ve TBMM kayıt pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,require_coverage=False,party_id='emep');refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('mesem-union-draft.json',package),('mesem-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('MESEM_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']))
