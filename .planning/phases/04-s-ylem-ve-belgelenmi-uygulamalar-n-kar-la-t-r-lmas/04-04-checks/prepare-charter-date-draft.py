import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-immutable-verification-draft.json').read_text())
s=next(x for x in pkg['practice_records']['practice_statement'] if x['id']=='0404-samsun-soz-statement');assert s['statement_at']=='2026-07-24' and s['version_id']=='epm-charter-v1';s.update(statement_at=None,date_precision='unknown',period_basis='Kuruluş tüzüğü 22 Temmuz tarihli kaynak olarak saklanmış; 24 Temmuz kuruluşundan sonraki geçerlilik ilişkisi inceleniyor.',uncertainty_reason='Hükmün olay tarihinde geçerliliği ve üyenin delege statüsü ayrıca araştırılır.')
r=next(x for x in pkg['practice_records']['practice_relation'] if x['id']=='0404-samsun-soz-iliski-id');r['temporal_context']='Tüzük kaynağı 22 Temmuz tarihli; parti 24 Temmuzda kuruldu, haber konusu kongre 25 Ekim 2026 tarihlidir.'
(p/'package-charter-date-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
