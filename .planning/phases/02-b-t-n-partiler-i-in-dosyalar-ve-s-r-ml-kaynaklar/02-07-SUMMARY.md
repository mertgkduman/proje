---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
plan: "07"
subsystem: kaynak derlemesi ve tam parti teslimi
tags: [dbp, bdp, kimlik, kronoloji, tuzuk, program, utf8, pasif-arsiv, makbuz]
requires:
  - phase: "02-06"
    provides: Tam Yeni Yol dosyası, korunmuş önceki partiler ve zincirli makbuz
provides:
  - DBP için kaynaklı yedi alanlı kart, beş tarihli kuruluş/ad/yönetim olayı ve günü bilinmeyen kurucu başkan kaydı
  - 2025 değişiklikli tam parti tüzüğü, tarihsiz DBP tüzük taraması ve açık atıflı tarihsel BDP belge kopyaları
  - Ayrı immutable DBP raporu ve Yeni Yol makbuzuna bağlı doğrulanmış tam teslim
  - Eski http-equiv kaynaklarında Türkçeyi koruyan erken UTF-8 bildirimi ve regresyon testi
affects: [02-08, 02-09, 02-10, 03]
tech-stack:
  added: []
  patterns: [açık BDP–DBP belge bağlantısı, günü bilinmeyen kurucu yönetim kaydı, özgün baytları koruyan UTF-8 türevi]
key-files:
  created:
    - data/dossiers/02-dbp.json
    - data/deliveries/02-07-dbp.json
    - data/releases/4a4ce5448c894a9ebc3c12e97cacb6dd/index.html
    - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-07-CHECKS.json
  modified: [data/current.json, src/arsiv_gorunum.py, tests/test_archive_views.py]
key-decisions:
  - Sabit dbp kimliği korunarak eski TBMM anahtarı gerçek yargitay-117 siciline kontrollü geçirildi; kuruluş 02.05.2008 olarak kaynaklandı.
  - BDP–DBP bağı 11 Temmuz 2014 ad değişikliği haberi ve DBP tüzüğünün BDP tüzüğünü kaldıran 112. maddesiyle açıkça belgelendi; başka partilere tüzel birleşme çıkarılmadı.
  - Tarihsel BDP program kopyaları açık yayıncı atfıyla derlendi; ayrı güncel DBP programı ve bilinmeyen belge tarihleri açık bırakıldı.
  - Pasif türeve erken UTF-8 bildirimi eklendi; altı yeni DBP görünümü yeni hashlerle üretildi, ilk aday ve eski görünümler korunarak son Yeni Yol tabanından tekrar yayımlandı.
requirements-completed: []
coverage:
  - id: DBP-SOURCES
    description: Sicil, ilk kongre, BDP–DBP bağı ve tarihsel belge kopyalarının maddi anlamı
    verification: []
    human_judgment: true
    rationale: Kaynakların anlamı faz sonu değerlendirmesinde incelenir; kaynak kullanımına her belge için insan kabul kapısı eklenmedi.
  - id: DBP-INTEGRITY
    description: Tam dosya, tek parti prefix'i, yöntem kesimi ve önceki içeriklerin korunması
    verification:
      - {kind: integration, ref: 'python3 src/arsiv.py dossier-check --input data/dossiers/02-dbp.json', status: pass}
      - {kind: integration, ref: 'python3 src/arsiv.py audit --release current --phase 2 --party dbp', status: pass}
      - {kind: integration, ref: 'python3 src/arsiv.py audit --release current --phase 1', status: pass}
      - {kind: other, ref: '02-07-CHECKS.json#preservation', status: pass}
      - {kind: unit, ref: 'python3 tests/run.py --pattern test_dossiers.py', status: pass}
    human_judgment: false
  - id: DBP-READING
    description: Masaüstü/mobil kaynak gezinmesi, UTF-8, metin renkleri ve doğru özgün PDF
    verification:
      - {kind: automated_ui, ref: '02-07-CHECKS.json#browser', status: pass}
      - {kind: integration, ref: '02-07-CHECKS.json#pdf_http', status: pass}
      - {kind: unit, ref: 'tests/test_archive_views.py#test_utf8_is_declared_early_for_legacy_meta_and_headless_fragments', status: pass}
    human_judgment: false
  - id: DBP-RECEIPT
    description: Yeni Yol teslimine bağlı tam DBP makbuzu
    verification:
      - {kind: integration, ref: 'python3 src/arsiv.py receipt-check --input data/deliveries/02-07-dbp.json', status: pass}
    human_judgment: false
actuals:
  tokens: null
  tasks: 3
  commits: 4
plan_head_before: a3dc768708bf22f66851f63908ed26eb2287e782
duration: 50min
completed: 2026-11-11
status: complete
---

# Phase 2 Plan 7: DBP kaynak dosyası özeti

**DBP’nin sicil kimliği, kuruluş/ilk kongre/ad değişikliği kronolojisi ve tüzük/program edinim sonuçları 20 kaynaklı özet/alıntı çiftiyle ayrı rapor ve Yeni Yol’a bağlı makbuz olarak hazırlandı; tarihsel BDP kopyaları güncel DBP programından açıkça ayrıldı.**

## Teslim ve üç görev

- [Değişmez yerel rapor](../../../data/releases/4a4ce5448c894a9ebc3c12e97cacb6dd/index.html): **`4a4ce5448c894a9ebc3c12e97cacb6dd`**. Şema **5**, kaynak politikası **2**, dosya doğrulama **2**, renderer **13** korunur.
- [Makbuz](../../../data/deliveries/02-07-dbp.json), **02-06-yeni-yol.json** makbuzuna bağlıdır. `stage=complete`; prefix **tip, dem, iyi, yeni-yol, dbp**; method-1 ve **2026-11-10T14:38:46.154751+00:00** kesimi değişmedi.
- [Kontrol kaydı](02-07-CHECKS.json), gerçek Chromium sonuçlarını, kaynak/PDF hash denetimlerini ve **1.201 önceki değişmez dosyanın** korunmasını belgeler. Eski tablo satırları korunur; yalnız DBP parti satırının belgeli sicil geçişi kontrollü değişikliktir.

1. **Kaynak edinimi:** [Girdi](../../../data/dossiers/02-dbp.json) **275 kayıt**, **11 seçilmiş kaynak sürümü**, **7 kart alanı**, **6 kronoloji kaydı** ve **10 seçilmiş pasif HTML görünümü** taşır. Beş zorunlu alan kaynaklıdır. Sicil `/sipar/117`, ad/kısa ad **DEMOKRATİK BÖLGELER PARTİSİ / DBP**, kuruluş **02.05.2008**, başkanlar **Keskin Bayındır ve Çiğdem Kılıçgün Uçar** ve merkez adresiyle okundu. `yargitay-117` adres anahtarıdır; ayrıca açıklanmış bir numara sayılmadı. Eski TBMM anahtarı ve kapsam gözlemleri geçmişte kaldı.
2. **Ayrı yerel rapor:** Son Yeni Yol sürümünden açılan temiz workspace’e girdi yüklendi ve yalnız **publish --party dbp** çalıştırıldı. Kuruluş/Tüzük/Program altında **13/5/2 çift** vardır. Kuruluş, **7 Eylül 2008** ilk kongresi ve **11 Temmuz 2014** ad/kısaltma/yönetim kayıtları ayrı gösterilir. Kurucu başkan Mustafa Ayzit kaynaklıdır; ayrı seçim/atama günü belirtilmediğinden o kayıt **tarihi bilinmiyor** kaldı. Beş tarihli kayıt vardır; bilinmeyen güne tarih uydurulmadı.
3. **Zincirli teslim:** Gerçek son rapordan üretilen DBP makbuzu bağımsız **receipt-check** ile **DELIVERY_RECEIPT_OK** verdi. Eklenen kart/kronoloji/belge kaynakları ve önemli eksikler makbuzdadır. Kamu yayını ve `gh-pages` değiştirilmedi; sıradaki parti çalışmasına geçilmedi.

## Kaynak anlamı ve sınırlar

- **BDP–DBP bağlantısı açık metinle desteklidir.** Şemdinli Haber ve Evrensel’in olay günlü **11 Temmuz 2014** haberleri ad/kısaltma ve eş başkan seçimini anlatır. Yargıtay alanından alınan **49 sayfalık** DBP tüzüğünün son sayfasındaki **112. madde**, BDP tüzüğünü yürürlükten kaldırır. İlk iki ve son sayfa görsel okundu; iki kısa pasaj mevcut `manual_passage` yoluyla kaydedildi. Tüm PDF’ye OCR veya ayrıntılı madde analizi yapıldığı iddia edilmez. DTP, HDP ve DEM Parti ile hukuki birleşme sonucu çıkarılmadı.
- **Partinin tam HTML tüzüğü edinildi.** Başlığı **12 Ocak 2025 tarihli 7. Olağan Kongre değişikliklerini** belirtir; metin **114. maddeye** kadar erişilir. Kısa özet, amaçlar, üyelik hakları ve yönetimin kongrede seçilmesini anlatır. Bu gün web sayfasının yayın günü olarak kullanılmadı. Tarihsiz Yargıtay taramasının kabul/son değişiklik günü ve kesin sürüm sırası bilinmiyor.
- **Ayrı güncel DBP programı bulunamadı.** WordPress’te Barış ve Demokrasi Partisi adıyla ve Blogspot’ta BDP adıyla yayımlanan tarihsel program kopyaları tam metin bağlantılarıyla derlendi. Yeni anayasa/haklar, barışçı çözüm, kadın eşitliği, emek, ekoloji, yerinden yönetim, ekonomik ve sosyal politika başlıkları kopyalara atfedildi. Blogların kurumsal sahipliği, kabul/son değişiklik günleri ve güncel DBP programıyla ilişkisi bilinmiyor; iki kopya **related** ilişkisinde, öncelik sırası uydurulmadan gösterilir. Tüzük sayfası ayrı program yerine geçirilmedi.
- **Kuruluş dilekçesi, tam kurucu kurul ve ilk kongrenin doğrudan tutanağı bulunamadı.** Millî Gazete’nin **7 Aralık 2009** tarihli Haber Merkezi haberi kurucu başkanı ve ilk kongreyi anlatır; adı geçen bazı kurucular tam liste sayılmadı. Mevcut yönetim sayfaları kesin görev başlangıcı vermez.
- Söylem–uygulama ve gerçekleşmiş finansman/harcamalar **Henüz incelenmedi** durumundadır. Ayrıntılı tüzük/program karşılaştırması yapılmadı. Ortak dört gereksinim, diğer parti planları tamamlanmadan tamamlandı işaretlenmedi.

## Doğrulama ve commit’ler

Önceki Yeni Yol makbuzu **DELIVERY_RECEIPT_OK**, değişmez raporu **PHASE2_PARTY_OK** verdi. Düzeltilmiş yeni girdi **DOSSIER_INPUT_OK**, son parti **PHASE2_PARTY_OK**, pilot **PHASE1_AUDIT_OK**, makbuz **DELIVERY_RECEIPT_OK** verdi. Dosya sözleşmesinin **10 testi** ile arşiv görünümünün **6 testi** geçti. Yeni bağımlılık, tablo veya bayrak eklenmedi; veri, alıntı ve hash denetimi gevşetilmedi.

Chromium’da **1365 ve 360 px** okuması yapıldı: amaç metni önde, yöntem kapalı, alıntılar siyah ve özetler koyu mavidir. Sicil, tüzük ve tarihsel program doğru pasif kopyalara; DBP–BDP tüzük bağlantısı doğru özgün PDF’ye açılır. Üç HTML kaynakta **UTF-8**, script/form yokluğu, yerel varlıklar ve yatay taşma yokluğu denetlendi. PDF yanıtı **application/pdf** ve SHA-256 özgünle aynıdır. Otomatik başarı maddi kaynak doğruluğunun insan kabulü değildir.

**Görünüm sınırı:** Bazı SVG logolar, dış tema/avatar varlıkları ve görseller alınamadı. TBMM’nin çok sayıda gezinme görseli için kalan yakalamalarda yeni varlık denemeleri **12 adresle** sınırlandı; özgün HTML ve tam metin korundu. Tüzüğün bazı özgün paragraf biçimleri masaüstünde yan sütuna uzanır; mobil akış ve ana rapor okunur. Bu sınırlar CHECKS ve görünüm manifestlerinde korunur; piksel eşdeğerliği iddia edilmez.

Görev commit’leri: **`0244d21`** kaynak girdisi/arşivler; **`0b4b076`** denetlenmiş rapor; **`ef623c5`** zincirli makbuz ve kontrol kaydı. Ek hata düzeltmesi **`88eb43a`**. Üretim değişiklikleri **262 dosyadır**. Süre yaklaşık **50 dakika**; `actuals.tokens` gerçekleşen metinsel Git farkının UTF-8 replacement çözümlemesi sonrası karakter/4 ölçüsüdür, model faturası veya harness token sayısı değildir. Commit sayısı kalıcı plan ledger’ından ölçüldü.

## Plandan sapma: düzeltilen karakter kodlaması

**[Rule 1 — Bug]** Gerçek tarayıcı kontrolü, WordPress’in eski `http-equiv Content-Type` bildiriminin pasif kopyada temizlenirken UTF-8 bildiriminin kaybolduğunu gösterdi. Türkçe karakterler bozuluyordu. `build_view`, ürettiği UTF-8 metnin kodlamasını uzun başlık/stillerden önce açıkça bildirir. Yeni regresyon, eski meta biçimini ve başlıksız HTML parçasını kapsar: düzeltme öncesi iki alt durum başarısız, düzeltme sonrası altı arşiv testi başarılıdır.

Altı etkilenen DBP görünümü aynı özgün baytlardan ve daha önce alınmış yerel varlıklardan yeni hashlerle üretildi. İlk **679d9709aefd40fc8c5061387a675101** adayı ve eski görünüm baytları korunur; bu aday makbuz almadı. Yerel pointer son teslim edilmiş Yeni Yol’a atomik olarak döndürülüp yeni temiz workspace’ten **4a4ce5448c894a9ebc3c12e97cacb6dd** üretildi. Nihai makbuz yalnız bu düzeltilmiş rapora bağlıdır. Bu, planın hata sonrası son denetlenmiş tabandan yeniden üretim yoludur; kabul sözleşmesi veya önceki release’ler değiştirilmedi.

İlk girdi kontrolünde, sicil ile parti yönetim yayını birlikte kullanılan başkan özetinin atıflı `claim` kökeni de düzeltildi; kayıt doğrulayıcıları değiştirilmedi. Atlanmış otomatik kontrol veya hedefi engelleyen bir placeholder yoktur. Yeni güvenlik yüzeyi eklenmedi.

## Self-Check: PASSED

Girdi, son rapor, makbuz ve CHECKS diskte; dört üretim commit’i Git’te doğrulandı. Önceki 1.201 değişmez dosya, eski aday/görünümler, yöntem kesimi, prefix ve makbuz zinciri korundu. `.gsd/` ve `.planning/milestone.lock` yerinde bırakıldı. Faz 2 **7/10** plandadır; sonraki plan **02-08 EMEP**, DBP tesliminin kullanıcıya bildirilmesinden sonradır.
