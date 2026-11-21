import json
from datetime import datetime, timezone
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
ev, rel = '0404-cocuk-soru-51913-event', '0404-cocuk-soru-51913-iliski-id'
program = '0303-epm-program-cocuk-isciligi-p1'
proposal, owner, date, recipient = '0404-tbmm-cocuk-soru-51913-p', '0404-tbmm-cocuk-soru-51913-owner-p', '0404-tbmm-cocuk-soru-51913-date-p', '0404-tbmm-cocuk-soru-51913-recipient-p'
sources = [program, proposal, owner, date, recipient]
items = [
    ('practice_event_evidence', ev+'|'+proposal+'|initiative', [proposal], 'Soru özeti çocuk işçiliğiyle mücadele konusunu gösterir.'),
    ('practice_event_evidence', ev+'|'+owner+'|initiative', [owner], 'Kayıt önerge sahibini bildirir.'),
    ('practice_event_evidence', ev+'|'+date+'|initiative', [date], 'Başkanlığa geliş tarihi 23 Ekimdir.'),
    ('practice_event_evidence', ev+'|'+recipient+'|initiative', [recipient], 'Muhatap Çalışma ve Sosyal Güvenlik Bakanıdır.'),
    ('practice_event', ev, sources[1:], 'Yazılı sorunun konusu, sahibi, muhatabı ve geliş tarihi ayrı kaydedildi.'),
    ('practice_relation', rel, sources, 'Program ve yazılı soru aynı soruna ilişkindir.'),
    ('practice_relation.target_finding_id', rel, [program], 'Hedef programın çocuk işçiliği hükmüdür.'),
    ('practice_relation.explanation_finding_id', rel, sources, 'Açıklama yazılı soruyu yanıt veya sonuç saymıyor.'),
]
sections = {program:'Program çocuk işçiliği pasajı', proposal:'7/51913 soru özeti', owner:'7/51913 önerge sahibi', date:'7/51913 geliş tarihi', recipient:'7/51913 muhatabı'}
reviews = []
for kind, ident, refs, claim in items:
    versions = ['epm-program-v1' if ref == program else '0404-tbmm-cocuk-soru-51913-v1' for ref in refs]
    reviews.append(dict(subject_kind=kind, subject_id=ident, reviewer_kind='agent', reviewed_at=datetime.now(timezone.utc).isoformat(timespec='seconds'), source_version_ids=json.dumps(list(dict.fromkeys(versions)), ensure_ascii=False), passage_ids=json.dumps(refs, ensure_ascii=False), inspected_sections=json.dumps([sections[ref] for ref in refs], ensure_ascii=False), supported_claim=claim, limitations='Yazılı soru, yanıt veya çocuk işçiliğine ilişkin fiili sonuç sayılmaz.', result='reviewed', reason='Program ve TBMM 7/51913 künyesi ve özeti karşılaştırıldı.'))
(p/'child-labor-question-review-draft.json').write_text(json.dumps(dict(status='draft_unvalidated', practice_source_review=reviews), ensure_ascii=False, indent=2)+'\n')
