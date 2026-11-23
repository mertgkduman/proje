"""Beş olayın tüm kaynak incelemesi hedeflerini pasajlarla karşılaştır."""
import hashlib, json
from pathlib import Path
from arsiv import pdf_page_text
from uygulamalar import practice_review_targets
c=Path(__file__).resolve().parent;root=c.parents[3]
p=c/'4114-tail-draft.json';r=c/'4114-tail-review-draft.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p)=='e1d815c485448981c7e4dc5be340a5e96fab3e620958edb5ba58622130bcbe35'
assert sha(r)=='301dbb41ab3fae5e18dfbdb297c681c490b484a38f506c9ea4b172928aa69603'
payload=json.loads(p.read_text());review=json.loads(r.read_text());data=dict(payload['practice_records'])
for x in payload['entries']:data.setdefault(x['kind'],[]).append(x['values'])
names=('practice_event','practice_event_evidence','practice_contribution','practice_candidate')
wanted=tuple(f'0406-4114-madde{n}-' for n in (18,19,20,'gecici1','gecici2','14-anayasa'))
sel={k:[x for x in data.get(k,[]) if str(x.get('id',x.get('event_id',''))).startswith(wanted)] for k in names}
targets=practice_review_targets(data,sel);rows={(x['subject_kind'],x['subject_id']):x for x in review['practice_source_review']}
assert len(targets)==44
for key,(passages,_) in targets.items():assert key in rows and set(json.loads(rows[key]['passage_ids']))==passages,key
pdf=root/'data/practices/sources/dem/objects/977202aa2e935ac7038dbff7d26443ae314f0b9369d45a800594c46752b96826/original.pdf'
passages=[x['values'] for x in payload['entries'] if x['kind']=='passage' and x['values']['id'].startswith(wanted)]
assert len(passages)==8 and all(x['exact'] in pdf_page_text(pdf,x['pdf_page_index']) for x in passages)
print('TARGETS_44_AND_EIGHT_EXACT_PASSAGES_OK')
