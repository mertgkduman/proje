"""Beş olayın tüm kaynak incelemesi hedeflerini pasajlarla karşılaştır."""
import hashlib, json
from pathlib import Path
from arsiv import pdf_page_text
from uygulamalar import practice_review_targets
c=Path(__file__).resolve().parent;root=c.parents[3]
p=c/'4114-fourteen-seventeen-draft.json';r=c/'4114-fourteen-seventeen-review-draft.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p)=='ab3d53d0cb4a2316799e1ffd3ef76550ea44c6e0049cdd30a6246a76f2114c77'
assert sha(r)=='d87be1ae7259791d1fa892d6eb2d5fd74dac7a3285db4c43bf07f4a8cfba75e0'
payload=json.loads(p.read_text());review=json.loads(r.read_text());data=dict(payload['practice_records'])
for x in payload['entries']:data.setdefault(x['kind'],[]).append(x['values'])
names=('practice_event','practice_event_evidence','practice_contribution','practice_candidate')
wanted=tuple(f'0406-4114-madde{n}-' for n in range(14,18))
sel={k:[x for x in data.get(k,[]) if str(x.get('id',x.get('event_id',''))).startswith(wanted)] for k in names}
targets=practice_review_targets(data,sel);rows={(x['subject_kind'],x['subject_id']):x for x in review['practice_source_review']}
assert len(targets)==28
for key,(passages,_) in targets.items():assert key in rows and set(json.loads(rows[key]['passage_ids']))==passages,key
pdf=root/'data/practices/sources/dem/objects/977202aa2e935ac7038dbff7d26443ae314f0b9369d45a800594c46752b96826/original.pdf'
passages=[x['values'] for x in payload['entries'] if x['kind']=='passage' and x['values']['id'].startswith(wanted)]
assert len(passages)==4 and all(x['exact'] in pdf_page_text(pdf,x['pdf_page_index']) for x in passages)
print('TARGETS_28_AND_FOUR_EXACT_PASSAGES_OK')
