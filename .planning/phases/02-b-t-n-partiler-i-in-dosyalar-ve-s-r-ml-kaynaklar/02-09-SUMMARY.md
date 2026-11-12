---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
plan: "09"
subsystem: kaynak derlemesi ve tam parti teslimi
tags: [saadet, sicil, kronoloji, tuzuk, program, pasif-arsiv, makbuz]
requires:
  - phase: "02-08"
    provides: Tam EMEP dosyası ve sıralı teslim makbuzu
provides:
  - Saadet için yedi alanlı kart, kuruluş/ilk yönetim/ilk kongre kronolojisi ve iki sicile bağlı Yeni Yol ayrımı
  - Tam 25 sayfalık tüzük, 70 sayfalık program, 2002 ikinci baskı tarihsel tüzük ve erişilebilir belge geçmişi
  - Ayrı immutable rapor ve EMEP makbuzuna bağlı doğrulanmış Saadet teslimi
affects: [02-10, 03]
tech-stack:
  added: []
  patterns: [PDF yayıncı metniyle doğrudan atıf, güncel belge dizininden özgün PDFye erişim, aynı baytlı iki dağıtım adresini related olarak bağlama]
key-files:
  created:
    - data/dossiers/02-saadet.json
    - data/deliveries/02-09-saadet.json
    - data/releases/d42f5105a1a1431d86cdfb3db8669fe2/index.html
    - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-09-CHECKS.json
  modified: [data/current.json]
key-decisions:
  - Sabit saadet kimliği korunarak TBMM anahtarı gerçek yargitay-70 siciline geçirildi; kuruluş 20.07.2001dir.
  - Saadet ile ayrı Yeni Yol sicili iki kaynağa bağlı notta ayrıldı; ortak gruptan bireysel üyelik veya ad değişikliği çıkarılmadı.
  - Program kapağının 03.11.2019 tarihi, tüzüğün 2016/2019 değişiklik notu ve 05.01.2020 GİK eki kendi anlamlarıyla tutuldu; kesin bütün sürüm/yürürlük zinciri üretilmedi.
  - Ana site uygulama kabuğu yerine yayıncının gerçek tam PDFleri kullanıldı; eski ve güncel dosya adreslerinin aynı hashleri sürüm ilişkisinde gösterildi.
requirements-completed: []
coverage:
  - id: SAADET-SOURCES
    description: Sicil, ilk yönetim/ilk kongre, belge sürümleri ve kurucu milletvekili sayılarının kaynak anlamı
    verification: []
    human_judgment: true
    rationale: Otomatik bütünlük kaynak anlamının insan kabulü değildir; faz sonu kaynak değerlendirmesi korunur, kaynak kullanımı için ön onay aranmaz.
  - id: SAADET-INTEGRITY
    description: Tam dosya, tek parti prefixi, yöntem kesimi ve eski dosyaların korunması
    verification:
      - {kind: integration, ref: 'python3 src/arsiv.py dossier-check --input data/dossiers/02-saadet.json', status: pass}
      - {kind: integration, ref: 'python3 src/arsiv.py audit --release current --phase 2 --party saadet', status: pass}
      - {kind: integration, ref: 'python3 src/arsiv.py audit --release current --phase 1', status: pass}
      - {kind: unit, ref: 'python3 tests/run.py --pattern test_dossiers.py', status: pass}
      - {kind: other, ref: '02-09-CHECKS.json#preservation', status: pass}
    human_judgment: false
  - id: SAADET-READING
    description: Masaüstü/mobil rapor, gerçek kaynak bağlantıları ve özgün PDF okuması
    verification:
      - {kind: automated_ui, ref: '02-09-CHECKS.json#browser', status: pass}
      - {kind: other, ref: '02-09-CHECKS.json#source_body_reading', status: pass}
    human_judgment: false
  - id: SAADET-RECEIPT
    description: EMEP makbuzuna bağlı tam Saadet teslimi
    verification:
      - {kind: integration, ref: 'python3 src/arsiv.py receipt-check --input data/deliveries/02-09-saadet.json', status: pass}
    human_judgment: false
actuals:
  tokens: null
  tasks: 3
  commits: 3
plan_head_before: ee6807576f0fd18a3ddd172ed3f19d27777ad59a
duration: 60min
completed: 2026-11-11
status: complete
---

# Phase 2 Plan 9: Saadet kaynak dosyası özeti

**Saadet Partisi’nin gerçek sicil kimliği, kuruluş/ilk yönetim/ilk kongre kronolojisi ve tam tüzük–program nüshaları 21 kaynaklı özet/alıntı çiftiyle ayrı yerel rapora ve EMEP’e bağlı makbuza eklendi; bilinmeyen dönemler ile kaynakların farklı kurucu milletvekili sayıları açık kaldı.**

## Teslim ve üç görev

- [Değişmez yerel rapor](../../../data/releases/d42f5105a1a1431d86cdfb3db8669fe2/index.html): **`d42f5105a1a1431d86cdfb3db8669fe2`**. Şema **5**, kaynak politikası **2**, dosya doğrulama **2**, renderer **13** korunur.
- [Makbuz](../../../data/deliveries/02-09-saadet.json), **02-08-emep.json** makbuzuna bağlıdır; `stage=complete`. Prefix yalnız **tip, dem, iyi, yeni-yol, dbp, emep, saadet** oldu. Method-1 ve **2026-11-10T14:38:46.154751+00:00** kesimi değişmedi.
- [Kontrol kaydı](02-09-CHECKS.json), gerçek tarayıcı/HTTP sonuçlarını, ilk girdi düzeltmelerini ve **1.678 önceki değişmez dosyanın** korunmasını belgeler. Eski tablo satırları korunur; Saadet’in kontrollü sicil geçişi tek parti kimlik değişikliğidir.

1. **Kaynak edinimi:** [Girdi](../../../data/dossiers/02-saadet.json) **296 kayıt**, **11 kaynak sürümü**, **7 kart alanı**, **3 tarihli kronoloji kaydı**, **2 aynı-nüsha sürüm ilişkisi**, **2 kaynaklı kimlik notu** ve **4 pasif HTML görünümü** taşır. Beş zorunlu kart alanı kaynaklıdır. Yargıtay **/sipar/70**, **SAADET PARTİSİ / SAADET**, **20.07.2001** kuruluşunu verir. Başkan **MAHMUT ARIKAN** ve **Zübeyde Hanım Mah. Tesviyeci Cad. No: 31 Altındağ/ANKARA** adresi sicildeki değerleriyle, tarihsel başlangıcı bilinmeden tutulur. `yargitay-70` adres anahtarıdır; ayrıca ilan edilmiş bir sicil numarası değildir. Eski TBMM anahtarı ve kapsam gözlemleri silinmez.
2. **Ayrı yerel rapor:** Son EMEP snapshot’ından temiz yerel workspace açıldı; girdi yüklenerek yalnız **publish --party saadet** çalıştırıldı. Kuruluş/Tüzük/Program altında **10/8/3 çift** vardır. Kuruluş **20 Temmuz 2001**, ilk yönetim **aynı gün**, ilk olağan kongre **11 Mayıs 2003** olarak kendi kaynaklarıyla gösterilir. Ayrı Yeni Yol siciliyle iki kaynaklı not, ortak grup/siyasi işbirliği/kişisel üyelik ayrımını korur. Demokrat Parti çalışmasına geçilmedi.
3. **Zincirli teslim:** Gerçek rapordan üretilen makbuz bağımsız **receipt-check** ile **DELIVERY_RECEIPT_OK** verdi. Eklenen içerik, önemli açıklar, sürümler ve önceki makbuz bağlantısı gerçektir. Kamu raporu ve `gh-pages` değiştirilmedi.

## Kaynak içeriği ve gerçek açıklar

- **Kuruluş ve ilk yönetim:** TBMM Bülteni **85**, **Ağustos–Ekim 2001**, basılı **sayfa 16**, kuruluş dilekçesinin **20 Temmuz 2001** tarihinde İçişleri Bakanlığına verildiğini ve aynı gün Kurucular Kurulunda **Recai Kutan’ın** genel başkanlığa seçildiğini aktarır; 50 kişilik GİK ve Yüksek Disiplin Kurulunu da bildirir. Başvuru aslı veya toplantı tutanağı edinilmedi. Bülten sayfası görsel okundu; OCRdeki ad yazımı yeni bir kişi gibi kullanılmadı.
- **İlk kongre:** Anadolu Ajansının **Sefa Şahin ve Süleyman Tunç** imzalı **1 Kasım 2019** haberi, **11 Mayıs 2003** ilk olağan kongresinde Kutan’ın aday olmadığını ve **Necmettin Erbakan’ın** seçildiğini aktarır. **6 Kasım 2019** web güncellemesi olay tarihi yapılmadı. Tam ilk kongre tutanağı bulunamadı. Haberlerdeki **SP** kullanımı, sicildeki **SAADET** kısa adının değiştiği anlamına getirilmedi; belgeli bir ad/kısa ad değişikliği veya kapanma bulunmadığı araştırma kaydında açık tutulur.
- **Kurucu milletvekili sayıları:** TBMM Bülteni **32 FP kökenli milletvekili**, **21 Temmuz 2001 Yeni Şafak** arşivi **135 kişilik kurulda 51 milletvekili** bildirir. Kapsam/zaman farkı asıl kurucular listesi olmadan çözülmedi; toplam için tek kesin sayı üretilmedi. Her iki kısa pasaj arşivlidir. Bu açık parti hakkında siyasi sonuç değildir.
- **Tüzük:** Güncel parti belge dizininden **25 sayfalık tam PDF** edinildi. Üyelik/itiraz hakları **4, 6, 8**, yönetim/seçim **10–11**, gündeme ekleme **14** ve disiplin **50. maddeler** üzerinden kısaca tanıtılır. **24. sayfa**, **30 Ekim 2016** kongresinde değişen metnin **9, 21, 22, 23, 27, 37. maddelerinin 3 Kasım 2019** kongresinde değiştiğini söyler. **25. sayfa**, **5 Ocak 2020 tarihli 125 sayılı GİK kararını** içerir. Bu tarihler bütün PDFnin kesin yayın/kabul günü veya bütün maddelerin kesintisiz yürürlük dönemi yapılmadı.
- **Tüzük geçmişi:** TBMM Kütüphanesindeki **Ankara 2002, ikinci baskı**, **75 PDF sayfalık** eski tüzük ayrı saklanır. İç başlık görsel okundu; ikinci baskı ve yıl korunur, kesin gün uydurulmaz. Aradaki bütün nüsha ve değişiklik tutanakları bulunmadı. Güncel ve eski yükleme adreslerinden gelen modern tüzük dosyaları aynı SHA-256’ya sahiptir; **related** ilişkisi aynı nüshanın iki dağıtım adresini gösterir.
- **Program:** Tam **70 sayfalık** PDFnin kapağı **03 Kasım 2019, Ankara** der. Parti amaç ve ilkeleri; siyaset/yönetim anlayışı, demokrasi-haklar, ekonomi-kalkınma, eğitim-sağlık, çevre, kadın-gençlik, güvenlik ve dış ilişkiler başlıklarıyla kısaca tanıtıldı. Amaç, ahlak/maneviyat, hak/adalet, hukukun üstünlüğü, üretim ve sosyal güvenlik hedefleri partiye atfedilir. 2019 ajans haberinin programın oylanacağı duyurusu kabul tutanağı sayılmadı. Daha eski tam program bulunamadı; seçim beyannameleri önceki program sürümü yapılmadı.
- **Gerçek dosya zinciri:** Ana site HTMLsi yalnız uygulama kabuğu döndürür. Sitenin belge kategorisi yanıtı → PDF önizleyici → **admin.saadet.org.tr/dosyalar/** bağlantıları izlendi. Güncel tüzük/program, eski **saadet.org.tr/upload/file/** adresleriyle birebir aynı hashleri verdi. Yayıncı/iletişim yanıtı kendi gövdesinde **Saadet Partisi** ve **https://saadet.org.tr/** alanlarını taşır. Dosya adındaki sayılar tarih yapılmadı; boş HTMLden sahte parti metni üretilmedi.
- Başkanlık/adresin tarihsel başlangıçları ve belgelerin kesin bitiş dönemleri bilinmiyor. Söylem–uygulama ve gerçekleşmiş finansman/harcamalar **Henüz incelenmedi**; ayrıntılı tüzük/program karşılaştırması sonraki fazdadır. Ortak dört gereksinim, **02-10** tamamlanmadan tamamlandı işaretlenmedi.

## Doğrulama ve okuma deneyimi

Önceki EMEP makbuzu **DELIVERY_RECEIPT_OK**, immutable raporu **PHASE2_PARTY_OK** verdi. Son girdi **DOSSIER_INPUT_OK**, Saadet **PHASE2_PARTY_OK**, pilot **PHASE1_AUDIT_OK**, yeni makbuz **DELIVERY_RECEIPT_OK** verdi. Dosya sözleşmesinin **10 testi** geçti. Yeni üretim kodu, bağımlılık, tablo veya bayrak eklenmedi; kanıt/kimlik/atıf/hash denetimleri değiştirilmedi.

Chromium’da **1365 ve 360 px** rapor ve kaynak bağlantıları açıldı: amaç metni önde, yöntem kapalı, alıntı siyah, özet koyu mavidir. Sicil UTF-8, scriptsiz/formsuz ve yerel stilli/görselli pasif sayfaya açılır. Tüzük, program ve 2002 tüzüğü doğru özgün PDFleri açar; HTTP **application/pdf** yanıtları ve SHA-256 değerleri birebir eşleşir. Programın **6. sayfasındaki** amaç/siyaset metnine gerçek PDF gezinmesi yapıldı ve iki genişlikte görüntüler alındı; masaüstü ve mobil seçilmiş görüntüler ajan tarafından okundu. Seçilmiş PDF sayfaları da Poppler/Cairo görüntüleriyle karşılaştırıldı. Otomatik başarı insan kaynak kabulü sayılmaz.

**Görünüm sınırı:** Sicilde parti amblemini taşıyan data-URL görseli pasif politika nedeniyle yerelleştirilmedi; kurum logosu ve temel düzen/stiller yereldir. Tarihsel gazetenin bazı görsel/CSS adresleri 404 verdi; AA/Meclis görünümlerinde bazı font veya yan stiller kaynak türü/erişim/bütçe sınırlarında kaldı. Özgünler ve ilk türevler korunur, son seçilmiş görünümler kendi manifestlerine bağlıdır. Piksel eşdeğerliği iddia edilmez. Özgün PDFler sabit sayfa düzenindedir; mobilde büyük yakınlaştırmada kaydırma gerekir.

## Görev commitleri, süre ve girdi düzeltmeleri

1. **Kaynak/girdi/arşivler:** `8ae6851`
2. **Denetlenmiş ayrı rapor:** `99c34d1`
3. **Zincirli makbuz ve CHECKS:** `08366bb`

Başlangıç **2026-11-11T20:52:29.189562+00:00**; süre yaklaşık **60 dakika**. Üç üretim görevi **117 dosyadır**. `actuals.tokens`, gerçekleşen dosya metinlerinin UTF-8 replacement çözümlemesinden sonra karakter/4 ölçüsüdür; model faturası veya harness token sayısı değildir.

İlk iki girdi adayında kategori JSONunun kendi gövdesinde tam yayıncı adını taşımaması atıf denetiminde reddedildi. Özgün kategori yanıtı/keşif kayıtları korundu; teknik kategori çifti okur bulgularından çıkarılarak tam kurum adı/siteURL içeren kaynak kaydı kullanıldı. Sonraki adayda iki **version_relation.id** eksikliği yakalandı ve mevcut şemaya göre tamamlandı. İlk sonuçlar CHECKS içindedir; nihai girdi bütün kontrollerden geçti. Bu düzeltmeler yeni mimari veya kapsam sapması değildir. Başarılı önceki makbuz, test ve görünüm kontrolleri gereksiz yere tekrarlanmadı; uzun denetimler kalıcı süreçlerde ayrı çıkış/sonuç kayıtlarıyla tamamlandı.

## Self-Check: PASSED

Girdi, rapor, makbuz ve CHECKS diskte; üç görev commit’i Git’te doğrulandı. **1.678** eski immutable dosya, önceki tablo satırları, yöntem kesimi ve doğru prefix korunur. `.gsd/` ile `.planning/milestone.lock` yerinde bırakıldı. Faz 2 **9/10** plandadır; sonraki plan **02-10 Demokrat Parti**, bu Saadet tesliminin bildirilmesinden sonradır.
