---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
plan: "04"
subsystem: kaynak derlemesi ve tam parti teslimi
tags: [dem, kimlik, kronoloji, tuzuk, program, pasif-arsiv, makbuz]
requires:
  - phase: "02-03"
    provides: Tam TİP dosyası, kaynak politikası 2 ve zincirli önceki makbuz
provides:
  - DEM Parti için kaynaklı kart, kuruluş ve ad/kısa ad kronolojisi
  - İki tüzük kopyası, tarihsel program aktarımı ve ayrı programatik kongre belgesi
  - Ayrı immutable yerel rapor, dört pasif görünüm ve zincirli makbuz
affects: [02-05, 02-06, 02-07, 02-08, 02-09, 02-10]
tech-stack:
  added: []
  patterns: [Türkçe yayıncı adı normalizasyonu, aynı yayıncı ve ana makine üzerinde arşivli HTML dayanağı]
key-files:
  created:
    - data/dossiers/02-dem.json
    - data/deliveries/02-04-dem.json
    - data/releases/77074f17144b41399615da5ee4b37bcf/index.html
    - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-04-CHECKS.json
  modified: [src/kaynaklar.py, tests/test_source_policy.py, data/current.json]
key-decisions:
  - DEM’in sabit parti kimliği korundu; TBMM anahtarı geçmişte bırakılarak gerçek yargitay-157 siciline kontrollü geçiş yapıldı.
  - Sicilin 30 Kasım 2012 kuruluş günü ile haberlerin 25 Kasım kuruluş toplantısı ayrı tutuldu; HDP ayrı sicildir.
  - Güncel bağımsız program bulunamadı; tarihsel program aktarımı ve kongre kararı ayrı türlerle sunuldu.
requirements-completed: []
coverage:
  - id: DEM-SOURCES
    description: 23 kaynaklı özet/alıntı çiftinin anlamı, kimlik ayrımı ve belge kapsamı
    verification: []
    human_judgment: true
    rationale: Kaynakların maddi anlamı ve tarihsel yorum otomatik dosya bütünlüğünden ayrıdır; faz sonu okumasında değerlendirilir, kaynak kullanımına yeni bir kabul kapısı konmaz.
  - id: DEM-INTEGRITY
    description: Dosya yükleme, tek parti prefix’i ve önceki dosyaların korunması
    verification:
      - kind: integration
        ref: python3 src/arsiv.py dossier-check --input data/dossiers/02-dem.json
        status: pass
      - kind: integration
        ref: python3 src/arsiv.py audit --release current --phase 2 --party dem
        status: pass
      - kind: integration
        ref: python3 src/arsiv.py audit --release current --phase 1
        status: pass
    human_judgment: false
  - id: DEM-READING
    description: Masaüstü/mobil rapor, doğru belge bağlantıları ve pasif HTML görünümleri
    verification:
      - kind: automated_ui
        ref: 02-04-CHECKS.json#browser
        status: pass
    human_judgment: false
  - id: DEM-ATTRIBUTION
    description: Türkçe yayıncı adı ve aynı ana makinedeki kısa adlı yayın desteği
    verification:
      - kind: unit
        ref: tests/test_source_policy.py#test_turkish_publisher_case_preserves_dotted_and_dotless_i
        status: pass
      - kind: unit
        ref: tests/test_source_policy.py#test_short_name_html_uses_same_party_host_and_full_name_anchor
        status: pass
    human_judgment: false
  - id: DEM-RECEIPT
    description: TİP makbuzuna bağlı tam DEM teslimi
    verification:
      - kind: integration
        ref: python3 src/arsiv.py receipt-check --input data/deliveries/02-04-dem.json
        status: pass
    human_judgment: false
actuals:
  tokens: 1344644
  tasks: 3
  commits: 3
plan_head_before: e2982c163bf4757d2f056407b5f658d1ec34f736
duration: 26min
completed: 2026-11-11
status: complete
---

# Phase 2 Plan 4: DEM Parti tam kaynak dosyası özeti

**DEM Parti’nin kuruluşu, ad/kısa ad geçmişi, temel tüzük kuralları ve erişilebilen programatik metinleri 23 kaynaklı özet/alıntı çiftiyle ayrı yerel rapor ve zincirli makbuz olarak teslim edildi.**

## Teslim

- [DEM, TİP ve korunan Yeni Parti raporu](../../../data/releases/77074f17144b41399615da5ee4b37bcf/index.html): `77074f17144b41399615da5ee4b37bcf`; şema **5**, kaynak politikası **2**, dosya doğrulama **2**, renderer **13**.
- [Tam DEM makbuzu](../../../data/deliveries/02-04-dem.json), `02-03-tip.json` makbuzuna bağlıdır; `stage=complete`, `completed_prefix=['tip','dem']` ve mevcut method-1 kesimi korunur.
- [Kalıcı kontrol kaydı](02-04-CHECKS.json), denetim sonuçlarını, gerçek Chromium çıktısını, arşiv PDF’sinin HTTP/hash kontrolünü ve önceki dosyaların korunma kanıtını içerir.
- Kamu yayını yapılmadı. Bu plan İYİ Parti araştırmasına başlamadı; sıradaki plan **02-05**’tir.

## Tamamlanan üç görev

1. **Gerçek kaynak ve kimlik derlemesi:** Yargıtay `/sipar/157` kaydı, ayrı HDP `/sipar/154` kaydı, Adalet Bakanlığının AİHM çevirisi, tarihli parti açıklamaları ve atıflı kongre haberleri birlikte okundu. **16 kaynak sürümü**, **314 yeniden uygulanabilir kayıt**, **7 kart alanı**, **5 kronoloji olayı** ve **23 özet/alıntı çifti** hazırlandı. Beş zorunlu kart alanı kaynaklıdır. Sabit `dem` kimliği korunurken eski TBMM anahtarı `party_identity_revision` içinde bırakıldı; kapsam, Meclis gözlemleri, bireysel üyelik ve grup kayıtları değiştirilmedi.
2. **Ayrı yerel sürüm:** Girdi temiz workspace’e yüklendi ve yalnız `publish --party dem` ile yeni tam teslim üretildi. Kuruluş/Tüzük/Program başlıklarında sırasıyla **15/5/3 çift** vardır. Üyelik itirazı, öneri ve eleştiri hakları, Büyük Kongre yetkileri ve partinin temel amaçları kısa derlemelerle sunulur. **32 sayfalık HEDEP** ve **36 sayfalık DEM Parti** kısa adlı iki PDF aynı tüzük geçmişine belirsiz ilişkiyle bağlanır. Dört HTML parti yayını yerel stil/görsel kullanan pasif görünümde açılır; tüzük görünümü doğru arşiv PDF’sine gider.
3. **Zincirli teslim:** Makbuz gerçek rapor yolunu, 16 kaynak sürümünü, eklenen içeriği ve önemli açıkları taşır. Önceki TİP teslimine bağlanan `receipt-check` geçti. Yeni Parti ve TİP’in bütün mevcut içeriği korundu; söylem–uygulama ve gerçekleşmiş mali araştırma bu yeni dosyada **Henüz incelenmedi** kaldı.

Yargıtay kuruluşu **30 Kasım 2012** olarak verir. **25 Kasım 2012** kuruluş toplantısı ve ilk eş sözcüler, tarihli haberlerin kuruluş öncesi bağlamı olarak açıklandı; inceleme başlangıcı geriye alınmadı ve dönem dışı olay satırı yazılmadı. AİHM’nin 2022 kararındaki eski ad, 2023 ad değişikliği haberi ve bugünkü sicil ayrı kaynaklar olarak izlenir. HDP’nin ayrı sicili, siyasi ilişkiyi tüzel özdeşliğe çevirmemek için bağlam bulgusuna bağlandı; yardımcı parti veya yeni kapsam satırı oluşturulmadı.

Program bölümünde **2012 tarihli Agos aktarımı** ile partinin yayımladığı **4’üncü Olağanüstü Büyük Kongre Kararları** ayrı belge türleri olarak gösterilir. Kongre metni bağımsız güncel parti programı diye sunulmaz. Bugünkü Yeşil Sol sitesindeki 2024 metni, doğrudan metin/tüzel kimlik zinciri elde edilmediğinden DEM’e taşınmadı.

## Doğrulama

- Planın `dossier-check`, DEM parti audit’i, Faz 1 audit’i ve `receipt-check` komutları sırasıyla **DOSSIER_INPUT_OK**, **PHASE2_PARTY_OK**, **PHASE1_AUDIT_OK** ve **DELIVERY_RECEIPT_OK** verdi. Yayımlanmış current üzerinde aynı girdinin tekrar kontrolü de geçti.
- **10 dosya testi** ve **11 kaynak politikası testi**, toplam **21 test** geçti. TDD kaynak/veri işine uygulanmadı; ek iki test gerçek yayıncı/atıf hatalarını ve farklı alan adı/yayıncı reddini sınar. Yeni paket kurulmadı.
- Gerçek Chromium’da **1365px ve 360px**: DEM sekmesi, görünür kuruluş gerekçesi, kapalı kimlik/yöntem ayrıntıları, siyah alıntı/koyu mavi özet, kaynak tıklamaları ve iki ayrı doğru arşiv kontrol edildi. HTML arşivlerde **script=0**, **form=0**, bütün görseller yüklü, varlık istekleri yerel ve sayfa taşması yoktu. Raporun mobil ve kongre belgesinin masaüstü görüntüleri ayrıca görsel olarak okundu.
- Arşiv tüzük PDF’si HTTP **200 / application/pdf** verdi; indirilen baytların SHA-256 değeri kaynak sürümüyle eşleşti.
- Önceki sürümün **1.206 kaydı**, beklenen DEM sicil geçişi dışındaki bütün eski satırlar için aynen korundu. Önceki **630 nesne/görünüm/release dosyası** ile **15 renderer dosyasının** Git nesne özetleri değişmedi. Silinen dosya yoktur.
- Kod, test ve JSON girdisinde whitespace kontrolü geçti. Üretilen HTML’nin devraldığı özgün kaynak pasajlarındaki boşluklar normalize edilmedi; kaynak ve immutable sürüm baytları değişmedi.

Otomatik kontroller dosya, ilişki, atıf ve bağlantı bütünlüğünü sınar. Kaynağın maddi anlamı ayrı tutuldu; ajan incelemesi veya önceki pilot UAT’si yeni kaynaklar için insan kabulü diye sunulmadı. İçerik kullanımı için her kaynağa yeni insan onayı koşulu getirilmedi.

## Commit’ler

| Commit | Görev |
|---|---|
| `9de4984` | 02-04-01: DEM kaynakları, kart/kronoloji, tüzük/program derlemesi ve iki dar atıf düzeltmesi |
| `2b0d021` | 02-04-02: denetlenmiş tam DEM yerel sürümü |
| `78cba89` | 02-04-03: TİP’e bağlı makbuz ve kalıcı kontroller |

`actuals.tokens`, üç üretim commit’inin gerçekleşmiş Git diff karakterlerinin dörde bölünmesidir; kaynak/HTML/CSS/JSON kopyalarını içerir ve model kullanım token sayısı değildir. `actuals.commits`, kayıtlı başlangıç Git tabanından SUMMARY öncesi ölçülmüştür. Süre yaklaşık 26 dakikadır.

## Plandan sapmalar ve çözülen sorunlar

1. **[Rule 1 — Türkçe yayıncı adı]** Genel `casefold`, `HALKLARIN` ile `Halkların` içindeki **I/ı** farkını doğru normalleştirmediği için gerçek DEM yayını reddediliyordu. `folded` Türkçe **I→ı**, **İ→i** dönüşümünü koruyacak biçimde düzeltildi. Türkçe eşleşme ve farklı harfin reddi ayrı test edildi. Dosyalar: `src/kaynaklar.py`, `tests/test_source_policy.py`; commit `9de4984`.
2. **[Rule 1 — kısa adlı HTML yayını]** Tüzük bağlantı sayfası ve kongre metni yalnız **DEM Parti** kısa adını kullanıyordu. PDF için var olan destek, aynı partinin ve aynı ana makinenin tam adı taşıyan arşivli HTML yayınına dayanacak biçimde HTML için de uygulandı. Tam adını kendi ham baytlarında taşıyan dayanak zorunludur; başka yayıncı veya alan adı reddedilir. Sahiplik, sicil kimliği, kaynak türü, alıntı ve hash kuralları korunur. Aynı dosyalar ve commit; olumlu/olumsuz birim testi geçti.

İki dar hata otomatik giderildi; yeni API, tablo, bayrak veya bağımlılık eklenmedi. Engelleyici stub, atlanmış zorunlu kontrol veya açık uygulama hatası bırakılmadı.

## Gerçek kaynak açıkları ve faz sınırı

- **Bağımsız güncel tam parti programı bulunamadı.** Bu, belgenin var olmadığı iddiası değildir; 2012 aktarımı ve kongre kararı kendi tür ve dönemleriyle görünürdür.
- İki tüzüğün kesin kabul/değişiklik günleri ve yürürlük ilişkisi belirtilmiyor. Erişim günü belge tarihi yapılmadı.
- Sicilde **Oğuzlar/Balgat**, parti sayfasında **Barbaros/Çankaya** adresi vardır; hangisinin kesimde geçerli olduğu kaynaklardan ayırt edilemiyor.
- **2–3 Nisan 2016** kongresindeki kısa ad kararının kesin günü bilinmiyor; tek gün uydurulmadı.
- Söylem–uygulama ve gerçekleşmiş finansman/harcamalar sonraki fazlardadır. Faz 2 **4/10** plandadır; dört ortak gereksinim fazın bütün partileri tamamlanmadan bitmiş işaretlenmedi.

## Self-Check: PASSED

Girdi, immutable rapor, makbuz ve CHECKS dosyası diskte; üç üretim commit’i Git’te doğrulandı. Kesim, prefix, önceki içerik ve kaynak zinciri denetimleri geçti. `.gsd/` ve `.planning/milestone.lock` sahiplik dışı dosyalar olarak korundu. Üç görev tamamlandı; sonraki partiye geçiş bu teslimin kullanıcıya bildirilmesinden sonradır.
