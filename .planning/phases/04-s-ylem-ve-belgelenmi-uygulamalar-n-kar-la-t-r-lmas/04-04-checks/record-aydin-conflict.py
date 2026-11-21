import json
from pathlib import Path

p = Path('data/practices/04-yeni-parti-tranches.json')
q = json.loads(p.read_text())
q['queries'].append(dict(at='2026-11-21', query='"Dilaver Demir" "26 Ekim 2026" "kongre" seçildi Yeni Parti'))
q['candidate_leads'].append(dict(
    url='https://ihbaraydin.com/yeni-parti-aydinda-kongre-tarihi-belli-oldu-demir-tek-aday-olarak-girecek/',
    state='source_records_draft',
    note='19 Ekim tarihli İhbar Aydın haberi 18 Ekim ön seçiminde Dilaver Demir için 4.094 ve toplam 10.610 oy bildiriyor; diğer yerel haber 4.152 bildiriyor. Sayılar uzlaştırılamadı. Haberde 26 Ekim kongresi gelecekteki plan olarak geçer; kongrenin yapıldığına kanıt değildir. Bağlı pasaj 0404-aydin-onsecim-ihbar-p; özgün bayt SHA256 4dc3d5985cbe15499fa24172154eb6c84f817ea126563e56429a1413c1da3e3b.'))
p.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n')
