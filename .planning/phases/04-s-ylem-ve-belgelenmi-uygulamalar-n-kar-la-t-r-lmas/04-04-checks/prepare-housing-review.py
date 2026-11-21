import json
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
r=json.loads((p/'national-review-draft.json').read_text())
event='0404-barinma-grup-onerisi'; rel='0404-barinma-iliski-id'; program='0303-epm-program-barinma-konut-p1'; proposal='0404-barinma-grup-oneri-p'; result='0404-barinma-grup-oylama-p'
items=[
 ('practice_statement','0404-barinma-program-statement',[program],'Program sosyal konut stokunu artırmayı ve kiralık modelleri geliştirmeyi öneriyor.'),
 ('practice_statement.summary_finding_id','0404-barinma-program-statement',[program],'Programın barınma önerisinin özeti kaynakla karşılaştırıldı.'),
 ('practice_statement.quote_finding_id','0404-barinma-program-statement',[program],'Programın barınma alıntısı özgün pasajla karşılaştırıldı.'),
 ('practice_event_evidence',event+'|'+proposal+'|initiative',[proposal],'Grup önerisi araştırma önergesinin öne alınmasını istiyor.'),
 ('practice_event_evidence',event+'|'+result+'|initiative',[result],'Başkan görüşme sonunda grup önerisinin kabul edilmediğini açıklıyor.'),
 ('practice_event',event,[proposal,result],'7 Ağustos grup önerisi ve oylama TBMM tutanağında birbirini izliyor.'),
 ('practice_relation',rel,[program,proposal,result],'Program barınmayı, grup önerisi ise barınma araştırmasının öne alınmasını konu ediyor.'),
 ('practice_relation.target_finding_id',rel,[program],'Program sosyal konut stoku ve kiralık modelleri öneriyor.'),
 ('practice_relation.explanation_finding_id',rel,[program,proposal,result],'Açıklama program, grup önerisi ve oylamayı ayırıyor.'),
]
versions={program:'epm-program-v1',proposal:'0404-tbmm-barinma-tutanak-v1',result:'0404-tbmm-barinma-tutanak-v1'}
sections={program:'Program, Bölüm IV barınma hakkı',proposal:'TBMM 122. birleşim Yeni Parti grup önerisi',result:'Aynı grup önerisi görüşmesinin sonunda başkanın oylama açıklaması'}
for kind,identity,passages,claim in items:
 r['practice_source_review'].append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at='2026-11-21T20:46:19+00:00',source_version_ids=json.dumps(list(dict.fromkeys(versions[x] for x in passages)),ensure_ascii=False),passage_ids=json.dumps(passages,ensure_ascii=False),inspected_sections=json.dumps([sections[x] for x in passages],ensure_ascii=False),supported_claim=claim,limitations='Reddedilen işlem araştırma önergesinin öne alınmasına dair grup önerisidir; temel önergenin sonraki aşaması veya konut üretimi gösterilmez.',result='reviewed',reason='Program ve 7 Ağustos TBMM tutanağı karşılaştırıldı.'))
r['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in r['practice_source_review']]
(p/'housing-review-draft-v2.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('HOUSING_REVIEW_DRAFT',len(r['practice_source_review']))
