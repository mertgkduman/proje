import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, 'src')
import uygulamalar as rules

checks = Path(__file__).resolve().parent
working = Path('data/practices')
release = Path('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
party = 'emep'
topic = 'dis-politika'
case = '0410-tezkere-1310'
event = case + '-event'
relation = case + '-relation'
statement = case + '-statement'
candidate = case + '-candidate'


def read(path):
    return json.loads(path.read_bytes())


package = read(working / '04-emep.json')
review = read(working / '04-emep-review.json')
baseline = dict(events=72, relations=71)
entries, records = package['entries'], package['practice_records']
assert len(records['practice_event']) == baseline['events']
assert len(records['practice_relation']) == baseline['relations']
assert not any(row.get('common_event_key') == 'tbmm-27-5-11-3-1704-tezkere' for row in records['practice_event'])
assert not records['practice_closure']
new_sources = read(checks / 'tezkere-1310-source-draft.json')['entries']
entries.extend(new_sources)
source_passages = {
    row['values']['id']: row['values']
    for row in new_sources if row['kind'] == 'passage'
}
source_versions = {
    row['values']['id']: row['values']
    for row in new_sources if row['kind'] == 'document_version'
}


def add(table, **values):
    records[table].append(values)


def insert(table, **values):
    entries.append({'kind': table, 'values': values})


def finding(suffix, text, provenance, refs, heading, pair_id):
    ident = case + '-' + suffix
    insert('finding', id=ident, party_id=party, heading=heading, pair_id=pair_id,
           text=text, provenance=provenance, epistemic_type='claim')
    insert('review', id='review-' + ident, kind='finding', subject_id=ident,
           reviewer_kind='agent', reviewed_at=now, result='reviewed',
           reason='Özgün açıklama, birleşim tutanağı veya kararın ilgili bölümü incelendi.')
    for pid in refs:
        insert('finding_evidence', finding_id=ident, passage_id=pid, role='support')
        insert('verification', finding_id=ident, passage_id=pid, checked_at=now, result='confirmed',
               reason='İlgili kaynak pasajı bu bulgunun belgelediği ifadeyi veya işlemi içeriyor.')
    return ident


pids = {name: case + '-' + name + '-p' for name in (
    'party-scope', 'party-request', 'floor-opening', 'floor-procedure', 'floor-term',
    'floor-vote', 'registry-number', 'gazette-index-index', 'gazette-publication', 'gazette-term',
)}
statement_refs = [pids['party-scope'], pids['party-request']]
action_refs = [pids[key] for key in ('floor-opening', 'floor-term', 'floor-vote', 'registry-number', 'gazette-term')]
result_refs = [pids[key] for key in ('floor-vote', 'gazette-term', 'gazette-publication', 'gazette-index-index')]
summary = finding(
    'request-summary',
    'Selma Gürkan, 26 Ekim 2021 sabahı EMEP sitesinde yayımlanan açıklamada Irak ve Suriye tezkeresinin iki yıl daha uzatılmasına karşı çıktı ve Meclisteki partilere ret çağrısı yaptı.',
    'summary', statement_refs, 'Dış politika', statement,
)
quote = finding(
    'request-quote', source_passages[pids['party-request']]['exact'], 'quote',
    [pids['party-request']], 'Dış politika', statement,
)
result = finding(
    'decision-result',
    'TBMM Genel Kurulu, 26 Ekim 2021’de 3/1704 esas numaralı tezkereyi kabul etti. 1310 sayılı karar 28 Ekim’de yayımlandı. İzin süresi 30 Ekim 2021’den itibaren iki yıl uzatıldı.',
    'summary', result_refs, 'Belgelenmiş uygulamalar', case + '-decision-result',
)
explanation = finding(
    'comparison',
    'Gürkan’ın çağrısı ile Genel Kurulun kabulü aynı iki yıllık Irak ve Suriye tezkeresine ilişkin. Açıklama 09.22’de yayımlandı, birleşim 15.00’te açıldı ve başkan 18.23 arasından önce kabulü ilan etti. 1310 sayılı karar ve yayımlanma günü resmî belgelerde ayrı kayıtlı.',
    'summary', statement_refs + action_refs + [pids['gazette-publication']],
    'Belgelenmiş uygulamalar', case + '-comparison',
)

statement_scope = next(row['id'] for row in records['practice_scope_v2']
                       if row['topic_id'] == topic and row['research_kind'] == 'statement')
event_scope = next(row['id'] for row in records['practice_scope_v2']
                   if row['topic_id'] == topic and row['research_kind'] == 'event')
program = next(row for row in records['practice_statement'] if row['id'] == '0410-foreign-principles-statement')
add('practice_statement', id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at='2021-10-26T09:22:20+03:00',
    date_precision='instant', version_id=case + '-party-v1',
    period_basis='Özgün parti sayfasındaki yayın saati 09.22.20 +03 ve güncelleme saati 09.22.22 +03.',
    uncertainty_reason='Açıklamadaki çağrı, Genel Kurulda kayda geçmiş bir kişisel oy hakkında bilgi vermiyor.',
    comparison_row_id=program['comparison_row_id'])
add('practice_event', id=event, common_event_key='tbmm-27-5-11-3-1704-tezkere',
    event_at='2021-10-26', date_precision='day', date_unknown_reason=None,
    scope_context='27. dönem, 5. yasama yılı, 11. birleşim, 3/1704 ve 1310 sayılı karar',
    title='3/1704 Irak ve Suriye tezkeresinin kabulü',
    occurrence_basis='Genel Kurul başkanının 26 Ekim birleşimindeki kabul açıklaması ve 1310 sayılı karar.')
evidence = {
    'floor-opening': ('action', '26 Ekim birleşiminin 15.00 açılışı tutanakta kayıtlı.'),
    'floor-procedure': ('action', 'Görüşme usulü önerisinin ardından 3/1704 ayrı olarak okutuldu.'),
    'floor-term': ('action', '16 Ekim tarihli 3/1704, önceki iznin 30.10.2021’den itibaren iki yıl uzatılmasını istedi.'),
    'floor-vote': ('action', 'Başkan 3/1704 üzerindeki görüşmeleri bitirdi ve kabul edildiğini ilan etti.'),
    'registry-number': ('action', 'TBMM karar tablosu, 26.10.2021 ve 11. birleşim için 1310 numarasını kaydediyor.'),
    'gazette-index-index': ('result', '31642 sayılı Resmî Gazete fihristi 1310 sayılı kararı listeliyor.'),
    'gazette-publication': ('result', 'Özgün PDF başlığı 28 Ekim 2021 yayım tarihini ve 31642 sayısını gösteriyor.'),
    'gazette-term': ('result', 'Kararın son cümlesi 26 Ekim kabulünü ve 30 Ekim 2021’den itibaren iki yıllık süreyi kaydediyor.'),
}
bounds = 'Kesin kişisel oylar, sayısal oy toplamı ve yetkinin fiilî kullanımı bu kaynaklarda gösterilmiyor.'
for key, (stage, point) in evidence.items():
    pid = pids[key]
    add('practice_event_evidence', event_id=event, passage_id=pid, stage=stage,
        supported_point=point, concrete_basis=source_passages[pid]['section'],
        limitation=bounds, epistemic_type='claim')
    add('practice_evidence_assessment', event_id=event, passage_id=pid, stage=stage, basis_kind='document')
add('practice_relation', id=relation, statement_id=statement, event_id=event, party_id=party,
    topic_id=topic, scope_id=event_scope,
    comparability_reason='Açıklama ile 3/1704 aynı ülkelere ilişkin mevcut iznin iki yıl uzatılmasını konu alıyor.',
    target_finding_id=summary, result_finding_id=result, explanation_finding_id=explanation,
    temporal_context='26 Ekim sabahı parti yayını, öğleden sonra Genel Kurul işlemi, 28 Ekim yayımı, 30 Ekim süre başlangıcı.',
    authority_context='Selma Gürkan’ın parti açıklaması kamusal çağrıdır. 1310 sayılı karar TBMM Genel Kuruluna aittir.',
    uncertainty_reason=bounds)
add('practice_candidate', id=candidate, scope_id=event_scope, event_id=event, relation_id=relation,
    state='eligible', reason='Oylama öncesi ret çağrısı ve aynı tezkerenin kabulü özgün kaynaklarla tarih sırasına kondu.',
    passage_ids=json.dumps(action_refs))

for version, source in source_versions.items():
    scopes = (event_scope, statement_scope) if version == case + '-party-v1' else (event_scope,)
    sections = sorted({row['section'] for row in source_passages.values() if row['version_id'] == version})
    url = source['original_url']
    for scope in scopes:
        attempt = version + ('-statement-reading' if scope == statement_scope else '-event-reading')
        add('practice_scope_source', scope_id=scope, version_id=version,
            inspected_sections=json.dumps(sections, ensure_ascii=False), inspected_at=now)
        add('practice_attempt_v2', id=attempt, scope_id=scope, attempted_at=now, query=url, url=url,
            result='examined', reason='Özgün metin, yayın saati veya ilgili birleşim ve karar sayfaları okundu.',
            source_version_id=version)
        add('practice_lead', id='lead-' + attempt, scope_id=scope, url=url, state='examined',
            relevance_reason='3/1704 ve 1310 için partinin çağrısı, kabul, yayım veya süre kaydı.',
            attempt_ids=json.dumps([attempt]))

data = copy.deepcopy(read(release))
for entry in entries:
    rows = data.setdefault(entry['kind'], [])
    if entry['values'] not in rows:
        rows.append(entry['values'])
for table, rows in records.items():
    target = data.setdefault(table, [])
    target.extend(row for row in rows if row not in target)
rules.validate_practices(data)
targets = rules.practice_review_package_targets(
    data, records, {row['values']['id'] for row in entries if row['kind'] == 'passage'}, party_id=party,
)
passages = {row['id']: row for row in data['passage']}
reviews = list(review['practice_source_review'])
old_keys = {(row['subject_kind'], row['subject_id']) for row in reviews}
assert old_keys <= targets.keys()
points = {
    pids['party-scope']: 'Parti açıklaması Irak ve Suriye izni için iki yıllık uzatmayı tarif ediyor.',
    pids['party-request']: 'Selma Gürkan 26 Ekim 2021 sabahı tezkereye ret çağrısında bulundu.',
    **{pids[key]: point for key, (_, point) in evidence.items()},
}
for (kind, identity), (ids, _) in sorted(targets.items()):
    if (kind, identity) in old_keys:
        continue
    inspected = [passages[pid] for pid in sorted(ids)]
    refs = sorted(set(ids).intersection(points))
    assert refs, (kind, identity)
    reviews.append(dict(
        subject_kind=kind, subject_id=identity, reviewer_kind='agent', reviewed_at=now,
        source_version_ids=json.dumps(sorted({row['version_id'] for row in inspected})),
        passage_ids=json.dumps([row['id'] for row in inspected]),
        inspected_sections=json.dumps(sorted({row['section'] for row in inspected}), ensure_ascii=False),
        supported_claim=' '.join(points[pid] for pid in refs), limitations=bounds, result='reviewed',
        reason=f'{kind} kaydındaki {identity} hedefi için ilgili özgün pasajlar okundu.',
    ))
rules.validate_practice_source_review(data, reviews, party_id=party, target_keys=set(targets))
refs = [{key: row[key] for key in ('subject_kind', 'subject_id')} for row in reviews]
package['source_review_refs'] = refs
review['practice_source_review'] = reviews
review['source_review_refs'] = refs
for suffix, payload in (('draft', package), ('review-draft', review)):
    with (checks / f'tezkere-1310-{suffix}.json').open('x') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
print('TEZKERE_1310_SEMANTIC_OK', len(reviews), len(records['practice_event']), len(records['practice_relation']))
