---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
plan: "08"
subsystem: kaynak derlemesi ve tam parti teslimi
tags: [emep, kimlik, kronoloji, tuzuk, program, pasif-arsiv, makbuz]
requires:
  - phase: "02-07"
    provides: Tam DBP dosyası, korunmuş önceki partiler ve zincirli makbuz
provides:
  - EMEP için kaynaklı yedi alanlı kart, üç tarihli kuruluş/kongre/ad kaydı ve günü bilinmeyen kurucu başkan kaydı
  - Tam program ve tüzük HTML’si, tarihsiz 38 sayfalık öneri/metin PDF’si ve 1996 tarihsel kitap kopyası
  - Aynı adlı eski partiyi ayıran çift kaynaklı not, ayrı immutable rapor ve DBP’ye bağlı doğrulanmış makbuz
affects: [02-09, 02-10, 03]
tech-stack:
  added: []
  patterns: [iki kaynağa bağlı tarihsel kimlik notu, öneri ile kabul edilmiş belgeyi ayırma, yerel varlık tekrar kullanımı]
key-files:
  created:
    - data/dossiers/02-emep.json
    - data/deliveries/02-08-emep.json
    - data/releases/d0969b9cfaac47c69d09cf27c1f1ad39/index.html
    - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-08-CHECKS.json
  modified: [data/current.json]
key-decisions:
  - Sabit emep kimliği korunarak eski TBMM anahtarı gerçek yargitay-52 siciline kontrollü geçirildi; kuruluş 25.11.1996’dır.
  - 25.03.1996 kuruluşlu ve 14.02.1997’de kapatılmış eski Emek Partisi, mevcut sicilden ayrı iki kaynaklı notla gösterilir; siyasi mirastan tüzel süreklilik çıkarılmaz.
  - 2019 yayın, 2020 web güncellemesi ve kapak görselindeki 2017 yılı kabul veya yürürlük günü sayılmadı; içerik doğrudan atıflı parti yayını olarak derlendi.
  - Yargıtay’daki 38 sayfalık tarama değişiklik önerisiyle başlar; önerinin kabul edildiği ve HTML metniyle kesin sürüm sırası uydurulmadı.
requirements-completed: []
coverage:
  - id: EMEP-SOURCES
    description: Sicil, aynı adlı eski parti ayrımı, ilk kongre ve program/tüzük nüshalarının maddi anlamı
    verification: []
    human_judgment: true
    rationale: Kaynak anlamı faz sonu değerlendirmesinde incelenir; her kaynak için insan kabulü kullanım ön koşulu değildir.
  - id: EMEP-INTEGRITY
    description: Tam dosya, tek parti prefix’i, yöntem kesimi ve önceki içeriklerin korunması
    verification:
      - {kind: integration, ref: 'python3 src/arsiv.py dossier-check --input data/dossiers/02-emep.json', status: pass}
      - {kind: integration, ref: 'python3 src/arsiv.py audit --release current --phase 2 --party emep', status: pass}
      - {kind: integration, ref: 'python3 src/arsiv.py audit --release current --phase 1', status: pass}
      - {kind: unit, ref: 'python3 tests/run.py --pattern test_dossiers.py', status: pass}
      - {kind: other, ref: '02-08-CHECKS.json#preservation', status: pass}
    human_judgment: false
  - id: EMEP-READING
    description: Masaüstü/mobil kaynak gezinmesi, görünür tüzük metni, UTF-8 ve doğru özgün PDF
    verification:
      - {kind: automated_ui, ref: '02-08-CHECKS.json#browser', status: pass}
      - {kind: automated_ui, ref: '02-08-CHECKS.json#source_body_reading', status: pass}
      - {kind: integration, ref: '02-08-CHECKS.json#pdf_http', status: pass}
    human_judgment: false
  - id: EMEP-RECEIPT
    description: DBP makbuzuna bağlı tam EMEP teslimi
    verification:
      - {kind: integration, ref: 'python3 src/arsiv.py receipt-check --input data/deliveries/02-08-emep.json', status: pass}
    human_judgment: false
actuals:
  tokens: null
  tasks: 3
  commits: 3
plan_head_before: 7d9ab1e7e0cec8b9da562a8ccbb87f57c99bcd64
duration: 49min
completed: 2026-11-11
status: complete
---

# Phase 2 Plan 8: EMEP kaynak dosyası özeti

**EMEP’in gerçek sicil kimliği, kuruluş/ilk kongre/ad değişikliği kronolojisi ve program–tüzük nüshaları 22 kaynaklı özet/alıntı çiftiyle ayrı rapor ve DBP’ye bağlı makbuz olarak hazırlandı; aynı adlı eski parti ve kabul günü bilinmeyen belge sürümleri açıkça ayrıldı.**

## Teslim ve üç görev

- [Değişmez yerel rapor](../../../data/releases/d0969b9cfaac47c69d09cf27c1f1ad39/index.html): **`d0969b9cfaac47c69d09cf27c1f1ad39`**. Şema **5**, kaynak politikası **2**, dosya doğrulama **2** ve renderer **13** korunur.
- [Makbuz](../../../data/deliveries/02-08-emep.json), **02-07-dbp.json** makbuzuna bağlıdır. `stage=complete`; prefix **tip, dem, iyi, yeni-yol, dbp, emep**; method-1 ve **2026-11-10T14:38:46.154751+00:00** kesimi değişmedi.
- [Kontrol kaydı](02-08-CHECKS.json), Chromium okumasını, iki özgün PDF’nin HTTP/hash sonuçlarını ve **1.457 önceki değişmez dosyanın** korunmasını belgeler. Önceki tablo satırları korunur; yalnız EMEP’in belgeli sicil geçişi kontrollü değişikliktir.

1. **Kaynak edinimi:** [Girdi](../../../data/dossiers/02-emep.json) **277 kayıt**, **10 seçilmiş kaynak sürümü**, **7 kart alanı**, **4 kronoloji kaydı** ve **7 seçilmiş pasif HTML görünümü** taşır. Beş zorunlu alan kaynaklıdır. Sicil `/sipar/52`, ad/kısa ad **EMEK PARTİSİ / EMEP**, kuruluş **25.11.1996**, başkan **Seyit Aslan** ve **Necatibey Cd. No: 88/3 Çankaya / ANKARA** adresiyle okundu. `yargitay-52` adres anahtarıdır; ayrıca ilan edilmiş bir sicil numarası sayılmadı. Eski TBMM kimliği ve kapsam gözlemleri geçmişte korunur.
2. **Ayrı yerel rapor:** Son teslim edilmiş DBP sürümünden temiz workspace açıldı, girdi yüklendi ve yalnız **publish --party emep** çalıştırıldı. Kuruluş/Tüzük/Program altında **14/5/3 çift** bulunur. **25 Kasım 1996 kuruluş**, **14 Eylül 1997 ilk kongre** ve **27 Kasım 2005 ad değişikliği** kendi kaynak ve olay tarihleriyle gösterilir. Kurucu genel başkan **Levent Tüzel** parti yazısına atfedilir; ayrı göreve başlama/seçim günü bilinmediği için bu kayıt **tarihi bilinmiyor** kaldı.
3. **Zincirli teslim:** Son rapordan üretilen EMEP makbuzu bağımsız **receipt-check** ile **DELIVERY_RECEIPT_OK** verdi. Eklenen kart/kronoloji/belge kaynakları ve önemli açıklar makbuzdadır. Kamu yayını ve `gh-pages` değiştirilmedi; sonraki parti araştırmasına geçilmedi.

## Kaynak anlamı ve gerçek açıklar

- **Aynı adlı iki hukuki kayıt ayrıdır.** TBMM’nin kapatılmış partiler tablosu, **25.03.1996** kuruluşlu Emek Partisi’ni **14.02.1997**, **E.1996/1, K.1997/1** kapatma kaydıyla gösterir. Mevcut Yargıtay sicili **25.11.1996** kuruluşludur. İki pasajı birlikte veren normal özet/alıntı notu mevcut kayıt API’sinde tutuldu; yardımcı parti veya yeni şema yaratılmadı. Eski partinin kapanması mevcut EMEP’in kapanması sayılmaz. Geriye dönük parti yazısının başvuru sıralaması sicil/Meclis günlerinin yerine geçirilmedi.
- **Kuruluş adımları kaynaklı, sınırları açıktır.** Kadıköy Belediyesi kataloğu *Emeğin Partisi 1. genel kongresi belgeleri: 14 Eylül 1997* künyesini verir; tam kitap/kongre tutanağı değildir. Evrensel’in **2 Aralık 2005** haberi **27 Kasım 2005** kongresinde Emeğin Partisi adının Emek Partisi olarak değiştirildiğini ve Levent Tüzel’in yeniden seçildiğini aktarır. Kuruluş başvurusunun aslı ve ilk kongrenin tam tutanağı bulunamadı.
- **Tam HTML program ve tüzük edinildi.** Program, partinin işçi sınıfı/sınıfsız toplum hedefi ile demokratik haklar, emek, sosyal güvence, kadın eşitliği, eğitim, sağlık ve çevre talepleriyle kısa tanıtılır. Tüzüğün **4, 9–10 ve 30–31. maddeleri** üzerinden üyelik, eleştiri, seçme/seçilme ve genel kongre yetkileri kısaca derlendi. Bunlar beyan ve yazılı kurallardır; uygulanmış sonuç veya gerçekleşmiş harcama sayılmaz. **7 Mayıs 2019** yayın ve **31 Ağustos 2020** web güncelleme günleridir. Kaynak kapağında **2017** görünür; bunun HTML metninin kabul/sürüm günü olduğu ileri sürülmedi.
- **38 sayfalık Yargıtay PDF’si doğru adlandırıldı.** İlk sayfa 6. Kongre Divan Başkanlığına program ve tüzük değişikliği **önerisi**, GYK adına Selma Gürkan imzasını taşır. Ardından program/tüzük metinleri ve son sayfada **35 adlı kurucular kurulu listesi** vardır. Seçilmiş sayfalar görsel okundu; tüm PDF’ye OCR veya ayrıntılı karşılaştırma yapıldığı iddia edilmez. Önerinin kabul durumu/günü, listenin hangi kuruluş başvurusuna ait olduğu ve HTML metniyle kesin normatif sürüm sırası bilinmiyor.
- **1996 tarihsel kitap güncel program yerine konmadı.** TBMM item → ORIGINAL bundle → doğrudan PDF bağlantısı izlendi. *Emek Partisi Program ve Tüzüğü* kapağı/kataloğu **1996** yılını taşır; damganın kısmen örttüğü ay kesinleştirilmedi. Mevcut sicilin kuruluşundan önceki bu kitap ayrı tarihsel belge olarak saklandı. **2014** parti kongre yayını da üyelik normu değişikliğini ve 2015 için hazırlık kararını aktarır; planlanan kongrenin gerçekleştiği veya önerilerin kabul edildiği sonucu çıkarılmadı.
- Başkan/adres görev başlangıcı ve belge dönemlerinin kesin bitişi bilinmiyor. Söylem–uygulama ve gerçekleşmiş finansman/harcamalar **Henüz incelenmedi** durumundadır. Ayrıntılı tüzük/program karşılaştırması yapılmadı. Ortak dört gereksinim diğer parti planları tamamlanmadan tamamlandı işaretlenmedi.

## Doğrulama, görünüm sınırı ve commit’ler

Önceki DBP makbuzu **DELIVERY_RECEIPT_OK**, önceki immutable rapor **PHASE2_PARTY_OK** verdi. Son EMEP girdisi **DOSSIER_INPUT_OK**, son parti **PHASE2_PARTY_OK**, pilot **PHASE1_AUDIT_OK**, yeni makbuz **DELIVERY_RECEIPT_OK** verdi. Dosya sözleşmesinin **10 testi** geçti. Yeni bağımlılık, tablo, bayrak veya üretim kodu eklenmedi; kanıt, metin, tarih ve hash denetimi gevşetilmedi.

Chromium’da **1365 ve 360 px** okuması yapıldı: amaç metni önde, yöntem kapalı, alıntılar siyah ve özetler koyu mavidir. Sicil ve tam program/tüzük doğru pasif kopyalara; öneri paketi doğru özgün PDF’ye açılır. Program ve tüzük aynı özgün HTML sayfasında kendi başlık/pasajlarıyla sunulur. Tüzük metnine gerçek kaydırma yapılarak iki genişlikte görünürlük ve okunabilirlik incelendi. UTF-8, script/form yokluğu, yerel varlıklar ve yatay taşma yokluğu doğrulandı. İki PDF yanıtı **application/pdf** ve özgün SHA-256 ile aynıdır. Otomatik başarı kaynak anlamının insan kabulü değildir.

**Görünüm sınırı:** İlk üç parti türevinde 12 varlık bütçesi sosyal simgelerden sonra temel tema CSS’sini atlamıştı. Yerel varlıklar tekrar kullanılarak temel tema stilleri tamamlandı; ilk türevler ve özgün baytlar değişmedi, son görünümlerle girdi yeniden kontrol edildi. Bazı SVG simgeleri, dış görseller ve fontlar alınamadı; yeni galeri/font uçları sınırlandı. Tam metin ve yerel ana düzen okunur; piksel eşdeğerliği iddia edilmez. Sınırlar görünüm manifestleri ve CHECKS içindedir.

Görev commit’leri: **`a4e3598`** kaynak girdisi/arşivler; **`3b60c7b`** denetlenmiş rapor; **`5059853`** zincirli makbuz ve kontrol kaydı. Üretim değişiklikleri **225 dosyadır**. Kaydedilen kaynak çalışma başlangıcı **2026-11-11T19:59:30.288371+00:00**; bu noktadan süre yaklaşık **49 dakika**. `actuals.tokens`, gerçekleşen dosya metinlerinin UTF-8 replacement çözümlemesi sonrası karakter/4 ölçüsüdür; model faturası veya harness token sayısı değildir. Commit sayısı üç üretim görevinin kalıcı Git kaydından ölçüldü.

## Plandan sapmalar ve oturum kurtarması

Yeni mimari veya kapsam sapması yoktur. İlk önceki-makbuz exec oturumu sonuç kaydetmeden **SIGTERM/143** ile sonlandı; tamamlanmamış iki kontrol bir kez kalıcı süreçlerde yeniden çalıştırılıp ayrı exit/sonuç kayıtlarıyla başarılı oldu. Başarılı önceki teslim kontrolleri tekrar başlatılmadı. Görünüm iyileştirmesi planın özgünleri koruyan pasif türev edinimi içinde yapıldı; yeni test veya doğrulama istisnası eklenmedi. Kaynak erişimindeki 403/404 sonuçları gerçek girişimlerde durur; alternatif Meclis/kütüphane belgeleri edinildi.

## Self-Check: PASSED

Girdi, son rapor, makbuz ve CHECKS diskte; üç üretim commit’i Git’te doğrulandı. Önceki 1.457 değişmez dosya, tablo satırları, yöntem kesimi, doğru prefix ve makbuz zinciri korundu. `.gsd/` ve `.planning/milestone.lock` yerinde bırakıldı. Faz 2 **8/10** plandadır; sıradaki plan **02-09 Saadet**, EMEP tesliminin kullanıcıya bildirilmesinden sonradır.
