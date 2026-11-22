import json
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-full-union-draft.json').read_text());review=json.loads((p/'full-union-verified-review-draft.json').read_text());fragment=json.loads((p/'membership-online-slice-draft.json').read_text())
fields={'document':['id'],'document_version':['id'],'archive_view':['version_id'],'passage':['id'],'source_attribution':['version_id'],'finding':['id'],'finding_evidence':['finding_id','passage_id'],'verification':['finding_id','passage_id'],'review':['id']}
def key(e):return (e['kind'],*(e['values'].get(k) for k in fields[e['kind']]))
seen={key(e):e for e in pkg['entries']}
for entry in fragment['entries']:
    ident=key(entry)
    if ident in seen:assert seen[ident]==entry,ident
    else:seen[ident]=entry;pkg['entries'].append(entry)
for kind,rows in fragment['practice_records'].items():
    present={json.dumps(row,sort_keys=True,ensure_ascii=False) for row in pkg['practice_records'][kind]}
    for row in rows:
        assert json.dumps(row,sort_keys=True,ensure_ascii=False) not in present
        pkg['practice_records'][kind].append(row)
review['practice_source_review']+=json.loads((p/'membership-online-review-draft.json').read_text())['practice_source_review']
keys=[(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']];assert len(keys)==len(set(keys))
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
(p/'package-membership-union-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n');(p/'membership-union-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('entries',len(pkg['entries']),'reviews',len(keys),'closure',len(pkg['practice_records']['practice_closure']))
