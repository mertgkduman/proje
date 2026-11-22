import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
import uygulamalar as rules
D=Path(__file__).parent
read=lambda p: json.loads(Path(p).read_text())
package=read(D/'mekke-union-v3-draft.json'); previous=read(D/'mekke-union-v3-review-draft.json')
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json'); inventory=read('data/practices/04-inventory.json')
entries,records=package['entries'],package['practice_records']; now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
for name in ('aliaga-question-source-draft.json','aliaga-additional-passages.json'): entries.extend(read(D/name)['entries'])
scopes={c['research_kind']:c for c in inventory['cells'] if c['party_id']=='emep' and c['topic_id']=='is-sagligi'}
assert set(scopes)=={'statement','event'}
for c in scopes.values():
    row={k:c[k] for k in ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')}
    row.update(id=c['cell_id'],boundary_reason='Programın iş sağlığı hükmü ve Aliağa sorusu incelendi; diğer kaynaklar açık.')
    records['practice_scope_v2'].append(row)
def add(k,**v): entries.append(dict(kind=k,values=v))
def finding(fid,text,pids,provenance='summary',pair=None):
    add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=pair or fid,text=text,provenance=provenance,epistemic_type='claim')
    add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program ve TBMM kaydı ayrı okundu.')
    for pid in pids:
        add('finding_evidence',finding_id=fid,passage_id=pid,role='support')
        add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün program veya TBMM kayıt pasajı doğrulandı.')
program='0410-emep-safety-program-p'; date='0410-emep-question-31468-register-date-p'; owner='0410-emep-question-31468-register-owner-p'; topic='0410-emep-question-31468-register-topic-p'; reply='0410-emep-question-31468-register-answer-date-p'
sf,qf,ef='0410-safety-statement-finding','0410-safety-statement-quote','0410-aliaga-question-explanation'
finding(sf,'Program işyerlerinde sağlık koşulları ve iş kazalarına karşı yeterli önlemi savunur.',[program])
finding(qf,'Fabrika ve işyerlerinde azami\nsağlık koşulları; iş kazaları ve meslek hastalıklarına karşı yeterli önlem,\nişçi sağlığı ve yaşamının korunması için hijyenik ortam ve yeterli araç gereç.',[program],'quote',sf)
finding(ef,'Program iş kazalarına karşı yeterli önlemi savunur. Sevda Karaca, Aliağa gemi söküm tesislerindeki iş kazalarıyla ilgili 14 Temmuz 2025’te yazılı soru yöneltti; TBMM kaydına göre bakanlık yanıtı 10 Ekim 2025’te geldi.',[program,date,owner,topic,reply])
statement='0410-safety-statement';eid='0410-aliaga-731468-event';rid='0410-aliaga-731468-relation'
records['practice_statement'].append(dict(id=statement,party_id='emep',topic_id='is-sagligi',taxonomy_version=4,summary_finding_id=sf,quote_finding_id=qf,statement_at=None,date_precision='unknown',version_id='0208-emep-program-charter-v1',period_basis='2019 yayın ve 2020 web güncellemesi kabul tarihi değildir.',uncertainty_reason='2023 arşivi ara değişiklik veya 2025 hukuki yürürlük tarihi kanıtı değildir.',comparison_row_id='04-03-v3-0309-emep-program-036-0-row'))
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-3-7-31468-aliaga',event_at='2025-07-14',date_precision='day',date_unknown_reason=None,scope_context='TBMM yazılı soru ve cevap kaydı',title='Aliağa gemi sökümünde iş kazaları sorusu',occurrence_basis='TBMM kaydı sahibi, konuyu ve başkanlığa geliş tarihini içerir.'))
points={date:'Soru 14 Temmuz 2025’te başkanlığa geldi.',owner:'Soru sahibi Gaziantep Milletvekili Sevda Karaca olarak kaydedildi.',topic:'Soru Aliağa gemi söküm tesislerindeki iş kazaları hakkındadır.',reply:'TBMM kaydına göre yanıt 10 Ekim 2025’te geldi.'}
for pid,point in points.items():
    records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,supported_point=point,stage='action',concrete_basis='TBMM soru kayıt ekranı.',limitation='Yanıt gelişi, iddiaların doğrulanması veya soruşturmanın sonuçlandığı anlamına gelmez.',epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id='emep',topic_id='is-sagligi',scope_id=scopes['event']['cell_id'],comparability_reason='Program iş kazalarına karşı önlem ister; soru belli bir sektördeki iş kazaları hakkında bilgi ister.',target_finding_id=sf,result_finding_id=None,explanation_finding_id=ef,temporal_context='Programın 2023 arşivi, 2025 soru ve yanıtı ayrı tarihlerdir.',authority_context='Soru milletvekili Sevda Karaca’ya aittir; yanıt bakanlığa aittir.',uncertainty_reason='Yazılı soru ve yanıt kaydı, koşulların düzeltildiğini veya incelemenin sonuçlandığını göstermez.'))
records['practice_candidate'].append(dict(id='0410-aliaga-731468-candidate',scope_id=scopes['event']['cell_id'],event_id=eid,relation_id=rid,state='eligible',reason='İş sağlığına ilişkin tarihli TBMM soru kaydı.',passage_ids=json.dumps(list(points))))
versions={e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'}
sources=[('statement','0208-emep-program-charter-v1','https://www.emep.org/emek-partisi-program-ve-tuzugu','G/C/b iş sağlığı'),('event','0410-emep-question-31468-register-v1',None,'7/31468 tarih, soru sahibi, konu ve yanıt gelişi'),('event','0410-emep-question-31468-question-v1',None,'7/31468 üç sayfa soru'),('event','0410-emep-question-31468-answer-v1',None,'10 Ekim bakanlık yanıtı taraması')]
for i,(typ,version,url,section) in enumerate(sources):
    if version in versions: url=versions[version]['original_url']
    scope,aid=scopes[typ]['cell_id'],'0410-aliaga-attempt-'+str(i)
    records['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; diğer sonuçlar açık.',source_version_id=version))
data=copy.deepcopy(base)
for entry in entries:
    if entry['values'] not in data.setdefault(entry['kind'],[]):data[entry['kind']].append(entry['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_targets(data,records);passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
    if 'emep' not in parties:continue
    if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
    inspected=[passages[x] for x in sorted(pids)]
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program iş sağlığı önlemi ister; TBMM kaydı Aliağa sorusu ve yanıt gelişini gösterir.',limitations='Yanıt gelişi sorunun veya incelemenin sonuçlandığını kanıtlamaz.',result='reviewed',reason=kind+' / '+identity+' için ilgili program ve TBMM kayıt pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,require_coverage=False,party_id='emep');refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('aliaga-union-draft.json',package),('aliaga-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('ALIAGA_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']))
