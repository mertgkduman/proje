import json
from datetime import datetime, timezone
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
program=['0304-tip-program-emek-talepleri-p1','0304-tip-program-emek-talepleri-q']
proposal=['0405-tip-282121-summary-p']
dates=['0405-tip-282121-date-p']
specs=[
 ('practice_event','0405-tip-282121-event',proposal,'TBMM kayıtlı teklif ve kapsamı'),
 ('practice_event_evidence','0405-tip-282121-event|0405-tip-282121-summary-p|initiative',proposal,'Teklif özeti ve girişim aşaması'),
 ('practice_statement','0405-tip-calisma-statement',program,'Programda çalışma saatleri talepleri ve bağlamı'),
 ('practice_statement.summary_finding_id','0405-tip-calisma-statement',program,'Program özetinin çalışma saatleri, istihdam ve sosyal haklar kapsamı'),
 ('practice_statement.quote_finding_id','0405-tip-calisma-statement',[program[1]],'Programın özgün kısa alıntısı'),
 ('practice_relation','0405-tip-282121-relation',program+proposal+dates,'Program ile kanun teklifi kapsamı'),
 ('practice_relation.target_finding_id','0405-tip-282121-relation',program,'Programın genel hedefi'),
 ('practice_relation.explanation_finding_id','0405-tip-282121-relation',[program[0]]+proposal+dates,'Söylem ve girişimin sınırlı ilişkisi')]
now=datetime.now(timezone.utc).isoformat(); rows=[]
for kind,ident,refs,claim in specs:
 versions=sorted({'0203-tip-program-v1' if r.startswith('0304-') else '0405-tip-282121-v1' for r in refs})
 rows.append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(versions),passage_ids=json.dumps(refs),inspected_sections=json.dumps(['Program çalışma saatleri bağlamı','TBMM 28. dönem 2/2121 kayıt özeti ve geliş tarihi'],ensure_ascii=False),supported_claim=claim,limitations='Program sürümünün 2024 tarihindeki yürürlük durumu bilinmiyor; teklif yasalaşma veya sonuç değildir.',result='reviewed',reason='Program pasajı, TBMM kayıt özeti, tarih ve özgün yedi sayfalık teklif karşılaştırılarak okunmuştur.'))
(p/'policy-review-draft.json').write_text(json.dumps(dict(practice_source_review=rows),ensure_ascii=False,indent=2)+'\n')
