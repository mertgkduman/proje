import copy
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, 'src')
import uygulamalar as rules

D = Path(__file__).parent
read = lambda p: json.loads(Path(p).read_text())
package = read(D / 'migration-2134-union-draft.json')
previous = read(D / 'migration-2134-union-review-draft.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries, records = package['entries'], package['practice_records']
entries.extend(read(D / 'earthquake-workshop-2025-source-draft.json')['entries'])
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
scope = next(x['id'] for x in records['practice_scope_v2'] if x['party_id'] == 'emep' and x['topic_id'] == 'barinma-konut' and x['research_kind'] == 'event')

def add(table, **values):
    entries.append(dict(kind=table, values=values))

eid = '0410-earthquake-workshop-2025-event'
rid = '0410-earthquake-workshop-2025-relation'
fid = '0410-earthquake-workshop-2025-explanation'
program = '0309-emep-program-057-0-passage'
report = '0410-emep-earthquake-workshop-2025-report-p'
news = '0410-emep-earthquake-workshop-2025-news-p'
add('finding', id=fid, party_id='emep', heading='Belgelenmiş uygulamalar', pair_id=fid, text='Program parasız konut hakkını önerir. EMEP, deprem bölgesindeki sorunları tartışmak üzere Gaziantep’te bir çalıştay düzenledi; ikinci yıl raporunda bu buluşmanın ortak çalışma önerilerini aktardı.', provenance='summary', epistemic_type='claim')
add('review', id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program, parti raporunun toplantı bölümü ve ayrı gazete haberi okundu; toplantı önerileri sonuç olarak sunulmadı.')
for passage in (program, report, news):
    add('finding_evidence', finding_id=fid, passage_id=passage, role='support')
    add('verification', finding_id=fid, passage_id=passage, checked_at=now, result='confirmed', reason='İlgili özgün program, parti raporu veya gazete haberi okundu.')
records['practice_event'].append(dict(id=eid, common_event_key='emep-gaziantep-deprem-calistayi-2025', event_at=None, date_precision='unknown', date_unknown_reason='Haber gerçekleşmeyi 2 Şubatta bildirir, ancak toplantı gününü açıkça belirtmez; 1 Şubat duyurusu plan tarihidir.', scope_context='Gaziantep deprem bölgesi hakları ve yeniden inşa çalıştayı', title='Gaziantep’te deprem sorunları çalıştayı', occurrence_basis='2 Şubat 2025 Gaziantep Ekspres haberi ve parti raporu toplantının yapıldığını bildirir.'))
records['practice_event_evidence'].append(dict(event_id=eid, passage_id=news, supported_point='Gaziantep Ekspres, EMEP’in Gaziantep’te deprem sorunlarına ilişkin çalıştay düzenlediğini bildirir.', stage='action', concrete_basis='Samet Koçum imzalı 2 Şubat 2025 haberi.', limitation='Toplantının kesin günü haberde açık değildir; tartışılan taleplerin gerçekleştiği gösterilmez.', epistemic_type='claim'))
records['practice_evidence_assessment'].append(dict(event_id=eid, passage_id=news, stage='action', basis_kind='document'))
records['practice_relation'].append(dict(id=rid, statement_id='0410-earthquake-housing-statement', event_id=eid, party_id='emep', topic_id='barinma-konut', scope_id=scope, comparability_reason='Program parasız konut hakkını önerir; çalıştay deprem bölgesindeki barınma ve yeniden inşa sorunlarını tartışır.', target_finding_id='0309-emep-program-057-0-summary', result_finding_id=None, explanation_finding_id=fid, temporal_context='2019 program yayını ile 2025 çalıştay haberi ve raporu ayrı tarihlidir.', authority_context='Çalıştay EMEP tarafından düzenlenmiştir; gazete gerçekleşmeyi, parti raporu önerileri aktarır.', uncertainty_reason='Kesin toplantı günü, önerilerin sonradan uygulanması ve programın ara dönem yürürlüğü bu kaynaklardan kesinleşmez.'))
records['practice_candidate'].append(dict(id='0410-earthquake-workshop-2025-candidate', scope_id=scope, event_id=eid, relation_id=rid, state='eligible', reason='Parti raporunun toplantı bölümü ve bağımsız gazeteci haberi okundu.', passage_ids=json.dumps([news])))
for role, section in [('report', 'İkinci yıl deprem raporu'), ('news', 'Gaziantep deprem çalıştayı haberi')]:
    version_id = '0410-emep-earthquake-workshop-2025-'+role+'-v1'
    version = next(e['values'] for e in entries if e['kind'] == 'document_version' and e['values']['id'] == version_id)
    aid = '0410-earthquake-workshop-2025-'+role+'-attempt'
    records['practice_scope_source'].append(dict(scope_id=scope, version_id=version_id, inspected_sections=json.dumps([section], ensure_ascii=False), inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid, scope_id=scope, url=version['original_url'], relevance_reason=section, state='examined', attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid, scope_id=scope, attempted_at=now, query=version['original_url'], url=version['original_url'], result='examined', reason='Özgün rapor ve ayrı haber okundu; kesin gün ve uygulama sonucu açık.', source_version_id=version_id))

data = copy.deepcopy(base)
for entry in entries:
    if entry['values'] not in data.setdefault(entry['kind'], []):
        data[entry['kind']].append(entry['values'])
for table, rows in records.items():
    data.setdefault(table, []).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets = rules.practice_review_package_targets(data, records, {x['passage_id'] for x in records['practice_event_evidence']}, party_id='emep')
passages = {p['id']: p for p in data['passage']}
old = {(r['subject_kind'], r['subject_id']): r for r in previous['practice_source_review']}
reviews = []
for (kind, identity), (ids, parties) in sorted(targets.items()):
    if (kind, identity) in old:
        reviews.append(old[(kind, identity)])
        continue
    inspected = [passages[x] for x in sorted(ids)]
    reviews.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent', reviewed_at=now, source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})), passage_ids=json.dumps([p['id'] for p in inspected]), inspected_sections=json.dumps(sorted({p['section'] for p in inspected}), ensure_ascii=False), supported_claim='Program, parti raporu ve bağımsız haberin ilgili pasajları okundu.', limitations='Toplantıdaki önerilerin uygulanması ve kesin gün bilinmiyor.', result='reviewed', reason=kind+' / '+identity+' kaynak pasajları okundu.'))
rules.validate_practice_source_review(data, reviews, party_id='emep', target_keys=set(targets))
refs = [{k:r[k] for k in ('subject_kind', 'subject_id')} for r in reviews]
package['source_review_refs'] = refs
for name, obj in [('earthquake-workshop-2025-union-draft.json', package), ('earthquake-workshop-2025-union-review-draft.json', dict(practice_source_review=reviews, source_review_refs=refs))]:
    with (D/name).open('x') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')
print('WORKSHOP_SEMANTIC_PASS', len(reviews), 'EVENTS', len(records['practice_event']), 'RELATIONS', len(records['practice_relation']))
