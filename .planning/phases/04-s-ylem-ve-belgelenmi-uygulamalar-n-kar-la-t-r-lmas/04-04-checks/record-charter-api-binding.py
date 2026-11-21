import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text());u='https://api.yeni-parti.org.tr/api/haberler/295'
q['captures'].append(dict(url=u,sha256='4a1481d97a845c31a4b8c97384ccc94de1dee1014fc8e89ab39337f11e3af6d2',accessed_at='2026-11-21T21:35:30.869818+00:00',state='source_records_draft'))
q['initial_readings'].append(dict(read_at='2026-11-21',url=u,section='JSON özgün bayt, aynı bayttan pasif görünüm ve 9 Kasım sözcü pasajı',note='Normal capture MIME application/json bildirdi ve özgün bayt önceki JSON SHA ile eşleşti. Var olan kaynak görüntüleyicisi ile pasif görünüm ve belirli pasaj başarıyla doğrulandı; partiye bağlı belge/sürüm/atıf taslağı hazırlandı. Tam paket/source-check/preview yapılmadı; yayın başka alan adı üzerinden sözcü beyanıdır, tam tüzük değişiklik metni değildir.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
