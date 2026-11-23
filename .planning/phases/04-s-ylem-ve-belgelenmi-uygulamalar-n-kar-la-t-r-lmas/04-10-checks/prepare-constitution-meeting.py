import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text
import uygulamalar as rules

D=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text())
package=read(D/'erlau-28709-strengthened-union-draft.json')
previous=read(D/'erlau-28709-strengthened-preserved-review-draft.json')
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries,records=package['entries'],package['practice_records']
entries.extend(read(D/'constitution-meeting-20240605-source-draft.json')['entries'])
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='kurt-sorunu' and x['research_kind']=='event')
def add(k,**v):entries.append(dict(kind=k,values=v))
pid='0410-emep-constitution-meeting-emep-kurdish-p'
exact='Kürt sorununun eşit haklar temelinde demokratik yol ve yöntemlerle çözülmemiş olması'
assert exact in html_source_text((D/'constitution-meeting-20240605-emep.html').read_bytes())
add('passage',id=pid,version_id='0410-emep-constitution-meeting-emep-v1',exact=exact,prefix=None,suffix=None,article=None,section='Aslanın görüşme sonrası açıklaması',pdf_page_index=None,printed_page=None)
eid,rid,fid='0410-constitution-meeting-20240605-event','0410-constitution-meeting-20240605-relation','0410-constitution-meeting-20240605-explanation'
add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Program Kürt sorununun eşit haklar temelinde demokratik çözümünü savunur. EMEP heyeti TBMM Başkanı ile anayasa konusunu görüştü; Aslan görüşme sonrasında eşit haklar temelinde çözülmemiş Kürt sorununu saydığı sorunlar arasında andı.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program ve TBMM ile parti yayınları okundu; görüşme sonrasındaki beyan anayasa değişikliği veya kabul edilmiş ortak karar sayılmadı.')
pids=['0309-emep-program-007-0-passage','0410-emep-constitution-meeting-tbmm-p','0410-emep-constitution-meeting-emep-p',pid]
for p in pids:
 add('finding_evidence',finding_id=fid,passage_id=p,role='support')
 add('verification',finding_id=fid,passage_id=p,checked_at=now,result='confirmed',reason='Program ve özgün TBMM veya parti yayını okundu.')
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-baskani-emep-anayasa-gorusmesi-2024-06-05',event_at='2024-06-05',date_precision='day',date_unknown_reason=None,scope_context='EMEP heyetinin TBMM Başkanıyla anayasa görüşmesi ve görüşme sonrası açıklama',title='EMEP heyetinin TBMM Başkanıyla anayasa görüşmesi',occurrence_basis='5 Haziran tarihli TBMM yayını kabul ve katılanları belgeliyor.'))
for p,point in [('0410-emep-constitution-meeting-tbmm-p','TBMM yayını Aslan, Bayhan ve Karaca Demirin kabule katıldığını kaydeder.')]:
 records['practice_event_evidence'].append(dict(event_id=eid,passage_id=p,supported_point=point,stage='action',concrete_basis='TBMM ve parti özgün görüşme yayınları.',limitation='Görüşme bir anayasa değişikliği veya ortak kararın kabulünü göstermez.',epistemic_type='claim'))
 records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=p,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0410-kurdish-rights-statement',event_id=eid,party_id='emep',topic_id='kurt-sorunu',scope_id=scope,comparability_reason='Program eşit haklar ve demokratik çözümü savunur; Aslan görüşme sonrası aynı sorunu çözümsüz kalan meseleler arasında andı.',target_finding_id='0309-emep-program-007-0-summary',result_finding_id=None,explanation_finding_id=fid,temporal_context='2019 program yayını ve 5 Haziran 2024 görüşmesi ayrı tarihlerdir.',authority_context='Görüşme heyete, basın açıklamasındaki değerlendirme Aslana aittir.',uncertainty_reason='Partinin 2023 arşivlenmiş programının ara sürümleri ve olay anında kesintisiz yürürlüğü ayrıca kesinleştirilmedi; görüşme çözüm veya ortak kararın kabulünü göstermez.'))
records['practice_candidate'].append(dict(id='0410-constitution-meeting-20240605-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='TBMM kabul haberi ve parti açıklaması okundu.',passage_ids=json.dumps(pids[1:])))
for role in ('tbmm','emep'):
 v='0410-emep-constitution-meeting-'+role+'-v1';version=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==v);aid='0410-constitution-meeting-'+role+'-attempt'
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps(['Görüşmeye katılım ve açıklama'],ensure_ascii=False),inspected_at=now))
 records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=version['original_url'],relevance_reason='Anayasa görüşmesi ve açıklama',state='examined',attempt_ids=json.dumps([aid])))
 records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=version['original_url'],url=version['original_url'],result='examined',reason='Özgün görüşme haberi okundu; karar sonucu varsayılmadı.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='emep')
passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
 if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
 inspected=[passages[x] for x in sorted(ids)]
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program ve görüşmeye dair özgün kaynaklar okundu.',limitations='Görüşme anayasa değişikliği veya ortak kararın kabulü değildir.',result='reviewed',reason=kind+' / '+identity+' için ilgili kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets))
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('constitution-meeting-20240605-union-draft.json',package),('constitution-meeting-20240605-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('CONSTITUTION_MEETING_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
