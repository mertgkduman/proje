"""Beş olayın tüm kaynak incelemesi hedeflerini pasajlarla karşılaştır."""
import hashlib, json
from pathlib import Path
from arsiv import pdf_page_text
from uygulamalar import practice_review_targets
c=Path(__file__).resolve().parent;root=c.parents[3]
p=c/'4114-first-five-v3-draft.json';r=c/'4114-first-five-v4-review-draft.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p)=='bc539fe9b816d24508c12b3a79678c293c63f89d65f243eb3875376b81157a13'
assert sha(r)=='0407b6508d19d7b4ba1407c54f19d09a1b99a12a5ea66bda6efa3560e80931ae'
payload=json.loads(p.read_text());review=json.loads(r.read_text());data=dict(payload['practice_records'])
for x in payload['entries']:data.setdefault(x['kind'],[]).append(x['values'])
names=('practice_event','practice_event_evidence','practice_contribution','practice_candidate')
sel={k:[x for x in data.get(k,[]) if str(x.get('id',x.get('event_id',''))).startswith('0406-4114-madde')] for k in names}
targets=practice_review_targets(data,sel);rows={(x['subject_kind'],x['subject_id']):x for x in review['practice_source_review']}
assert len(targets)==35
for key,(passages,_) in targets.items():assert key in rows and set(json.loads(rows[key]['passage_ids']))==passages,key
pdf=root/'data/practices/sources/dem/objects/977202aa2e935ac7038dbff7d26443ae314f0b9369d45a800594c46752b96826/original.pdf'
passages=[x['values'] for x in payload['entries'] if x['kind']=='passage' and x['values']['id'].startswith('0406-4114-')]
assert len(passages)==7 and all(x['exact'] in pdf_page_text(pdf,x['pdf_page_index']) for x in passages)
print('TARGETS_35_AND_SEVEN_EXACT_PASSAGES_OK')
