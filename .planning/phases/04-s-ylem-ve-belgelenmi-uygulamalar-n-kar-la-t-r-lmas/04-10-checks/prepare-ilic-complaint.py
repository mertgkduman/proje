import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
import uygulamalar as rules

D = Path(__file__).parent
read = lambda p: json.loads(Path(p).read_text())
package = read(D/'earthquake-11963-union-draft.json')
previous = read(D/'earthquake-11963-union-review-draft.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries, records = package['entries'], package['practice_records']
entries.extend(read(D/'ilic-complaint-20240315-source-draft.json')['entries'])
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
scope = next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='doga-ekoloji' and x['research_kind']=='event')
def add(table, **values): entries.append(dict(kind=table, values=values))
eid, rid, fid = '0410-ilic-complaint-20240315-event', '0410-ilic-complaint-20240315-relation', '0410-ilic-complaint-20240315-explanation'
add('finding', id=fid, party_id='emep', heading='Belgelenmiş uygulamalar', pair_id=fid, text='Program toprak ve suyun korunmasını önerir. EMEP 15 Mart 2024’te İliç madenindeki kayma hakkında şirket ve ilgili kamu görevlileri için suç duyurusunda bulundu; parti madenin kapatılmasını ve sorumluların yargılanmasını istedi.', provenance='summary', epistemic_type='claim')
add('review', id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program, parti duyurusu ve Cumhuriyet haberi okundu; başvuru ve yargısal sonuç ayrıldı.')
pids=['0309-emep-program-041-0-passage', '0410-emep-ilic-complaint-party-p', '0410-emep-ilic-complaint-news-p']
for p in pids:
    add('finding_evidence', finding_id=fid, passage_id=p, role='support')
    add('verification', finding_id=fid, passage_id=p, checked_at=now, result='confirmed', reason='Program ve haberin ilgili metni okundu; suç isnadı karar olarak sunulmadı.')
records['practice_event'].append(dict(id=eid, common_event_key='emep-ilic-suc-duyurusu-2024-03-15', event_at='2024-03-15', date_precision='day', date_unknown_reason=None, scope_context='EMEP’in İliç madenindeki kayma hakkında suç duyurusu', title='EMEP’in İliç için suç duyurusu', occurrence_basis='15 Mart tarihli Cumhuriyet haberi başvuruyu İstanbul Çağlayan Adliyesinde belgeliyor.'))
p='0410-emep-ilic-complaint-news-p'
records['practice_event_evidence'].append(dict(event_id=eid, passage_id=p, supported_point='Cumhuriyet, Aslanın İliç için kamu görevlileri hakkında suç duyurusunu 15 Martta yaptığını aktarıyor.', stage='action', concrete_basis='Bağımsız 15 Mart 2024 tarihli haber.', limitation='Suç duyurusu soruşturma veya mahkeme sonucu değildir.', epistemic_type='claim'))
records['practice_evidence_assessment'].append(dict(event_id=eid, passage_id=p, stage='action', basis_kind='document'))
records['practice_relation'].append(dict(id=rid, statement_id='0410-climate-ecology-statement', event_id=eid, party_id='emep', topic_id='doga-ekoloji', scope_id=scope, comparability_reason='Programın doğal varlıkların korunması önerisi ile İliçte çevre ve işçi güvenliği için suç duyurusu aynı çevre koruma alanındadır.', target_finding_id='0309-emep-program-041-0-summary', result_finding_id=None, explanation_finding_id=fid, temporal_context='2019 program yayını ve 15 Mart 2024 duyurusu ayrı tarihlerdir.', authority_context='Başvuru parti adına Aslan ve vekillerine, haber Cumhuriyete aittir.', uncertainty_reason='Programın ara sürümleri ve olay tarihindeki kesintisiz yürürlüğü kesinleştirilmedi; suç duyurusu sonucu bilinmiyor. Parti dilekçesinde kayma yılı bir yerde 2023, diğer yerlerde 2024 geçer.'))
records['practice_candidate'].append(dict(id='0410-ilic-complaint-20240315-candidate', scope_id=scope, event_id=eid, relation_id=rid, state='eligible', reason='Parti duyurusu ve tarihli bağımsız haber okundu.', passage_ids=json.dumps(pids[1:])))
for role in ('party', 'news'):
    v='0410-emep-ilic-complaint-'+role+'-v1'; version=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==v); aid='0410-ilic-complaint-'+role+'-attempt'
    records['practice_scope_source'].append(dict(scope_id=scope, version_id=v, inspected_sections=json.dumps(['Suç duyurusu'], ensure_ascii=False), inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid, scope_id=scope, url=version['original_url'], relevance_reason='İliç başvurusu', state='examined', attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid, scope_id=scope, attempted_at=now, query=version['original_url'], url=version['original_url'], result='examined', reason='Duyuru ve haber okundu; sonuç varsayılmadı.', source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
    if e['values'] not in data.setdefault(e['kind'], []): data[e['kind']].append(e['values'])
for table, rows in records.items(): data.setdefault(table, []).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data, records, {x['passage_id'] for x in records['practice_event_evidence']}, party_id='emep')
passages={p['id']:p for p in data['passage']}; old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']}; reviews=[]
for (kind, identity), (ids, parties) in sorted(targets.items()):
    if (kind,identity) in old: reviews.append(old[(kind,identity)]); continue
    inspected=[passages[x] for x in sorted(ids)]
    reviews.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent', reviewed_at=now, source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})), passage_ids=json.dumps([p['id'] for p in inspected]), inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False), supported_claim='Program ve İliç duyurusu ile 15 Mart haberi okundu.', limitations='Duyuru suçlamadır; yargısal sonuç ve programa ait ara sürümler ayrıca doğrulanmadı.', result='reviewed', reason=kind+' / '+identity+' için ilgili kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets))
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs
for name,obj in [('ilic-complaint-20240315-union-draft.json',package),('ilic-complaint-20240315-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('ILIC_COMPLAINT_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
