"""Aday inceleme pasajlarını gerçek önizleme verisiyle hızlı karşılaştırır."""
import json
from pathlib import Path
from uygulamalar import practice_review_targets
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
base=Path('data/.staging/gsd-0406-dem-5344-62440960/releases/875ecd1b2f87439abace3b34aee03f51/records.json')
data=json.loads(base.read_text()); package=json.loads((p/'5344-kaya-draft.json').read_text()); review=json.loads((p/'5344-kaya-review-draft.json').read_text())
needed={'finding_evidence','finding','passage'} | {k for k in package['practice_records'] if k.startswith('practice_')}
canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
seen={k:{canonical(x) for x in data.get(k,[])} for k in needed}
for kind,values in [(e['kind'],e['values']) for e in package['entries']]+[(k,x) for k,rows in package['practice_records'].items() for x in rows]:
 if kind in needed and canonical(values) not in seen[kind]:
  data.setdefault(kind,[]).append(values);seen[kind].add(canonical(values))
targets=practice_review_targets(data)
bad=[]
for row in review['practice_source_review']:
 key=(row['subject_kind'],row['subject_id']); actual=set(json.loads(row['passage_ids']))
 expected=targets.get(key,(set(),))[0]
 if actual!=expected:bad.append({'key':key,'unexpected':sorted(actual-expected),'missing':sorted(expected-actual)})
print('REVIEW_TARGET_MISMATCHES',len(bad),flush=True)
for item in bad:print(json.dumps(item,ensure_ascii=False),flush=True)
raise SystemExit(bool(bad))
