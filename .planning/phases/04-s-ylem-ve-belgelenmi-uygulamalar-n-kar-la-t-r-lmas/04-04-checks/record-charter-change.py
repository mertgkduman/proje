import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
u='https://www.cumhuriyet.com.tr/turkiye/genis-katilimli-yonetim-yeni-parti-tuzugunu-degistirdi-pm-uye-sayisini-150-yapti-2554702'
q['initial_readings'].append(dict(read_at='2026-11-21',url=u,section='9 Kasım tüzük değişikliği haberi ve kaynak künyesi',note='Sarp Sağkal 9 Kasım 12:42: tüzük değişikliğinde parti meclisi sayısının 150ye çıkarıldığını ve üç gruba ayrıldığını haberleştiriyor. Haber tam tüzük metni veya değişikliğin tüm maddelerinin tarihsel sürümü değildir; kurucu tüzüğün sonraki geçerliliği varsayılmadı.'))
q['captures'].append(dict(url=u,sha256='5689a62efb7637e39095f77c7d9c6a3fc755b12dc36cf9a2d969657813da9904',accessed_at='2026-11-21T21:31:24.178068+00:00',state='source_records_draft'))
u='https://yeni-parti.org.tr/haber/295'
q['captures'].append(dict(url=u,sha256='5155c3dce109ec92afc48b70870cdbacab0fa269b8a195129e8101d8c57666e4',accessed_at='2026-11-21T21:31:24.847602+00:00',state='shell_only_not_source_bound'))
q['candidate_leads'].append(dict(url=u,state='shell_only',note='Arama indeksi 9 Kasım MYK açıklaması gösterdi; doğrudan yakalanan HTML ve web açımı okunabilir haber gövdesi içermiyor. Kaynağın API veya özgün açıklaması araştırılacak; boş kabuk pasaj veya tam metin olarak kullanılmadı.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
