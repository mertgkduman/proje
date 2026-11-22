import json
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
pkg = json.loads((p/'package-reconciled-verification-draft.json').read_text())
review = json.loads((p/'reconciled-review-draft.json').read_text())
fields = {'document':['id'], 'document_version':['id'], 'archive_view':['version_id'], 'passage':['id'], 'source_attribution':['version_id'], 'finding':['id'], 'finding_evidence':['finding_id','passage_id'], 'verification':['finding_id','passage_id'], 'review':['id']}
def key(entry): return (entry['kind'], *(entry['values'].get(k) for k in fields[entry['kind']]))
seen = {key(x):x for x in pkg['entries']}
for filename, reviewname in [('disability-access-slice-draft.json','disability-access-review-draft.json'), ('violence-slices-draft.json','violence-review-draft.json')]:
    fragment = json.loads((p/filename).read_text())
    for entry in fragment['entries']:
        ident = key(entry)
        if ident in seen: assert seen[ident] == entry, ident
        else: seen[ident] = entry; pkg['entries'].append(entry)
    for kind, rows in fragment['practice_records'].items():
        present = {json.dumps(row, sort_keys=True, ensure_ascii=False) for row in pkg['practice_records'][kind]}
        for row in rows:
            assert json.dumps(row, sort_keys=True, ensure_ascii=False) not in present
            pkg['practice_records'][kind].append(row)
    review['practice_source_review'] += json.loads((p/reviewname).read_text())['practice_source_review']
keys = [(r['subject_kind'],r['subject_id']) for r in review['practice_source_review']]
assert len(keys) == len(set(keys))
review['source_review_refs'] = [dict(subject_kind=r['subject_kind'],subject_id=r['subject_id']) for r in review['practice_source_review']]
(p/'package-reconciled-next-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
(p/'reconciled-next-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('entries',len(pkg['entries']),'reviews',len(keys),'closure',len(pkg['practice_records']['practice_closure']))
