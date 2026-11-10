---
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
plan: '06'
subsystem: report-and-acceptance
tags: [html, erişilebilirlik, sqlite, kaynak, denetim]
requires:
  - phase: 01-05
    provides: Kaynaklı eşleşmeler, mali araştırma ve eksik geçmişi
provides:
  - Sekmeli yerel rapor ve kaynak bağlantıları
  - Ajan pasaj inceleme kayıtları ve faz kabul denetimi
affects: [phase-verification]
tech-stack:
  added: []
  patterns: [sürümlü rapor üreticisi, salt okunur snapshot denetimi]
key-files:
  created: [tests/test_report.py, tests/test_acceptance.py, src/rapor_legacy.py, src/rapor_v2.py, src/rapor_v3.py, src/rapor_v4.py]
  modified: [src/rapor.py, src/arsiv.py, tests/browser_probe.py, README.md, data/current.json]
key-decisions:
  - Eski kapalı sürümler kendi rapor üretici sürümleriyle denetlenir.
  - Ajanın kaynak incelemesi insan incelemesi veya bağımsız olay doğrulaması sayılmaz.
actuals:
  tokens: 430114
  tasks: 2
  commits: 4
plan_head_before: 2c94f01886a35617ae88bbd859cc0d9dd62d1c99
requirements-completed: []
duration: yaklaşık 16 dakika
completed: 2026-11-10
status: complete
---

# Phase 01 Plan 06: Sekmeli rapor ve yerel kabul özeti

**Dokuz parti sekmesi, kaynak bağlantılı pilot rapor, 21 ajan pasaj incelemesi ve kapalı snapshot'tan faz denetimi yerel sürümde birleştirildi.**

## Sonuç ve doğrulama

- Güncel yerel sürüm `a179d4c5af0d4ab983cb0dbda61140c5`; kesim `2026-11-10T14:38:46.154751+00:00`. Dokuz parti ve karşılaştırmalı özet, beş ortak başlık, kapsam/yöntem, kaynak kayıtları ve çözümlenen eksiklerin geçmişi görünür. Diğer partiler ve karşılaştırmalar henüz incelenmemiş/hazırlanmamış olarak gösterilir.
- Gerçek özgün HTML kopyalarında 21 bulgunun bağlı pasajları ve çevreleri incelendi; `reviewer_kind=agent` kayıtları oluşturuldu. Haberlerdeki olay ve beyanların bağımsız doğrulandığı iddia edilmedi. İnsan incelemesi kaydı oluşturulmadı.
- HTML, JSON ve SQLite aynı kapalı sürümden denetlenir; arşiv, hash, FK, pasaj, tarih ve ilgili eşleşmeler kontrol edilir. Karşılaştırma kanıtsız kabul edilmez; çoklu kanıt FK'sı yalıtılmış veritabanında sınandı. Yerel sunucu yalnız loopback ve yayın/arşiv yollarını açar.
- `python3 tests/run.py`: `TESTS_OK count=37`, 29.244 saniye. `python3 src/arsiv.py audit --release current --phase 1`: `PHASE1_AUDIT_OK a179d4c5af0d4ab983cb0dbda61140c5`. Chromium testleri `file://` ve loopback üzerinde sekme tıklaması, klavye, kaynak hash'i, geri/fokus, kapatma, dar görünüm ve arşiv erişimini sınadı. URL/metin enjeksiyonu, kökten kaçış, eksik başlık ve sunucu yolu için negatif kontroller çalıştı.
- 18 uygun eşleşme korunur; toplu ve yerel olaylar ve ayrı açıklamalar örtüşebilir, sayı bağımsız olay toplamı değildir. Yeni Parti tüzük/program kopyalarının yetkisi doğrulanmadı; TİP belgesi yalnız ortak konu sözlüğündeki bir konuya dayanak sağlar. Mali sıfır ile bilinmeyen ayrıdır.

## Açık insan incelemeleri ve varsayımlar

Kaynak pasajları, TBMM/Yargıtay kopyaları, tarafsızlık ve arayüz faz sonu insan incelemesini bekler. Kullanıcı yerel raporda klavye ve dar ekranı, citation ve doğrudan kaynak hash'ini, geri/fokusu, özgün bağlantıyı, çevrimdışı arşivi, siyah tırnaklı alıntı ile koyu mavi özeti incelemelidir. Yalnız yapılmış inceleme kaydedilmelidir.

`COVERAGE.md` içindeki 13 satırın tamamı (`KAPS-01`, `KAPS-02`, `KAPS-03`, `KAPS-04`, `KAY-02`, `KAY-03`, `MET-01`, `MET-02`, `MET-03`, `MET-04`, `EKS-01`, `EKS-02`, `VER-01`) `category=unclassified`, `status=unresolved`, `verification=null`, `resolution=null`, `reason=null`, `probe="unclassified — review manually"` olarak kalır. Otomatik test bu uç varsayımlarını çözmez.

Dört descriptor-less prohibition `unresolved` ve `flagged-unverified` kalır: kapsam seçiminin siyasi sıralamaya dönüşmesi; uygun eşleşmenin sonuç yönüne göre gizlenmesi; kaynak dışı olgu veya beyanın gerçekleşmiş olguya dönüştürülmesi; eksik bilginin sıfır veya siyasi sonuca dönüştürülmesi. İnsanın kaynak ve tarafsızlık incelemesi gerekir. Ortak gereksinimler son faz doğrulayıcısına bırakıldı.

## Sapmalar

**[Rule 1] Kapalı sürüm uyumluluğu:** HTML üreticisi değişince geçmiş sürümün yeniden üretim audit'i bozuluyordu. Üretici sürümü manifestte tutuldu ve önceki üreticiler korundu (`4c8d4a5`, `5283fa9`). Ara sürümler de değişmez biçimde saklandı.

**[Rule 2] Sunucu sınırı ve kaynak URL'leri:** Sunucu loopback ve izin verilen yayın/nesne yollarıyla sınırlandı; render sırasında tehlikeli URL ve kök dışı arşiv yolu reddedildi (`5283fa9`).

**[Rule 2] Pasaj konumları:** Önceden konum alanı boş olan HTML pasajlarına özgün kopyadan çevre metni eklendi; özgün pasaj ve geçmiş sürümler korunur (`5283fa9`).

**Test çalışması:** Bir tam test çalışması, rapor üreticisi aynı anda güncellenirken tracer alt sürecinin farklı sürümü yüklemesi nedeniyle başarısız oldu; yazılar tamamlandıktan sonraki tam çalışma 37/37 geçti.

## Commitler

- `41dc1c5`: sekme sözleşmesi RED testi.
- `4c8d4a5`: sekmeli kaynak raporu ve ilk üretici uyumluluğu.
- `d35cf05`: faz kabulü RED testi.
- `5283fa9`: faz audit'i, ajan inceleme kayıtları, negatif kontroller ve yerel teslim.

## Self-Check: PASSED

Yukarıdaki commitler ve oluşturulan dosyalar mevcut; son snapshot faz auditinden geçti. İnsan incelemesi ve 13 uç varsayımı açık kalır.
