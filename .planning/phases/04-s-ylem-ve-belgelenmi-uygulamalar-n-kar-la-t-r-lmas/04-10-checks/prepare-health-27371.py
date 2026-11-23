import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
import uygulamalar as rules
D=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text())
package=read(D/'fund-question-749942-union-draft.json'); previous=read(D/'fund-question-749942-union-review-draft.json')
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries, records=package['entries'],package['practice_records']
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
for n in ('health-27371-source-draft.json','health-27371-passages.json'): entries.extend(read(D/n)['entries'])
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='is-sagligi' and x['research_kind']=='event')
program='0410-emep-safety-program-p'
pids=['0410-emep-question-27371-register-'+x+'-p' for x in ('date','owner','topic')]+['0410-emep-question-27371-notice-reply-p','0410-emep-question-27371-notice-listing-p']
eid='0410-health-27371-event'; rid='0410-health-27371-relation'; fid='0410-health-27371-explanation'
def add(k, **v): entries.append(dict(kind=k,values=v))
add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Program iş kazaları ve meslek hastalıklarına karşı önlem önerir. İskender Bayhan 15 Nisan 2025’te iş kazaları, meslek hastalıkları ve sağlık hizmetlerine erişim hakkında yazılı soru verdi; 22 Mayıs tarihli TBMM gelen kâğıtlarında soru süresinde cevaplanmayanlar arasında yer aldı.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program, TBMM kayıt ve soru metni ile Bakanlık yanıtı ayrı incelendi.')
for pid in [program]+pids:
 add('finding_evidence',finding_id=fid,passage_id=pid,role='support'); add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Program veya TBMM kayıt pasajı okundu.')
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-3-7-27371-isci-sagligi',event_at='2025-04-15',date_precision='day',date_unknown_reason=None,scope_context='TBMM yazılı soru ve cevap kaydı',title='İş sağlığı ve sağlık hizmetlerine ilişkin yazılı soru',occurrence_basis='TBMM kaydı ve 22 Mayıs 2025 gelen kâğıtlar soru ve süre içi yanıtsızlık ilanını gösterir.'))
points=['Soru 15 Nisan 2025’te başkanlığa geldi.','Soru sahibi İskender Bayhan olarak kaydedildi.','Soru iş kazaları ve meslek hastalıklarına ilişkindir.','22 Mayıs 2025 gelen kâğıtlar tarihidir.','Soru süre içinde cevaplanmayanlar arasında ilan edildi.']
for pid,point in zip(pids,points):
 records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,supported_point=point,stage='action',concrete_basis='TBMM soru kayıt ekranı veya 22 Mayıs gelen kâğıtları.',limitation='Süre içi yanıtsızlık ilanı sonraki tüm zamanları veya soru iddialarını doğrulamaz.',epistemic_type='claim')); records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0410-safety-statement',event_id=eid,party_id='emep',topic_id='is-sagligi',scope_id=scope,comparability_reason='Program iş kazaları ve meslek hastalıklarına karşı önlemler önerir; soru bu alandaki ölümleri ve sağlık hizmetlerine erişimi sorar.',target_finding_id='0410-safety-statement-finding',result_finding_id=None,explanation_finding_id=fid,temporal_context='2019/2020 program yayını, 15 Nisan soru ve 22 Mayıs 2025 süre içi yanıtsızlık ilanı ayrı tarihlerdir.',authority_context='Soru İskender Bayhan’a, süre içi yanıtsızlık ilanı TBMM’ye aittir.',uncertainty_reason='Programın 2025’te yürürlüğü, soru iddialarının doğruluğu ve parti etkisi bu belgelerle belirlenmez.'))
records['practice_candidate'].append(dict(id='0410-health-27371-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='Tarihli TBMM soru ve süre içi yanıtsızlık ilanı.',passage_ids=json.dumps(pids)))
versions={e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'}
for i,role in enumerate(('register','question','notice')):
 v='0410-emep-question-27371-'+role+'-v1'; url=versions[v]['original_url']; section={'register':'soru tarihi, sahibi ve konusu','question':'iki sayfa soru PDF metni','notice':'22 Mayıs 2025 gelen kâğıtlarda süresinde cevaplanmayan sorular bölümü'}[role]; aid='0410-health-27371-attempt-'+str(i)
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now)); records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid]))); records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; kapsam açık.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='emep'); passages={p['id']:p for p in data['passage']}; old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']}; reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
 if (kind,identity) in old: reviews.append(old[(kind,identity)]); continue
 inspected=[passages[x] for x in sorted(pids)]; reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program ve TBMM soru kayıt pasajları incelendi.',limitations='Soru ve süre içi yanıtsızlık ilanı iddiaları veya parti etkisini kanıtlamaz.',result='reviewed',reason=kind+' / '+identity+' için kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs
for n,obj in [('health-27371-union-draft.json',package),('health-27371-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/n).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('HEALTH_27371_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
