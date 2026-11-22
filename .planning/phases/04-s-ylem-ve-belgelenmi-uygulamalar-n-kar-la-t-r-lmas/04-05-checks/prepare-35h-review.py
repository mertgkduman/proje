import json
from datetime import datetime,timezone
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); st='0405-tip-pm35-statement'; rel='0405-tip-pm35-iliski'; pm='0405-tip-pm-nisan-thirtyfive-p'; pdf='0405-tip-282121-pdf-workhour-p'; tbmm='0405-tip-282121-summary-p'
specs=[('practice_statement',st,[pm],'Parti Meclisi 1 Mayıs için 35 saat talebi ilan etti.'),('practice_statement.summary_finding_id',st,[pm],'Özet 35 saatlik haftalık talebi koruyor.'),('practice_statement.quote_finding_id',st,[pm],'Kısa alıntı ilgili kaynak ifadesiyle eşleşiyor.'),('practice_relation',rel,[pm,tbmm,pdf],'9 Nisan hedefi ve 24 Nisan teklifinin genel haftalık süresi eşleşiyor.'),('practice_relation.target_finding_id',rel,[pm],'Hedef parti meclisinin 35 saat açıklamasıdır.'),('practice_relation.explanation_finding_id',rel,[pm,pdf],'Söylem ve teklif aynı süreyi içerir, sonuç ayrı değerlendirilir.')]
rows=[];now=datetime.now(timezone.utc).isoformat()
for kind,ident,refs,claim in specs:
 versions=sorted({'0405-tip-pm-nisan-v1' if v==pm else '0405-tip-282121-pdf-v1' if v==pdf else '0405-tip-282121-v1' for v in refs})
 rows.append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(versions),passage_ids=json.dumps(refs),inspected_sections=json.dumps(['9 Nisan PM öncelikli hedefler; 28. dönem teklif özeti ve madde 3'],ensure_ascii=False),supported_claim=claim,limitations='TBMM teklifi kanunlaşma ya da ülkedeki gerçekleşme değildir.',result='reviewed',reason='Bu alanın dönem, özne ve metin kapsamı ayrı okundu: '+kind))
(p/'policy-35h-review-delta.json').write_text(json.dumps(dict(practice_source_review=rows),ensure_ascii=False,indent=2)+'\n');print('DRAFT ONLY',len(rows))
