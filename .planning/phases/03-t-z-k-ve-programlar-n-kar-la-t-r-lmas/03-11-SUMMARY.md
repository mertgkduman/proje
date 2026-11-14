---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "11"
subsystem: kaynakli-karsilastirma
tags: [saadet, program, kaynak-atfi, kapsam]
requires:
  - phase: 03-10
    provides: Denetlenmiş tüzük karşılaştırmaları ve önceki yerel sürüm
provides:
  - Saadet programının ortak konu sözlüğündeki kaynaklı karşılaştırması
  - Kaynak satırı sahipliği, kapsam incelemesi ve program semantik kararları
affects: [03-14, 03-15, 03-16]
actuals:
  tokens: 21540281
  tasks: 2
  commits: 2
plan_head_before: f4b75c4e3ac687dc019a060a7313cf7d24595c07
tech-stack:
  added: []
  patterns: [sinirli-kapsam-incelemesi, kaynak-katmani-ayrimi, degismez-yerel-yayin]
key-files:
  created:
    - data/comparisons/03-saadet-program-1.json
    - data/comparisons/03-saadet-program-2.json
    - data/comparisons/03-saadet-program-semantic.json
    - .planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-11-topic-review.json
  modified:
    - data/current.json
key-decisions:
  - "Dar soruya eşlik eden bağlam olumlu politika yanıtı sayılmaz."
  - "Temel Vatandaşlık Geliri önerisinin doğum, çalışma ve vergi ödeme koşulları korunur."
requirements-completed: []
requirements-addressed: [PRG-01, KAR-02, RAP-02]
duration: unknown
completed: 2026-11-14
status: complete
---

# Phase 03 Plan 11: Saadet Programı Karşılaştırması Özeti

**Saadet programının 135 ortak konusu kaynaklı politika alanları ve dar kapsamlı yokluk kayıtlarıyla incelendi; koşullu gelir önerisi ve kaynak sınırları korundu.**

## Teslim ve kaynak sınırı

- `0209-saadet-current-program-v1` özgün PDF'sinin 70 sayfası okundu; SHA-256 `6718b7ca1b2997d0d1f0e52999c8c5ce852af648be7e83cb26c5a7eef060805c`. Kapaktaki 3 Kasım 2019 tarihi bütün metnin yürürlük veya kabul tarihi olarak sunulmaz. Önceki aynı içerikli farklı adresin tüm sürüm geçmişi olduğu varsayılmaz.
- 80 kaynak envanteri bölümü ve 2.411 benzersiz sayfa/satır kimliği iki görevin gerçek bölüm sahipliğiyle kaydedildi. On çapraz bölüm inceleme kuyruğu ele alındı. 135 konunun 95'i kaynaklı bulgu, 40'ı kendi dar kapsamına bağlı açık ifade bulunmaması kaydıdır. 279 alan (56 ilke, 24 hedef, 199 araç), 334 pasaj ve 319 gerekçeli semantik karar vardır. Kararlar ajan incelemesidir; bağımsız insan kabulü değildir.
- İlke, hedef ve araçlar kaynakları ve belirtilen koşullarıyla ayrıldı. Sayfa 41'deki Temel Vatandaşlık Geliri, ülkede doğmuş, ülke için çalışmış ve vergi ödemiş vatandaşlar için öneridir; sayfa 38'deki genel sosyal devlet ilkesi ödeme kapsamını değiştirmez. Gelirsizlik şartı veya koşulsuz evrensel kapsam eklenmedi.
- Dar erişim sorularıyla ilgili olmayan müfredat, öğretmen, sağlık personeli ve benzeri gerçek politika ifadeleri olumlu erişim yanıtına dönüştürülmedi. Ortak sözlükte karşılığı bulunmayan gerçek kaynaklı araçlar, kapsam farklarıyla birlikte 03-14 geri taraması için on somut aday olarak iki program paketinin `backfill_candidates` alanlarında korunur.
- Birinci yerel sürüm `3506b12dee39440ca233a251979215be`, son yerel sürüm `945f32db93854c19bd1dd1729ffcd691` olup raporlar bu sürümlerin `index.html` dosyalarındadır. Önceki `4926099ac08b40df96fd4c304064023b` sürümü, kaynak PDF ve Saadet tüzük verileri korundu. Kamuya yayın yapılmadı.

## Doğrulama

- Her iki sabit paket için `COMPARISON_INPUT_OK`, `COMPARISON_LOAD_OK` ve ilgili yerel sürümde `PHASE3_AUDIT_OK` alındı. Son sürümde `PHASE2_AUDIT_OK` alındı. Son raporda birinci paketin 69, ikinci paketin 66 satırının iki görünümdeki bulgu ve kaynak hedefleri doğrulandı. Kapsam ve gelir koşulu SQLite üzerinden ayrıca denetlendi.
- `DRAFT_PREFLIGHT_OK` konu, alan, kapsam, kaynak satırı ve pasaj kontrollerini tamamladı. Son kullanılan üç girdi baytının SHA'ları ile ilk sürüm, önceki sürüm, özgün PDF ve ilk semantik anlık görüntüsü doğrulandı. Günlükler, çıkış kodları ve işlem sahipliği `03-11-checks/` içindedir.
- `actuals.tokens`, başlangıç ile iki görev commit'i arasındaki 86.161.125 karakterlik Git farkının dörde bölünmüş ölçüsüdür; model tüketimi değildir. Otomatik kontroller kaynak anlamına ilişkin ajan değerlendirmesinin yerini almaz.

## Task Commits

1. Programın birinci konu paketi: `dfcbfe7fed03cbd6b18b9832646ca0de3ef3eaa8`.
2. Ekonomik ve sosyal politika paketi: `764fa0c8782f138beb74add9d009ceeb75f4c908`.

## Deviations from Plan

Program için ayrı semantik dosya kullanıldı; mevcut tüzük kararları korunarak dar soru kapsamları ve konu eşlemeleri yayın öncesinde kaynaklarına göre düzeltildi. Mevcut sözleşme `no_explicit_statement` satırında alan kabul etmediği için bağlam olumlu bulgu olarak yeniden sınıflandırılmadı.

## 03-14, 03-15 ve 03-16 aktarımı

- 03-14, iki program paketinin `backfill_candidates` alanlarındaki on kaynaklı adayın ortak sözlük kapsamını ve ilgili konu eşlemelerini değerlendirmelidir.
- 03-15/03-16: Mevcut renderer 18, tek kanonik `no_explicit_statement` satırının kapsamını ve eşlik eden bağlam pasajını iki ana görünümde göstermiyor; veritabanındaki kapsam ve konu inceleme kaydı bu gösterim sınırını ortadan kaldırmaz. Ayrı ilke/hedef/araç alanlarından bazıları için ayrıca açık ifade bulunmaması da mevcut görünümde ayrı gösterilmez. Bu sınırlar sonraki sunum ve kapsam çalışmasına taşınır; bağlam bir olumlu politika yanıtı değildir.
- Kısmi Faz 3 denetimi, fazın veya bütün gereksinimlerin tamamlandığı anlamına gelmez.

## Self-Check: PASSED

İki paket, ayrı semantik dosya, iki yerel rapor, konu incelemesi, denetim sonuçları ve iki görev commit'i doğrulandı.
