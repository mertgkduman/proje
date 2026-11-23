"""Beş olayın tüm kaynak incelemesi hedeflerini pasajlarla karşılaştır."""
import hashlib, json
from pathlib import Path
from arsiv import pdf_page_text
from uygulamalar import practice_review_targets
c=Path(__file__).resolve().parent;root=c.parents[3]
p=c/'4114-six-thirteen-v2-draft.json';r=c/'4114-six-thirteen-review-draft.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p)=='fb7ec8919f5326bb912209096de7cdb0a3aac92bb18340dda797b364979ff7b3'
assert sha(r)=='aebb6b9c23324584af9466ba1115b36b52525d41cf619153507b8a9257ba2553'
payload=json.loads(p.read_text());review=json.loads(r.read_text());data=dict(payload['practice_records'])
for x in payload['entries']:data.setdefault(x['kind'],[]).append(x['values'])
names=('practice_event','practice_event_evidence','practice_contribution','practice_candidate')
wanted=tuple(f'0406-4114-madde{n}-' for n in range(6,14))
sel={k:[x for x in data.get(k,[]) if str(x.get('id',x.get('event_id',''))).startswith(wanted)] for k in names}
targets=practice_review_targets(data,sel);rows={(x['subject_kind'],x['subject_id']):x for x in review['practice_source_review']}
assert len(targets)==58
for key,(passages,_) in targets.items():assert key in rows and set(json.loads(rows[key]['passage_ids']))==passages,key
pdf=root/'data/practices/sources/dem/objects/977202aa2e935ac7038dbff7d26443ae314f0b9369d45a800594c46752b96826/original.pdf'
passages=[x['values'] for x in payload['entries'] if x['kind']=='passage' and x['values']['id'].startswith(wanted)]
assert len(passages)==10 and all(x['exact'] in pdf_page_text(pdf,x['pdf_page_index']) for x in passages)
print('TARGETS_58_AND_TEN_EXACT_PASSAGES_OK')
