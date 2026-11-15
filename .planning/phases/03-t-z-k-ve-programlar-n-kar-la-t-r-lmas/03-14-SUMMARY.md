---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: '14'
subsystem: comparisons
tags: [taxonomy, provenance, synthesis, sqlite, compatibility]
requires:
  - phase: 03-13
    provides: Dokuz partilik belge envanteri, önceki karşılaştırma ve tarihsel kaynaklar
provides:
  - Dokuz taraflı kaynak ve kapsam incelemesine dayalı seçili v4 konu sözlüğü ve atomik soy eşlemesi
  - 305 konu için iddia ve taraf bazlı kaynaklı sentez ve yerel rapor
affects: [03-15, 03-16]
tech-stack:
  added: []
  patterns: [versioned selected view, typed source proof, atomic reconciliation]
key-files:
  created: [data/comparisons/03-synthesis-v4.json, data/comparisons/03-synthesis-v4-evidence.json, .planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-14-checks/phase16-source-probe-handoff.md]
  modified: [src/arsiv.py, tests/test_comparison_content.py, .planning/STATE.md, .planning/ROADMAP.md]
key-decisions:
  - Eski snapshot ve özgün kaynaklar korunurken seçili görünüm manifestte açık sözleşmeyle sürümlenir.
  - Olumlu taraf gerçek pasajla; dar yokluk gerçek kapsamla; belge açığı missing ve attempt ile gösterilir.
  - Değişmeyen anlamın mekanik soyu yeni yapılmış anlam onayı gibi gösterilmez.
requirements-completed: []
plan_head_before: e61db9c9720be25b1af6e5da994d39430687ee60
actuals:
  tokens: 8334239
  tasks: 2
  commits: 126
duration: 529min
completed: 2026-11-15
status: complete
---

# Phase 3 Plan 14: Ortak kapsam ve kaynaklı sentez özeti

Dokuz tarafın gerçek kapsamına dayalı 305 konu ve 854 tipli iddia, eski sürümleri koruyan atomik eşleme ve kaynaklı yerel raporla tamamlandı.

## Sonuçlar

- Kabul edilmiş yerel release `b513965558094e338a941be90a1960a4`: schema 6, renderer 18, taxonomy 4, comparison/sentez contract 2, seçili görünüm 1 ve complete. Seçili 305 konu, 4.935 satır ve 854 sentez; 514 çok-olumlu, 29 tek-olumlu ve 311 durum iddiası vardır.
- 30 ana ve 4 ek aday gerçek kaynak/alanlarla karara bağlandı; gelir, tıbbi üretim ve üç eğitim sorusunun dokuz taraf kapsamı özgül incelemelerle kapatıldı. İslam konusu v4'te netleştirildi ve dokuz taraf ayrıca incelendi. Olumlu, dar kapsam, tarihsel/ek belge ve somut belge açığı birbirine dönüştürülmedi.
- v3'ün 4.935 seçili satırı 4.917 mekanik taşıma ve 18 gerekçeli yerine-geçme/ayrılma olarak eksiksiz açıklandı; 17 doğrudan yeni satır ve ayrı Demokrat kongre hesap komisyonu seçilerek v4 toplamı 4.935 oldu. v2'nin 4.875 ve v3'ün 4.935 satırı korundu. 62 eski tablonun taban→workspace EXCEPT karşılaştırmasında kayıp satır yoktur.
- Sentez cümleleri her gerçek tarafın pasajı veya ilgili scope/missing-attempt bağıyla açıkça incelendi; helper anlam veya parti tutumu üretmedi. Demokrat hesap komisyonu, EMEP dinî devlet kurumları ve gerçek oy/tur/kademe koşulları dahil kaynak düzeltmeleri ve etkilenen cümleler özgül soyla kaydedildi.
- 03-15 görünüm devri `03-14-checks/row-partition-and-phase15-handoff.md`; 03-16 kaynak/locator devri `03-14-checks/phase16-source-probe-handoff.md`. Bu plan renderer/CSS değiştirmedi; R18, önceki manifest ve kapalı snapshot uyumluluğu korundu.

## Doğrulama

- TDD: `26d141d`, `17444b6`, `df3beb8` anlamlı RED testleri, atomik uygulama `5224373` öncesinde işlendi. Tarihsel typed sözleşme düzeltmesi için RED `c16f15b`, GREEN `5102fe6`. Eski contract 1 iki gerçek taraf kuralı, hatalı konu/parti/proof, aktif bulgu denetimi ve eski snapshot testleri korundu.
- `python3 tests/run.py --pattern test_comparison_content.py`: 27/27, exit 0; gerçek kod/test hash ve önceki fixture başarısızlığının dürüst kaydı `03-14-checks/comparison-content-final-test.md` içinde. R17/R18 byte-exact eski snapshot testleri dahil.
- Gerçek son v4 reconcile: exit 0; 305 konu, 4.935 satır, integrity OK ve foreign-key 0. Kaynak paketi ve 854 sentez ayrı yüklemelerle exit 0. Tüm finding review eksiği ve v4 sentez semantic review eksiği 0.
- Yerel publish exit 0; `comparison-check` backfill ve sentez için ayrı `COMPARISON_INPUT_OK`, exit 0; bağımsız `PHASE3_AUDIT_OK` ve `PHASE2_AUDIT_OK`, her ikisi aynı `b513965558094e338a941be90a1960a4` release'i ve exit 0. Kalıcı süreç kayıtları sırasıyla `/tmp/gsd-0314-final-publish.*`, `/tmp/gsd-0314-final-check-{backfill,synthesis}.*`, `/tmp/gsd-0314-final-audit-{3,2}.*`.

## Sapmalar ve sınırlar

- [Rule 1] Tarihsel typed-v2 sentezlerin yeni seçili taxonomy altında doğrulama hatası TDD ile düzeltildi; eski contract 1 gevşetilmedi.
- [Rule 1] İki son staging denemesi, yeni Demokrat alanında kayıt sırası ve alıntı/pasaj eşitliği nedeniyle başarısız oldu; gerçek özgün pasaj ve ortak özet bağıyla düzeltildi (`d1e30a3`, `17f8d90`, `ad33ba4`), üçüncü koşu exit 0. Önceki kabul edilmiş yayınlar yeniden yayımlanmadı.
- İlk workspace denemesi erken kesildi; yalnız kendi ölü süreçlerine ait stale lock başlangıçta yokluk, host/PID ve sabit current kanıtıyla temizlendi. İlk denemede token baytı korunmadığı sapması ve sonraki gerçek token/owner kanıtı `03-14-checks/workspace-launch-deviation.md` dosyasındadır. Başarılı f76 koşusunda değişmeyen salt okunur girdi önceden oluşturuldu, SHA kaydı koşu sonrasında eklendi; başarılı işlem tekrarlanmadı.
- İlk publish finding-review ilişkilerini eksik bulup reddetti; 108 gerçek önceki inceleme, pasaj ve soyları korunarak ilişkilendirildi, kayıp onay veya gerekçe uydurulmadı. Sonraki yayın tam kurallarla kabul edildi.
- Otomatik gerekçeli 72 taslak cümle kaynakçı onayı sayılmadı; gerçek özgül inceleme hattından dışlandı. Eski EMEP iki yanlış locator ve eski yanlış konu/kapsam kayıtları yalnız arşivde korunur.
- Faz 3'ün küresel sekiz gereksinimi ve 03-15/03-16 açık kalır; bu planın tamamlanması fazın veya kullanıcı arayüzü kabulünün tamamlandığı anlamına gelmez.

## Self-Check: PASSED

Kabul edilmiş release ve manifest mevcut; planın son verisi, kaynak/sentez paketleri, kanıt ve devir dosyaları mevcut. RED/GREEN ve son veri commit'leri Git geçmişindedir. 27 test, iki comparison-check, publish, P3 ve P2 için gerçek exit 0 kanıtları doğrulandı.
