---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
plan: "02"
subsystem: sürümlü kaynak görünümü
tags: [sqlite, html, kaynak, tdd, tip, tracer]
requires:
  - phase: "02-01"
    provides: TİP kuruluş tracer ve sürümlü dosya sözleşmesi
provides:
  - Kimlik kartı, kuruluş kronolojisi ve başlıklara ayrılmış sürümlü kaynak görünümü
  - Renderer 9 ile tarihsel denetim ve renderer 10 ile yeni tracer
  - Önceki makbuza bağlı yerel ara teslim
affects: [02-03, 02-04, 02-05, 02-06, 02-07, 02-08, 02-09, 02-10]
tech-stack:
  added: []
  patterns: [tekil pasaj hedefi, snapshot tabanlı renderer, tarihsel renderer seçimi]
key-files:
  created: [src/rapor_v9.py, data/deliveries/02-02-tip-sources.json]
  modified: [src/arsiv.py, src/dosyalar.py, src/rapor.py, tests/test_dossiers.py, README.md, data/current.json]
key-decisions:
  - TİP tracer tamamlanmış parti prefix'ini büyütmez; gerçek çoklu sürüm veya kimlik olgusu icat edilmez.
  - Kaynak türü ve sürüm yetkisi ayrı tutulur; tek sürüm ve bilinmeyen dönem açıkça belirtilir.
requirements-completed: []
actuals:
  tokens: null
  tasks: 3
  commits: 4
plan_head_before: 10a43600020da93cdcdc6f7b2e589f8f4745e3ba
duration: 7min
completed: 2026-11-11
status: complete
---

# Phase 2 Plan 2: Sürümlü kaynak görünümü özeti

**TİP kuruluş tracer'ına beş alanlı kimlik kartı, kaynaklı kronoloji ve belge sürümü geçmişi eklenerek denetlenmiş yerel rapor ve zincirli makbuz üretildi.**

## Sonuçlar

- `b14c96c54e4b420686c46e5cfb1071a3` sürümü renderer 10, `tip/tracer` ve boş `completed_prefix` taşır. Rapor `data/releases/b14c96c54e4b420686c46e5cfb1071a3/index.html`; makbuz `data/deliveries/02-02-tip-sources.json` yolundadır.
- Beş kaynak grubu, pasaj başına tek hedef, kaynak türü ve kısa künye, kaynak sürümleri ve gerekçeli dönem belirsizliği gösterilir. Bilgi kartı ve kronoloji kanıta bağlıdır; iki kimlik notu kendi pasajlarına bağlanır.
- Renderer 9 özgün haliyle `src/rapor_v9.py` içinde korunur; eski `ed725968b4714ec7b4c24eb12d692530` sürümü kendi renderer'ıyla denetlendi.
- Makbuz, önceki 02-01 makbuzuna bağlıdır; README çalışma alanı, yükleme, yayın, audit, makbuz ve kurtarma komutlarını açıklar.

## Doğrulama

- TDD RED: `test_tip_report_exposes_identity_and_grouped_sources` hedef davranışta başarısız oldu; kanıt `RED_EVIDENCE_OK` ile doğrulandı (`4710683`). GREEN uygulaması `99d1f66`.
- `test_dossiers.py`: 8 test; izole gerçek publish/audit, Chromium kaynak ve geçmiş gezintisi, tekil hedef, iki sentetik sürüm, kendine/başka belgeye/başka partiye ve döngüsel ilişkiye karşı kontroller geçti.
- `test_report.py`: 2 test; `test_documents.py`: 4 test; `test_publication.py`: 11 test geçti. Gerçek Chromium hem yerel dosya hem loopback üzerinden kaynak açma ve geri dönüşü çalıştırdı.
- Tam test grubu `python3 tests/run.py`: 52/52 geçti.
- Güncel ve önceki tracer için `PHASE2_TRACER_OK`; yeni zincirli makbuz için `DELIVERY_RECEIPT_OK` alındı.

## Kaynak sınırları ve insan incelemesi

Resmî ad, kısaltma, sicil kimliği ve resmî site henüz incelenmedi; kuruluş araştırması tamamlanmadı. Tüzük, program, söylem–uygulama ve finansman başlıkları tamamlanmadı. TİP tüzüğünün kesim tarihindeki yürürlük sürümü doğrulanmadı. Çoklu sürüm örneği test verisidir; gerçek parti olgusu değildir. Otomatik bütünlük denetimi kaynakların anlamına ilişkin insan incelemesi değildir; faz sonu görsel ve kaynak incelemesi bekler.

## Sapmalar

Yok. Yayın denetimindeki renderer sürüm kapısı tarihsel 9'u koruyarak 10'u kabul edecek şekilde genişletildi; bu, planlanan geriye dönük denetimin parçasıdır.

## Commits

- `4710683` — RED davranış testi.
- `99d1f66` — kaynak, kart ve kronoloji görünümü.
- `a5c6ce1` — yeni yerel tracer sürümü.
- `94efca8` — zincirli makbuz, işletim bilgisi ve ilişki negatifleri.

## Self-Check: PASSED

Renderer, test, rapor, makbuz ve dört commit doğrulandı.
