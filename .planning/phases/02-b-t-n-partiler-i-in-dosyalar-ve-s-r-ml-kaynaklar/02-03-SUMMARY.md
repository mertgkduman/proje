---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
plan: "03"
subsystem: kaynak derlemesi ve tam parti teslimi
tags: [tip, kaynak, sqlite, html, pasif-arsiv, makbuz]
requires:
  - phase: "02-02"
    provides: TİP kuruluş tracer'ı, kart/künye sözleşmesi ve önceki makbuz
  - phase: "quick-261111-epm"
    provides: D-13–D-16, kaynak politikası 2 ve Yeni Parti içerik düzeltmesi
provides:
  - TİP için tam Faz 2 dosyası, kaynaklı kart ve kuruluş araştırması
  - Tüzük/program ve erken parti yayınlarının özgün kopyaları ile dört pasif HTML görünümü
  - Korunan Yeni Parti kart/künye uyarlaması ve zincirli tam teslim makbuzu
affects: [02-04, 02-05, 02-06, 02-07, 02-08, 02-09, 02-10]
tech-stack:
  added: []
  patterns: [atıflı parti yayını, girişime bağlı tekrar yükleme, yerel statik varlık arşivi]
key-files:
  created:
    - data/dossiers/02-tip.json
    - data/dossiers/02-yeni-parti.json
    - data/deliveries/02-03-tip.json
    - data/releases/7d5f78dde79a4b0bb48f64a16fd263c1/index.html
    - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-03-CHECKS.json
  modified: [src/dosyalar.py, src/kaynaklar.py, src/arsiv_gorunum.py, tests/test_dossiers.py, tests/test_source_policy.py, tests/test_archive_views.py, README.md, data/current.json]
key-decisions:
  - TİP tam dosyası completed_prefix=['tip'] ile teslim edildi; söylem/uygulama ve mali araştırma sonraki fazlar için Henüz incelenmedi kaldı.
  - Parti yayınları yayıncı/URL atfıyla kullanıldı; sicil alan adı, kesin yürürlük veya her kaynak için insan kabulü ön koşulu aranmadı.
  - İlk yerel aday değiştirilmeden korundu; CSS düzeltmesi sonrası nihai sürüm temiz kabul edilmiş tabandan üretildi.
requirements-completed: []
actuals:
  tokens: 1778034
  tasks: 3
  commits: 3
plan_head_before: a64e1f708aee3bdf14974b1faffcee8127a60843
duration: 26min
completed: 2026-11-11
status: complete
---

# Phase 2 Plan 3: TİP tam kaynak dosyası özeti

**TİP’in kuruluş gerekçesi, kartı, tüzük/program içeriği ve erişilebilen belge geçmişi 16 kaynaklı özet/alıntı çiftiyle ayrı, denetlenmiş yerel sürüm ve zincirli makbuz olarak teslim edildi.**

## Teslim

- [TİP ve korunan Yeni Parti raporu](../../../data/releases/7d5f78dde79a4b0bb48f64a16fd263c1/index.html) — değişmez sürüm `7d5f78dde79a4b0bb48f64a16fd263c1`; şema **5**, kaynak politikası **2**, dosya doğrulama **2**, renderer **13**, `stage=complete`, `completed_prefix=['tip']`.
- [Tam teslim makbuzu](../../../data/deliveries/02-03-tip.json), değişmeyen `02-02-tip-sources.json` makbuzuna bağlıdır; kesim `2026-11-10T14:38:46.154751+00:00` olarak korunmuştur.
- [Makine denetimi](02-03-CHECKS.json) test sayıları, tarayıcı sonuçları ve eski dosyaların korunma kanıtını içerir.
- Kamu yayını yapılmadı; GitHub Pages düzeltmesinin önceki sürümü aynı adresinde kalır. Sonraki parti DEM’dir; bu plan DEM araştırmasına başlamadı.

## Tamamlanan üç görev

1. **Gerçek kaynak derlemesi:** Mevcut Yargıtay `/sipar/208` kaydı, parti tüzüğü, parti programı, **6 Ekim 2018 İlerici Kamuoyuna** açıklaması, genel başkan biyografisi, **Kasım 2018 ÇarkBaşak sayı 1** ve **2022 dosya adlı tüzük PDF’si** okundu. Altı yeni kaynak yakalaması ile önceki sicil/tüzük sürümleri toplam sekiz dosya kaynağına bağlandı. TİP girdisi **201 kayıt** taşır; her yeni bulguda yayıncı atfı, özgün pasaj, özet/alıntı çifti, kanıt ve ajan incelemesi vardır. Sicildeki **7 Kasım 2017** kuruluşu korunur; resmî ad, TİP kısaltması, URL’den türetilen sicil anahtarı ve **https://tip.org.tr** kart alanlarına bağlanır. Kurucu başkan anlatımı ve kaynakta yayımlanan merkez adresi, bilinmeyen geçerlilik günü uydurulmadan sunulur.
2. **Ayrı tam sürüm:** Yeni Parti’nin **37 kayıtlık** kart/künye uyarlaması önce, TİP girdisi sonra temiz workspace’e yüklendi. Pilotun beş kaynaklı kart alanı ve önemli içeriği yeniden kullanılabildi; önceki bulgu, kanıt, inceleme, eksik/çözüm ve mali satırların tamamı korundu. TİP’in Kuruluş/Tüzük/Program başlıklarında **9/3/4 özet–alıntı çifti** vardır. Üyelik/oy/itiraz hakları, Kongre yetkileri, parti içi tartışma, sosyalizm ve kamucu ekonomi, temel sosyal haklar ve ekoloji kısa parti yayını derlemeleri olarak görünür. Söylem–uygulama ve finansman–harcamalar **Henüz incelenmedi** kalır; yapılmamış araştırma için sahte eksik veya girişim yazılmadı.
3. **Zincirli makbuz:** Tam makbuz gerçek rapor yolunu, eklenen içeriği, sekiz kaynak sürümünü ve gerçek açıkları taşır. `receipt-check` makbuz/prefix/hash/kesim ve önceki teslim zincirini geçti. Kamu dalı, kapsam listesi veya yöntem kesimi değiştirilmedi.

Tüzük ve programın yeni HTML kopyaları ile kuruluş açıklaması ve biyografi, yerel stil/font/görseller kullanan **dört pasif görünüm** üzerinden açılır. Tüzük/program bağlantıları farklı doğru belgelere gider. PDF’nin Türkçe kapak başlığı özgün sayfanın Poppler/Cairo görüntüsünden okundu ve `manual_passage` kaydıyla açıklandı; sorunlu metin katmanından görünmeyen bir kabul tarihi türetilmedi. 2014 TKP kongre belgeleri içeren ayrı Komünist sayı 1 araştırma sırasında dışlandı; 2017 TİP tüzel kişisine kaynak sürümü olarak yüklenmedi.

## Doğrulama

- Her iki girdi için planın tam `dossier-check` komutu **DOSSIER_INPUT_OK** verdi; yayımlanmış nihai snapshot üzerinde tekrar kontrol de geçti.
- Nihai sürüm **PHASE2_PARTY_OK** ve **PHASE1_AUDIT_OK** aldı; makbuz **DELIVERY_RECEIPT_OK** verdi. Önceki makbuz zinciri eski tracer/snapshot’ları kendi renderer’larıyla denetler.
- Odak testleri: **10 dosya**, **9 kaynak politikası**, **4 arşiv görünümü**, **4 rapor**, **11 yayın**; toplam **38 geçti**. TDD bu kaynak/veri planına uygulanmadı; ek testler gerçek kabul/tekrar yükleme, PDF atfı ve CSS güvenliği hatalarını sınar.
- Gerçek Chromium’da **1365px ve 360px**: TİP sekmesi, görünür kuruluş gerekçesi, kapalı kimlik/yöntem ayrıntıları, siyah alıntı/koyu mavi özet, gerçek kaynak tıklamaları ve iki doğru arşiv kontrol edildi. İki belgede **script=0**, **form=0**, bütün görseller yüklü, varlık istekleri yerel ve sayfa taşması yoktu. Ekran görüntüleri ayrıca görsel olarak okundu.
- Plan öncesinden gelen **281 dosyanın baytları** Git nesne özetiyle aynı kaldı; eski kaynaklar, release’ler ve tarihsel renderer’lar korundu. Tamamlanan prefix yalnız TİP kadar büyüdü.
- Kaynakların özgün boşluk/CRLF baytları korundu; kaynak kopyalarına biçim düzeltmesi uygulanmadı. Kod, test ve girdi dosyalarının whitespace kontrolü geçti.

`actuals.tokens`, üretilmiş kaynak/HTML/CSS/JSON dosyaları dahil gerçekleşen Git diff’inin karakter/4 ölçüsüdür; model kullanım token sayısı değildir. `actuals.commits=3`, SUMMARY yazılmadan önce ledger tabanından ölçülen üretim commit sayısıdır.

## Commit’ler

| Commit | Görev |
|---|---|
| `d19ec38` | 02-03-01: gerçek TİP kaynakları, pilot kart uyarlaması, atıflı kayıtlar ve ilk pasif görünümler |
| `0966fc8` | 02-03-02: tam yerel sürüm, korunmuş ilk aday, CSS onarımı ve tarayıcıdan geçen nihai arşivler |
| `8e0e9ab` | 02-03-03: zincirli makbuz, kanıtlı tekrar yükleme ve kalıcı kontrol kaydı |

## Plandan sapmalar ve çözülen sorunlar

1. **[Rule 1 — faz kapsamı] Tam kabul beş başlığı da araştırılmış sayıyordu.** İlk üç başlığın kaynaklı/girişimli sonuçları zorunlu kaldı; sonraki iki başlık açıkça `not_researched` olabilir. Bu durumda o başlıkta bulgu/eksik bulunması reddedilir. Böylece sonraki fazlar araştırılmış gibi gösterilmez.
2. **[Rule 1 — parti PDF’si] Atıf kontrolü sıkıştırılmış PDF baytlarında düz parti adı arıyordu.** Aynı parti yayıncısının arşivli HTML yayınıyla aynı ana makineden gelen PDF için yayıncı ilişkisi kabul edilir. Yanlış yayıncı veya başka ana makine reddedilir; sicil kimliği denetimleri korunur.
3. **[Rule 1 — pasif görünüm] TİP’in temel stilleri bilinen CDN’lerden geliyordu; CSS kaçışı çıkarılırken kapanış parantezi de siliniyordu.** Sabit statik CSS/font CDN listesi eklendi; MIME/boyut/URL/CSP kontrolleri korundu. Bildirim temizliği kural parantezini koruyacak şekilde onarıldı. Gerçek Chrome’daki yerleşim kilitlenmesi bu düzeltmeyle kapandı. İlk `187323bb32fc4741946ca857c4865985` adayı değiştirilmeden saklandı; yalnız bu planın henüz makbuz verilmemiş işaretçisi önceki kabul edilmiş tabana alınıp nihai sürüm üretildi. Başka çalışmanın verisi geri alınmadı.
4. **[Rule 1 — tekrar yükleme] Erişim girişiminin türettiği pending→examined durumu, aynı girdiyi yeniden kontrol ederken çelişki sayılıyordu.** Aynı uç alanları ve gerçek eşleşen girişim varsa tekrar kabul edilir; girişim silinirse veya kaynak uyuşmazsa reddedilir. İzole test veri kopyası da canlı yazıcı kilidini taşımayacak şekilde düzeltildi. İlk kilit-kopyalama kaynaklı başarısız koşuların ardından nihai 10 dosya testi geçti.

## Gerçek kaynak açıkları ve faz sınırı

- Kuruluş Konferansı/ilk Büyük Kongrenin kesin günü ve kurucu başkan seçiminin gün/ayı elde edilen kaynaklarda belirtilmiyor. 2017 yılı, yapay bir gün/aya çevrilmedi.
- HTML tüzük/programın kabul/değişiklik günü ve eski kopyalarla kesin yürürlük ilişkisi belirtilmiyor. 2018 yayın izi bulundu; eski tam program metni elde edilmedi. Bu belirsizlikler parti yayınlarının okunmasını engellemiyor.
- Gerçekleşmiş TİP mali verileri ve söylem–uygulama karşılaştırmaları sonraki fazlarda. Yeni Parti’nin ulusal kesin hesap ve Kocaeli haberinin dönem başlangıcı açıkları önceki kayıtlarıyla korunur.
- İnsan kaynak kabulü varmış gibi sunulmadı; yeni içeriğin faz sonu okuması önceki pilot UAT’sine yüklenmedi. Çözülmemiş uygulama stubları veya atlanmış zorunlu kontroller yoktur.
- Faz 2 **3/10** plandadır; dört faz gereksinimi topluca tamamlanmış işaretlenmedi. Kullanıcıya bu teslim bildirildikten sonra sıradaki plan **02-04 / DEM Parti** olabilir.

## Self-Check: PASSED

İki girdi, nihai immutable rapor, makbuz ve CHECKS dosyası diskte bulundu; üç üretim commit’i Git’te doğrulandı. Kesim, prefix, pilot korunması ve kaynak/rapor denetimleri geçti. Üç görev tamamlandı; `.gsd/` ve mevcut `.planning/milestone.lock` sahiplik dışı dosyalar olarak korundu.

