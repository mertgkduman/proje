import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text())
package=read(D/'media-kind-fixed-union-draft.json');previous=read(D/'media-kind-fixed-union-review-draft.json')
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
inventory=read('data/practices/04-inventory.json')
entries,records=package['entries'],package['practice_records'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
for n in ['climate-vote-source-draft.json','climate-register-source-draft.json']:entries.extend(read(D/n)['entries'])
for kind in ['statement','event']:
 c=next(c for c in inventory['cells'] if c['party_id']=='emep' and c['topic_id']=='doga-ekoloji' and c['research_kind']==kind)
 records['practice_scope_v2'].append(dict(id=c['cell_id'],party_id='emep',topic_id='doga-ekoloji',taxonomy_version=4,period_start=c['period_start'],cutoff_at=c['cutoff_at'],research_kind=kind,boundary_reason='Program doğal varlıkların korunmasını ister; İklim Kanunu kesin oylaması incelenir, diğer olaylar ve sonuçlar açık.'))
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='doga-ekoloji' and x['research_kind']=='event')
records['practice_statement'].append(dict(id='0410-climate-ecology-statement',party_id='emep',topic_id='doga-ekoloji',taxonomy_version=4,summary_finding_id='0309-emep-program-041-0-summary',quote_finding_id='0309-emep-program-041-0-quote',statement_at=None,date_precision='unknown',version_id='0208-emep-program-charter-v1',period_basis='2019 parti yayını ve 2020 web güncellemesi; programın kabul tarihi bilinmiyor.',uncertainty_reason='Ara program değişiklikleri ve bütün dönem boyunca yürürlük durumu bilinmiyor.',comparison_row_id='04-03-v3-0309-emep-program-041-0-row'))
program='0309-emep-program-041-0-passage';pids=['0410-emep-climate-2025-register-number-p','0410-emep-climate-2025-ballot-bayhan-p','0410-emep-climate-2025-ballot-karaca-p']
eid='0410-climate-22927-event';rid='0410-climate-22927-relation';fid='0410-climate-22927-explanation'
def add(k,**v):entries.append(dict(kind=k,values=v))
for old_finding in ('0309-emep-program-041-0-summary','0309-emep-program-041-0-quote'):
 add('verification',finding_id=old_finding,passage_id=program,checked_at=now,result='confirmed',reason='Özgün program paragrafı ve ilgili Faz 3 bulgusu tekrar okundu.')
add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Program doğal varlıkların korunmasını önerir. 2 Temmuz 2025 İklim Kanunu kesin oylamasında Sevda Karaca Demir ret oyu verdi; cetvel İskender Bayhan için katılmadı kaydı gösterir.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program, TBMM teklif kaydı ve açık oy cetvelinin ayrı pasajları incelendi.')
for pid in [program]+pids:
 add('finding_evidence',finding_id=fid,passage_id=pid,role='support');add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='İlgili program veya TBMM kayıt pasajı incelendi.')
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-3-104-2-2927-iklim-kanunu',event_at='2025-07-02',date_precision='day',date_unknown_reason=None,scope_context='TBMM 104. birleşim kesin açık oy cetveli',title='İklim Kanunu kesin açık oylaması',occurrence_basis='TBMM kesin açık oy cetveli ve 2/2927 teklif kaydı.'))
points=['TBMM kayıt ekranı İklim Kanunu teklifinin esas numarasını 2/2927 olarak gösterir.','Kesin cetvel Bayhan için katılmadı ve pusula yok kaydını gösterir.','Kesin cetvel Karaca Demir için ret oyunu gösterir.']
for pid,point in zip(pids,points):
 records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,supported_point=point,stage='action',concrete_basis='TBMM teklif kaydı ve kesin açık oy cetveli.',limitation='Bayhan’ın katılmama nedeni ve oy tercihi çıkarılmaz; Karaca Demir’in oyu bireyseldir.',epistemic_type='claim'))
 records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0410-climate-ecology-statement',event_id=eid,party_id='emep',topic_id='doga-ekoloji',scope_id=scope,comparability_reason='Program doğal varlıkların korunmasını ele alır; oylanan İklim Kanunu iklim değişikliğiyle mücadeleye ilişkin düzenlemedir. Oy tercihi program hükmünün gerçekleşmesi sayılmaz.',target_finding_id='0309-emep-program-041-0-summary',result_finding_id=None,explanation_finding_id=fid,temporal_context='2019/2020 program yayını ve 2 Temmuz 2025 kesin oylama ayrı tarihlerdir.',authority_context='Oylar ayrı ayrı Sevda Karaca Demir ve İskender Bayhan’a aittir.',uncertainty_reason='Programın 2025 döneminde yürürlüğü ve Bayhan’ın katılmama nedeni bilinmez; yasanın etkisi oy cetvelinden çıkarılmaz.'))
records['practice_candidate'].append(dict(id='0410-climate-22927-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='2/2927 kesin cetvelindeki iki EMEP milletvekilinin farklı kayıtları.',passage_ids=json.dumps(pids)))
versions={e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'}
for i,role in enumerate(('register','ballot')):
 v='0410-emep-climate-2025-'+role+'-v1';url=versions[v]['original_url'];section={'register':'2/2927 teklif kaydı','ballot':'Karaca Demir ve Bayhan kesin oy satırları'}[role];aid='0410-climate-22927-attempt-'+str(i)
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; kapsam açık.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
new_passages={x['passage_id'] for x in records['practice_event_evidence']};targets=rules.practice_review_package_targets(data,records,new_passages,party_id='emep');passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
 if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
 inspected=[passages[x] for x in sorted(pids)]
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program doğanın korunmasını önerir; TBMM kaydı teklif ve ayrı iki oy satırını gösterir.',limitations='Katılmama nedeni ve yasanın sonucu çıkarılmaz.',result='reviewed',reason=kind+' / '+identity+' için ilgili program ve TBMM kayıt pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for n,obj in [('climate-union-draft.json',package),('climate-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/n).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('CLIMATE_UNION_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']))
