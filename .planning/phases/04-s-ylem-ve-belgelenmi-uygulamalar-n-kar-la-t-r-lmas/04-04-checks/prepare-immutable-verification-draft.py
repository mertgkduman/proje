import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-selected-rows-draft.json').read_text())
keys={('0105-action-provinces','0105-provinces-p'),('0105-tbmm-statement','0105-tbmm-statement-p'),('0105-tbmm-statement','0105-tbmm-statement-detail-p')}
removed=[x for x in pkg['entries'] if x['kind']=='verification' and (x['values']['finding_id'],x['values']['passage_id']) in keys]
assert {(x['values']['finding_id'],x['values']['passage_id']) for x in removed}==keys
pkg['entries']=[x for x in pkg['entries'] if x not in removed]
(p/'package-immutable-verification-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
