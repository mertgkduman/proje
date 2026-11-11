---
phase: quick-261111-j4v
plan: "01"
subsystem: archive
tags: [pdf, ctypes, poppler, lru-cache, integrity]
requires:
  - phase: 02-06
    provides: Mevcut Yeni Yol sürümü ve İYİ Parti'ye bağlı teslim makbuzu
provides:
  - Başarılı PDF kütüphane ve sayfa metni işlemlerinin sınırlı süreç içi yeniden kullanımı
  - Gerçek PDF, değişen baytlar, bağımlılık sırası ve sıcak denetim bozulma regresyonları
affects: [archive-validation, receipt-check]
actuals:
  tokens: 4587
  tasks: 2
  commits: 1
  plan_head_before: 3afdb4e5d5fef1c7cefa9b67ef81f31dec63eaf1
tech-stack:
  added: []
  patterns: [bounded-success-only-process-cache, current-byte-sha256]
key-files:
  created:
    - .planning/quick/261111-j4v-ayn-pdf-sayfalar-n-n-s-re-i-indeki-yinel/261111-j4v-SUMMARY.md
  modified: [src/arsiv.py, tests/test_documents.py]
key-decisions:
  - Kütüphane anahtarı etkin find_library nesnesi; sınır 4 başarılı yükleme.
  - Metin anahtarı çözümlenmiş yol, güncel gerçek baytların SHA256 değeri ve sayfa indeksi; sınır 256 başarılı metin.
  - Makbuz ve ata denetimleri her çağrıda çalışır; sonuçları önbelleğe alınmaz.
requirements-completed: [QUICK-261111-j4v]
duration: 9min
completed: 2026-11-11
status: complete
---

# Quick 261111-j4v: PDF yeniden kullanımı özeti

**Gerçek PDF sayfasının yinelenen okuması üç kütüphane yüklemesi ve tek ayrıştırmayla aynı metni verir; her çağrı güncel baytları yeniden özetler.**

## Uygulama

Başarılı kök doğrulamasından son ölçümün kaydına kadar ölçülen aralık 18:53:55–19:02:40 UTC'dir (yaklaşık dokuz dakika; başlangıç bağlam okumaları hariç).

- Başarılı yerel kütüphane yüklemeleri `lru_cache(maxsize=4)` içinde etkin `ctypes.util.find_library` nesnesine göre tutulur; gerekli ctypes imzaları bir kez hazırlanır.
- Başarılı `str` metinleri `lru_cache(maxsize=256)` içinde çözümlenmiş yol, gerçek dosya SHA256 değeri ve sayfa indeksine göre tutulur. İstatistik metadata'sı anahtar olarak kullanılmaz.
- Bağımlılık kontrolü dosya erişiminden önce kalır. Başarısız yükleme/ayrıştırma saklanmaz; belge, sayfa ve metin işaretçilerinin mevcut `finally` temizliği korunur. PDF baytları saklanmaz.
- `sha`, export, sürüm/ata denetimleri, makbuz döngüleri, doğrulayıcılar ve rapor üreticileri değiştirilmedi; kalıcı önbellek veya yeni paket yoktur.

## Doğrulama

| Kontrol | Sonuç | Süre |
|---|---|---|
| PDFReuseTest + mevcut bağımlılık hatası testi | 7 test geçti | 0.108 s |
| PDFReuseTest + WarmAuditTest + bağımlılık hatası testi | 8 test geçti | 0.920 s |
| `python3 tests/run.py --pattern test_documents.py` | TESTS_OK count=11 | unittest 78.574 s; real 79.26 s |
| `python3 tests/run.py --pattern test_publication.py` | TESTS_OK count=11 | unittest 42.591 s; real 43.07 s |
| `python3 tests/run.py --pattern test_source_policy.py` | TESTS_OK count=12 | unittest 47.554 s; real 48.02 s |

Üç paket bağımsız süreçlerde eşzamanlı çalıştırıldı; toplam 34 test geçti. Tarihsel renderer/politika denetimi korunur. Yeni sıcak denetim regresyonu gerçek tarihsel sürümün yalnız gereken dosyalarının geçici kopyasında PDF özgün kaynağını, okunabilir kopyayı, HTML çıktısını ve manifesti sırayla bozar; her bileşeni geri yükledikten sonra başarılı denetimi yeniden doğrular. Böylece önceki bozulma sonraki reddi maskelemez.

Görev içi RED çalıştırmasında gerçek arşiv PDF'sinin iki okuması 6 kütüphane yüklemesi ve 2 Poppler ayrıştırması yaptı; hedef 3/1 idi. SHA çağrı sayısı da hedef 2 yerine 0 idi. GREEN aynı gerçek yol için 3/1 ve iki gerçek SHA hesaplamasını doğrular. Gerçek CDLL ve Poppler açma işlevleri araçlandırıldı; sahte PDF metni kullanılmadı. Aynı boyut ve geri yüklenmiş `mtime_ns` ile bozuk baytlar reddedildi; sıcak bağımlılık hatası dosyaya erişmedi; yükleme ve ayrıştırma hataları sonraki çağrılarda yeniden denendi.

## Tek sınırlı mevcut makbuz ölçümü

Komut: `time -p timeout 180 python3 src/arsiv.py receipt-check --input data/deliveries/02-06-yeni-yol.json`.

- Çıkış kodu **124**; Bash `real 180.01`, `user 75.19`, `sys 7.50`; Python monoton saatiyle 180.020 s.
- `DELIVERY_RECEIPT_OK` üretilmedi. Süre sınırı aşıldığından bu ölçüm makbuz başarısı veya toplam hızlanma kanıtı değildir. Önceki yaklaşık beş dakikalık gözlem yeniden ölçülmedi; ikinci bir makbuz kontrolü başlatılmadı.
- Mevcut makbuz baytları bellekte önce/sonra birebir karşılaştırıldı: **eşit**. SHA256 her iki durumda `03ac996bf65356e9b7bcbee83a3eea2546c099b659567a9085690ffc32c18e6f`.
- Makbuz `mtime_ns` değeri önce/sonra **1794422205153240000**; `release_id` önce/sonra **732fcd2bfc954200b4292c51ef29f526**.
- `data/` altındaki **1.215 dosyanın** tamamının SHA256 ve `mtime_ns` değerleri aynı Python sürecinde bellekte önce/sonra karşılaştırıldı. Eklenen/silinen dosya, değişen içerik veya değişen mtime yoktur.

## Commit ve kapsam

Görev 1: `a475f5aa3155c42739dd53c45ab5d2ce8cc79726` — `perf(quick-261111-j4v): reuse successful PDF libraries and page text`.

Commit yalnız `src/arsiv.py` ve `tests/test_documents.py` dosyalarını içerir; normal Git hook yolu kullanıldı. Görev 2 bu doğrulama kaydıdır; PLAN/SUMMARY/STATE belge commit'i orkestratöre aittir. Git ledger tabanı `3afdb4e5d5fef1c7cefa9b67ef81f31dec63eaf1`; `git rev-list --count <taban>..HEAD` ölçümü bu özet yazılırken **1** idi. `actuals.tokens`, kaynak/test diff'i ile bu yeni özetin diff'i üzerindeki karakter/4 ölçeğidir.

Faz 2 ilerleyişi **6/10**, sıradaki plan **02-07 DBP** olarak kaldı. Yeni veri, sürüm, makbuz, yayın veya okuyucu içeriği üretilmedi. Mevcut `.gsd/` ve `.planning/milestone.lock` korunur.

## Sapmalar ve sınırlar

- Ortamda `/usr/bin/time` yoktur. İlk üç çağrı test başlatmadan 127 döndü; üç suite ve tek makbuz ölçümü Bash'in `time -p` aracıyla çalıştırıldı. `timeout 180` sınırı korunur.
- Başlangıçta guard metnini bağlayan değiştirmenin kapsamı atama dışına taştı ve sahte `pin-unbound` hatası verdi. Aynı hücrede sonuç kontrolü eksik olduğundan yalnız test patch'i yine uygulanmıştı; üretim kodu veya commit henüz yoktu. Gerçek kök doğruydu. Orkestratörün açık kurtarma kararıyla yalnız ilk atama bağlandı; `ROOT_PIN_OK` alındı ve commit öncesinde yeniden denetlendi.
- Görev içi RED → GREEN kanıtı yukarıdadır; ayrı RED test commit'i oluşturulmadı, üretim ve regresyonlar tek atomik performans commit'inde tutuldu. Plan `type: execute` biçimindedir; plan düzeyinde TDD kapısı çalıştırılmadı.
- Makbuzun 180 saniye içinde tamamlanması doğrulanamadı. Bu sınırlı quick görevi PDF yeniden kullanımını kanıtlar; bütün makbuz denetiminin toplam süresi için başarı iddiası yapmaz.

## Self-Check: PASSED

Üretim commit'i mevcut ve yalnız iki beklenen dosyayı içeriyor; `git diff --check` temiz. Atlanan test, uygulama stub'ı veya yeni ağ/şema yüzeyi yoktur. Bu özet oluşturuldu; belge commit'i ve quick STATE kaydı orkestratör tarafından tamamlanacaktır.
