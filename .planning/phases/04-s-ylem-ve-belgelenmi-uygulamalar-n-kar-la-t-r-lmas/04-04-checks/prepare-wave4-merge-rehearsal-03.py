"""Freeze reviewed party inputs and decisions for a third isolated preview."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from uygulama_birlestirme import _json, merge_packages
from uygulamalar import _digest

checks = Path(__file__).resolve().parent
data = Path('data')
source_commit = sys.argv[1]
audit = json.loads((checks / 'wave4-common-event-audit-07.json').read_bytes())
previous = json.loads((checks / 'wave4-merge-rehearsal-02-decisions.json').read_bytes())
previous_by_key = {row['id']: row for row in previous['decisions']}
inventory = json.loads((data / 'practices/04-inventory.json').read_bytes())
base = json.loads((data / 'releases' / inventory['base_release'] / 'records.json').read_bytes())
assert audit['base_release'] == inventory['base_release']
new_same = {
    'tbmm-28-5-012-yeni-yol-genel-gorusme-fon-gundem': (
        4, 3, 'Dört grubun katkıları aynı 8/153 gündem işlemiyle ilgili. İmzalı başvuru, esas kaydı ve 3 Kasım tam tutanağı ortak.'),
    'tbmm-28-5-012-10-4961-gundem': (
        4, 3, 'Dört grubun katkıları aynı 10/4961 gündem işlemiyle ilgili. İmzalı önerge, esas kaydı ve 3 Kasım tutanağı ortak.'),
    'tbmm-28-4-106-10-4314-gundem': (
        3, 3, 'Üç grubun katkıları 24 Haziran 106. Birleşimdeki ilk grup gündem önerisine bağlı. İmzalı 10/4314, esas ve birleşim tutanağı ortak.'),
    'tbmm-28-4-108-10-4343-gundem': (
        3, 1, '1 Temmuz 108. Birleşimde iki yetersayı oylaması ve üçüncü oylamadaki ret aynı 10/4343 ön görüşme isteğine ait.'),
    'tbmm-28-3-104-2-2927-iklim-kanunu': (
        2, 2, '2 Temmuz 104. Birleşimde 198 sıra sayılı teklifin tümünün kesin açık oy cetveli, 2/2927 ve 7552 aynı oylamayı gösteriyor.'),
}

def digest(raw):
    return sha256(raw).hexdigest()

def committed(path):
    return subprocess.check_output(['git', 'show', f'{source_commit}:{path}'])

inputs, envelopes, stages = [], {}, {}
for party, expected in audit['packages'].items():
    package_raw = committed(f'data/practices/04-{party}.json')
    review_raw = committed(f'data/practices/04-{party}-review.json')
    assert digest(package_raw) == expected['package_sha256']
    assert digest(review_raw) == expected['companion_review_sha256']
    package = json.loads(package_raw)
    stages[party] = package['stage']
    package['stage'] = 'partial'
    records = package['practice_records']
    for row in records['practice_contract']:
        row['stage'] = 'partial'
    records['practice_source_review'] = json.loads(review_raw)['practice_source_review']
    records['practice_source_review_contract'] = [{'version': 1}]
    raw = _json(package).encode()
    envelopes[party] = digest(raw)
    inputs.append(dict(identity=party, raw=raw))

decisions = []
for candidate in audit['common_event_candidates']:
    key = candidate['candidate_key']
    members = candidate['party_records']
    previous_row = previous_by_key.get(key)
    event_refs = [
        dict(event_id=member['event']['id'], input_package_sha256=envelopes[member['party']])
        for member in members
    ]
    if key in new_same:
        assert not candidate['differing_fields']
        member_count, source_count, reason = new_same[key]
        assert len(members) == member_count and len(candidate['common_evidence_sha256']) == source_count
        shared_digests = set(candidate['common_evidence_sha256'])
        source_passages = sorted({
            row['passage_id'] for member in members for row in member['evidence']
            if row['source_sha256'] in shared_digests
        })
        row = dict(id=key, candidate_keys=[key], decision='same',
            canonical_event_id=members[0]['event']['id'], source_passage_ids=source_passages,
            overlap_reason=reason, reviewer_kind='agent',
            reviewed_at=datetime.now(timezone.utc).isoformat())
    else:
        assert previous_row is not None
        assert {ref['event_id'] for ref in previous_row['event_refs']} == {ref['event_id'] for ref in event_refs}
        row = {key: value for key, value in previous_row.items() if key != 'event_refs'}
    row['event_refs'] = event_refs
    decisions.append(row)
assert len(decisions) == 20 and sum(row['decision'] == 'same' for row in decisions) == 8
decision_bytes = (_json(dict(decisions=decisions, input_digests=envelopes,
    inventory_digest=_digest(inventory), version=1)) + '\n').encode()
output = merge_packages(inventory, inputs, decision_bytes,
    decisions_sha256=digest(decision_bytes), base_records=base)
mirror = merge_packages(inventory, inputs[::-1], decision_bytes,
    decisions_sha256=digest(decision_bytes), base_records=base)
assert output == mirror
records = output['payload']['practice_records']
counts = (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure']))
input_events = sum(row['events'] for row in audit['packages'].values())
input_relations = sum(row['relations'] for row in audit['packages'].values())
reductions = sum(len(row['event_refs']) - 1 for row in decisions if row['decision'] == 'same')
assert counts == (input_events - reductions, input_relations, 0), counts
receipt = dict(git_commit=source_commit, original_packages=audit['packages'], original_stages=stages,
    isolated_stage='partial', isolated_envelope_sha256=envelopes, decisions_sha256=digest(decision_bytes),
    output_sha256=digest(_json(output).encode()), input_events=input_events, input_relations=input_relations,
    merged_events=counts[0], merged_relations=counts[1], closure_count=counts[2],
    event_aliases=len(output['aliases']), review_origins=len(output['review_origins']),
    same_keys=sorted(row['id'] for row in decisions if row['decision']=='same'),
    unresolved_candidates=sum(row['decision']=='unresolved' for row in decisions))
with (checks / 'wave4-merge-rehearsal-03-decisions.json').open('xb') as file:
    file.write(decision_bytes)
with (checks / 'wave4-merge-rehearsal-03.json').open('x') as file:
    file.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print('REHEARSAL_03_INPUTS_AND_ORDER_OK', counts, receipt['output_sha256'], flush=True)
