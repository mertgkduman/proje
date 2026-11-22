"""Doğrulama adayı: sabit tracer ile Hakkâri fragmanı, ortak pakete yazmaz."""
import hashlib,json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
def read(name):return json.loads((p/name).read_text())
base_name='package-tracer-dossier-compatible-draft.json';base=read(base_name);fragment=read('hakkari-event-fragment-draft.json')
base['entries']+=fragment['entries'];r=base['practice_records']
r.update({'practice_variant_contract':[dict(version=1,inventory_json=json.dumps(base['scope_inventory'],ensure_ascii=False))],'practice_scope':[],'practice_attempt':[],'practice_unmatched':[]})
r.update({'practice_evidence_contract':[dict(version=1)],'practice_evidence_assessment':[],'practice_actor_period':[],'practice_dispute':[],'practice_dispute_evidence':[],'practice_position_change':[]})
r['practice_evidence_assessment'].append(dict(event_id='tracer-cesme',passage_id='0105-cesme-p',stage='action',basis_kind='independent_report'))
for x in r['practice_event_evidence']:
 r['practice_evidence_assessment'].append(dict(event_id=x['event_id'],passage_id=x['passage_id'],stage=x['stage'],basis_kind='independent_report' if x['event_id']=='0406-2023-congress' else 'document'))
for k,rows in fragment['practice_records'].items():r[k]+=rows
review=read('source-tracer-checked-draft.json');extra=read('hakkari-event-review-draft.json');review['practice_source_review']+=extra['practice_source_review'];review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
keys=[(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']];assert len(set(keys))==len(keys)
(p/'hakkari-combined-draft.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n')
(p/'hakkari-combined-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('HAKKARI_COMBINED_DRAFT',len(base['entries']),len(keys),'tracer_sha256',hashlib.sha256((p/base_name).read_bytes()).hexdigest())
