---
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
plan: '05'
subsystem: research-archive
tags: [kanıt, eşleştirme, mali-denetim, sqlite, kaynak-zinciri]
requires:
  - phase: 01-04
    provides: Kaynaklı ortak konu sözlüğü ve belge otoritesi
provides:
  - Ayrı açıklama ve oluş kanıtlarıyla uygun eşleşmeler ve aday geçmişi
  - Mali dönem, kimlik, para birimi, kapsam ve eksik doğrulaması
  - Girişim destekli güncel mali araştırma sonuçları
affects: [01-06, phase-verification]
tech-stack:
  added: []
  patterns: [aday ve eksik çözümü geçmişi, kaynaklı mali dönem, Decimal metni]
key-files:
  created: [tests/test_matches.py, tests/test_finance.py]
  modified: [src/arsiv.py, src/rapor.py, tests/test_tracer.py, data/current.json]
key-decisions:
  - Eşleşme adayları ve çözümlenen eksikler geçmişi korunarak kaydedilir.
  - Güncel partiye eski 2009 hesabı veya dönemi doğrulanmamış mali tutar bağlanmaz.
actuals:
  tokens: 2265748
  tasks: 2
  commits: 6
plan_head_before: 8a5937baa53feaab2fdf5db41e69cecb90876540
requirements-completed: []
duration: yaklaşık 53 dakika
completed: 2026-11-10
status: complete
---

# Phase 01 Plan 05: Söylem, uygulama ve mali araştırma özeti

**Kaynakları ayrı izlenen 18 söylem–uygulama eşleşmesi ve girişimlere dayalı mali araştırma; tutarı doğrulanmayan kayıtlar sıfıra çevrilmez.**

## Sonuçlar

- İki ayrı açıklama, 18 uygun eşleşme, gerekçeli dışlama ve doğrulanamayan adaylar kaydedildi. Toplu ve tekil il kayıtları örtüşebilir; bağımsız olay toplamı değildir. Ön seçim nihai kongre seçimi değildir.
- Aktör yetkisi ve ayrı oluş kanıtı kontrol edilir; bireysel milletvekili oyu kurumsal uygulama sayılmaz. Aday ve çözümlenen eksik tarihçesi korunur.
- Mali satır doğrulaması tüzel kimlik, kaynak pasajı, kaynakla ilişkili hesap dönemi, yayın tarihi, para birimi ve örgütsel kapsam gerektirir. Ondalık tutar metindir; girişime bağlı NULL ile belgeli sıfır ayrıdır. Hedefli mali audit beş başlığın araştırma ve kanıt/eksik durumunu kontrol eder.
- AYM 2013/103 özgün kararının web aracındaki önbellek metni 2009 hesabını ve 2012 birleşmesini gösterir: 2026 tüzel kişiliğine bağlanmadı. Doğrudan PDF 404, alternatif AYM dergisi sertifika doğrulaması hatası verdi; bu engeller kaydedildi.
- Kocaeli TV haberindeki il saymanlığına atfedilen tablo kaynaklı bir haber bulgusu olarak kaydedildi. Özgün tablo ve kesin başlangıç günü doğrulanmadığından mali tutar satırı üretilmedi. Haberin kaynak gösterdiği Bugün Kocaeli doğrudan erişimde 403 verdi; web önbelleği görüldü ancak yerel özgün kopyası alınamadı. Ulusal ve yerel rakamlar birleştirilmedi. Parti alan adı yetkisi ve özgün mali belgeler açık sınırlardır.
- Güncel yerel sürüm `5fb4e4eeb57d47cba243647f1979f2fc`; kesim `2026-11-10T14:38:46.154751+00:00` korunur.

## Doğrulama

Son sürümde `python3 tests/run.py` 31 test, `python3 tests/run.py --pattern test_finance.py` 3 test, genel audit ve `python3 src/arsiv.py audit --release current --check finance` geçti. Görev 1'de altı eşleşme testi ve `audit --check matches` geçti. Önemli açıklama, eylem ve mali kaynak pasajlarının insan incelemesi aşama sonunda bekliyor; yazılım metnin maddi anlamını veya kaynağın yetkisini kendiliğinden kanıtlamaz.

## Commitler

- `e61b7e6`: ilk yüzeysel eşleşme RED testi; davranış kanıtı olarak yeterli değildi.
- `8376061`: düzeltilmiş davranışsal eşleşme RED testi.
- `434e32f`: görev 1 eşleşme ve araştırma verileri.
- `993c59e`: görev 2 mali davranış RED testleri.
- `bc6d391`: görev 2 mali doğrulama, rapor ve araştırma verileri.
- `2984b8a`: haberin işaret ettiği kaynağın erişim girişimi ve zinciri.

## Sapmalar ve sorunlar

**[Rule 2] Aday ve eksik geçmişi:** Aynı adaya yeni kanıt geldiğinde eski eksik ve girişimleri korumak için aday ve çözüm ilişkileri eklendi; doğrulama görev 1 testlerindedir (`434e32f`).

**[Rule 1] Tracer testi:** Sabit toplam bulgu sayısı, yalnız kuruluş kanıtlarını sayacak şekilde düzeltildi (`434e32f`).

**[Rule 3] Kök koruması ve yürütme devamı:** İlk koruma çıkarma girişimi ve geniş yürütücü başarısız oldu; orkestratör bağlı kök korumasını sağlayıp görevi devam ettirdi. Üretim commitleri öncesi koruma çalıştırıldı. İlk sığ RED ardından davranışsal RED kaydedildi.

**[Rule 3] Kaynak zinciri:** Erişilen mali haberin atfettiği kaynak sonradan işlendi; 403 engeli gerekçeli eksik olarak korundu (`2984b8a`).

## Sınırlamalar

AYM araması erişilebilen sonuçlarla sınırlıdır; sonuçsuz arama kararın mevcut olmadığını kanıtlamaz. İl düzeyi haber ve ulusal bağış iddiaları bütün parti hesaplarını, yıllık toplamı veya kaynağın kesin dönemini kanıtlamaz. Bulunan diğer haberler ve parti alan adı için daha fazla doğrulama gerekebilir; yeni ilgili kaynaklarla tarama yeniden açılmalıdır. Doğrulanmış mali tutar bulunmaması sıfır gelir ya da harcama anlamına gelmez. Gereksinimlerin tamamlanması ortak aşama doğrulamasına bırakıldı.

## Self-Check: PASSED

Plan dosyaları ve listelenen commitler mevcut; son sürüm mali auditinden geçti.
