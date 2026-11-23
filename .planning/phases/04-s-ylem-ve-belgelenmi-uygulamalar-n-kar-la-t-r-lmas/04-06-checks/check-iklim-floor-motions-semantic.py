"""48 olaylı gerçek preview üzerine sıralı adayın farkını yalnız bellekte dener."""
import hashlib,json
from pathlib import Path
from uygulamalar import validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3]
old=root/'data/practices/04-dem.json';candidate=c/'iklim-floor-motions-dem-draft.json'
assert hashlib.sha256(old.read_bytes()).hexdigest()=='41dcecda6759d881634fa06bb764ff73ebc76863a7176b9fe6823a95f986a6a2'
assert hashlib.sha256(candidate.read_bytes()).hexdigest()=='9cf37562ff02b983dd28a457cd6426168dc9de8f98b06e33ab2dab453b951f56'
base,new=json.loads(old.read_text()),json.loads(candidate.read_text())
snapshot=root/'data/.staging/gsd-0406-dem-2026-congress-62497999/releases/5141f7e98ebb4235909b585e14301c35/records.json'
data=json.loads(snapshot.read_text());canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
prior={canon(x) for x in base['entries']}
for entry in new['entries']:
 if canon(entry) not in prior:data.setdefault(entry['kind'],[]).append(entry['values'])
for kind,rows in new['practice_records'].items():
 prior={canon(x) for x in base['practice_records'].get(kind,[])}
 data.setdefault(kind,[]).extend(row for row in rows if canon(row) not in prior)
validate_practices(data)
print('IKLIM_58_FULL_SEMANTIC_PASS')
