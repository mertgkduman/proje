---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
plan: "06"
subsystem: kaynak derlemesi ve tam parti teslimi
tags: [yeni-yol, kimlik, ortak-grup, kronoloji, belge-eksikleri, pasif-arsiv, makbuz]
requires:
  - phase: "02-05"
    provides: Tam İYİ Parti dosyası, korunmuş önceki dosyalar ve zincirli makbuz
provides:
  - Yeni Yol için kaynaklı kimlik kartı, kuruluş/grup/yönetim kronolojisi ve ayrı eski tüzel kişilik açıklaması
  - Tüzük/program taslak onayı haberi ile gerçek aramalara bağlı tam belge, site ve kongre eksikleri
  - Sekiz seçilmiş kaynak sürümü, altı pasif HTML görünümü, ayrı immutable rapor ve İYİ Parti’ye bağlı makbuz
affects: [02-07, 02-08, 02-09, 02-10]
tech-stack:
  added: []
  patterns: [mevcut manual_passage ile taranmış kararın görselden okunması, ortak grup ile tüzel kimliğin ayrılması, kullanılmayan ham yanıtların açık envanteri]
key-files:
  created:
    - data/dossiers/02-yeni-yol.json
    - data/dossiers/02-yeni-yol-capture-notes.json
    - data/deliveries/02-06-yeni-yol.json
    - data/releases/732fcd2bfc954200b4292c51ef29f526/index.html
    - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-06-CHECKS.json
  modified: [data/current.json]
key-decisions:
  - Sabit yeni-yol kimliği korunarak TBMM sayfa anahtarı geçmişte bırakıldı; gerçek yargitay-331 kaydının YENİ YOL adı ve 13.01.2025 kuruluşuyla kontrollü geçiş yapıldı.
  - Parti tüzel kişiliği, ortak Meclis grubu ve tekil üyelik ayrı tutuldu; grup adına konuşmadan milletvekili üyeliği veya tüzel birleşme türetilmedi.
  - Aynı adlı eski parti kararı, güncel sicille iki kaynaklı açıklamada ayrıldı; tam tüzük/program bulunamadığında başka partinin belgeleri kullanılmadı.
requirements-completed: []
coverage:
  - id: YY-SOURCES
    description: Sicil kimliği, ortak grup, ayrı eski tüzel kişilik ve belge edinim sonuçlarının maddi anlamı
    verification: []
    human_judgment: true
    rationale: Kaynakların anlamı faz sonu değerlendirmesinde incelenir; kaynak kullanımına insan kabul kapısı eklenmedi.
  - id: YY-INTEGRITY
    description: Tam dosya, yöntem kesimi, tek parti prefix’i ve önceki içeriklerin korunması
    verification:
      - kind: integration
        ref: python3 src/arsiv.py dossier-check --input data/dossiers/02-yeni-yol.json
        status: pass
      - kind: integration
        ref: python3 src/arsiv.py audit --release current --phase 2 --party yeni-yol
        status: pass
      - kind: integration
        ref: python3 src/arsiv.py audit --release current --phase 1
        status: pass
      - kind: other
        ref: 02-06-CHECKS.json#preservation
        status: pass
      - kind: unit
        ref: python3 tests/run.py --pattern test_dossiers.py
        status: pass
    human_judgment: false
  - id: YY-READING
    description: Masaüstü/mobil rapor, doğru kaynak arşivleri, renkler ve karar PDF’sinin HTTP/hash kontrolü
    verification:
      - kind: automated_ui
        ref: 02-06-CHECKS.json#browser
        status: pass
      - kind: integration
        ref: 02-06-CHECKS.json#pdf_http
        status: pass
    human_judgment: false
  - id: YY-RECEIPT
    description: İYİ Parti teslimine bağlı tam Yeni Yol makbuzu
    verification:
      - kind: integration
        ref: python3 src/arsiv.py receipt-check --input data/deliveries/02-06-yeni-yol.json
        status: pass
    human_judgment: false
actuals:
  tokens: null
  tasks: 3
  commits: 3
plan_head_before: d5e756cd7afe2410fde32504800e7d9dd5210e36
duration: 37min
completed: 2026-11-11
status: complete
---

# Phase 2 Plan 6: Yeni Yol kaynak dosyası özeti

**Yeni Yol’un sicil kimliği, ortak Meclis grubu, kuruluş/yönetim kayıtları ve aynı adlı eski partiyle ayrımı 13 kaynaklı özet/alıntı çiftiyle ayrı rapor ve İYİ Parti’ye bağlı makbuz olarak hazırlandı; bulunamayan tam tüzük, program ve site adresi gerçek aramalarla açık bırakıldı.**

## Teslim ve üç görev

- [Değişmez yerel rapor](../../../data/releases/732fcd2bfc954200b4292c51ef29f526/index.html): `732fcd2bfc954200b4292c51ef29f526`; şema **5**, kaynak politikası **2**, dosya doğrulama **2**, renderer **13**.
- [Makbuz](../../../data/deliveries/02-06-yeni-yol.json), `02-05-iyi.json` makbuzuna bağlıdır. `stage=complete`, prefix **tip, dem, iyi, yeni-yol**, method-1 ve **2026-11-10T14:38:46.154751+00:00** kesimi korunur.
- [Kontrol kaydı](02-06-CHECKS.json), otomatik denetimleri, gerçek Chromium sonuçlarını, PDF HTTP/hash kontrolünü ve **1.078 eski değişmez dosyanın** korunmasını belgeler. Önceki tablo satırları korunur; yalnız `yeni-yol` parti satırının belgeli kimlik geçişi kontrollü değişikliktir.

1. **Kaynak edinimi:** [Girdi](../../../data/dossiers/02-yeni-yol.json) **220 kayıt**, **8 seçilmiş kaynak sürümü**, **7 kart alanı**, **3 tarihli kronoloji kaydı**, **6 pasif HTML görünümü** taşır. Beş zorunlu kart alanından dördü sicille, site alanı gerçek aramalı eksikle karşılanır; başkan ve merkez bilgisi ayrıca kaynaklıdır. Gerçek `/sipar/331` kaydında ad/kısa ad **YENİ YOL**, kuruluş **13.01.2025**, başkan **İZZETTİN KÜÇÜK** olarak okundu. `yargitay-331` URL anahtarıdır; ayrıca açıklanmış bir sicil numarası sayılmadı. Eski TBMM anahtarı kimlik geçmişinde kaldı.
2. **Ayrı yerel rapor:** Temiz workspace’e yükleme ve yalnız `publish --party yeni-yol` ile yeni parti teslimi yapıldı. Kuruluş/Tüzük/Program altında **11/1/1 çift** vardır. DHA’nın hazırlık anlatımı, Kaya’nın **15 Ocak 2025** Meclis konuşması ve **13 Ocak 2026** yönetim devrini aktaran Millî Gazete haberi yayıncı/yazar/tarihiyle derlendi. Grup adına konuşma tekil üyeliğe, ortak grup tüzel birleşmeye, hazırlık günü hukuki kuruluş gününe çevrilmedi. Kaynakta doğrulanmayan ilk yönetim seçim günü veya ilk kongre olayı yazılmadı.
3. **Zincirli teslim:** Gerçek rapor ve kaynak sürümlerinden makbuz üretildi; bağımsız `receipt-check` **DELIVERY_RECEIPT_OK** verdi. Makbuz, eklenen içeriği ve site/tüzük/program/kongre açıklarını taşır. Kamu yayını ve `gh-pages` değişmedi; DBP çalışması başlatılmadı.

## Kaynak anlamı ve belge sınırı

- **Tam tüzük ve program bulunamadı.** KARAR’ın **10 Ocak 2025** haberi taslakların onaylandığını söyler; bu, tam belgelerin edinildiği anlamına gelmez. Bu nedenle tüzük maddeleri, program hedefleri, kabul/değişiklik günleri ve sürüm geçmişi üretilmedi. DEVA, Gelecek ve Saadet belgeleri Yeni Yol belgesi sayılmadı.
- **Aynı adlı eski parti ayrıldı.** Resmî Gazete’den alınan AYM **E.2023/3 (Değişik İşler), K.2023/10** kararı **30 Kasım 2023** tarihlidir; yayın günü **19 Ocak 2024**’tür. Üç taranmış sayfa görsel olarak okundu ve iki kısa pasaj mevcut `manual_passage` yoluyla kaydedildi. III/4’teki **4/5/2020** kuruluşu ile güncel **13.01.2025** sicili ayrı gösterildi. III/6’daki **4/5/2000** yazımı iç tutarsızlık olarak araştırma kaydında tutuldu; yeni tarih veya güncel parti geçmişi yapılmadı. Kimlik açıklaması mevcut bulgu ve iki kaynak kanıt zincirinde sunuldu; kapsam listesine yardımcı parti eklenmedi.
- Bağımsız **resmî site**, ilk büyük kongreye ilişkin doğrudan belge, ilk başkanın kesin seçim günü ve tam ilk kurucu kurul bu taramada elde edilmedi. Bilinmeyen dönemler erişim günüyle doldurulmadı.
- Söylem–uygulama ve gerçekleşmiş finansman/harcamalar sonraki fazlar için **Henüz incelenmedi** durumundadır. Ayrıntılı karşılaştırma yapılmadı; dört ortak gereksinim bütün partiler tamamlanmadan bitmiş işaretlenmedi.

## Doğrulama ve commit’ler

- Önceki İYİ Parti makbuzu başlangıçta doğrulandı; önceki immutable parti audit’i **PHASE2_PARTY_OK** verdi.
- Yeni girdi **DOSSIER_INPUT_OK**, parti **PHASE2_PARTY_OK**, pilot **PHASE1_AUDIT_OK**, makbuz **DELIVERY_RECEIPT_OK** verdi. Mevcut dosya sözleşmesinin **10 testi geçti**. Yeni test, bağımlılık, tablo, bayrak veya üretim kodu eklenmedi.
- Chromium’da **1365 ve 360 px** rapor ve kaynak okuması denetlendi: amaç metni önde, yöntem kapalı, alıntı siyah, özet koyu mavidir. Sicil ve tutanak bağlantıları doğru pasif kopyalara; ayrı eski parti açıklaması doğru özgün PDF’ye açılır. Rapor, sicil ve tutanak okumasında yatay taşma yoktur. Pasif kaynaklarda script/form yoktur; yüklenen varlıklar yereldir. PDF yanıtı `application/pdf` ve SHA-256 özgünle aynıdır.
- **Görünüm sınırı:** Sicil görünümünde parti amblemi; TBMM ve haber görünümlerinde bazı logo/ikon/font/görseller alınamadı veya desteklenmedi. Metin ve özgün baytlar korunur. Bütün görsellerin taşındığı iddia edilmez; ayrıntılar manifestlerde ve CHECKS kaydındadır.

Görev commit’leri: **`bf711a3`** kaynak girdisi ve arşivler; **`19e232a`** denetlenmiş rapor; **`7ff3e75`** makbuz, kontrol kaydı ve ek ham yakalama notu. Üretim değişiklikleri **128 dosyadır**. Yaklaşık süre **37 dakika**; `actuals.tokens`, gerçekleşen metinsel Git farkının UTF-8 replacement çözümlemesi sonrası karakter/4 ölçüsüdür; model faturası veya harness token sayısı değildir. Commit sayısı kalıcı plan ledger’ından ölçüldü.

## Plandan sapma ve yakalama kaydı

Üretim kodunda sapma veya otomatik düzeltme yoktur. Ek bir [ham yakalama notu](../../../data/dossiers/02-yeni-yol-capture-notes.json) oluşturuldu: ilk ek taramada iki capture dizisinin aynı geçici metadata dosyasını kullanması, **bulgularda kullanılmayan iki ön HTML yanıtının** ilk erişim metadata satırlarının kaybolmasına yol açtı. Sonraki diziler sırayla çalıştırıldı. Özgünler değişmeden korundu; hash, HTML’nin kanonik adres beyanı ve sonraki capture bağlantısı kaydedildi. Kaybolan erişim saati uydurulmadı; dosya mtime bilgisi erişim/yayın günü sayılmadı. Bu iki ön yanıt teslimin sürüm geçmişi veya bulgu dayanağı olarak gösterilmez. Teslimdeki sekiz seçilmiş sürümün atıf/erişim kayıtları tamdır.

Bu açık kayıt, araştırma sınırıdır; işlevi engelleyen bir placeholder veya atlanmış otomatik kontrol yoktur. Kaynağın maddi doğruluğunun insan değerlendirmesi faz sonuna aittir; ajan okuması insan kabulü sayılmadı.

## Self-Check: PASSED

Girdi, ek yakalama notu, immutable rapor, makbuz ve CHECKS dosyası diskte; üç üretim commit’i Git’te doğrulandı. Kesim, prefix, önceki içerikler ve kaynak/rapor hash zinciri geçti. `.gsd/` ve `.planning/milestone.lock` korundu. Faz 2 **6/10** plandadır; sonraki plan **02-07 DBP**, bu teslimin kullanıcıya bildirilmesinden sonradır.
