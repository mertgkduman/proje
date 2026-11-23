"""Inspect current party drafts for shared-event evidence and metadata differences."""

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

data = Path('data')
slugs = ('yeni-parti','tip','dem','iyi','yeni-yol','dbp','emep','saadet','demokrat')
base_id = json.loads((data/'current.json').read_bytes())['release_id']
base = json.loads((data/'releases'/base_id/'records.json').read_bytes())
groups = defaultdict(list)
package_receipts = {}
for party in slugs:
    path = data/'practices'/f'04-{party}.json'
    raw = path.read_bytes()
    package = json.loads(raw)
    assert package['base_release'] == base_id and package['party_id'] == party
    records = package['practice_records']
    tables = {}
    for name in ('passage','document_version'):
        tables[name] = {row['id']:row for row in base[name]}
        tables[name].update({entry['values']['id']:entry['values'] for entry in package['entries']
                             if entry['kind']==name})
    proof = defaultdict(list)
    for row in records['practice_event_evidence']:
        passage = tables['passage'][row['passage_id']]
        version = tables['document_version'][passage['version_id']]
        proof[row['event_id']].append(dict(passage_id=passage['id'],version_id=version['id'],
            source_sha256=version['sha256'],source=version['final_url'],stage=row['stage'],
            section=passage['section'],claim=row['supported_point']))
    candidate_proof = defaultdict(dict)
    for row in records['practice_candidate']:
        if not row['event_id']:
            continue
        for passage_id in json.loads(row['passage_ids']):
            passage = tables['passage'][passage_id]
            version = tables['document_version'][passage['version_id']]
            candidate_proof[row['event_id']][passage_id] = dict(
                passage_id=passage_id, source_sha256=version['sha256'],
                source=version['final_url'], section=passage['section'])
    refs = {(row['subject_kind'],row['subject_id']) for row in package['source_review_refs']}
    embedded = {(row['subject_kind'],row['subject_id']) for row in records.get('practice_source_review', [])}
    review_path = path.with_name(f'04-{party}-review.json')
    review = json.loads(review_path.read_bytes())
    companion = {(row['subject_kind'],row['subject_id']) for row in review['practice_source_review']}
    assert refs <= companion
    package_receipts[party] = dict(package_sha256=sha256(raw).hexdigest(),
        companion_review_sha256=sha256(review_path.read_bytes()).hexdigest(),events=len(records['practice_event']),
        relations=len(records['practice_relation']),closures=len(records['practice_closure']),
        external_review_ref_count=len(refs-embedded))
    for event in records['practice_event']:
        key = event['common_event_key']
        if key:
            groups[key].append(dict(party=party,event=event,evidence=proof[event['id']],
                candidate_evidence=list(candidate_proof[event['id']].values())))

shared = []
for key, members in sorted(groups.items()):
    if len(members) < 2:
        continue
    digests = [{row['source_sha256'] for row in member['evidence']} for member in members]
    candidate_digests = [{row['source_sha256'] for row in member['candidate_evidence']} for member in members]
    shared.append(dict(candidate_key=key, party_records=members,
        common_evidence_sha256=sorted(set.intersection(*digests)),
        common_candidate_evidence_sha256=sorted(set.intersection(*candidate_digests)),
        differing_fields=[field for field in sorted(members[0]['event']) if field!='id' and
                           len({member['event'][field] for member in members})>1]))
print(json.dumps(dict(base_release=base_id,packages=package_receipts,common_event_candidates=shared),
                 ensure_ascii=False,indent=2))
