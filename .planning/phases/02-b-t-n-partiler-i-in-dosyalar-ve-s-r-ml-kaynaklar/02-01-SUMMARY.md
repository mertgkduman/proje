---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
plan: "01"
subsystem: kaynaklı dosya ve yerel yayın
tags: [sqlite, arşiv, kaynak, tdd, tip, tracer]
requires:
  - phase: "01"
    provides: Kaynak arşivi, Yeni Parti pilotu, yöntem kesimi ve renderer 8
provides:
  - TİP sicilinden kart ve kronolojiye uzanan kaynaklı tracer
  - Eklemeli dosya şeması, parti/sıra denetimi ve değişmez yayın
  - Denetlenmiş yerel rapor ve ayrı tracer makbuzu
affects: [02-02, 02-03, 02-04, 02-05, 02-06, 02-07, 02-08, 02-09, 02-10]
tech-stack:
  added: []
  patterns: [SQLite yedekli transaction, kaynaklı bulgu çifti, sıralı immutable teslim]
key-files:
  created: [src/dosyalar.py, src/rapor_v8.py, tests/test_dossiers.py, data/deliveries/02-01-tip-tracer.json]
  modified: [src/arsiv.py, src/rapor.py, tests/test_dates.py, tests/test_publication.py, tests/test_scope.py, data/current.json]
key-decisions:
  - Tracer tamamlanmış parti prefix'ini büyütmez; tam TİP teslimine kadar DEM'e geçilmez.
  - Eski renderer 8 dosyası özgün baytlarıyla korunur ve kendi sürümüne göre audit edilir.
  - Kaynak incelemesi agent kaydıdır; insan incelemesi veya tam parti kabulü değildir.
patterns-established:
  - Kaynak sahipliği ve kuruluş günü kayıt ve export sırasında aynı sözleşmeyle denetlenir.
requirements-completed: []
coverage:
  - id: tracer-integrity
    description: Gerçek TİP sicil pasajından izole veri kökünde rapora, yayına ve audit'e ulaşma
    verification:
      - kind: e2e
        ref: python3 tests/run.py --pattern test_dossiers.py
        status: pass
    human_judgment: false
  - id: source-meaning
    description: Sicil metninin maddi anlamı ve araştırma kapsamının insan değerlendirmesi
    verification: []
    human_judgment: true
    rationale: Kaynakların anlamı ve tüm dosyanın yeterliliği hash veya otomatik testten çıkarılamaz.
actuals:
  tokens: null
  tasks: 3
  commits: 7
plan_head_before: c36aef448a8f0678d3c9bb7a06031d4581aff366
duration: 21min
completed: 2026-11-11
status: complete
---

# Phase 2 Plan 1: TİP kaynaklı tracer özeti

**Arşivli Yargıtay sicilindeki TİP kuruluş tarihi kaynaklı kart ve kronolojiye bağlandı; denetlenmiş değişmez rapor ve ayrı ara teslim makbuzu üretildi.**

## Sonuçlar

- `ed725968b4714ec7b4c24eb12d692530` yerel sürümü `tip/tracer`, boş `completed_prefix` ve renderer 9 taşır. Rapor ve makbuz `data/releases/.../index.html` ve `data/deliveries/02-01-tip-tracer.json` içindedir.
- Workspace kopyası migration öncesinde yedeklenir; transaction, FK ve SQLite bütünlük kontrolleri uygulanır. Şema 4 eski kontrolleri korur; tarihsel renderer 8 özgün dosya olarak saklanır.
- Kayıt, export, yayın, faz denetimi, girdi kontrolü ve makbuz yollarında partiye ait kanıt, tarih, kaynak, sıra ve kimlik kuralları kullanılır. Test yayını ayrı `DATA` kopyasında yapılır.

## Kaynağın maddi incelemesi

Arşivdeki `tip-registry-v1` Yargıtay sayfasının “Kuruluş Tarihi” satırında `07.11.2017` vardır; kimlik gözlemindeki `2017-11-07` ile uyuşur. [Yargıtay TİP sicil sayfası](https://www.yargitaycb.gov.tr/sipar/208) ayrıca kontrol edildi. Yayındaki kısa özet, tarih alıntısı ve kronoloji aynı arşivli pasajı gösterir. Bu kaynak incelemesi agent tarafından yapılmıştır; insan kabulü değildir. Kaynak yakalama zamanı, olay tarihi ve yöntem kesimi birbirinin yerine kullanılmamıştır.

## Otomatik bütünlük ve doğrulama

- `python3 tests/run.py --pattern test_dossiers.py`: 6 test geçti; gerçek arşiv kaynağıyla izole publish/audit/HTML, kimlik ve sahiplik, döngü, migration ve pointer kontrolleri içerir.
- `python3 tests/run.py --pattern test_dates.py`: 1 test; `python3 tests/run.py --pattern test_publication.py`: 11 test geçti.
- Tam test grubu son sahiplik denetimi eklenmeden hemen önce 49/49 geçti; bu son ekleme sonrasında ilgili 6 dosya testi ve istenen üç test komutu tekrar geçti.
- `audit --release current --phase 2 --party tip --stage tracer`: `PHASE2_TRACER_OK`; `audit --release current --phase 1`: `PHASE1_AUDIT_OK`; `receipt-check`: `DELIVERY_RECEIPT_OK`.
- Eski `26de2a4efc584b5b9f81ea67dcb8d65c` sürümü kendi renderer 8 çıktısıyla audit edildi ve izole testte dosya hash'leri değişmedi.

## TDD ve görev commitleri

- `44b47f0`: gerçek sicille partiye özgü kuruluş sözleşmesinin yokluğunu gösteren RED. Unittest çıktısı kayıpsız test adı ve sonuçlarıyla TAP'a çevrilip `check tdd-red-evidence` tarafından `RED_EVIDENCE_OK` olarak doğrulandı.
- `721f2af`, `0f2ae5e`: kuruluş ve dosya/publish sözleşmesi GREEN; tracer uçtan uca tekrar doğrulandı.
- `228d51c`: gerçek tracer sürümü; `e5f05a8`: makbuz.
- `affa1c7`, `c9d7d2b`: ilerleyen işaretçiyle sabit Faz 1 test tabanı, eksik kuruluş işleme ve resmî site/sicil sahipliği düzeltmeleri.

## Plandan sapmalar

1. **[Rule 1 — Bug]** Güncel işaretçi Faz 2'ye ilerleyince Faz 1 testlerinin yalın yayın denemeleri Faz 2 sıra kapısına takılıyordu. `tests/test_dates.py`, `tests/test_publication.py`, `tests/test_scope.py` yalıtılmış kopyada eski Faz 1 release'ini sabit taban olarak kullanır (`affa1c7`).
2. **[Rule 1 — Bug]** Makbuzda kısmi kuruluş araştırması “henüz incelenmedi” görünüyordu; “araştırma tamamlanmadı” ve Türkçe alan adlarıyla düzeltildi (`e5f05a8`).
3. **[Rule 2 — Kritik]** Resmî site ve sicil kartlarının partiye ait doğrulanmış yetki/sicile bağlanması açıkça denetlendi (`c9d7d2b`).

## Kalan kaynak sınırları

Resmî ad, kısaltma, sicil kimliği ve resmî site kart alanları henüz incelenmedi. Kuruluş dosyası tamamlanmadı; tüzük, program, söylem–uygulama ve finansman dosyası tamamlanmadı. Arşivli TİP tüzüğünün kesim tarihinde yürürlükteki sürüm olduğu doğrulanmadı. Bu sınırlamalar araştırma kapsamıdır; sıfır değer veya tamamlanmış TİP kabulü değildir. Önce 02-02 ve 02-03 yürütülmelidir.

## Self-Check: PASSED

Temel kaynak, renderer, test, release ve makbuz dosyaları ile yukarıdaki yedi commit doğrulandı.
