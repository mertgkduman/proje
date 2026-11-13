---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "01"
subsystem: comparison-publication
tags: [sqlite, html, kaynak, karşılaştırma, tracer]
requires:
  - phase: "02"
    provides: Dokuz parti dosyası ve doğrulanmış teslim zinciri
provides:
  - Kaynaklara bağlı schema6 karşılaştırma kayıtları ve renderer16
  - İYİ Parti ve TİP merkez yönetimi seçimi için yerel dar karşılaştırma
affects: [03-02, 03-16]
tech-stack:
  added: []
  patterns: [eklemeli migration, değişmez yerel yayın, sürümlü renderer]
key-files:
  created: [src/rapor_v15.py, src/rapor_v16.css, tests/test_comparisons.py, data/comparisons/03-tracer.json]
  modified: [src/arsiv.py, src/dosyalar.py, src/rapor.py, data/current.json]
key-decisions:
  - İYİ ve TİP seçimi mevcut kaynak arşivlerine dayanan dar mühendislik dilimidir; siyasi öncelik değildir.
  - Yedi diğer parti bu konuda henüz incelenmedi olarak kalır; tam Faz 3 kabulü yapılmaz.
requirements-completed: []
actuals:
  tokens: 591621
  tasks: 2
  commits: 3
  plan_head_before: 512c9416e732852bc29722dce690c549a9b7c73e
duration: yaklaşık 59min
completed: 2026-11-13
status: complete
---

# Faz 3 Plan 01: Kaynaklı karşılaştırma tracer özeti

**İYİ Parti ve TİP merkez yönetimi seçimi kaynaklardan schema6 kayıtlarına ve iki bağlantılı HTML görünümüne taşındı; İYİ madde 48 için iki gerçek önce/sonra değişikliği gösterildi.**

## Teslim ve kapsam

- Yerel rapor: `data/releases/9119e174a8d94f2d9c77efa155347242/index.html`; release `9119e174a8d94f2d9c77efa155347242`, taban `ac4b8fdec02f4a9ebb666036ed251683`. Kamuya dağıtım yapılmadı.
- İYİ tüzük sürümleri `0205-iyi-charter-istanbul-v1` ve `0205-iyi-charter-download-v1`: madde 48'de 50 asıl/25 yedek → 60/30 ve gündem teklifi onda bir → beşte bir. Tespit edilen sürümler hukuki yürürlük iddiası değildir.
- Dokuz parti sabit sırada; diğer yedi partinin bu konudaki satırı henüz incelenmedi. Kaynaklı karşılaştırma ve dosya görünümü aynı kayıtlara bağlanır. Otomatik bütünlük denetimi maddi anlam incelemesi değildir.
- Renderer15 donduruldu, önceki CSS değiştirilmedi; schema6 sözleşmesi ve renderer16 yeni sürümde kullanıldı. Eski yayınlar ve Faz 2 teslim sırası korundu.

## Doğrulama

- `python3 tests/run.py --pattern test_comparisons.py`: 7/7 geçti, 417.528 saniye. Gerçek kaynak, iki görünüm, yanlış sahiplik ve eksik kanıtın reddi, migration geri alma, tarihsel renderer, metin kaçışlama, yayınlanmış kanıt ve stil korunumu sınandı.
- `comparison-check --input data/comparisons/03-tracer.json`: `COMPARISON_INPUT_OK`.
- Yeni sürümde `audit --release current --phase 3 --stage tracer`: `PHASE3_AUDIT_OK`; `audit --release current --phase 2`: `PHASE2_AUDIT_OK`.
- Önceki çalışma oturumunda `test_topics.py` 3/3, `test_documents.py` 11/11, `test_publication.py` 11/11 ve enjeksiyonlu karşılaştırma testleri 5/5 geçti. Başlangıçta Faz 2 audit ve dokuz dosya doğrulaması başarılıydı.
- Eski sürümlere ait 212 dosya özeti ve tarihsel CSS SHA-256 `721a9fe91d18231d01941d8788bac0264862870957c1a85cc13090ec5603fef4` değişmedi.

## Görev commitleri

1. `3a91261` — başarısız kabul testi (RED).
2. `983612b` — kaynaklı karşılaştırma ve tarihsel renderer (GREEN).
3. `fd874f5` — yeni stil ve yerel kapalı sürüm.

## Sapmalar ve sorunlar

Yeniden başlatma sonrası önceki test çalışmaları kesintili olduğundan son kabul ve paket kontrolü yeniden çalıştırıldı. Yazıcı kilidinin aynı makinedeki sahibi bağımsız olarak ölü bulundu ve README'deki yönteme göre kilit kaldırıldı. Plan kapsamını değiştiren sapma yoktur.

## Sonraki çalışma

Bu plan sonraki karşılaştırma dilimleri için altyapıyı sağlar; Faz 3 gereksinimleri ve insan değerlendirmesi bütün faz tamamlanmadan bitmiş sayılmaz. `actuals.tokens`, ikili SQLite dosyası dışındaki gerçekleşmiş metin diff karakterlerinin dörde bölünmesiyle ölçülmüştür.

## Self-Check: PASSED

Plan dosyaları, yerel rapor ve üç görev commiti doğrulandı.
