import json
from datetime import datetime,timezone
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');sid='0404-cevrimici-uyelik-statement';ev='0404-cevrimici-uyelik-cesme-event';rel='0404-cevrimici-uyelik-cesme-iliski-id';program='0303-epm-detail-uyelik-kabul-itiraz-basvuru-sekli-p';source='0404-cevrimici-uyelik-cesme-p'
items=[('practice_statement',sid,[program],'Tüzük elektronik başvuru olanağını düzenler.'),('practice_statement.summary_finding_id',sid,[program],'Özet il/ilçe veya elektronik başvuru hükmüne dayanır.'),('practice_statement.quote_finding_id',sid,[program],'Alıntı tüzüğün başvuru şekli hükmüdür.'),('practice_event_evidence',ev+'|'+source+'|action',[source],'12 Ağustos haberi çevrim içi sistem ve ilçe rehberini aktarır.'),('practice_event',ev,[source],'Sistem hakkında haber açılış gününü kesin belirtmiyor.'),('practice_relation',rel,[program,source],'Elektronik başvuru hükmü ve haber verilen başvuru kanalı ilişkilidir.'),('practice_relation.target_finding_id',rel,[program],'Hedef tüzükteki başvuru şeklidir.'),('practice_relation.explanation_finding_id',rel,[program,source],'Açıklama haberden tekil kabul veya kesin açılış günü çıkarmıyor.')]
reviews=[]
for kind,ident,refs,claim in items:
    versions=['epm-charter-v1' if x==program else '0404-cevrimici-uyelik-cesme-v1' for x in refs]
    reviews.append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),source_version_ids=json.dumps(list(dict.fromkeys(versions)),ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps(['Tüzük üyelik başvuru biçimi' if x==program else 'Çeşme haberi sistem ve rehber' for x in refs],ensure_ascii=False),supported_claim=claim,limitations='Haberde sistemin kesin açılış günü ve belirli başvuruların kabulü açıklanmıyor.',result='reviewed',reason='Kuruluş tüzüğü ve Çeşme’nin Sesi 12 Ağustos haber pasajı karşılaştırıldı.'))
(p/'membership-online-review-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',practice_source_review=reviews),ensure_ascii=False,indent=2)+'\n')
