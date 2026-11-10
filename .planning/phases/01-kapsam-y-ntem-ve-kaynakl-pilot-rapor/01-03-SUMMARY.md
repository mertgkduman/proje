---
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
plan: "03"
subsystem: kaynak-zinciri
tags: [kaynak, ysk, sqlite, eksik-bilgi]
requires: [01-02]
provides: [kaynak-kuyrugu, girisime-bagli-eksik-durumlari, ysk-arsivi]
affects: [01-04, 01-05, 01-06]
tech-stack:
  added: [sistem-Poppler-glib]
  patterns: [baglantili-girisim, degistirilmez-belge-surumu, acik-arastirma-durumu]
key-files:
  created: [tests/test_chain.py, tests/test_missing.py]
  modified: [src/arsiv.py, src/rapor.py, data/current.json, .planning/WINDOWS.md]
key-decisions:
  - "Alan adı sahipliği, incelenen Yargıtay ve TBMM kayıtlarıyla doğrulanamadığında doğrulanmamış bırakılır."
  - "YSK PDF pasajı Poppler ile belirtilen PDF sayfasında doğrulanır; yayımlanma günü bilinmiyor."
status: complete
completed: 2026-11-10
duration: "yaklaşık 22 dakika"
plan_head_before: fc915082e129be9647d3153b77203d29ca4fd098
actuals:
  tokens: 70653
  tasks: 2
  commits: 8
---

# Phase 1 Plan 3: Kaynak zinciri ve eksik durumları özeti

İlgili kaynak uçları, erişim ve doğrulama girişimleri, kapanma ve yeniden açılma geçmişi yerel kayıtlara bağlandı; YSK faaliyet raporunun özgün PDF'si ve ittifak protokolü başlığı doğrulanıp arşivlendi.

## Kaynaklar ve bulgular

- YSK 2023 faaliyet raporu `2026-11-10T15:09:42.988717+00:00` anında yakalandı; SHA-256 `8192d9d796b57b7d478baf7f74cf47f94265ad2d89d8c195a3df76442ce201f2`. PDF'nin 76. sayfasındaki (basılı 69) ittifak protokolü başlığı `ysk-2023-protocol` pasajıdır. Daha önce açık kalan WINDOWS kaydı kapatıldı. İlk başarısız erişimden sonra tekrar denemesi başarıyla sonuçlandı.
- `https://yeni-parti.org` için güncel denemede HTTP 522 alındı; bu girişime dayalı Erişilemedi kaydı belge yokluğu anlamına gelmez. `https://yeni-parti.org.tr/` HTML yanıtı arşivlendi; alan adı sayfasının kendi beyanı sahiplik doğrulaması sayılmadı. İki alan adı için incelenen arşivli Yargıtay ve TBMM kayıtlarında ilgili adres bulunmadığından yetki bağı Doğrulanamadı olarak kaydedildi.
- Önceki planın Yargıtay ve TBMM yakalamaları girişimleriyle ilişkilendirildi; TBMM sandalye sayfasından listeye gerçek bağlantı kaydedildi. Önceki arama sorguları bilinmediği yerde yeni sorgu uydurulmadı. Mevcut kapsam kesimi `2026-11-10T14:38:46.154751+00:00` korunmuştur. Gerçek tarama kapanışı oluşturulmamıştır.
- Güncel yerel release `663b315e2f9742e1bbe86b0af9d3bf0e`; kamuya yayın yapılmadı. Söylem/uygulama ile finansman başlıkları Henüz incelenmedi durumundadır.

## Doğrulama

- `python3 tests/run.py --pattern test_chain.py`: 1 test; `python3 tests/run.py --pattern test_missing.py`: 2 test. Sentetik durumlar kopyalanmış izole çalışma veritabanlarında kullanıldı.
- `python3 tests/run.py`: 17 test, `TESTS_OK`; mevcut release için `AUDIT_OK`. Önceki sekiz release ayrıca denetlendi.
- URL normalizasyonu, yinelenen URL/hash, yeni hash, döngü kuyruğu, bekleyen uç, yeniden açma, girişim kapsamı ve üç eksik durumunun eşlemesi test edildi.
- PDF metin doğrulaması çalışma ortamındaki `libpoppler-glib` sistem kütüphanesine bağlıdır. PDF erişimi ve pasajın insan tarafından incelenmesi faz sonu kontrolünün yerini almaz.

## Görevler ve commitler

1. Zincir: RED `1b71f66`, GREEN `4a07ab9`; ek düzeltme ve testler `cdf2594`, `0815418`, `81eb5e1`, `7ccc9f1`.
2. Eksik durumları: RED `1b2411b`, GREEN `5a546de`.

## Deviations from Plan

- [Rule 3 - Engeli giderme] PDF pasajı doğrulaması önce yalnız ham baytları arıyordu; sayfaya bağlı metin çıkarmak için mevcut sistem Poppler kütüphanesi kullanıldı. Paket kurulmadı.
- [Rule 1 - Hata] Erişilemeyen kaynak için tanımlı URL ve girişim adresi eşleşmesi zorunlu kılındı; eski release HTML denetimini korumak için zincir bağlantısı gösterimi snapshot seçeneğiyle sürümlendi.
- İlk zincir RED testi mevcut olmayan yazıcı işlevini doğruluyordu; ayrıntılı davranış testleri GREEN sırasında genişletildi. Bu nedenle ilk RED, kapanma davranışının doğrudan başarısızlık kanıtı değildir; faz doğrulayıcısı bu TDD sınırlamasını göz önünde bulundurmalıdır.

## Self-Check: PASSED

Test dosyaları, görev commitleri ve arşivli YSK PDF'si mevcut; test ve release denetimleri yukarıda kaydedildi.
