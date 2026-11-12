---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
fixed_at: 2026-11-12T00:39:46Z
review_path: .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-REVIEW.md
iteration: 2
findings_in_scope: 3
fixed: 2
skipped: 1
status: partial
---

# Faz 02: Kod İnceleme Düzeltme Raporu

## CR-10 — Tamamlanmış fazın yerel raporu yenilenemiyordu

**Durum:** Düzeltildi; mantık değişikliği insan doğrulaması gerektirir.

**Kod commit:** `353a5ee`

**Yayın commit:** `72b6908`
**Dosyalar:** `src/arsiv.py`, `src/dosyalar.py`, `tests/test_dossiers.py`

Yeni `publish --refresh` yolu yalnız tam teslim sırası ve değişmemiş son teslim kimliğiyle kabul edilir. Normal sıradaki parti kuralları, politika inişi, önceki dosya kayıtlarının korunması, bütün parti ve faz 1 denetimleri ve işaretçi öncesi yayın denetimi korunur. Kısmi, yeniden sıralanmış veya değiştirilmiş teslimler ve partiyle birlikte yenileme reddedilir. Üç odaklı test geçti. Resmî CLI ile yeni yerel `1d6b49b307f04a258c1a11d90978fe7c` üretildi; `PHASE2_AUDIT_OK` alındı ve kayıtlar önceki sürümle kimlik alanı dışında eşit. Komutlar ve değişmezlik kanıtı `02-REFRESH.md` dosyasındadır. Eski makbuzlar ve yayınlar değiştirilmedi.

## İkinci inceleme — 2026-11-12

**Durum:** CR-07 ve CR-08 düzeltildi; CR-09 meta/BOM bildirimli HTML için düzeltildi, yalnız HTTP başlığında kalan kodlama sınırı nedeniyle kısmen açık. Mantık değişiklikleri için insan doğrulaması gereklidir.

### CR-07 — Yazar atfı sürüm geçmişinde kayboluyordu

**Commit:** `4610441`  
**Dosyalar:** `src/rapor.py`, `tests/test_report.py`  
Her sürüm geçmişinde kendi kayıtlı yazarı ve atıf dayanağı, o sürümün etiketi altında gösterilir. Yayıncı, tarih veya gerekçe başka sürümün künyesine taşınmaz. Üç gerçek yazar kaydı ve farklı künyeli kardeş sürümler test edildi.

### CR-08 — Kimlik notunda entity çözümlemesi kaynak türünü göz ardı ediyordu

**Commit:** `acef9a2`  
**Dosyalar:** `src/rapor.py`, `tests/test_report.py`  
Kimlik notunun kendi ve ilişkili pasajları kaynak türünü belirlemek için kullanılır; HTML entity'leri çözülür, PDF'deki literal dizeler korunur. Her iki köken test edildi.

### CR-09 — HTML kodlama zinciri kısmen düzeltildi

**Commit:** `d56106c`  
**Dosyalar:** `src/arsiv.py`, `src/kaynaklar.py`, `tests/test_archive_views.py`  
Meta/BOM bildirimli HTML, yakalama, okunabilir türev, kaynak atfı, kimlik ve pasaj/export kontrollerinde ortak kodlama çözümlemesini kullanır. Eski replacement tabanlı türevler de doğrulanır ve yerinde değiştirilmez; yeni çözülemeyen yakalamalar açık hatayla durur. Windows-1254 meta bildirimli örnek yakalamadan pasaj/export ve yayıncı atfına kadar test edildi.

**Kalan sınır:** HTTP başlığında bulunan ancak HTML baytlarında meta/BOM ile bulunmayan UTF-8 dışı charset mevcut sürümlü kayıt şemasında kalıcı tutulamaz. Böyle bir yeni yakalama açık hatayla reddedilir; yeniden üretilebilir destek için sürümlü metadata ve geçmişle uyumlu migration gerekir. Bu nedenle CR-09 bütünüyle kapanmış sayılmaz. HTTP bilgisi ile bayttan çözümlenen içerik aynıysa yakalama kabul edilir.

### Mobil arayüz ve regresyon testi

**Commit:** `dda76a8`  
Yalnız üretici 14 yeni `src/rapor_v14.css` dosyasını kullanır: mobil yatay gezinme ipucu, daha büyük kaynak/bölüm bağlantıları, okunaklı küçük metinler ve araştırma raporu başlığı eklendi. Gerçek Chromium'da sekme klavye gezintisi, kaydırılabilirlik, hedef alanları ve metin boyutu doğrulandı. Üretici 13 ve `src/rapor_v11.css` değiştirilmedi.

**Commit:** `8b85586`  
TİP yayın entegrasyon testi yeni yayın üreticisini sabit 13 yerine etkin üretici sürümüyle karşılaştırır; eski 13'ün bayt eşitliği ayrıca sınanmaya devam eder.

### İkinci tur doğrulama

- `PYTHONPATH=src:tests python -m unittest test_archive_views test_report` — 25 test geçti; gerçek Chromium mobil DOM kontrolü dahildir.
- `PYTHONPATH=src:tests python -m unittest -v test_source_policy.SourcePolicy.test_turkish_publisher_case_preserves_dotted_and_dotless_i test_source_policy.SourcePolicy.test_short_name_html_uses_same_party_host_and_full_name_anchor` — 2 test geçti (8.191 saniye).
- Düzeltme öncesi `python3 tests/run.py` — 91 test, 90 başarılı ve 1 başarısız; 1583.953 saniye. Tek hata `tests/test_dossiers.py:170` için `14 != 13` idi. Günlük: `/tmp/phase02-regression-final.log`; wrapper sonuç JSON'u oluşmadı.
- `PYTHONPATH=src:tests python -m unittest -v test_dossiers.DossierTracer.test_real_tip_publish_audit_html_and_receipt_in_isolated_data` — başarısız olan entegrasyon testi düzeltmeden sonra geçti; 1 test, 13.225 saniye.
- Geçici dokuz partili rapor ve Chromium görüntüleri: `/tmp/phase02-renderer14-visual/data/releases/review/index.html`, `/tmp/phase02-renderer14-visual/report-360.png`, `/tmp/phase02-renderer14-visual/report-1365.png`. 360 ve 1365 genişlikte sayfa taşması yok; iki pasif arşiv bağlantısı doğrulandı (`BROWSER_ARCHIVES_OK`).
- Tarihsel CSS 11, renderer 13, özgün nesneler ve yayınlar değiştirilmedi. Yeni okuyucu çıktısı için yeni yayın gerekir; mevcut sürümün göçü gerekmez.

## Birinci inceleme — 2026-11-12

**Düzeltilme zamanı:** 2026-11-12T00:08:12Z  
**Kaynak inceleme:** `02-REVIEW.md`  
**Yineleme:** 1

Altı kritik bulgu düzeltildi; atlanan bulgu yok. Bulgular davranış ve mantık hataları olduğundan her düzeltmenin durumu **fixed: requires human verification** olarak değerlendirilmelidir.

## Düzeltilen Bulgular

### CR-01: Varlık yönlendirmesi doğrulanmadan hedefe istek gönderiliyor

**Dosyalar:** `src/arsiv_gorunum.py`, `tests/test_archive_views.py`  
**Commit:** `15b5e99`  
Her istek ve yönlendirmede izinli ana makine ve tüm DNS sonuçları kontrol edilir; genel ağ dışı, multicast veya ayrılmış adresler reddedilir. Bağlantı çözümlenen ve kontrol edilen IP'ye sabitlenir; HTTPS sertifika denetimi özgün ana makine adıyla yapılır. Yönlendirme sayısı sınırlıdır. Testler özel ağa yönlendirmeyi, DNS yeniden çözümlemesini ve karma DNS yanıtını ağ isteği göndermeden sınar.

### CR-02: Kapanış etiketi olmayan embed sonrasındaki içerik siliniyor

**Dosyalar:** `src/arsiv_gorunum.py`, `tests/test_archive_views.py`  
**Commit:** `2fad684`  
Boş yasak öğeler blok yığınına eklenmeden çıkarılır; sonraki metnin ve kapanış etiketlerinin korunduğu test edilir.

### CR-03: UTF-8 dışındaki HTML belgeleri bozuk metne dönüştürülüyor

**Dosyalar:** `src/arsiv_gorunum.py`, `src/arsiv.py`, `tests/test_archive_views.py`  
**Commit:** `ed88e9b`  
BOM, isteğe bağlı HTTP charset ve HTML meta bildirimi sırasıyla değerlendirilir; çözümleme hataları yerine koyma karakteriyle gizlenmez. Yakalama sonucu varsa HTTP charset değerini ayrıca verir; mevcut kayıt şeması ve özgün baytlar değiştirilmez. Testler Windows-1254, UTF-8, BOM, HTTP charset, hata ve özgün hash durumlarını kapsar.

### CR-04: Görünüm kimliği manifestteki kaynak adresini kapsamıyor

**Dosyalar:** `src/arsiv_gorunum.py`, `tests/test_archive_views.py`  
**Commit:** `fbaf1c1`  
Yeni biçim 2 kimliği, kaynak URL'si ve sınırlamalar dahil manifestin anlamlı alanlarından türetilip doğrulanır. Biçim 1 görünümleri eski kimlikleri ve baytları değiştirilmeden kabul edilir. Farklı URL ve sınırlamalar ayrı kimlik üretir.

### CR-05: Yazar tamamlama başka sürümün tüm künyesini kullanıyor

**Dosyalar:** `src/rapor.py`, yeni `src/rapor_v13.py`, `src/arsiv.py`, `tests/test_report.py`  
**Commit:** `4e4a975`  
Desteklenmeyen aynı hash üzerinden atıf devralma kaldırıldı. Her sürüm kendi yazar, yayıncı, tarih ve dayanağını korur. Mevcut üretici 13 birebir donduruldu, yeni üretici 14'e geçildi ve eski/yeni üretici yönlendirmesi sağlandı. Aynı hash'li farklı atıflar test edilir.

### CR-06: HTML entity çözümlemesi PDF'deki birebir alıntıyı değiştiriyor

**Dosyalar:** `src/rapor.py`, `tests/test_report.py`  
**Commit:** `f08bb25`  
PDF pasajları ve bulguları düz metin olarak HTML için kaçışlanır; eski ham HTML pasajlarının entity çözümlemesi korunur. `&copy;`, `&amp;` ve sayısal entity benzeri gerçek PDF dizeleri kaynak künyesinde ve bulguda aynen görünür.

## Doğrulama ve uyumluluk

Doğrulamalar, oturumda önceden kararlaştırıldığı üzere **ana çalışma alanında** yapıldı; ayrı worktree kullanılmadı.

- Her commit öncesinde değişen bölüm yeniden okundu ve Python AST sözdizimi kontrolü yapıldı: `python -c "import ast; from pathlib import Path; [ast.parse(Path(p).read_text()) for p in (...)]"`. CR-01 için ayrıca `python -m py_compile src/arsiv_gorunum.py tests/test_archive_views.py` çalıştırıldı.
- `PYTHONPATH=src:tests python -m unittest test_archive_views test_report` — **20 test geçti**. Ağ güvenliği testleri dış veya özel ağ isteği yapmadan taklit edilmiş DNS/soketleri kullanır.
- `git show e6c2b92:src/rapor.py | cmp -s - src/rapor_v13.py` — başarı; dondurulan dosya önceki üreticiyle bayt olarak eşittir. Rapor testi `bcc67d04d9d741e191589d0f5ac173ca` yayınının üretici 13 ile birebir üretildiğini ayrıca doğrular.
- Gerçek mevcut biçim 1 arşiv görünümleri arşiv testlerinde doğrulandı. Nesneler, görünümler, snapshot'lar, yayınlar, işaretçiler ve makbuzlar değiştirilmedi.
- Pahalı yayın, makbuz ve audit zincirleri tekrarlanmadı. Mevcut yayın geçerliliğini korur; düzeltmelerin okuyucuya yansıması istenirse üretici 14 ile **yeni** yayın gerekir, eski yayının yerinde göçü gerekmez.

---

_Düzelten: gsd-code-fixer; yineleme 1_
