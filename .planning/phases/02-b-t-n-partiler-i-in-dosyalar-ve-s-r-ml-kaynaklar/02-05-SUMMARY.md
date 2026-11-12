---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
plan: "05"
subsystem: kaynak derlemesi ve tam parti teslimi
tags: [iyi, kimlik, kronoloji, tuzuk, program, pasif-arsiv, makbuz]
requires:
  - phase: "02-04"
    provides: Tam DEM dosyası, korunmuş TİP ve Yeni Parti, zincirli makbuz
provides:
  - İYİ Parti için kaynaklı kart ve kuruluş, ilk yönetim ve ilk kurultay kronolojisi
  - 2020 ve 2026 değişiklikli tüzük kopyaları ve tam HTML program metni
  - Ayrı immutable yerel rapor, pasif kaynak görünümleri ve DEM’e bağlı makbuz
affects: [02-06, 02-07, 02-08, 02-09, 02-10]
tech-stack:
  added: []
  patterns: [PDF’nin kendi metninden yayıncı atfı, statik açılmış program panelleri, görsellerin fontlardan önce arşivlenmesi]
key-files:
  created:
    - data/dossiers/02-iyi.json
    - data/deliveries/02-05-iyi.json
    - data/releases/45fdfa3f6abe4a8882c52b2658fc6c6d/index.html
    - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-05-CHECKS.json
  modified: [src/kaynaklar.py, src/arsiv_gorunum.py, tests/test_source_policy.py, tests/test_archive_views.py, data/current.json]
key-decisions:
  - Sabit iyi kimliği korunarak TBMM sayfa anahtarı geçmişte bırakıldı ve gerçek yargitay-207 sicil anahtarına kontrollü geçildi.
  - Tüzük kapaklarının 2020 ve 2026 günleri işlenmiş değişiklik tarihleridir; PDF yayın günü veya bütün maddelerin yürürlük dönemi yapılmadı.
  - Tam program HTML’si parti yayını olarak kullanıldı; alınamayan PDF ve bilinmeyen program kabul/sürüm tarihi ayrı tutuldu.
requirements-completed: []
coverage:
  - id: IYI-SOURCES
    description: 21 özet/alıntı çiftinin kaynak anlamı, erken yönetim kronolojisi ve belge kapsamı
    verification: []
    human_judgment: true
    rationale: Kaynakların maddi anlamı faz sonu okumasında değerlendirilir; kaynak kullanımına yeni bir insan kabul kapısı konmaz.
  - id: IYI-INTEGRITY
    description: Tam dosya, tek parti prefix’i, yöntem kesimi ve önceki içeriklerin korunması
    verification:
      - kind: integration
        ref: python3 src/arsiv.py dossier-check --input data/dossiers/02-iyi.json
        status: pass
      - kind: integration
        ref: python3 src/arsiv.py audit --release current --phase 2 --party iyi
        status: pass
      - kind: integration
        ref: python3 src/arsiv.py audit --release current --phase 1
        status: pass
      - kind: other
        ref: 02-05-CHECKS.json#preservation
        status: pass
    human_judgment: false
  - id: IYI-READING
    description: Masaüstü/mobil rapor ve tam program okuması, doğru tüzük PDF bağlantısı
    verification:
      - kind: automated_ui
        ref: 02-05-CHECKS.json#browser
        status: pass
      - kind: integration
        ref: 02-05-CHECKS.json#pdf_http
        status: pass
    human_judgment: false
  - id: IYI-SOURCE-FIXES
    description: Sıkıştırılmış PDF atfı, statik paneller ve görsel/font bütçesi regresyonları
    verification:
      - kind: unit
        ref: tests/test_source_policy.py#test_compressed_pdf_publisher_text_does_not_need_host_html
        status: pass
      - kind: unit
        ref: tests/test_archive_views.py#test_static_panels_stay_readable_and_images_precede_font_budget
        status: pass
    human_judgment: false
  - id: IYI-RECEIPT
    description: DEM makbuzuna bağlı tam İYİ Parti teslimi
    verification:
      - kind: integration
        ref: python3 src/arsiv.py receipt-check --input data/deliveries/02-05-iyi.json
        status: pass
    human_judgment: false
actuals:
  tokens: null
  tasks: 3
  commits: 3
plan_head_before: c1520f2e2bbbcf6446848f16f0c9800d1e78f5ab
duration: 38min
completed: 2026-11-11
status: complete
---

# Phase 2 Plan 5: İYİ Parti kaynak dosyası özeti

**İYİ Parti’nin kimliği, kuruluş ve ilk yönetim adımları, iki tüzük kopyası ve tam HTML programı 21 kaynaklı özet/alıntı çiftiyle ayrı yerel rapor ve DEM’e bağlı makbuz olarak hazırlandı.**

## Teslim ve üç görev

- [Değişmez yerel rapor](../../../data/releases/45fdfa3f6abe4a8882c52b2658fc6c6d/index.html): `45fdfa3f6abe4a8882c52b2658fc6c6d`; şema **5**, kaynak politikası **2**, dosya doğrulama **2**, renderer **13**.
- [Tam makbuz](../../../data/deliveries/02-05-iyi.json), `02-04-dem.json` makbuzuna bağlıdır; `stage=complete`, `completed_prefix=['tip','dem','iyi']`, method-1 ve `2026-11-10T14:38:46.154751+00:00` kesimi korunur.
- [Kalıcı kontrol kaydı](02-05-CHECKS.json), denetimleri, gerçek Chromium sonuçlarını, PDF HTTP/hash kontrolünü ve **714 eski değişmez dosyanın** korunduğunu belgeler. Önceki tüm tablo satırları korunur; yalnız `iyi` parti satırının belgeli sicil geçişi kontrollü değişikliktir.

1. **Kaynak edinimi:** **295 yeniden uygulanabilir kayıt**, **14 kaynak sürümü**, **7 kart alanı** ve **4 kronoloji satırı** hazırlandı. Gerçek `/sipar/207` kaydında resmî ad ve kısa ad **İYİ PARTİ**, kuruluş günü **25.10.2017** olarak okundu. `yargitay-207` URL anahtarıdır; ayrıca verilmiş bir sicil numarası sayılmadı. Eski TBMM anahtarı kimlik geçmişinde kaldı. AA’nın 25 Ekim ilk yönetim seçimi, 27 Ekim görev dağılımı ve 10 Aralık ilk olağan kurultay haberleri yazar/tarihleriyle derlendi. Görev dağılımı haberinin yayın günü kesin karar günü yapılmadı. İncelenen kaynaklarda ad değişikliği veya aynı adlı ayrı tüzel kişilik notu gerektiren bir uç bulunmadı; araştırma kaydı bunu sınırlı tarama sonucu olarak tutar.
2. **Ayrı yerel rapor:** Girdi temiz `/tmp` workspace’ine yüklendi ve yalnız `publish --party iyi` ile tamamlandı. Kuruluş/Tüzük/Program altında **12/5/4 çift** vardır. Her biri **54 sayfalık** tüzüklerin kapakları, sırasıyla **20 Eylül 2020** ve **18 Ocak 2026** değişikliklerini işlediğini belirtir; bu günler PDF yayın gününe çevrilmedi. Üyelik, kurultay yetkileri ve temel program hedefleri kısa derlemelerle sunulur. Ayrıntılı karşılaştırma ve gerçekleşmiş mali araştırma yapılmadı.
3. **Zincirli teslim:** Makbuz gerçek rapor, prefix, kaynak sürümleri, içerik ve önemli açıklarla üretildi; bağımsız `receipt-check` **DELIVERY_RECEIPT_OK** verdi. Sonraki partiye geçilmedi. Kamu yayını veya `gh-pages` değişikliği yapılmadı.

## Doğrulama ve commit’ler

- Girdi **DOSSIER_INPUT_OK**, parti **PHASE2_PARTY_OK**, pilot **PHASE1_AUDIT_OK**, makbuz **DELIVERY_RECEIPT_OK** verdi.
- Kaynak politikası **12**, dosya sözleşmesi **10**, pasif arşiv **5** olmak üzere **27 test geçti**. İki gerçek dar hata için başarısız regresyon ve sonrasında başarılı kontrol alındı; veri planı genel bir TDD planına dönüştürülmedi.
- Chromium’da **1365 ve 360 px** rapor/program gezinmesi, kaynak açılması, siyah alıntı ve koyu mavi özetler, kapalı yöntem ayrıntıları ve doğru **2026 PDF** bağlantısı denetlendi. Programın **sekiz bölümü görünür**, **5/5 görseli yerel** ve bu okuma yolunda yatay taşma yoktur. PDF yanıtı `application/pdf` ve özgün SHA-256 ile aynıdır.
- Beş başlık, kart, kronoloji ve tüzük sürüm geçmişi gerçek HTML’de bulunur. Önceki Yeni Parti, TİP ve DEM kayıtları ve rapor üreticisi baytları korunur.

Görev commit’leri: **`7af3c05`** kaynak/girdi ve gerekli dar düzeltmeler; **`fa797a5`** denetlenmiş yerel sürüm; **`b20fb17`** makbuz ve kontrol kaydı. Üretim değişiklikleri **387 dosyadır**. Yaklaşık süre **38 dakika**; `actuals.tokens` gerçekleşen metinsel Git farkının karakter/4 ölçüsüdür ve arşivlenen HTML hacmini de içerir; model faturası veya harness token sayısı değildir. Commit sayısı kalıcı plan ledger’ından ölçüldü.

## Plandan sapmalar

**1. [Rule 1 — Bug] Sıkıştırılmış PDF’nin kendi yayıncı metni kabul edildi.** İstanbul tüzüğü alınabildiği halde aynı alanın HTML sayfaları 503 verdi. Önceki kontrol, PDF içindeki parti adını okumadan aynı alan üzerinde HTML dayanağı bekliyordu. `src/kaynaklar.py`, PDF’nin çıkarılmış metnindeki doğru parti adını da kabul eder; yanlış yayıncı reddedilir. Gerçek 2020 PDF’siyle regresyon önce başarısız oldu, düzeltmeden sonra geçti. `tests/test_source_policy.py`; commit `7af3c05`. Sicil kimliği kontrolü değişmedi.

**2. [Rule 1 — Bug] Scriptsiz programdaki kapalı paneller ve görsel önceliği düzeltildi.** Tarayıcı ilk pasif program kopyasında sekiz bölümün gizli kaldığını, fontların varlık bütçesini doldurduğunu gösterdi. `src/arsiv_gorunum.py`, yeni türevlerde panelleri statik açar ve görselleri fontlardan önce alır. `tests/test_archive_views.py` regresyonu ve gerçek program okuması geçti; commit `7af3c05`. Eski türevler ve özgün baytlar korunarak yeni görünüm kimlikleri oluşturuldu. Yeni paket, tablo, yayın bayrağı veya renderer sürümü eklenmedi.

Toplam **iki dar otomatik düzeltme**. İlk veri kontrollerinde yakalanan girişim bağlantısı, kaynak türü ve pasaj konumu eksikleri yayın öncesinde girdi içinde tamamlandı; kayıt atlanmadı.

## Kaynak açıkları ve görünüm sınırı

- **Tam program HTML’si edinildi; PDF indirmesine erişilemedi.** Üç eski merkez PDF yolu 404 verdi; ilgili WeTransfer bağlantısı PDF yerine JavaScript gerektiren sayfa döndürdü. Başka bir program kopyasıyla metin özdeşliği veya sürüm sırası varsayılmadı.
- Programın kabul/son değişiklik günü ve bütün tüzük ara sürümleri bilinmiyor. Kapaktaki değişiklik günleri bütün maddelerin eksiksiz yürürlük aralığı değildir.
- İlk görev dağılımının ayrı karar günü ile sicil/parti adreslerindeki cadde adlarının eşdeğerliği ve geçerlilik günleri açıklanmıyor; erişim günü bunların yerine kullanılmadı.
- **Kurumsal kadro sayfasının pasif görünümü sınırlıdır:** kaynak 364 görsel öğesi içerir; 40 varlık sınırı bütün portreleri taşımaz ve bu sayfada yatay taşma vardır. Bu, ana rapor/programın taşmasız okuma sonucundan ayrıdır. Özgün HTML tam korunur; tüzük PDF’si ve tam program metni okunabilir. Varlık ve dekoratif SVG/ikon/font sınırları manifestlerde ve CHECKS kaydındadır.
- Söylem–uygulama ve gerçekleşmiş finansman/harcamalar sonraki fazlar için **Henüz incelenmedi** durumundadır. Faz 2 **5/10** plandadır; dört ortak gereksinim bütün partiler tamamlanmadan bitmiş işaretlenmedi.

## Self-Check: PASSED

Girdi, immutable rapor, zincirli makbuz ve CHECKS dosyası diskte; üç üretim commit’i Git’te doğrulandı. Kesim, prefix, önceki içerikler ve kaynak zinciri geçti. `.gsd/` ve `.planning/milestone.lock` korundu. Ajan okuması insan kabulü sayılmadı. Sonraki plan **02-06 Yeni Yol Partisi**, bu teslimin kullanıcıya bildirilmesinden sonradır.
