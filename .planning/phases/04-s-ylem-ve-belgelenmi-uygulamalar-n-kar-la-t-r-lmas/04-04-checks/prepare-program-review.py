"""Record the passages actually read for the asgari ücret proposal."""
import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
r=json.loads((p/'mugla-review-draft-v4.json').read_text())
program='0303-epm-program-asgari-ucret-p1'; proposal='0404-tbmm-asgari-ucret-p'; group='0404-tbmm-gelen-kagit-p'; event='0404-asgari-ucret-teklif'; statement='0404-asgari-program-statement'; relation='0404-asgari-iliski-id'
items=[
 ('practice_event_evidence',event+'|'+proposal+'|initiative',[proposal],'TBMM teklif özetinde 45.800 lira tutarı öneriliyor.'),
 ('practice_event_evidence',event+'|'+group+'|initiative',[group],'Gelen kâğıtlarda genel başkan ve grup başkanvekilleri teklif sahipleri olarak yer alıyor.'),
 ('practice_event',event,[proposal,group],'2/3790 için kaynaklar teklifi ve sahiplerini gösteriyor.'),
 ('practice_statement',statement,[program],'Program insanca yaşam düzeyinde asgari ücret hedefliyor.'),
 ('practice_statement.summary_finding_id',statement,[program],'Özet asgari ücret hedefini ve hesap yönteminin açıklanmadığını aktarıyor.'),
 ('practice_statement.quote_finding_id',statement,[program],'Alıntı programdaki tek cümleye karşılaştırıldı.'),
 ('practice_relation',relation,[program,proposal,group],'Program hedefi ve aynı konudaki kanun teklifi birlikte incelendi.'),
 ('practice_relation.target_finding_id',relation,[program],'Hedef, programdaki asgari ücret hükmüdür.'),
 ('practice_relation.explanation_finding_id',relation,[program,proposal,group],'Açıklama programı, teklifi ve teklif sahiplerini ayırıyor.')]
versions={program:'epm-program-v1',proposal:'0404-tbmm-asgari-ucret-v1',group:'0404-tbmm-gelen-kagit-v1'}
sections={program:'Kurucu program, Güvenceli Emek ve Nitelikli İstihdam',proposal:'TBMM 2/3790, teklif özeti',group:'TBMM gelen kâğıtları, 2/3790 ve teklif sahipleri'}
for kind,identity,passages,claim in items:
 r['practice_source_review'].append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at='2026-11-21T19:32:00+00:00',source_version_ids=json.dumps([versions[x] for x in passages],ensure_ascii=False),passage_ids=json.dumps(passages,ensure_ascii=False),inspected_sections=json.dumps([sections[x] for x in passages],ensure_ascii=False),supported_claim=claim,limitations='TBMM dinamik sayfasının yayın tarihi ve teklifin kesim tarihindeki sonraki aşaması kesinleştirilmedi; teklif yasalaşma değildir.',result='reviewed',reason='Program pasajı ve iki TBMM kayıt bölümündeki olay ile öneri karşılaştırıldı.'))
r['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in r['practice_source_review']]
(p/'program-review-draft.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('PROGRAM_REVIEW_DRAFT',len(r['practice_source_review']))
