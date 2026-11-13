---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "05"
subsystem: kaynakli-karsilastirma
tags: [dem, tuzuk, kongre, program-acigi, semantik-inceleme]
requires:
  - phase: 03-04
    provides: kaynaklı ortak konu sözlüğü, önceki parti karşılaştırmaları ve denetlenmiş yerel sürüm
provides:
  - DEM ve HEDEP kısa adlı iki tüzük nüshasının kaynaklı ortak konu karşılaştırması
  - Bağımsız program açığı ile kongre kararlarının ayrı türde ortak konu karşılaştırması
affects: [03-14, 03-15, 03-16]
actuals:
  tokens: 9486418
  tasks: 2
  commits: 2
plan_head_before: 6fbcd53460aa48c01ab6e38a42bc9d23b091c1a8
tech-stack:
  added: []
  patterns: [degismez-yerel-yayin, surumlu-kapsam, kaynakla-ajan-anlam-incelemesi]
key-files:
  created:
    - data/comparisons/03-dem-charter.json
    - data/comparisons/03-dem-semantic.json
    - data/comparisons/03-dem-program.json
  modified:
    - data/current.json
key-decisions:
  - "İki tüzüğün farklı hükümleri kaynaklı alternatiflerdir; kabul veya yürürlük sırası erişim, sayfa sayısı ya da kısa addan çıkarılmadı."
  - "Kongre kararları ek belgedir; bağımsız tam program açığı ve ayrı HDP tüzel kimliği korunur."
  - "Kongre kararlarındaki temel yurttaşlık geliri geliri olmayan tüm yurttaşlarla sınırlıdır."
requirements-completed: []
requirements-addressed: [TUZ-01, TUZ-02, TUZ-03, TUZ-04, PRG-01, KAR-01, KAR-02, RAP-02]
coverage:
  - id: D1
    description: DEM'in iki tüzük nüshasının ortak konu ve kaynak kapsamı
    verification:
      - kind: integration
        ref: python3 src/arsiv.py audit --release current --phase 3 --stage partial
        status: pass
    human_judgment: true
    rationale: Kaynağın koşul ve organ anlamına ilişkin araştırma değerlendirmesi otomasyonla bütünüyle kanıtlanamaz.
  - id: D2
    description: Kongre ek belgesi ve bağımsız programın belgelenmiş açığı
    verification:
      - kind: integration
        ref: python3 src/arsiv.py audit --release current --phase 2
        status: pass
    human_judgment: true
    rationale: Arama kapsamı ve kaynakların maddi yorumu araştırma değerlendirmesi gerektirir.
duration: ölçülmedi
completed: 2026-11-13
status: complete
---

# Phase 03 Plan 05: DEM Tüzük ve Program Karşılaştırması Özeti

**DEM'in iki tüzük nüshası ve kongre kararları, belge sürümüne bağlı alıntılar, ajan incelemeleri ve bağımsız program açığıyla iki yerel rapor görünümüne işlendi.**

## Teslimler ve kaynak kapsamı

- Tüzük kaynakları `0204-dem-charter-v1` (36 sayfa, SHA-256 `97f552324d044a6a0ec4ad9d1dd99ac66ba50540a3ad397ebefaa3fbd7e1a471`) ve `0204-dem-charter-older-v1` (32 sayfa, SHA-256 `7c54e58c28d9e0bfadc72a5be640169a15137dc8aca8c93b4c1b6a1fc16470c4`). İki metnin Madde 1–61 kapsamı üyelik, seçme ve seçilme, merkez, il ve ilçe organları, hesap, görüş, disiplin ve itiraz konularıyla incelendi. Her iki belgenin kabul günü ve hukuki yürürlük sırası bilinmiyor.
- Tüzük paketi 485 satır, 389 kaynaklı alan ve 96 somut kapsam kaydı içerir; 166 ortak tüzük konusu önceki il-disiplin kaydıyla birlikte karşılanır. Eski merkez seçimi `not_researched` satırı kaynaklı Parti Meclisi bulgusuna bağlandı. 388 yeni pasajın her biri kendi özgün PDF sayfasıyla birebir eşleşti; 485 semantik karar inceleme dosyasıyla eşleşti.
- Maddi farklar arasında Büyük Kongre doğal delegeleri, il kongresi doğal üyeleri, ilçe kongresi doğal üyeleri, İl Disiplin Kurulunun toplanmaması halinde dosya incelemesi, doğrudan merkez disiplin başvurusunda Parti Meclisi kararı ve disiplin yaptırımları bulunur. İl örgütü bulunmayan yerde kurucu ataması, köy-mahalle delege birleştirmesi ve af/ceza ölçütleri için tek nüshada açık hüküm bulunması diğer nüshaya aktarılmadı. Yazılı kurallar gerçekleşmiş uygulama olarak sunulmadı.
- Tüzük sürümü `b051e5f7f7534616bbaa0602c2286dc9`; rapor `data/releases/b051e5f7f7534616bbaa0602c2286dc9/index.html`; görev commiti `8f77e5c`.
- Kongre ek belgesi `0204-dem-policies-v1`, özgün SHA-256 `0ba81cd43ab9b5455db4a77ca66fc4bdf08df72a3dcb4fd40405ab977cc8ec45`; 4'üncü Olağanüstü Büyük Kongre kararlarının bütün başlık ve paragrafları ortak konular açısından incelendi. Kesin yayın veya kabul günü kaynaktan çıkarılmadı. 82 yeni kaynaklı alan, 55 somut kapsam kaydı ve bunlara ait 192 semantik karar üretildi; 214 yeni pasaj özgün HTML ile eşleşti.
- 13 Kasım 2026 17:41:39 UTC aramasında DEM resmî menüsü, tüzük sayfası, kongre dizini ve web sonuçları yeniden izlendi. Bağımsız güncel tam program elde edilmedi; `0305-dem-search-independent-program` ve `0305-dem-program-search-closure` arama/sonuç sınırını kaydeder. Eski `0204-dem-missing-current-program` kaydı 135 ortak program konusunda kullanılır. Ayrı HDP programı DEM programına dönüştürülmedi; kongre kararı `supplement` olarak kalır. Bu sonuç programın var olmadığı iddiası değildir.
- Program sürümü `6090bfda16a14ce99a1b6c9d3ff47d71`; rapor `data/releases/6090bfda16a14ce99a1b6c9d3ff47d71/index.html`; görev commiti `65f7e0c`. Son sürümde DEM için `not_researched` satırı yoktur.

## Doğrulama

- İki paket için `comparison-check`: **COMPARISON_INPUT_OK**; her biri denetlenmiş current tabanından scratch workspace'e `comparison-load` ile yüklendi ve **COMPARISON_LOAD_OK** verdi.
- Tüzük sürümünde **PHASE3_AUDIT_OK b051e5f7f7534616bbaa0602c2286dc9**; program sürümünde **PHASE3_AUDIT_OK 6090bfda16a14ce99a1b6c9d3ff47d71** ve **PHASE2_AUDIT_OK 6090bfda16a14ce99a1b6c9d3ff47d71** alındı. Son manifestte Faz 2 `phase2_delivery`, önceki `b54b8fe4805741d4bd6b87b5dd81da4c` ile eşittir.
- Tüzükte 484/484 etkin yeni satır, program paketinde 325/325 satır için parti dosyası ve karşılaştırma görünümünün kimlik ve karşılıklı bağlantıları kontrol edildi. Programın 192/192 kanonik semantik kararı inceleme dosyasıyla eşleşti; 135 program konusunun tümü aynı gerçek bağımsız belge açığına bağlıdır.
- Önceki 03-04 sonrası kanıtta geçen 124 benzersiz test bu yalnız veri planında yeniden çalıştırılmadı; her iki görevde paket, gerçek kaynak, yayın ve audit kontrolleri yapıldı. İki sürüm yereldir; kamuya dağıtım yapılmadı.
- `actuals.tokens`, plan başlangıç commitinden iki görev commitine git metin farkının 37.945.670 karakterinin dörde bölünmesiyle ölçülmüştür; model token tüketimi değildir. Başlangıç zamanı güvenilir biçimde kaydedilmediğinden süre ölçülmedi.

## 03-14, 03-15 ve 03-16 aktarımı

- Temel yurttaşlık gelirinin ortak tanımı bütün partilerde geri taranmalıdır: DEM kongre kararı **geliri olmayan tüm yurttaşları**, Yeni Parti programı **her vatandaşı** söyler; TİP'in kapsamlı nakit gelir yokluğu ve çalışamayacak kişilere sosyalist toplum koşullu nitel güvencesi kendi şartlarında kalır. DEM ek belgesindeki eşdeğer işe eşit ücret ve ücret kaybı olmadan altı saat çalışma da kaynaklı geri tarama adaylarıdır. Önceki Yeni Parti ve TİP aday kuyrukları korunur.
- Renderer 17 `no_explicit_statement` satırında sürüm ve kapsamı satır içinde göstermiyor. Bu plan gerçek kaynak alıntısına bağlı görünür mavi açıklamayla somut soruyu ve incelenen sürümü ayrıca gösterir; kanonik `comparison_review_scope` korunur. Satır içi sunum ve bütün faz kabulü 03-15/03-16'da değerlendirilmelidir.
- İnceleme kararları ajana aittir; bağımsız insan kabulü değildir. Diğer parti planları, ortak geri tarama ve faz sonu doğrulaması bitmeden sekiz ortak gereksinim tamamlanmış işaretlenmez.

## Sapmalar ve sorunlar

Plan kapsamını değiştiren mimari veya uygulama kodu değişikliği yoktur. Yeni kaynak aramasında bağımsız program bulunamaması belgelenmiş araştırma sınırı olarak korunmuştur. Renderer 17'nin yukarıdaki sunum sınırı mevcut sürümü değiştirmeden giderilecek sonraki iş olarak devredildi.

## Self-Check: PASSED

Üç paket, iki yerel rapor ve her iki görev commiti dosya ve git nesnesi olarak doğrulandı; son sürümde canlı yazıcı kilidi kalmadı.
