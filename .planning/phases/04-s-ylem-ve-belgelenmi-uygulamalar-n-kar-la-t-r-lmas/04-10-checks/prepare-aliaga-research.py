import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent;read=lambda p:json.loads(Path(p).read_text());package=read(D/'mesem-union-draft.json');previous=read(D/'mesem-union-review-draft.json');base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json');entries,records=package['entries'],package['practice_records'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
for name in ('aliaga-research-source-draft.json','aliaga-research-passages.json'):entries.extend(read(D/name)['entries'])
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='is-sagligi' and x['research_kind']=='event');program='0410-emep-safety-program-p';pre='0410-emep-research-104172-register-';pids=[pre+x+'-p' for x in ('date','owner','topic')]
def add(k,**v):entries.append(dict(kind=k,values=v))
fid='0410-aliaga-104172-explanation';eid='0410-aliaga-104172-event';rid='0410-aliaga-104172-relation'
add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Program iş kazalarına karşı yeterli önlem savunur. İskender Bayhan’ın ilk imza sahibi olduğu çok imzalı Aliağa ağır sanayi işçi sağlığı araştırma önergesi 7 Mayıs 2026’da TBMM’ye sunuldu.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program, TBMM kaydı ve imzalı araştırma önergesi ayrı okundu.')
for pid in [program]+pids:
    add('finding_evidence',finding_id=fid,passage_id=pid,role='support');add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='İlgili program veya TBMM kayıt pasajı okundu.')
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-4-10-4172-aliaga-is-sagligi',event_at='2026-05-07',date_precision='day',date_unknown_reason=None,scope_context='TBMM çok imzalı Meclis araştırması önergesi',title='Aliağa ağır sanayide iş sağlığı araştırma önergesi',occurrence_basis='TBMM kaydı ve çok imzalı özgün önerge.'))
points=['Önerge 7 Mayıs 2026’da başkanlığa geldi.','İskender Bayhan ilk imza sahibi olarak kaydedildi.','Önerge Aliağa ağır sanayide çalışan işçilerin sorunları ve iş sağlığı önlemlerinin araştırılmasını istiyor.']
for pid,point in zip(pids,points):
    records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,supported_point=point,stage='action',concrete_basis='TBMM kayıt ekranı.',limitation='Önerge verilmesi komisyon kurulduğu, kabul veya fiilî sonuç anlamına gelmez.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0410-safety-statement',event_id=eid,party_id='emep',topic_id='is-sagligi',scope_id=scope,comparability_reason='Program iş kazalarına karşı önlem savunur; önerge Aliağa ağır sanayide iş sağlığı ve alınacak tedbirlerin araştırılmasını ister.',target_finding_id='0410-safety-statement-finding',result_finding_id=None,explanation_finding_id=fid,temporal_context='Programın 2023 arşivi ve 2026 önergesi ayrı tarihlerdir.',authority_context='İlk imza İskender Bayhan; diğer imzacılar arasında farklı partilerin milletvekilleri vardır.',uncertainty_reason='Önergenin kabulü veya fiilî koşulların değiştiği gösterilmedi; gerekçedeki iddialar bağımsız doğrulama değildir.'))
records['practice_candidate'].append(dict(id='0410-aliaga-104172-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='İş sağlığı konusunda tarihli Meclis araştırma önergesi.',passage_ids=json.dumps(pids)))
versions={e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'}
for i,role in enumerate(('register','pdf')):
    version='0410-emep-research-104172-'+role+'-v1';url=versions[version]['original_url'];section='Geliş, ilk imza ve konu' if role=='register' else 'Sekiz tarama sayfası: imzalar ve gerekçe';aid='0410-aliaga-research-attempt-'+str(i)
    records['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; nihai durum açık.',source_version_id=version))
data=copy.deepcopy(base)
for entry in entries:
    if entry['values'] not in data.setdefault(entry['kind'],[]):data[entry['kind']].append(entry['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_targets(data,records);passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
    if 'emep' not in parties:continue
    if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
    inspected=[passages[x] for x in sorted(pids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program iş sağlığı önlemini savunur; TBMM kaydı Aliağa araştırma önergesini gösterir.',limitations='Araştırma açılması talebi, kabul veya gerçekleşmiş önlem değildir.',result='reviewed',reason=kind+' / '+identity+' için program ve TBMM kayıt pasajları incelendi.'))
rules.validate_practice_source_review(data,reviews,require_coverage=False,party_id='emep');refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('aliaga-research-union-draft.json',package),('aliaga-research-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('ALIAGA_RESEARCH_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']))
