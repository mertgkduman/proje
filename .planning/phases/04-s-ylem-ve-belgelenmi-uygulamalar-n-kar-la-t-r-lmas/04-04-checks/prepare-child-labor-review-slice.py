import json
from datetime import datetime, timezone
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
sid, ev, rel = '0404-cocuk-isciligi-statement', '0404-cocuk-emegi-4687-event', '0404-cocuk-emegi-4687-iliski-id'
program = '0303-epm-program-cocuk-isciligi-p1'
proposal, owner, date = '0404-tbmm-cocuk-emegi-4687-p', '0404-tbmm-cocuk-emegi-4687-owner-p', '0404-tbmm-cocuk-emegi-4687-date-p'
items = [
    ('practice_statement', sid, [program], 'Program çocuk işçiliğinin kaldırılmasını hedefler.'),
    ('practice_statement.summary_finding_id', sid, [program], 'Özet çocuk işçiliği pasajına dayanır.'),
    ('practice_statement.quote_finding_id', sid, [program], 'Alıntı programda yer alır.'),
    ('practice_event_evidence', ev+'|'+proposal+'|initiative', [proposal], 'TBMM özeti çocuk işçiliği ve MESEM araştırma konusunu gösterir.'),
    ('practice_event_evidence', ev+'|'+owner+'|initiative', [owner], 'Kayıt önerge sahibi ve 19 milletvekilini bildirir.'),
    ('practice_event_evidence', ev+'|'+date+'|initiative', [date], 'Başkanlığa geliş tarihi 12 Ekimdir.'),
    ('practice_event', ev, [proposal, owner, date], 'Önergenin konusu, sahibi ve geliş tarihi ayrı kaydedildi.'),
    ('practice_relation', rel, [program, proposal, owner, date], 'Program ve araştırma talebi aynı soruna ilişkindir.'),
    ('practice_relation.target_finding_id', rel, [program], 'Hedef programın çocuk işçiliği hükmüdür.'),
    ('practice_relation.explanation_finding_id', rel, [program, proposal, owner, date], 'Açıklama araştırma talebini gerçekleşmiş sonuç saymıyor.'),
]
sections = {program: 'Program çocuk işçiliği pasajı', proposal: '10/4687 önerge özeti', owner: '10/4687 önerge sahibi', date: '10/4687 geliş tarihi'}
reviews = []
for kind, ident, refs, claim in items:
    versions = ['epm-program-v1' if ref == program else '0404-tbmm-cocuk-emegi-4687-v1' for ref in refs]
    reviews.append(dict(subject_kind=kind, subject_id=ident, reviewer_kind='agent', reviewed_at=datetime.now(timezone.utc).isoformat(timespec='seconds'), source_version_ids=json.dumps(list(dict.fromkeys(versions)), ensure_ascii=False), passage_ids=json.dumps(refs, ensure_ascii=False), inspected_sections=json.dumps([sections[ref] for ref in refs], ensure_ascii=False), supported_claim=claim, limitations='Önergenin kabulü, komisyon kurulması ve çocuk işçiliğinde sonuç çıkarılmaz.', result='reviewed', reason='Program ve TBMM 10/4687 künyesi ve özeti karşılaştırıldı.'))
(p/'child-labor-review-slice-draft.json').write_text(json.dumps(dict(status='draft_unvalidated', practice_source_review=reviews), ensure_ascii=False, indent=2)+'\n')
