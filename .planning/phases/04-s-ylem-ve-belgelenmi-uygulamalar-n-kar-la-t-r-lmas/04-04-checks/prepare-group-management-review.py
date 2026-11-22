import json
from datetime import datetime,timezone
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');ev='0404-tbmm-grup-yonetim-0728-event';rel='0404-tbmm-grup-yonetim-0728-iliski-id';program='0303-epm-grup-tbmm-grup-p2';source='0404-grup-yonetim-ekonomim-p';context='0404-grup-yonetim-ekonomim-context-p';allrefs=[program,context,source]
items=[('practice_event_evidence',ev+'|'+context+'|action',[context],'Ekonomim TBMM kapalı grup toplantısını bildirir.'),('practice_event_evidence',ev+'|'+source+'|action',[source],'Haberde beş grup yönetim kurulu üyesi listelenir.'),('practice_event',ev,[context,source],'28 Temmuz tarihli haber toplantı ve grup yönetimini aktarır.'),('practice_relation',rel,allrefs,'Tüzüğün grup yönetimini belirleme hükmü ile haber ilişkilidir.'),('practice_relation.target_finding_id',rel,[program],'Hedef tüzükteki grup organlarını belirleme hükmüdür.'),('practice_relation.explanation_finding_id',rel,allrefs,'Açıklama haberin göstermediği usul uygunluğunu çıkarmıyor.')]
sections={program:'Tüzük grup organlarını belirleme',context:'Ekonomim TBMM toplantısı paragrafı',source:'Ekonomim grup yönetimi isimleri'};reviews=[]
for kind,ident,refs,claim in items:
    versions=['epm-charter-v1' if x==program else '0404-grup-yonetim-ekonomim-v1' for x in refs]
    reviews.append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),source_version_ids=json.dumps(list(dict.fromkeys(versions)),ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps([sections[x] for x in refs],ensure_ascii=False),supported_claim=claim,limitations='Haber grup iç yönetmeliğinin bütün usulünü veya sonraki görev değişikliklerini tek başına belirlemez.',result='reviewed',reason='Kuruluş tüzüğü ve Ekonomim’in 28 Temmuz tarihli haber pasajları okundu.'))
(p/'group-management-review-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',practice_source_review=reviews),ensure_ascii=False,indent=2)+'\n')
