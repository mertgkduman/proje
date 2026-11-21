import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');r=json.loads((p/'national-locals-review-draft.json').read_text()); speech='0105-speech-p'
for slug,city,ref in [('bursa','Bursa','0404-bursa-onsecim-p'),('sakarya','Sakarya','0404-sakarya-onsecim-p')]:
 ev='0404-'+slug+'-onsecim-event';rel='0404-'+slug+'-iliski-id'; versions={speech:'0105-speech-v1',ref:'0404-'+slug+'-onsecim-v1'};sections={speech:'Euronews 4 Ağustos başkan seçimi beyanı',ref:city+' 18 Ekim yerel ön seçim haberi'}
 items=[('practice_event_evidence',ev+'|'+ref+'|action',[ref],city+' ön seçim haberi.'),('practice_event',ev,[ref],city+' il başkanlığı ön seçimi aktarıldı.'),('practice_relation',rel,[speech,ref],city+' ön seçimi beyanın ilgili konusunu izliyor.'),('practice_relation.target_finding_id',rel,[speech],city+' için karşılaştırılan seçim yöntemi beyanı.'),('practice_relation.explanation_finding_id',rel,[speech,ref],city+' yerel haber ve beyan karşılaştırması.')]
 for kind,identity,passages,claim in items:
  r['practice_source_review'].append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at='2026-11-21T21:07:17+00:00',source_version_ids=json.dumps([versions[x] for x in passages],ensure_ascii=False),passage_ids=json.dumps(passages,ensure_ascii=False),inspected_sections=json.dumps([sections[x] for x in passages],ensure_ascii=False),supported_claim=claim,limitations='Sandık tutanağı görülmedi; il kongresi ve sayısal ayrıntılar ayrıca araştırılıyor.',result='reviewed',reason=city+' haberi ile beyan karşılaştırıldı.'))
r['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in r['practice_source_review']]
(p/'bursa-sakarya-review-draft.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('BURSA_SAKARYA_REVIEW_DRAFT',len(r['practice_source_review']))
