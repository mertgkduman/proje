import json
from datetime import datetime, timezone
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
sid='0404-tbmm-grup-charter-statement';ev='0404-tbmm-grup-secim-0724-event';rel='0404-tbmm-grup-secim-0724-iliski-id';program=['0303-epm-grup-tbmm-grup-p'+str(i) for i in range(2,6)];source='0404-grup-kurulus-dunya-p';refs=program+[source]
items=[('practice_statement',sid,program,'Tüzük grup organlarının belirlenmesi ve görevlerini düzenler.'),('practice_statement.summary_finding_id',sid,program,'Özet tüzüğün grup yönetimi, görevi ve toplantı pasajlarına dayanır.'),('practice_statement.quote_finding_id',sid,program[:1],'Alıntı grup başkanvekillerinin belirlenmesi hükmüdür.'),('practice_event_evidence',ev+'|'+source+'|action',[source],'Dünya haberi kapalı grup toplantısındaki üç başkanvekilinin seçimini bildirir.'),('practice_event',ev,[source],'24 Temmuz grup başkanvekili seçimi haberden kaydedildi.'),('practice_relation',rel,[program[0],source],'Tüzükteki grup belirleme yetkisi ve haber verilen seçim ilişkilidir.'),('practice_relation.target_finding_id',rel,program,'Hedef TBMM grup yetki ve görevleri hükmüdür.'),('practice_relation.explanation_finding_id',rel,[program[0],source],'Açıklama seçim haberinden bütün usul uygunluğunu çıkarmıyor.')]
sections={program[0]:'Tüzük grup organlarını belirleme',program[1]:'Tüzük başkanvekillerinin görevi',program[2]:'Tüzük grup yönetiminin görevi',program[3]:'Tüzük MYK üyelerinin toplantıya katılması',source:'Dünya kapalı grup seçimi paragrafı'}
reviews=[]
for kind,subject,refs,claim in items:
    versions=['epm-charter-v1' if x in program else '0404-grup-kurulus-dunya-v1' for x in refs]
    reviews.append(dict(subject_kind=kind,subject_id=subject,reviewer_kind='agent',reviewed_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),source_version_ids=json.dumps(list(dict.fromkeys(versions)),ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps([sections[x] for x in refs],ensure_ascii=False),supported_claim=claim,limitations='Haber tek başına grup iç yönetmeliğinin bütün usulünü ve sonraki görev değişikliklerini belirlemez.',result='reviewed',reason='Kuruluş tüzüğünün TBMM grubu hükümleri ve Dünya Gazetesinin 24 Temmuz haberi okundu.'))
(p/'group-founding-review-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',practice_source_review=reviews),ensure_ascii=False,indent=2)+'\n')
