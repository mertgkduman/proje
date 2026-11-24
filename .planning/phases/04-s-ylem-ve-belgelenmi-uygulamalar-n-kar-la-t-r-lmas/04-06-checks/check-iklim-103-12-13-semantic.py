"""51 olaylı gerçek preview üzerine sıralı adayın farkını yalnız bellekte dener."""
import hashlib,json
from pathlib import Path
from uygulamalar import validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3]
old=root/'data/practices/04-dem.json';candidate=c/'iklim-103-12-13-dem-draft.json'
assert hashlib.sha256(old.read_bytes()).hexdigest()=='560d462a1d24a52b7535a7f41f646613f9795e840f6be52f61b7ccad4f9916d9'
assert hashlib.sha256(candidate.read_bytes()).hexdigest()=='bba343874a79888cfeffde83b483067a3dbf4d5262a1d0d046cca1ce02afb3f6'
base,new=json.loads(old.read_text()),json.loads(candidate.read_text())
snapshot=root/'data/.staging/gsd-0406-dem-iklim-103-62520605/releases/5f142fd001bc47cea563461af553b925/records.json'
data=json.loads(snapshot.read_text());canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
prior={canon(x) for x in base['entries']}
for entry in new['entries']:
 if canon(entry) not in prior:data.setdefault(entry['kind'],[]).append(entry['values'])
for kind,rows in new['practice_records'].items():
 prior={canon(x) for x in base['practice_records'].get(kind,[])}
 data.setdefault(kind,[]).extend(row for row in rows if canon(row) not in prior)
validate_practices(data)
print('IKLIM_103_12_13_74_FULL_SEMANTIC_PASS')
