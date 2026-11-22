import json
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-group-management-reconciled-draft.json').read_text());review=json.loads((p/'group-management-reconciled-review-draft.json').read_text());coverage=json.loads((p/'group-coverage-draft.json').read_text())['practice_records']
scope=next(x['id'] for x in coverage['practice_scope_v2'] if x['research_kind']=='event')
relations={'0404-tbmm-grup-secim-0724-iliski-id','0404-tbmm-grup-yonetim-0728-iliski-id'}
found=0
for row in pkg['practice_records']['practice_relation']:
    if row['id'] in relations:
        assert row['scope_id'] is None;row['scope_id']=scope;found+=1
assert found==2
for kind,rows in coverage.items():
    present={json.dumps(row,sort_keys=True,ensure_ascii=False) for row in pkg['practice_records'][kind]}
    for row in rows:
        assert json.dumps(row,sort_keys=True,ensure_ascii=False) not in present
        pkg['practice_records'][kind].append(row)
(p/'package-group-scoped-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
(p/'group-scoped-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('scope',scope,'attempts',len(coverage['practice_attempt_v2']),'candidates',len(coverage['practice_candidate']),'closures',len(pkg['practice_records']['practice_closure']))
