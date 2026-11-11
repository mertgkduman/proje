---
phase: quick-261111-epm
plan: "01"
quick_id: 261111-epm
status: complete
subsystem: archive-report-publication
tags: [kaynak-derleme, atif, yeni-parti, pasif-arsiv, github-pages]
requires:
  - phase: 02-02
    provides: Şema 4, renderer 10 ve TİP kaynak tracer teslimi
provides:
  - Kaynak politikası 2, şema 5 ve sürümlü yayıncı/yazar/hesap atfı
  - Yeni Parti için 30 kaynaklı özet ve alıntı çifti
  - Yerel font/logo/CSS içeren iki ayrı pasif tüzük/program görünümü
  - Okuyucu öncelikli renderer 13 ve doğrulanmış GitHub Pages yayını
affects: [02-03, 02-04, 02-05, 02-06, 02-07, 02-08, 02-09, 02-10]
tech-stack:
  added: []
  patterns: [SQLite eklemeli migration, source_attribution, pasif HTML türevi, sürüme göre renderer dispatch]
key-files:
  created:
    - src/kaynaklar.py
    - src/arsiv_gorunum.py
    - src/rapor_v10.py
    - src/rapor_v11.py
    - src/rapor_v12.py
    - src/rapor_v11.css
    - tests/test_source_policy.py
    - tests/test_archive_views.py
    - tests/archive_browser.cjs
    - data/dossiers/261111-epm-yeni-parti.json
    - data/releases/e0467880febd44068d476a448e09608f/manifest.json
  modified:
    - src/arsiv.py
    - src/dosyalar.py
    - src/rapor.py
    - data/current.json
    - AGENTS.md
    - README.md
    - .planning/PROJECT.md
    - .planning/REQUIREMENTS.md
    - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-CONTEXT.md
    - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-03-PLAN.md
key-decisions:
  - D-13: Parti yayınları, haberler ve sosyal paylaşımlar açık atıfla derlenir; sicil alan adı kanıtı ve her kaynak için insan kabulü ön koşulu kaldırıldı.
  - D-14: Kuruluş gerekçesi ve parti içeriği önde; sicil/künye/yöntem ve geçmiş girişimler kapalı ayrıntılarda.
  - D-15: Özgün baytlar korunur; HTML için yerel varlıklı, scriptsiz, ayrı hash manifestli türev üretilir.
  - D-16: Yeni Parti düzeltmesi mevcut kamu yayınına uygulandı; Faz 2 ve TİP tamamlanma durumu ilerletilmedi.
duration: 38min
started: "2026-11-11T15:45:49Z"
completed: "2026-11-11"
plan_head_before: d0797648a2b61bed3e96f839293156fef87bde92
actuals:
  tokens: 643918
  tasks: 3
  commits: 6
---

# Quick 261111-epm: Yeni Parti kaynak derlemesi ve okunabilir arşiv

**Parti yayınlarını doğrudan kullanan atıflı kaynak politikası, gerçek tüzük/program içeriği ve özgün görünümlü pasif arşivler mevcut kamu raporunda yayımlandı.**

## Teslim

- [Güncel rapor](https://mertgkduman.github.io/proje/) — değişmez sürüm `e0467880febd44068d476a448e09608f`, şema **5**, kaynak politikası **2**, dosya doğrulama **2**, renderer **13**.
- [Tüzük arşivi](https://mertgkduman.github.io/proje/views/5ad0d30f04d349ca9c6e55a913f9d4b1/index.html) — özgün SHA-256 `b3709f52e07f6d65797d021f571c2b97eca5ac02771a633fe55aafec4130518e`, canonical `/parti-tuzugu`.
- [Program arşivi](https://mertgkduman.github.io/proje/views/bb13963f4a7945c12f748e1c4f1e1aba/index.html) — özgün SHA-256 `58fa220ab814bd82a4c8d0d233bf55ab268eb9f856750cd88abc544e17ceba1b`, canonical `/parti-programi`.
- [GitHub Pages dağıtımı](https://github.com/mertgkduman/proje/actions/runs/43057194277) — `4fcc8ac21496d76add225746551b83cd38963a63`, **completed / success**.

## Tamamlanan üç görev

1. **Kaynak derleme politikası:** `source_policy` ve `source_attribution` kayıtları gerçek record/load/export/render/publish/audit zincirine bağlandı. Parti tüzüğü/programı ve kaynaklı resmî site için sicil alan adı/otorite zinciri beklenmiyor. Haber ve sosyal içerik açık atıfla kullanılabiliyor; sosyal paylaşımda hesap/yazar, tarih ve kalıcı adres zorunlu. Sicil kimliği, sahiplik, gerçek pasaj, alıntı eşitliği, hash, FK, güvenli URL ve teslim sırası denetimleri korundu. Politika ve geçişteki eski kayıt sınırları silinerek denetim atlanamıyor. D-13–D-16, yönetici belgelerine ve **02-03–02-10'un gerçek eylem/kabul/tehdit talimatlarına** işlendi; tamamlanmış 02-01/02-02 geçmişi değiştirilmedi.
2. **Gerçek Yeni Parti içeriği:** Kuruluş gerekçesi/siyasal kimlik, üye hakları ve ifade sınırı, genel başkan/Parti Meclisi seçimi ve denetimi, kuruluş dönemi hükmü, başlıca program vaatleri, haberlerde aktarılan ön seçimler, tüzüğün aidat/gelir/harcama/bütçe/kesin hesap kuralları ve atıflı Kocaeli mali haberi derlendi. **30 özet/alıntı çifti** ve altı kaynak ailesine ait dokuz künye kaydı mevcut. Ekonomim'in kaynak metadatasındaki **Haber Merkezi**, Kocaeli TV'nin metadatasındaki **Bugün Kocaeli** yazar bilgileri ayrı ek kaynak sürümlerinde korundu; eski eksik künyeler değiştirilmedi. Ön seçim, nihai kurultay seçimi olarak sunulmuyor. Site/tüzük/programa ilişkin geçersiz kalan eksikler kanıtlı çözüm kayıtlarıyla tarihçeye taşındı.
3. **Okuma akışı ve yayın:** İlk panel neden kurulduğunu ve ne söylediğini gösteriyor. Sicil anahtarı, kart dayanakları, önceki bulgular ve yöntem kapalı ayrıntılara alındı. Alıntı siyah/tırnaklı, kaynaklı özet koyu mavi; kaynak tıklaması, geri odak ve klavye sekmeleri çalışıyor. Tüzük/program görünümleri özgün statik düzen, logo, CSS ve fontları yerelden okuyor; script/handler/form/frame/aktif gömülü içerik çalışmıyor. Özgün HTML indirme olarak korunuyor. Normal push, önceki `gh-pages` commit'ini ve eski rapor adreslerini korudu.

## Doğrulama

- `python3 tests/run.py`: **65/65 geçti**, son koşu **166,897 saniye**. Politika, saldırı örnekleri, gerçek belge eşleştirmesi, yayın/audit, veri bütünlüğü ve Chrome okuma yolları dahildir.
- Odak testleri: `test_source_policy.py` **8**, `test_archive_views.py` **3**, `test_report.py` **4** test içerir. Politika RED testi uygulamadan önce gerçek assertion hatası verdi ve GSD `RED_EVIDENCE_OK` aldı; arşiv ve okuyucu testleri de uygulama öncesi assertion hatasıyla başladı.
- Güncel Faz 1 ve `--phase 2 --party tip --stage tracer` denetimleri geçti. `02-01-tip-tracer.json` ve `02-02-tip-sources.json` makbuzları değişmeden geçti.
- Önceki `b14c96c54e4b420686c46e5cfb1071a3` / renderer 10, Faz 1 `26de2a4efc584b5b9f81ea67dcb8d65c` ve yeni ara renderer 11/12 sürümleri kendi üreticileriyle denetlendi. Başlangıçta sabitlenen **228 eski dosyanın baytları değişmedi**.
- Nihai JSON girdisi, `b14c96...` tabanından yalıtılmış veri kopyasında yeniden **load → publish → Faz 2 tracer audit** yolundan geçti; dokuz atıf, iki görünüm ve boş prefix doğrulandı. Bu geçici deneme canlı işaretçiyi değiştirmedi.
- Sekiz kalan plan için **16/16 frontmatter ve plan-structure kontrolü** geçti.
- Gerçek Chrome'da canlı sayfa ile yerel görünümün masaüstü ve 360px ekran görüntüleri incelendi. Kamu raporunda da iki arşive gerçek bağlantı tıklaması, pasif içerik, yüklenen yerel görseller/fontlar, dış kaynak isteği olmaması, kapalı yöntem ayrıntıları ve taşma olmaması doğrulandı. Kamu kök adresi doğru değişmez sürüme yönlendi.
- **111 kamu dosyasının SHA-256'sı yerel paketle birebir eşleşti.** İki önceki rapor URL'si de eski yerel HTML baytlarıyla eşleşiyor. Kamu özgün HTML `.bin` dosyaları `application/octet-stream` sunuluyor.
- Ayrıntılı makine kanıtı: `261111-epm-CHECKS.json`.

## Commit'ler

| Commit | İçerik |
|---|---|
| `cd0a6ab` | Kaynak politikası için başarısız uçtan uca RED testleri |
| `b6b09dd` | Politika 2, şema 5, renderer 10 dondurma ve yönetici/kalan plan değişiklikleri |
| `0c85f0b` | Pasif ve okunabilir arşiv RED testleri |
| `0bab7b1` | Gerçek belge içeriği, pasif arşiv üreticisi, yerel varlıklar ve yeniden uygulanabilir girdi |
| `e1ab067` | İçerik öncelikli okuyucu ve ayrı arşiv bağlantıları RED testleri |
| `7e18593` | Nihai okuyucu, künye iyileştirmeleri, tarihsel renderer'lar, testler ve değişmez yerel sürümler |
| `4fcc8ac` | Ayrı `gh-pages` ağacında kamu raporu/arşiv paketi; normal push |

`actuals.tokens`, üretilmiş HTML/JSON snapshot'ları dahil gerçekleşen Git diff'inin karakter/4 hesabıdır; çalışma oturumunun model token sayısı değildir. `actuals.commits`, plan öncesi ledger SHA'sından ana üretim dalında ölçülen **6** commit'tir; ayrı yayın dalındaki commit bu sayıya dahil değildir.

## Plandan sapmalar

**[Rule 1 — değişmez sürüm uyumluluğu] Nihai renderer 13 oldu.** İlk kapalı renderer 11 sürümü `7f816c5afd704cf3a88f2cfd8638528f` üretildikten sonra görsel inceleme, sicil ayrıntılarını kuruluş gerekçesinden sonraya taşımayı gerektirdi. Son künye okuması da kaynakta bulunan haber yazarlarını ekledi. Bu iyileştirmelerde önceki kapalı baytları değiştirmek yerine renderer 11 ve 12 donduruldu; ara `6b195b85f7cc4bf3a20b3f8fc3240e8a` da korunarak nihai renderer 13 yayımlandı. Aktif sözleşme ve belgeler buna uyarlandı. Kaynak politikası 2 ve şema 5 korundu.

## Kalan gerçek sınırlar ve faz durumu

- Arşiv görünümlerinde yalnız dekoratif SVG doku efekti çıkarıldı; belge metni, düzen, logo, stil ve fontlar korunuyor. Etkin site işlevleri pasif arşivin parçası değildir.
- Güncel ulusal kesin hesap/bağımsız mali denetim sonucu bu düzeltmede elde edilmedi. Kocaeli haberinin hesap başlangıcı kesin gün olarak bilinmiyor; haberdeki tutarlar yıllık/ulusal mali toplam haline getirilmedi.
- **Faz 2 halen 2/10; sıradaki plan 02-03 hiç başlamadı.** TİP `stage=tracer`, `completed_prefix=[]`; yeni TİP tamamlama makbuzu yok. Ayrıntılı karşılaştırma ve kapsamlı mali araştırma sonraki fazlarda kalıyor. Model/maliyet ayarları değiştirilmedi.
- Engelleyici stub, atlanan test veya çalıştırılmamış zorunlu doğrulama yok. Yeni kullanıcı onayı ya da kimseye mesaj gönderme gereksinimi doğmadı.
- STATE'nin nihai quick-task satırı ve PLAN/SUMMARY/CHECKS metadata commit'i, orkestratörün açık görev paylaşımı gereği ana ajana bırakıldı.

## Self-Check: PASSED

Ana kod/veri commit'leri Git geçmişinde mevcut; yeni kaynak girdisi, iki görünüm, dokuz künye, nihai kapalı sürüm ve kamu artifact'leri bulunuyor. Eski baytlar, auditler, makbuzlar, boş teslim prefix'i ve yayımlı dosyaların digest eşitliği doğrulandı. Üç üretim görevi tamamlandı.
