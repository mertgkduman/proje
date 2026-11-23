"""48 olaylı gerçek preview üzerine sıralı adayın farkını yalnız bellekte dener."""
import hashlib,json
from pathlib import Path
from uygulamalar import validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3]
old=root/'data/practices/04-dem.json';candidate=c/'iklim-final-dem-draft.json'
assert hashlib.sha256(old.read_bytes()).hexdigest()=='af249fce72f3d37a197b087d725a2a8094ef3bf6ef9c94c5c6c8c4b5574d652d'
assert hashlib.sha256(candidate.read_bytes()).hexdigest()=='25e2bf1f7869461cd1d553dfeb9f7f1daa1b7a454265f4a97b5db37ca572757f'
base,new=json.loads(old.read_text()),json.loads(candidate.read_text())
snapshot=root/'data/.staging/gsd-0406-dem-teacher-4314-62494452/releases/741e2eabe2674e9ca959fa42f2b6d84b/records.json'
data=json.loads(snapshot.read_text());canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
prior={canon(x) for x in base['entries']}
for entry in new['entries']:
 if canon(entry) not in prior:data.setdefault(entry['kind'],[]).append(entry['values'])
for kind,rows in new['practice_records'].items():
 prior={canon(x) for x in base['practice_records'].get(kind,[])}
 data.setdefault(kind,[]).extend(row for row in rows if canon(row) not in prior)
validate_practices(data)
print('IKLIM_52_FULL_SEMANTIC_PASS')
