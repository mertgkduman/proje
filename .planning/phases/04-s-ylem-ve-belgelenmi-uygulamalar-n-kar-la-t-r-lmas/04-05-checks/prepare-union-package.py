import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
base=json.loads((p/'policy-tracer-checked-draft.json').read_text()); delta=json.loads((p/'union-slice-draft.json').read_text())
markers={'practice_contract','practice_variant_contract','practice_evidence_contract','practice_coverage_contract'}
records={k:(v if k in markers else []) for k,v in base['practice_records'].items()}
records['practice_evidence_assessment']=[v for v in base['practice_records']['practice_evidence_assessment'] if v['event_id']=='tracer-cesme']
for key,values in delta['practice_records'].items():records.setdefault(key,[]).extend(values)
package=dict(contract_version=1,base_release=base['base_release'],party_id='tip',taxonomy_version=4,stage='partial',entries=delta['entries'],practice_records=records,scope_inventory=base['scope_inventory'],tranches=[],source_review_refs=[])
(p/'union-package-draft.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n');print('DRAFT ONLY',len(package['entries']))
