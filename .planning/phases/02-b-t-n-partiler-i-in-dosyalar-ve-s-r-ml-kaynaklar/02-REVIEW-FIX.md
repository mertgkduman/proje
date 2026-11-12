---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
fixed_at: 2026-11-12T00:08:12Z
review_path: .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-REVIEW.md
iteration: 1
findings_in_scope: 6
fixed: 6
skipped: 0
status: all_fixed
---

# Faz 02: Kod İnceleme Düzeltme Raporu

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
