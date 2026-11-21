import json
from datetime import datetime, timezone
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
sid, ev, rel = '0404-engelli-erisim-program-statement', '0404-engelli-erisim-752416-event', '0404-engelli-erisim-752416-iliski-id'
program = '0303-epm-program-engellilik-p1'
prefix = '0404-tbmm-housing-access-752416'
proposal, owner, date, recipient = prefix+'-p', prefix+'-owner-p', prefix+'-date-p', prefix+'-recipient-p'
all_refs = [program, proposal, owner, date, recipient]
items = [
    ('practice_statement', sid, [program], 'Program ulusal erişilebilirlik seferberliğini öngörür.'),
    ('practice_statement.summary_finding_id', sid, [program], 'Özet programın erişilebilirlik pasajına dayanır.'),
    ('practice_statement.quote_finding_id', sid, [program], 'Alıntı programda yer alır.'),
    ('practice_event_evidence', ev+'|'+proposal+'|initiative', [proposal], 'Soru özeti Diyarbakır engelli hizmetlerinin erişilebilirliğini gösterir.'),
    ('practice_event_evidence', ev+'|'+owner+'|initiative', [owner], 'Kayıt önerge sahibini bildirir.'),
    ('practice_event_evidence', ev+'|'+date+'|initiative', [date], 'Başkanlığa geliş tarihi 3 Kasımdır.'),
    ('practice_event_evidence', ev+'|'+recipient+'|initiative', [recipient], 'Muhatap Aile ve Sosyal Hizmetler Bakanıdır.'),
    ('practice_event', ev, all_refs[1:], 'Soru konusu, sahibi, muhatabı ve geliş tarihi kaydedildi.'),
    ('practice_relation', rel, all_refs, 'Program ve soru hizmetlerin erişilebilirliği üzerinedir.'),
    ('practice_relation.target_finding_id', rel, [program], 'Hedef programın erişilebilirlik hükmüdür.'),
    ('practice_relation.explanation_finding_id', rel, all_refs, 'Yazılı soru yanıt veya sonuç sayılmıyor.'),
]
sections = {program:'Program erişilebilirlik pasajı', proposal:'7/52416 soru özeti', owner:'7/52416 önerge sahibi', date:'7/52416 geliş tarihi', recipient:'7/52416 muhatabı'}
reviews = []
for kind, ident, refs, claim in items:
    versions = ['epm-program-v1' if ref == program else prefix+'-v1' for ref in refs]
    reviews.append(dict(subject_kind=kind, subject_id=ident, reviewer_kind='agent', reviewed_at=datetime.now(timezone.utc).isoformat(timespec='seconds'), source_version_ids=json.dumps(list(dict.fromkeys(versions)), ensure_ascii=False), passage_ids=json.dumps(refs, ensure_ascii=False), inspected_sections=json.dumps([sections[ref] for ref in refs], ensure_ascii=False), supported_claim=claim, limitations='Yazılı soru yanıt veya fiili erişilebilirlik sonucu sayılmaz.', result='reviewed', reason='Program ve TBMM 7/52416 künyesi ve özeti karşılaştırıldı.'))
(p/'disability-access-review-draft.json').write_text(json.dumps(dict(status='draft_unvalidated', practice_source_review=reviews), ensure_ascii=False, indent=2)+'\n')
