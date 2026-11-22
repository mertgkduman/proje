import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent;read=lambda p:json.loads(Path(p).read_text());package=read(D/'mesem-research-union-v2-draft.json');previous=read(D/'mesem-research-union-v2-review-draft.json');base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json');entries,records=package['entries'],package['practice_records'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
entries.extend(read(D/'mandate-3761-source-draft.json')['entries'])
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='dis-politika' and x['research_kind']=='event');program='0309-emep-program-016-0-passage';speech='0410-emep-tezkere-3761-session-emep-p';ballot='0410-emep-tezkere-3761-ballot-emep-p';pids=[speech,ballot]
def add(k,**v):entries.append(dict(kind=k,values=v))
fid='0410-mandate-3761-explanation';eid='0410-mandate-3761-event';rid='0410-mandate-3761-relation'
add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Program ülkeler arası ilişkilerde egemenliğe saygı ve barış ilkesini savunur. İskender Bayhan 17 Ekim 2023’te EMEP adına 3/761 sayılı tezkereye hayır diyeceklerini açıkladı; kesin açık oy cetvelinde kendi oyu ret olarak yer aldı.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program, EMEP adına açıklama ve bireysel oy ayrı kaynaklarda okundu.')
for pid in [program]+pids:
    add('finding_evidence',finding_id=fid,passage_id=pid,role='support');add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='İlgili program, tutanak veya oy cetveli pasajı incelendi.')
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-2-008-3-761-tezkere',event_at='2023-10-17',date_precision='day',date_unknown_reason=None,scope_context='TBMM 8. birleşim, Irak ve Suriye tezkeresi',title='3/761 tezkere açıklaması ve açık oylaması',occurrence_basis='Tutanak ve isimli kesin açık oy cetveli.'))
for pid,point in [(speech,'İskender Bayhan EMEP adına tezkereye hayır açıklaması yaptı.'),(ballot,'Kesin açık oy cetvelinde Bayhan’ın bireysel oyu ret olarak kaydedildi.')]:
    records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,supported_point=point,stage='action',concrete_basis='Özgün TBMM tutanağı veya kesin açık oy cetveli.',limitation='EMEP adına açıklama, o tarihte TBMM grubu olduğunu göstermez.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0410-foreign-principles-statement',event_id=eid,party_id='emep',topic_id='dis-politika',scope_id=scope,comparability_reason='Program barış ve egemenlik temelindeki ilişkileri savunur; açıklama ve oy sınır ötesi yetki tezkeresi hakkındadır.',target_finding_id='0410-foreign-principles-finding',result_finding_id=None,explanation_finding_id=fid,temporal_context='2023 program arşivi ve Ekim 2023 tezkere işlemi ayrı kaynak ve tarihlerdir.',authority_context='Açıklama Bayhan tarafından EMEP adına yapıldı; cetveldeki oy Bayhan’a aittir.',uncertainty_reason='Oturumda açıklanan toplamlarla kesin cetvel arasında fark vardır; nedenine ilişkin bir çıkarım yapılmadı.'))
records['practice_candidate'].append(dict(id='0410-mandate-3761-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='Dış politika alanında tutanak ve kesin cetvelle belgelenmiş açıklama ve oy.',passage_ids=json.dumps(pids)))
versions={e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'}
for i,role in enumerate(('session','ballot')):
    version='0410-emep-tezkere-3761-'+role+'-v1';url=versions[version]['original_url'];section='Bayhan’ın EMEP adına konuşması' if role=='session' else 'Bayhan’ın bireysel oy satırı ve kesin cetvel';aid='0410-mandate-3761-attempt-'+str(i)
    records['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; ilk anons ve kesin cetvel arasındaki fark açık.',source_version_id=version))
data=copy.deepcopy(base)
for entry in entries:
    if entry['values'] not in data.setdefault(entry['kind'],[]):data[entry['kind']].append(entry['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_targets(data,records);passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
    if 'emep' not in parties:continue
    if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
    inspected=[passages[x] for x in sorted(pids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program dış ilişkilerde barış ilkesini savunur; Bayhan EMEP adına hayır dedi ve bireysel ret oyu verdi.',limitations='EMEP adına konuşma grup bulunduğu anlamına gelmez; toplam farklılığı açık.',result='reviewed',reason=kind+' / '+identity+' için program, tutanak ve cetvel pasajları incelendi.'))
rules.validate_practice_source_review(data,reviews,require_coverage=False,party_id='emep');refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('mandate-3761-union-draft.json',package),('mandate-3761-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('MANDATE_3761_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']))
