---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
plan: "10"
subsystem: kaynak derlemesi ve dokuz dosyalı teslim zinciri
tags: [demokrat, dyp, sicil, kronoloji, tuzuk, program, pasif-arsiv, makbuz]
requires:
  - phase: "02-09"
    provides: Tam Saadet dosyası ve sıralı teslim makbuzu
provides:
  - Demokrat Parti için kaynaklı kart, kuruluş/ad değişikliği/ilk kongre/ilk yönetim kronolojisi ve ayrı tüzel kimlik notları
  - Tam arşiv tüzük ve programı ile DYP döneminden erişilebilir eski kitaplar ve kısa kaynaklı içerik özeti
  - Dokuz dosyalı immutable rapor ve Saadete bağlı makbuz; sekiz tam parti makbuzunun son makbuzdan sonraki sıralı kapanış kontrolleri
affects: [03, phase-02-final-verification]
tech-stack:
  added: []
  patterns: [arşivdeki özgün parti PDFlerine atıf, TBMM katalogdan bitstreama belge zinciri, kesin günü bilinmeyen eski nüshaları related olarak bağlama]
key-files:
  created:
    - data/dossiers/02-demokrat.json
    - data/deliveries/02-10-demokrat.json
    - data/releases/bcc67d04d9d741e191589d0f5ac173ca/index.html
    - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-10-CHECKS.json
  modified: [data/current.json, tests/test_report.py]
key-decisions:
  - Sabit demokrat kimliği korunarak TBMM anahtarı gerçek yargitay-3 kaydına geçirildi; kuruluş 23.06.1983 ve DYPden Demokrat Partiye 27.05.2007 ad değişikliği ayrı olaylardır.
  - 1946daki aynı adlı parti ile 28.05.2007 kuruluşlu ayrı güncel DYP kendi kaynaklarıyla ayrıldı; siyasi miras anlatımı tüzel kimlik veya yeni kuruluş tarihi yapılmadı.
  - Canlı dp.org.tr zaman aşımı, atıflı 2021 program ve 2022 tüzük arşiv nüshalarının kullanımını engellemedi; bunların bugün son sürüm olduğu veya kesin yürürlük günü bilindiği iddia edilmedi.
  - Eski DYP belge tarihleri, katalog yükleme tarihleri, arşiv yakalamaları ve metindeki kabul notları kendi anlamlarıyla korundu; bütün ara sürüm zinciri üretilmedi.
requirements-completed: []
coverage:
  - id: DEMOKRAT-SOURCES
    description: Sicil, ad değişikliği, ayrı tüzel kimlikler, ilk yönetim/kongre ve belge sürümlerinin kaynak anlamı
    verification: []
    human_judgment: true
    rationale: Otomatik bütünlük maddi kaynak anlamının insan kabulü değildir; kaynak kullanımı için ön insan onayı aranmaz. Dört ham probe ve üç descriptor-less prohibition çözülmeden korunur.
  - id: DEMOKRAT-INTEGRITY
    description: Tam Demokrat dosyası ve pilot dahil dokuz dosyanın ortak denetimi
    verification:
      - {kind: integration, ref: 'python3 src/arsiv.py dossier-check --input data/dossiers/02-demokrat.json', status: pass}
      - {kind: integration, ref: 'python3 src/arsiv.py audit --release current --phase 2 --party demokrat', status: pass}
      - {kind: integration, ref: 'python3 src/arsiv.py audit --release current --phase 1', status: pass}
      - {kind: integration, ref: 'python3 src/arsiv.py audit --release current --phase 2', status: pass}
      - {kind: other, ref: '02-10-CHECKS.json#preservation', status: pass}
    human_judgment: false
  - id: DEMOKRAT-READING
    description: Masaüstü/mobil kart, kronoloji, kaynak bağlantıları ve gerçek özgün PDF gövdesinin açılması
    verification:
      - {kind: automated_ui, ref: '02-10-CHECKS.json#browser', status: pass}
      - {kind: other, ref: '02-10-CHECKS.json#source_body_reading', status: pass}
    human_judgment: false
  - id: FINAL-EIGHT-RECEIPTS
    description: Son Demokrat makbuzu üretildikten sonra sekiz tam parti makbuzunun sıralı kapanış kontrolü
    verification:
      - {kind: integration, ref: '02-10-CHECKS.json#operations', status: pass}
    human_judgment: false
  - id: FINAL-REGRESSION
    description: Altı zorunlu dosya, eksik, zincir, yayın, rapor ve kabul süiti
    verification:
      - {kind: integration, ref: '02-10-CHECKS.json#tests', status: pass}
    human_judgment: false
actuals:
  tokens: null
  tasks: 3
  commits: 5
plan_head_before: e2564c6ad354bae74c36f38e42a5bbc281c603cd
duration: 128min
completed: 2026-11-11
status: complete
---

# Phase 2 Plan 10: Demokrat Parti ve dokuz dosyalı kapanış özeti

**Demokrat Parti'nin mevcut tüzel kimliği, ayrı ad değişikliği, ilk kongre/ilk yönetim kanıtları ve tam tüzük–program arşivleri 30 kaynaklı özet/alıntı çiftiyle dokuz dosyalı yerel rapora eklendi; son makbuzdan sonra sekiz tam parti makbuzu sırayla denetlendi.**

## Teslim ve üç görev

- [Değişmez yerel rapor](../../../data/releases/bcc67d04d9d741e191589d0f5ac173ca/index.html): **`bcc67d04d9d741e191589d0f5ac173ca`**. Önceki Saadet sürümü **`d42f5105a1a1431d86cdfb3db8669fe2`** tabandır. Şema **5**, kaynak politikası **2**, dosya doğrulama **2** ve renderer **13** değişmedi.
- [Makbuz](../../../data/deliveries/02-10-demokrat.json), **02-09-saadet.json** makbuzuna bağlıdır; `stage=complete`. Prefix tam **tip, dem, iyi, yeni-yol, dbp, emep, saadet, demokrat** oldu. Method-1 ve **2026-11-10T14:38:46.154751+00:00** kesimi, dokuz partili kapsam ve onay/sunum sıraları korunur.
- [Kontrol kaydı](02-10-CHECKS.json), gerçek CLI çıkışlarını, sekiz son makbuz denetiminin zaman ve sırasını, 32 testi, tarayıcı/PDF okumalarını, ilk başarısız sonuçları ve **1.791 önceki değişmez dosyanın** korunmasını taşır. Önceki tablo satırları, kontrollü Demokrat kimlik geçişi ve kendi araştırma durumları dışındaki eski içerikler korunur.

1. **Gerçek kaynak/girdi:** [Girdi](../../../data/dossiers/02-demokrat.json) **417 kayıt**, **14 belge ailesi**, **17 kaynak sürümü**, **7 kart alanı**, **4 kronoloji olayı**, **3 related sürüm ilişkisi**, **3 seçilmiş pasif HTML görünümü**, **9 görsel kontrol edilmiş PDF pasajı**, **37 gerçek erişim/araştırma girişimi** taşır. Altı kart alanı kaynaklıdır; resmî site alanı gerçek TLS zaman aşımıyla **Erişilemedi** durumundadır. Kuruluş/Tüzük/Program altında **13/10/7** kısa özet/alıntı çifti bulunur. Söylem–uygulama ve mali başlıklar **Henüz incelenmedi** kalır.
2. **Ayrı yerel rapor:** Son Saadet snapshot'ından temiz workspace açıldı, `dossier-load` ve yalnız `publish --party demokrat` çalıştı. Demokrat Parti **PHASE2_PARTY_OK**, kabul edilmiş pilot **PHASE1_AUDIT_OK** ve parti verilmeden dokuz dosyanın tamamı **PHASE2_AUDIT_OK** verdi. Eski audited sürümler ve Yeni Parti pilotu korundu.
3. **Makbuz kapanışı:** Gerçek release'ten Demokrat makbuzu üretildikten sonra **02-03 TİP → 02-04 DEM → 02-05 İYİ → 02-06 Yeni Yol → 02-07 DBP → 02-08 EMEP → 02-09 Saadet → 02-10 Demokrat** sırasındaki sekiz ayrı mevcut `receipt-check` çağrısı tamamlandı. Her biri **DELIVERY_RECEIPT_OK** verdi; kendi immutable raporu, prefix'i ve önceki makbuz bağlantısı denetlendi. Tarihsel sonuçlar yeni kapanış yerine kullanılmadı. Kamu raporu/`gh-pages` değişmedi.

## Kaynak içeriği ve gerçek açıklar

- **Mevcut tüzel kimlik:** Yargıtay **/sipar/3**, **DEMOKRAT PARTİ / DP**, kuruluş **23.06.1983**, başkan **GÜLTEKİN UYSAL** ve **Dr. Sadık Ahmet Caddesi No:3 Balgat Çankaya/ANKARA** adresini verir. Başkanlık/adresin tarihsel başlangıcı bilinmiyor. `yargitay-3` arşivin URL anahtarıdır; ayrıca ilan edilmiş bir sicil numarası değildir. Eski TBMM anahtarı kimlik revizyonunda korunur.
- **Ad değişikliği:** Anayasa Mahkemesinin **E.2014/7, K.2014/9**, **25 Eylül 2014** kararı, **24 Aralık 2014** Resmî Gazete yayını ve ilgili çoğunluk değerlendirmesi DYP adının **27 Mayıs 2007** kongresinde Demokrat Parti olarak değiştiğini belirtir. 16 sayfalık özgün PDF, doğrudan bağlantı 404/uygulama kabuğu verdiği için 2025 arşiv yakalamasından edinildi. Dilekçe anlatımı ile karar gerekçesi ayrılır; 2007 mevcut partinin yeni kuruluş günü yapılmadı.
- **Ayrı DYP ve eski Demokrat Parti:** Yargıtay **/sipar/112** kaydı **28.05.2007** kuruluşlu ayrı DYP'yi gösterir; iki sicile dayalı not bu partiyle mevcut DP'yi birleştirmez. Atatürk Ansiklopedisinin **Sabit DOKUYAN** imzalı, **16 Ağustos 2023** yayımlanan/**4 Temmuz 2024** güncellenen, 2025 arşivinden edinilen makalesi **7 Ocak 1946** kuruluşlu ve **29 Eylül 1960** kapanışlı aynı adlı partiyi anlatır. Bu tarihler mevcut partinin kronolojisine aktarılmaz; siyasi miras anlatımı tüzel süreklilik kanıtı sayılmaz.
- **İlk yönetim ve kongre:** Hüseyin Çavuşoğlu'nun **“12 Eylül ve Merkez Sağ”**, SDÜ dergisi **2007/2, sayı 6**, basılı **183–206** araştırması, **194. sayfada** ilk genel başkan **Ahmet Nusret Tuna**, **7 Temmuz 1983** veto ve sonraki yönetim sürecini aktarır. İlk genel başkanın seçildiği kesin gün kaynağın bu pasajından çıkarılmaz; kronoloji kaydı tarihi bilinmeyen durumdadır. Çağdaş gazete sayfasına girişimler 403/404 verdi. **14 Mayıs 1985 I. Büyük Kongre** kabul tarihi eski parti yayınının iç kapağındadır; aynı gün Cumhuriyet'in birinci sayfa kongrenin o gün başladığını bildirir. Asıl kuruluş dilekçesi, ilk yönetim ve kongrenin tam tutanakları bulunamadı.
- **Tam tüzük ve kısa içerik:** **48 sayfalık** `DP.Tüzük.2022.pdf`, parti URL'sinin **18 Haziran 2022** ham arşiv yakalamasından edinildi. Amaç/ilkeler, üye hak ve görevleri, kongre yetkileri, konuşma/gündem ve seçim kuralları **1–2, 11–12, 38, 41, 44, 47. maddeler** ile geçici değişiklik notundan kısaca tanıtılır. Dosya adındaki 2022 veya yakalama günü kesin kabul/yürürlük günü yapılmaz. SHA-256 **`379499d93d88c2ea209706ed34d337adb8bc22422127c5411bb9fc01dbe809b4`**.
- **Tam program ve kısa içerik:** **83 sayfalık** `DP.Yeni.Program.pdf`, parti URL'sinin **29 Aralık 2021** ham arşiv yakalamasından edinildi. Demokrasi, hukuk/haklar, siyasal model, üretim ekonomisi, güvenlik, sosyal politika ve dış politika bölümleri; iş, eğitim, sağlık, sosyal/hukuki güvenlik, eşit fırsat ve üretim hedefleri partiye atfedilir. Önsözün **31 Ekim 2009** bütünleşme anlatımı programın kabul günü yapılmadı. SHA-256 **`6554ec05b00d37f62159e1d722f4464ff8b32569ddf7455108530cc772747da2`**. Ayrıntılı karşılaştırma sonraki fazdadır; amaç beyanlarından uygulama sonucu çıkarılmadı.
- **Belge geçmişi:** TBMM Kütüphanesinin gerçek katalog → kayıt → ORIGINAL bundle → bitstream zincirinden **1983 (113 PDF sayfa), 1985 (105), 1988 (123), 1990 birleşik kitap (124), 1990 tüzük (89), 1990.2 tüzük (93)** edinildi. Kapak/iç kapaklardaki **14 Mayıs 1985**, **15 Mayıs 1988**, **24 Kasım 1990** notları kendi anlamlarıyla ve bilinmeyen kesin tarihler açık tutularak saklanır. Üç `related` bağı belgesiz bir supersedes/yürürlük zinciri üretmez. Katalogdaki 2017 yükleme tarihleri belge yayım günü yapılmadı.
- **II. Demokrasi Programı:** Ayrı **1. cilt (14 sayfa), 2. cilt (17 sayfa), özet (26 sayfa)** tam PDFleri edinildi. Birleşik büyük PDF mevcut **20 MiB** yakalama sınırını aştı ve bu gerçek erişim açığı kaydedildi. **3–7. ciltlerin** tam metinleri ile ara kabul tutanakları bulunamadı; seçim beyannameleri program sürümü yerine konmadı.
- **Erişim ve dönem sınırı:** `dp.org.tr` www/çıplak adresi, parti tarihi, tüzük/program sayfaları ve doğrudan güncel PDF yolları TLS zaman aşımı verdi. Arşivde erişilen atıflı parti yayınları D-13 gereği kullanılabilir; canlı sitenin erişilebildiği, bunların bugün son sürüm olduğu, bütün ara değişiklik/kabul tutanakları veya kesin yürürlük bitişlerinin bulunduğu iddia edilmez. Kaynak yayıncısı/yazarı/tarihi/URLsi ve tarih türleri ayrı tutulur. Finansman/harcamalara sıfır yazılmadı.

## Doğrulama ve okuma deneyimi

Önceki Saadet makbuzu **DELIVERY_RECEIPT_OK**, kendi raporu **PHASE2_PARTY_OK** verdi. Nihai girdi **DOSSIER_INPUT_OK**, Demokrat **PHASE2_PARTY_OK**, pilot **PHASE1_AUDIT_OK** ve dokuz dosyanın tamamı **PHASE2_AUDIT_OK** verdi. Yeni makbuz ve sonrasında sekiz makbuzun tamamı geçti. Altı zorunlu süit **32/32**: **dossiers 10, missing 2, chain 1, publication 11, report 4, acceptance 4**. Planın her zorunlu son makbuz giriş noktası gerçekten çalıştırıldı. Uzun işlemler kalıcı süreçte, ayrı argüman/çıkış/süre kayıtlarıyla ve mevcut kanonik `arsiv.main` üzerinden yürüdü; bütünlük doğrulaması atlanmadı veya başarı önbelleği eklenmedi.

Chromium'da **1365 ve 360 px** gerçek Demokrat paneli açıldı; amaç metni önce, yöntem kapalı, alıntı **siyah**, özet **koyu mavi**; rapor, kart ve kronoloji taşmıyor. Sicil UTF-8, scriptsiz/formsuz, yerel CSS/font/kurum logolu pasif görünümde açılır. Gerçek rapor kaynak bağlantılarından tüzük, program ve 1983 eski kitap özgün PDFleri **HTTP 200/application/pdf** döndürür; SHA-256ları özgünlerle eşleşir. Programın **4. PDF sayfası / basılı 10. sayfası** gerçek PDF görüntüleyicide açılarak masaüstü/mobil gövde metni okundu. Kart, kronoloji, tarihsel ansiklopedi gövdesi ve seçilmiş eski PDF kapak/iç sayfaları da görüntüyle incelendi. Ajan okuması insan kabulü değildir; Faz 1 UAT'ı yeni kaynaklara genişletilmedi.

**Görünüm sınırları:** Sicilin data-URL parti amblemi mevcut pasif politika gereği yerelleştirilmedi; kurum logoları ve temel düzen/fontlar yereldir. Tarihsel ansiklopedi paragrafları 360 pxde okunur; eski statik sayfanın bazı öğeleri yatay kaydırma yaratır, bazı arşiv eklenti/yan stil adresleri erişilemedi. Özgün PDFler sabit sayfa düzenindedir; mobilde yüzde 100 yakınlaştırma yatay kaydırma gerektirir. Piksel eşdeğerliği iddia edilmez. Özgün baytlar ve ilk türev görünümler korunur; son seçilmiş üç görünüm kendi manifestlerine bağlıdır.

## Görev commitleri ve düzeltmeler

1. **Kaynak/girdi/arşivler:** `b6ea88a430522654dd35e64f5d3097420e6c8a2c`
2. **Gerçek rapora uygun regresyon varsayımı:** `2353b75bc6ffa5da2a77bec5b7d922dd492dacfb`
3. **Denetlenmiş dokuz dosyalı rapor:** `abe0bc404dcce2a417ba6f1ab3a3094591939c32`
4. **Zincirli makbuz ve CHECKS:** `6a7eb8adbefed75ec2f167036902829d0596a607`

Başlangıç **2026-11-11T21:57:44.255891+00:00**, bitiş **2026-11-12T00:05:23.191555+00:00**; süre yaklaşık **128 dakika**. Üç görev ve dar test düzeltmesi **163 dosyadır**; **5 üretim commit'i**, başlangıç ledger'ı **`e2564c6ad354bae74c36f38e42a5bbc281c603cd`** üzerinden ölçüldü. `actuals.tokens` gerçek değişen dosya içeriklerinin UTF-8 replacement çözümlemesinden sonra karakter/4 ölçüsüdür; model faturası veya harness token sayısı değildir.

- **Kural 1 — hatalı test varsayımı:** `test_report.py` canlı raporda toplam iki arşiv görünümü varsayıyordu; Faz 2nin 44 görünümünde reddetti. Gerekli iki pilot sürümün korunması ve bütün sürüm kimliklerinin tekilliği denetlenerek gerçek tarayıcı probu korundu; dört rapor testi geçti. Üretim doğrulayıcısı/kanıt/hash/kimlik/atıf kuralları değiştirilmedi. Bu tek dar kod sapması ayrı test commit'indedir.
- **Girdi düzeltmesi:** İlk aday, alıntıyı içermeyen ek bağlam pasajını alıntı bulgusuna da bağladığı için reddedildi. Ek bağlam yalnız özet bulgusuna bağlandı; gerçek alıntı kendi tam pasajında kaldı. Son girdi geçti, ilk sonuçlar CHECKS içinde korundu.
- **Yerel varlık toplama:** İlk edinim betiği data-URLleri ve aynı fontun çoklu biçimlerini ağ bütçesinde sayarak ana CSSyi eksik bırakmıştı; gerçek ekran okuması bunu gösterdi. Geçici toplama betiği düzeltilerek ana CSS, Türkçe normal/kalın fontlar ve kurum logoları yerelleştirildi. Özgünler ve ilk türevler silinmedi; yeni üretim motoru/bağımlılık eklenmedi.
- **İşlem çakışması:** İlk publication testi eşzamanlı dossier-check'in canlı `.write.lock` dosyasını test kopyasına taşıdı. Publish yazıcı kilidini bıraktıktan sonra aynı süit bir kez tekrarlandı ve **11/11** geçti. Bu test ortamı çakışması başarısız ilk kaydıyla belgelidir.
- **PDF ekranı:** İlk gövde ekranı PDF boyaması tamamlanmadan kapağı gösterdi. Görüntüleme beklemesi düzeltilip yalnız gövde okuması tekrarlandı; gerçek sayfa ve iki genişlikte metin görsel olarak okundu. İlk görüntü kaydı korunur.

Yeni şema, bayrak, tablo, paket, performans mimarisi veya genel model değişikliği yoktur. Açık kaynaklar için yeni bir insan ön onay kapısı eklenmedi. Başarılı süitler gereksiz yere tekrar edilmedi; sekiz son makbuz kontrolü plan gereği yeni son makbuzdan sonra yapıldı.

## Çözülmeden korunan ham uçlar ve yasaklar

Bu dört ham kayıt normal kabul testleriyle sınıflandırılmadı:

| Requirement | category | status | verification | resolution | reason | probe |
|---|---|---|---|---|---|---|
| DOS-01 | unclassified | unresolved | null | null | null | unclassified — review manually |
| DOS-02 | unclassified | unresolved | null | null | null | unclassified — review manually |
| KAY-01 | unclassified | unresolved | null | null | null | unclassified — review manually |
| KAY-04 | unclassified | unresolved | null | null | null | unclassified — review manually |

Descriptor'ı bulunmayan şu üç prohibition aynen **status: unresolved** ve **flagged-unverified / unverified-prohibition — human review recommended** kalır:

1. “Kapsam seçimi ve parti teslim sırası siyasi destek, başarı sıralaması veya oy yönlendirmesi olarak sunulamaz.”
2. “Aynı adlı ayrı tüzel partiler, milletvekili üyeliği ve ortak Meclis grubu tek bir siyasi kimlikmiş gibi sunulamaz.”
3. “Kaynak türü, eksik kanıt ve sürüm/kesim belirsizliği parti lehine veya aleyhine sonuç, bağımsız doğrulama veya güncellik güvencesi haline getirilemez.”

Kontrollerin geçmesi bu yedi açık kaydı doğrulanmış/sınıflandırılmış yapmaz; maddi kaynak anlamı ve genel faz hedefi root son inceleme/doğrulamasına taşınır. Bu durum D-13 kaynak derlemesi için tekil insan kabulü ön koşulu değildir. Ortak **DOS-01, DOS-02, KAY-01, KAY-04** gereksinimleri burada erken kapatılmadı.

## Self-Check: PASSED

Girdi, immutable rapor, makbuz ve CHECKS diskte; dört üretim commit'i ve başlangıç ledger'ı Git'te doğrulandı. **1.791** eski immutable dosya, önceki bulgular, kapsam/sunum sırası, yöntem kesimi ve tam sekiz parti prefix'i korunur. `.gsd/` ile `.planning/milestone.lock` yerinde bırakıldı. Faz 2 plan yürütümü **10/10** oldu; fazın tamamı ve gereksinim kapanışı root son inceleme/regresyon/doğrulamasını bekler. Sonraki faza geçilmedi.
