import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json')
q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in [
    '"Yeni Parti" "2026" "kadın" "kanun teklifi" TBMM',
    '"Yeni Parti" "2026" "eğitim" "araştırma önergesi" TBMM',
    '"Yeni Parti" "2026" "çevre" "araştırma önergesi"',
    '"Yeni Parti" "2026" "sağlık" "kanun teklifi" TBMM',
]]
q['candidate_leads'] += [
    dict(url='https://tbmm.gov.tr/Milletvekili/UyeMeclisArastirmaOnergeleri?Id=02abfc41-7624-469b-bf2d-01886c91c8ff&ortakDonemId=134155f0-c3d6-4d24-893b-f3a2ef695ae7',state='read_partial_unbound',note='TBMM arama sonucunda 29 Temmuz 2026 tarihli 10/4445 meslek hastalıkları önergesi listeleniyor; tekil künyesi, ilk imza ve parti aidiyetinin işlem tarihinde doğrulanması, program bağlantısı ve metni takip edilmeli. Eski yıllara bugünkü parti etiketinin uygulanması tarihsel aidiyet kanıtı değildir.'),
    dict(url='https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T2/WebOnergeMetni/5f8508bd-ea43-45cb-a7e8-7a95c045acc1.pdf',state='read_partial_unbound',note='TBMM arama sonucunda 2/3866, Şeref Arpacı imzalı sosyal sigorta teklifi ve TBMM 1 Ekim kayıt damgası görülüyor; metnin amacı, tüm sayfalar, dinamik künye ve kesimdeki aşama ayrıca okunacak.'),
    dict(url='https://vekilpedia.com/onerge/10-5047-devlet-okullarinda-kayit-parasi-bagis-veya-farkli-adlar-altinda-para-toplanmasi-uygulamal',state='outside_cutoff_lead',note='11 Kasım 2026 tarihli 10/5047 araştırma önergesi kaynağın bildirdiği tarihle 10 Kasım kesiminden sonra; kesim içi olay olarak kullanılamaz.'),
    dict(url='https://vekilin.com/teklif/2-4056-saglik-hizmetleri-temel-kanununda-degisiklik-yapilmasina-dair-kanun-teklifi',state='outside_cutoff_lead',note='16 Kasım 2026 tarihli 2/4056 teklifi kaynağın bildirdiği tarihle kesim dışı.'),
]
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
