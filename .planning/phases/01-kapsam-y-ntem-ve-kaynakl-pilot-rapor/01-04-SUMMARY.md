---
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
plan: "04"
subsystem: belge-ve-ortak-konu
tags: [kaynak-otoritesi, tüzük, program, taksonomi, sqlite]
requires: [01-03]
provides: [yetki-zinciri, pilot-belge-arama-kayitlari, kaynakli-ortak-konu]
affects: [01-05, 01-06]
tech-stack:
  added: []
  patterns: [sayfa-gorselinin-elle-dogrulanmasi, surumlu-konu, girisime-bagli-eksik]
key-files:
  created: [tests/test_documents.py, tests/test_topics.py]
  modified: [src/arsiv.py, src/rapor.py, data/current.json]
key-decisions:
  - "TİP belgesi yalnız ortak sözlük dayanağıdır; parti dosyasını incelenmiş yapmaz."
  - "Yeni Parti kopyalarının otoritesi veya 9 Kasım sürüm değişikliği doğrulanmadan içerik parti bulgusu yapılmaz."
requirements-completed: []
status: complete
completed: 2026-11-10
duration: "yaklaşık 18 dakika"
plan_head_before: 3e483e07550b06a29d4daca560107a528b6acefd
actuals:
  tokens: 361987
  tasks: 2
  commits: 4
---

# Phase 1 Plan 4: Belge otoritesi ve ortak konular özeti

Yeni Parti için arşivlenen tüzük ve program kopyalarının doğrulanamayan yetkisi başlıklarda açıkça gösterildi; TBMM ve Yargıtay zinciriyle doğrulanan TİP tüzüğü ortak sözlüğün organ seçimi konusuna dayanak yapıldı.

## Kaynaklar ve sınırlar

- Tüzük ve program için `yenipartiyiz.biz` üzerindeki HTML ve PDF kopyaları baytlarıyla arşivlendi. Alan adının parti adına yetkisi ve imzalı özgün sürümle bağlantısı doğrulanmadığından iki başlıkta girişime bağlı **Doğrulanamadı** durumu yer alır; bu, belge bulunmadığı veya içeriklerin yanlış olduğu iddiası değildir. PDF kapaklarındaki tarihler doğrulanmış belge tarihi olarak işlenmedi.
- 9 Kasım 2026 tarihli bir haber tüzük değişikliği olasılığına işaret eder. Doğrudan arşivleme girişimi HTTP 403 verdi; ilgili uç engelli ve tarama açık bırakıldı. Yanlış yazılmış bir PDF adresindeki gerçek HTTP 404 da kaydedildi. Haber dizini özgün belge yerine kullanılmadı.
- Yargıtay'ın TİP sicili ile TBMM'de yayımlanan TİP komisyon raporunun PDF sıra 5 / basılı 6. sayfası ad, genel merkez adresi ve `tip.org.tr` alanını ilişkilendirir. Taranmış PDF sayfası Poppler-glib ve Cairo ile görüntülenerek elle kontrol edildi; otomatik metin doğrulaması iddia edilmedi. PDF SHA-256: `467bbd88a6f97cee9c144e610f0eb3e2dd958dc59f8844b19e95652f6c5bc274`.
- Bu zincirle erişilen TİP tüzüğündeki kongre seçimi pasajı, sürüm 1 ortak sözlükte **Organ seçimi** için dayanak oldu. Belgenin kesim anındaki sürümü doğrulanmadı; bu kayıt TİP dosyasının araştırıldığı veya tarihsel içeriğinin doğrulandığı anlamına gelmez. Diğer 11 öneri dayanağı doğrulanmamış adaydır.
- Veri kesimi `2026-11-10T14:38:46.154751+00:00` korunur. Arama sorguları, kaynak uçları, yönlendirmeler, kontrol girişimleri ve planlanan kurumsal/yetkili/bireysel aktör sorguları kaydedildi; gerçek tarama kapanışı iddia edilmedi. Güncel yerel release `a60bae844196479aa15f47e7564622b1`.

## Doğrulama

- `python3 tests/run.py --pattern test_documents.py`: 2 test; `python3 tests/run.py --pattern test_topics.py`: 3 test.
- `python3 tests/run.py`: 22 test, `TESTS_OK`; `python3 src/arsiv.py audit --release current`: `AUDIT_OK`.
- Yanlış parti kanıtı, yetkisiz parti otoritesi ve dayanağı bulunmayan onaylı konu reddi kontrol edildi. PDF bayt özeti ve sayfa varlığı denetlenir; taranmış sayfa metninin doğruluğu elle kontrol kaydına dayanır.
- Faz sonu insan kontrolünde arşivli TİP PDF sıra 5 sayfasındaki ad/adres/alan adı ve TİP tüzüğündeki kısa pasaj tekrar karşılaştırılmalı; Yeni Parti belgelerinin yetki ve sürüm sınırı değerlendirilmelidir. Bu, otomatik testlerin yerine geçtiği iddia edilmeyen, faz sonuna toplanmış kontroldür.

## Görev commitleri

1. Belge ve kaynak sınırları: RED `0cf44e4`, GREEN `ec3b59d`.
2. Ortak konu: RED `1d2a705`, GREEN `f8abd15`.

## Deviations from Plan

TİP kaynağı planın açıkça izin verdiği ortak sözlük dayanağı olarak kullanıldı. Yeni Parti özgün otoritesi ve güncel tüzük sürümü bağı doğrulanamadığından kaynaklı parti özelliği üretilmedi; mevcut iki başlık doğrulanamama durumunu ve girişimlerini gösterir. TİP'in kesim anındaki sürümü için ayrıca kanıt yoktur.

## Self-Check: PASSED

Görev commitleri, iki test dosyası, TİP kaynakları ve güncel release mevcuttur; otomatik doğrulamalar yukarıda verilmiştir.
