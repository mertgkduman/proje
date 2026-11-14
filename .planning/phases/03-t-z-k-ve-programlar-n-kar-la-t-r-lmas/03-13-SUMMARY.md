---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "13"
subsystem: kaynakli-karsilastirma
tags: [demokrat, program, dyp, tarihce, kaynak-atfi]
requires:
  - phase: 03-12
    provides: Denetlenmiş Demokrat tüzüğü ve önceki yerel sürüm
provides:
  - Demokrat programının kaynaklı kurumsal, hak, ekonomik ve sosyal karşılaştırmaları
  - Aynı tüzel zincirde erişilen DYP programlarından tarihsel pasaj çiftleri
affects: [03-14, 03-15, 03-16]
actuals:
  tokens: 25794780
  tasks: 2
  commits: 2
plan_head_before: c2f977a0ec91605005d519d996ec003bd1c495bc
tech-stack:
  added: []
  patterns: [sayfa-ve-paragraf-envanteri, sinirli-kapsam-incelemesi, degismez-yerel-yayin]
key-files:
  created:
    - data/comparisons/03-demokrat-program-1.json
    - data/comparisons/03-demokrat-program-2.json
    - data/comparisons/03-demokrat-program-semantic.json
  modified:
    - data/current.json
key-decisions:
  - "Arşiv yakalama tarihi programın kabul tarihi veya güncel yürürlük kanıtı değildir."
  - "Kota olmadan katılımın artması öngörüsü kota yasağı sayılmaz; geçici önlem ve parite önerisinin kapsamı ayrı korunur."
  - "Asgari nakit gelir ifadesine kaynakta açıklanmayan eşit ödeme veya gelir eşiği koşulu eklenmez."
  - "Tarihsel farklar aynı tüzel zincirdeki iki gerçek pasajla ve bilinmeyen ara sıra varsayılmadan sunulur."
requirements-completed: []
requirements-addressed: [PRG-01, KAR-02, RAP-02]
duration: unknown
completed: 2026-11-14
status: complete
---

# Phase 03 Plan 13: Demokrat Programı Karşılaştırması Özeti

**Demokrat programının 83 sayfası ile erişilen aynı tüzel zincirdeki DYP program pasajları iki kaynaklı karşılaştırma paketine işlendi.**

## Teslim ve kaynak sınırı

- `0210-demokrat-program-archive-v1` özgün PDF SHA-256 `6554ec05b00d37f62159e1d722f4464ff8b32569ddf7455108530cc772747da2`; 29.12.2021 arşiv yakalaması kabul tarihi veya bugün yürürlükteki son metin kanıtı değildir.
- 83 PDF sayfasının tüm bölüm ve başlıksız paragrafları iki göreve atandı. Envanter 78 başlık ve 2.740 metin satırı içerir. Metin katmanı boş 1, 8, 24, 30 ve 83. sayfalar ayrıca görüntüden incelendi: 1 ve 83 kapak, 24 ve 30 boş, 8 ise maddi önsöz devamıdır. Sekizinci sayfadaki Senato ve seçim barajı pasajları dahil dokuz görsel ek kanıt ikinci pakette korunur.
- 135 ortak konu gerçek kaynak kapsamına göre ele alındı: 102'sinde kaynaklı içerik, 33'ünde dar kapsamlı açık ifade yokluğu kaydı vardır. Yokluk satırlarına alan veya ilgisiz olumlu yanıt eklenmedi; ilgili bağlam pasajları semantik dosyada ayrıca gösterildi. 41 çapraz-konu incelemesi ve koşul ayrımları kayıt altındadır. 241 ajan semantik kararı bağımsız insan onayı değildir.
- Kadın ve gençlerin özel kota önlemi olmadan katılımının artacağı öngörüsü ile kadınların siyasi katılımı ve temsilinde geçici kota önlemi ve parite yasası önerisi ayrı bağlam ve araçlarıyla korunur; kaynakta süresi belirtilmez ve kota yasağı veya kesin çelişki çıkarılmaz.
- Asgari nakit gelir pasajı gelir eşiği, eşit ödeme, koşulsuzluk veya uygulama mekanizmasını açıklamaz. Tarım ve düşük gelirli işçilerle ilgili sosyal sigorta hükmü ayrı kapsamda tutuldu. Kömür kullanımı, yenilenebilir enerji ve nükleer destek ayrı korunur; 2020 emisyon hedefi öngörülen baz senaryoya göredir.
- Erişilebilir taranmış DYP programları aynı hukuki zincir sınırında görsel olarak incelendi. Yargı kurulları, yerel gelirler ve sağlık sigortası için gerçek tarihsel ve Demokrat pasajları eşleştirildi; ara sürüm sırası veya metinlerin kabul tarihleri varsayılmadı.
- İlk yerel sürüm `ba6f647546f64cb98516b04ff6736c33`, son sürüm `ae42ae1897864fda810b033ce3ac1e8f` ve ilgili raporlar `data/releases/<sürüm>/index.html` içindedir. Önceki sürüm ve ilk yeni sürümün baytları korundu; kamuya yayın yapılmadı.

## Doğrulama

- Her iki paket için `COMPARISON_INPUT_OK`, `COMPARISON_LOAD_OK` ve `PHASE3_AUDIT_OK`; son sürüm için `PHASE2_AUDIT_OK` alındı. Rapor bağlantı kontrolleri ilk pakette 66, ikinci pakette 77 ve ek alan/kanıt kapsamıyla 90 satırı iki görünümde doğruladı.
- Sabit paketlerin özetleri, ilk sürümün dört dosyası ve temel özgün kaynak tekrar doğrulandı. Günlükler, çıkış kodları, sahiplik ve sürüm özetleri `03-13-checks/` altındadır. Otomatik kontroller kaynak anlamına ilişkin ajan incelemesinin yerini almaz.
- `actuals.tokens`, iki görev commit'i farkının 103.179.122 karakterinin dörde bölünmüş ve aşağı yuvarlanmış ölçüsüdür; model tüketimi değildir.

## Task Commits

1. Kurumlar ve haklar: `283260a`.
2. Ekonomi, sosyal konular ve tarihsel kanıtlar: `3ce0090`.

## Deviations from Plan

None - plan executed exactly as written.

## 03-14, 03-15 ve 03-16 aktarımı

- 03-14 bütün partilerde gelir güvencesi ve nakit gelir ayrımı dahil yedi geri tarama adayını kaynak ve koşullarıyla ele alır.
- 03-15/03-16: mevcut görüntüleyici dar yokluk kapsamını, bağlam pasajlarını ve alan bazındaki eksikliği her iki ana görünümde yeterince göstermiyor. Bağlam olumlu hüküm değildir.
- Kısmi Faz 3 denetimi bütün fazın veya ortak gereksinimlerin tamamlandığı anlamına gelmez.

## Self-Check: PASSED

İki paket, semantik kayıt, iki yerel sürüm, denetim ve bağlantı sonuçları, değişmez bayt özetleri ve iki görev commit'i doğrulandı.
