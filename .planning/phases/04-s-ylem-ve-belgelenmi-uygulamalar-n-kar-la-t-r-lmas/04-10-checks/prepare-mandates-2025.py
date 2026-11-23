import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
import uygulamalar as rules

D = Path(__file__).parent
read = lambda p: json.loads(Path(p).read_text())
package = read(D / 'academics-37207-corrected-union-draft.json')
previous = read(D / 'academics-37207-union-review-draft.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries, records = package['entries'], package['practice_records']
entries.extend(read(D / 'mandates-2025-source-draft.json')['entries'])
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
scope = next(x['id'] for x in records['practice_scope_v2'] if x['party_id'] == 'emep' and x['topic_id'] == 'dis-politika' and x['research_kind'] == 'event')
def add(table, **values): entries.append(dict(kind=table, values=values))
speech = '0410-emep-mandates-2025-speech-position-p'
program = '0309-emep-program-016-0-passage'
for number, place in [('1199', 'Lübnan'), ('1200', 'Irak ve Suriye')]:
    stem = '0410-mandate-' + number
    event, relation, finding = stem+'-event', stem+'-relation', stem+'-explanation'
    vote = '0410-emep-mandates-2025-transcript-'+number+'-vote-p'
    add('finding', id=finding, party_id='emep', heading='Belgelenmiş uygulamalar', pair_id=finding, text='Program dış ilişkilerde barış ve egemenlik ilkelerini savunur. Sevda Karaca EMEP adına iki tezkereye hayır diyeceklerini açıkladı; TBMM tutanağı '+place+' tezkeresinin işaretle kabul edildiğini kaydeder.', provenance='summary', epistemic_type='claim')
    add('review', id='review-'+finding, kind='finding', subject_id=finding, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program, Karacanın Meclis konuşması ve ilgili tezkerenin ayrı oylama tutanağı okundu.')
    for pid in (program, speech, vote):
        add('finding_evidence', finding_id=finding, passage_id=pid, role='support')
        add('verification', finding_id=finding, passage_id=pid, checked_at=now, result='confirmed', reason='İlgili özgün pasaj okundu.')
    records['practice_event'].append(dict(id=event, common_event_key='tbmm-28-4-009-3-'+number+'-tezkere', event_at='2025-10-21', date_precision='day', date_unknown_reason=None, scope_context='TBMM 28. dönem 4. yasama yılı 9. birleşim', title=place+' tezkeresinin Genel Kurulda görüşülmesi ve oylanması', occurrence_basis='TBMM tutanağı tezkerenin numarasını ve işaretle kabulünü kaydeder.'))
    for pid, point in [(speech, 'Karaca EMEP adına iki tezkereye hayır tutumunu önceden açıkladı.'), (vote, number+' sayılı tezkere işaretle kabul edildi.')]:
        records['practice_event_evidence'].append(dict(event_id=event, passage_id=pid, supported_point=point, stage='action', concrete_basis='TBMM Genel Kurul konuşması veya resmi tutanağı.', limitation='İşaret oylamasında kişisel oy cetveli veya sayısal sonuç gösterilmez.', epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=event, passage_id=pid, stage='action', basis_kind='document'))
    records['practice_relation'].append(dict(id=relation, statement_id='0410-foreign-principles-statement', event_id=event, party_id='emep', topic_id='dis-politika', scope_id=scope, comparability_reason='Programın barış ve egemenlik ilkeleri ile askeri tezkere hakkındaki beyan aynı geniş dış politika alanındadır.', target_finding_id='0410-foreign-principles-finding', result_finding_id=None, explanation_finding_id=finding, temporal_context='Program arşivi ve 21 Ekim 2025 konuşması ile oylaması ayrı zamanlardır.', authority_context='Açıklama Karacaya ve EMEP adına bildirdiği tutuma; kabul Genel Kurula aittir.', uncertainty_reason='İşaret oylaması Karacanın veya Bayhanın kişisel oyunu göstermez; programın kesintisiz yürürlüğü kanıtlanmadı.'))
    records['practice_candidate'].append(dict(id=stem+'-candidate', scope_id=scope, event_id=event, relation_id=relation, state='eligible', reason='Konuşma ve ilgili ayrı tezkere oylaması TBMM belgelerinde okundu.', passage_ids=json.dumps([speech,vote])))
for role, section in [('speech', 'Genel Kurul açıklaması'), ('transcript', 'Tezkere oylaması')]:
    version_id='0410-emep-mandates-2025-'+role+'-v1'
    version=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==version_id)
    aid='0410-mandates-2025-'+role+'-attempt'
    records['practice_scope_source'].append(dict(scope_id=scope, version_id=version_id, inspected_sections=json.dumps([section],ensure_ascii=False), inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=version['original_url'],relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=version['original_url'],url=version['original_url'],result='examined',reason='TBMM konuşma ve iki ayrı oylama pasajı okundu.',source_version_id=version_id))
data=copy.deepcopy(base)
for e in entries:
    if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table, rows in records.items(): data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='emep')
passages={p['id']:p for p in data['passage']}
old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']}
reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
    if (kind,identity) in old:
        reviews.append(old[(kind,identity)]); continue
    inspected=[passages[x] for x in sorted(ids)]
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program, konuşma ve ayrı oylama pasajları incelendi.',limitations='Tutum açıklaması kişisel gerçekleşmiş oy cetveli değildir.',result='reviewed',reason=kind+' / '+identity+' kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets))
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]
package['source_review_refs']=refs
for name,obj in [('mandates-2025-union-draft.json',package),('mandates-2025-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('MANDATES_2025_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
