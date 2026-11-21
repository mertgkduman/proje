import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-tbmm-legacy-draft.json').read_text())
mapping={
 '0404-samsun-soz-statement':'04-03-v3-0303-epm-fifth-kongrede-soz-y-row',
 '0404-yargi-program-statement':'04-03-v3-0303-epm-program-detail3-yargi-bagimsizligi-row',
 '0404-cocuk-haklari-statement':'04-03-v3-0303-epm-program-detail-cocuk-haklari-row',
 '0404-aile-politikalari-statement':'04-03-v3-0303-epm-program-aile-politikalari-row',
}
seen=set()
for s in pkg['practice_records']['practice_statement']:
    if s['id'] in mapping:
        assert '04-03-v3-'+s['comparison_row_id']==mapping[s['id']]
        s['comparison_row_id']=mapping[s['id']];seen.add(s['id'])
assert seen==set(mapping)
(p/'package-selected-rows-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
