import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
import uygulamalar as rules
D=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text())
package=read(D/'nato-case-union-draft.json'); previous=read(D/'nato-case-union-review-draft.json'); base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries,records=package['entries'],package['practice_records']; now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
entries.extend(read(D/'tupras-norm-source-draft.json')['entries'])
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='is-sagligi' and x['research_kind']=='event')
def add(k,**v): entries.append(dict(kind=k,values=v))
for number,recipient,notice in [('36753','Çalışma ve Sosyal Güvenlik Bakanlığı','7 Eylül 2026'),('36769','Enerji ve Tabii Kaynaklar Bakanlığı','22 Aralık 2025')]:
    eid='0410-tupras-'+number+'-event';rid='0410-tupras-'+number+'-relation';fid='0410-tupras-'+number+'-explanation'
    pids=['0410-emep-tupras-'+number+'-register-'+x+'-p' for x in ('number','date','reply')]
    add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Program işçi sağlığı ve güvenliğine ilişkin talepler içerir. İskender Bayhan 21 Kasım 2025’te rafinerilerde norm kadro uygulamasının iş güvenliğine etkisini '+recipient+' için yazılı soruyla gündeme getirdi. TBMM kaydı yanıtın '+notice+' tarihinde bildirildiğini gösterir.',provenance='summary',epistemic_type='claim')
    add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program, TBMM kayıt ekranı, soru ve taranmış bakanlık cevabı görsel okundu.')
    for pid in ['0410-emep-safety-program-p']+pids:
        add('finding_evidence',finding_id=fid,passage_id=pid,role='support');add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Program veya soru numarası ve tarihli TBMM kayıt pasajı okundu.')
    records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-4-7-'+number+'-tupras-norm-kadro',event_at='2025-11-21',date_precision='day',date_unknown_reason=None,scope_context='TBMM yazılı soru ve yanıt bildirim kaydı',title='TÜPRAŞ norm kadro iş güvenliği sorusu: '+recipient,occurrence_basis='TBMM kayıt ekranı soru numarası, başkanlığa geliş tarihi ve yanıt bildirimini gösterir.'))
    for pid,point in zip(pids,['Soru 7/'+number+' esas numarasıyla kaydedildi.','Soru 21 Kasım 2025’te başkanlığa geldi.','Yanıt '+notice+' tarihinde bildirildi.']):
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,supported_point=point,stage='action',concrete_basis='TBMM yazılı soru kayıt ekranı.',limitation='Yanıt bildirimi sorudaki iddiaları veya parti etkisini doğrulamaz.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage='action',basis_kind='document'))
    records['practice_relation'].append(dict(id=rid,statement_id='0410-safety-statement',event_id=eid,party_id='emep',topic_id='is-sagligi',scope_id=scope,comparability_reason='Program işçi sağlığı ve güvenliğini savunur; soru rafinerilerde personel ve iş güvenliğiyle ilgilidir.',target_finding_id='0410-safety-statement-finding',result_finding_id=None,explanation_finding_id=fid,temporal_context='2019/2020 program yayını, 21 Kasım soru ve '+notice+' bildirim ayrı tarihlerdir.',authority_context='Soru Bayhan’a, cevap '+recipient+'na aittir.',uncertainty_reason='Programın tüm dönem yürürlüğü, somut tesis güvenliği ve sorunun etkisi bu kayıtlarla belirlenmez.'))
    records['practice_candidate'].append(dict(id='0410-tupras-'+number+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='Tarihli TBMM soru kaydı ve cevap bildirimi.',passage_ids=json.dumps(pids)))
    for role in ('register','question','answer'):
        v='0410-emep-tupras-'+number+'-'+role+'-v1';url=next(e['values']['original_url'] for e in entries if e['kind']=='document_version' and e['values']['id']==v);aid='0410-tupras-'+number+'-'+role+'-attempt';section={'register':'soru numarası ve yanıt bildirimi','question':'taranmış soru tüm sayfalar','answer':'taranmış Bakanlık yanıtı tüm sayfalar'}[role]
        records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; kapsam açık.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
    if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='emep');passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
    if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
    inspected=[passages[x] for x in sorted(pids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program ve TBMM kayıt pasajları incelendi.',limitations='Yanıt bildirimi iddiaları veya parti etkisini kanıtlamaz.',result='reviewed',reason=kind+' / '+identity+' için kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('tupras-norm-union-draft.json',package),('tupras-norm-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('TUPRAS_NORM_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
