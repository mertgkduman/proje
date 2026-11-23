"""Correct the copied occurrence label using the retained Kocasinan sources."""

from hashlib import sha256
import json
from pathlib import Path
import sys

here=Path(sys.argv[1])
party=Path('data/practices/04-saadet.json')
old='27 Eylül tarihli Bursa Saati ve Vatan Havadis haberleri ve ön duyuru.'
new='28 Ağustos tarihli Kayseri Haber kongre programı ve 29 Ağustos tarihli Kayseri Haber ile Talas Express Haber aktarımları.'
eid='0411-saadet-2026-kocasinan-kongre-event'
package=json.loads(party.read_bytes())
assert sha256(party.read_bytes()).hexdigest()=='fa81e2544f5ed0307b91e5299fba1e3e454e08a92f8708c947fc805b4393b7bb'
event,=(row for row in package['practice_records']['practice_event'] if row['id']==eid)
assert event['occurrence_basis']==old
links=[row for row in package['practice_records']['practice_event_evidence'] if row['event_id']==eid]
assert all(row['passage_id'].startswith('0411-kocasinan-congress-') for row in links)
assert {'initiative','action','result'}=={row['stage'] for row in links}
event['occurrence_basis']=new
out=here/'kocasinan-provenance-draft.json'
with out.open('x') as stream:
    stream.write(json.dumps(package,ensure_ascii=False,indent=2)+'\n')
print(sha256(out.read_bytes()).hexdigest())
