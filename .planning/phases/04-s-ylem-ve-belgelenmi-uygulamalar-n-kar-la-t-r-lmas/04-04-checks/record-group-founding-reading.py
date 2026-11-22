import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" 2026 "parti meclisi" "disiplin kurulu" karar','"Yeni Parti" 2026 "merkez yönetim kurulu" "atandı"','"Yeni Parti" "2026" "grup başkanvekili" "seçildi" meclis','"Yeni Parti" "2026" "üyelik" "itiraz" "disiplin"','"Yeni Parti" "grup başkanvekilleri" "Temmuz" 2026 "Günaydın"','"Yeni Parti" "grup yönetimi" "30 Temmuz" 2026 seçildi','"Yeni Parti" 2026 "grup yönetim kurulu" "seçildi" milletvekili','"Yeni Parti" 2026 üyeliği "kabul edilmedi" "itiraz"']]
q['candidate_leads'] += [
 dict(url='https://www.dunya.com/gundem/yeni-partinin-grup-baskan-vekilleri-pm-ve-ydk-uyeleri-belli-oldu-haberi-833547',state='source_records_draft',note='Dünya Gazetesi, 24 Temmuz 2026: Kurucular Kurulu toplantısından sonra kapalı grup toplantısında Ali Mahir Başarır, Murat Emir ve Gökhan Günaydın grup başkanvekili seçildi. 21 Kasım özgün HTML SHA256 ba51c913e2e9057d8c78da61b60e8c78dc9e1724aa059de7a566279c3fa2373b; 0404-grup-kurulus-dunya-p. Seçim organı ve diğer kurullar ayrı tutulmalı.'),
 dict(url='https://www.nefes.com.tr/yeni-partinin-pm-ve-ydk-uyeleri-belli-oldu-140697',state='read_unbound',note='Nefes/Haber Merkezi 24 Temmuz haberinde aynı üç grup başkanvekilinin kapalı grup toplantısında seçildiği aktarılıyor. 21 Kasım HTTP 200 bayt SHA256 5e4a7e6ea0c890ff455ae6ed5adeeee00576d6215354858f41656c8e535caae7; sürüm bağı henüz kurulmadı.'),
 dict(url='https://medyascope.tv/2026/11/16/yeni-partide-cizik-iddialari-ali-mahir-basarir-medyascopea-anlatti-veda-degil-kizlarimdan-ozur/',state='read_partial_unbound',note='16 Kasım tarihli PM/grup görevi açıklaması kesim sonrasıdır; 10 Kasım öncesi görev sonucu olarak kullanılmaz. O döneme ilişkin iddialar ayrı tarihli kaynakla araştırılmalı.'),
]
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
