import json
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
pkg = json.loads((p/'package-samsun-attribution-draft.json').read_text())
review = json.loads((p/'samsun-reply-review-draft.json').read_text())
fragments = [
    ('union-slice-draft.json', 'union-review-slice-draft.json'),
    ('child-labor-slice-draft.json', 'child-labor-review-slice-draft.json'),
    ('child-labor-4553-slice-draft.json', 'child-labor-4553-review-draft.json'),
    ('child-labor-question-slice-draft.json', 'child-labor-question-review-draft.json'),
    ('housing-extra-slices-draft.json', 'housing-extra-review-draft.json'),
]
fields = {'document':['id'], 'document_version':['id'], 'archive_view':['version_id'], 'passage':['id'], 'source_attribution':['version_id'], 'finding':['id'], 'finding_evidence':['finding_id','passage_id'], 'verification':['finding_id','passage_id'], 'review':['id']}
def key(entry):
    return (entry['kind'], *(entry['values'].get(k) for k in fields[entry['kind']]))
seen = {key(x):x for x in pkg['entries']}
elder = json.loads((p/'elder-care-slice-draft.json').read_text())
elder_sources = json.loads((p/'elder-care-source-records.json').read_text())
work = [(json.loads((p/filename).read_text()), json.loads((p/reviewname).read_text())['practice_source_review']) for filename, reviewname in fragments]
work.append((dict(entries=elder_sources['entries']+elder['additional_entries'], practice_records=elder['practice_records']), elder['practice_source_review']))
for fragment, source_reviews in work:
    for entry in fragment['entries']:
        identity = key(entry)
        if identity in seen:
            assert seen[identity] == entry, identity
        else:
            seen[identity] = entry
            pkg['entries'].append(entry)
    for kind, rows in fragment['practice_records'].items():
        existing = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in pkg['practice_records'][kind]}
        for row in rows:
            serialized = json.dumps(row, sort_keys=True, ensure_ascii=False)
            assert serialized not in existing, (kind, row)
            pkg['practice_records'][kind].append(row)
            existing.add(serialized)
    review['practice_source_review'] += source_reviews
keys = [(r['subject_kind'], r['subject_id']) for r in review['practice_source_review']]
assert len(keys) == len(set(keys)), 'duplicate review subject'
review['source_review_refs'] = [dict(subject_kind=r['subject_kind'], subject_id=r['subject_id']) for r in review['practice_source_review']]
(p/'package-reconciled-draft.json').write_text(json.dumps(pkg, ensure_ascii=False, indent=2)+'\n')
(p/'reconciled-review-draft.json').write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n')
print('entries', len(pkg['entries']), 'reviews', len(keys))
