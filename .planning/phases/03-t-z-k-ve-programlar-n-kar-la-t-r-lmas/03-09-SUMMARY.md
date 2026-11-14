---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "09"
subsystem: kaynakli-karsilastirma
tags: [emep, tuzuk, program, kaynak-atfi]
requires:
  - phase: 03-08
    provides: Denetlenmiş ortak sözlük ve önceki yerel sürüm
provides:
  - EMEP tüzük organları, üyelik ve disiplin hükümlerinin kaynaklı karşılaştırması
  - EMEP programının ortak alanlarda kaynaklı karşılaştırması ve incelenmiş kapsam sınırları
  - Yargıtay önerisi ile metin gövdesinin kabul ve sıra belirsizliğini koruyan gösterimi
affects: [03-14, 03-15, 03-16]
actuals:
  tokens: 16463687
  tasks: 2
  commits: 2
plan_head_before: 7c8894b45a574ca0321e4cc934788d8ff8246554
tech-stack:
  added: []
  patterns: [kaynak-katmani-ayrimi, sinirli-kapsam-incelemesi, degismez-yerel-yayin]
key-files:
  created:
    - data/comparisons/03-emep-charter.json
    - data/comparisons/03-emep-program.json
    - data/comparisons/03-emep-semantic.json
  modified:
    - data/current.json
key-decisions:
  - "Yargıtay paketindeki kongre değişikliği önerisi ve program/tüzük gövdesi türleriyle gösterilir; kabul ve sıraları kanıtlanmamıştır."
  - "1996 tarihli ayrı Emek Partisi belgesi güncel EMEP programının yerine veya tüzel kimliğine aktarılmaz."
  - "Koşullu destek hükümleri genel ve koşulsuz temel gelir olarak sunulmaz."
requirements-completed: []
requirements-addressed: [TUZ-01, TUZ-02, TUZ-03, TUZ-04, PRG-01, KAR-01, KAR-02, RAP-02]
duration: 150min
started: 2026-11-14T01:21:55Z
completed: 2026-11-14
status: complete
---

# Phase 03 Plan 09: EMEP Tüzük ve Program Karşılaştırması Özeti

**EMEP tüzüğü ve programı ortak konularda kaynaklarına bağlandı; kongreye sunulan öneri ile kabul ve sırası belirsiz metin gövdesi ayrıldı.**

## Teslimler ve kaynak sınırı

- Birleşik HTML kaynağının tüzük başlangıcından sonuna 1–65 maddesi ve programının giriş ile A–G bölümleri okundu; 166 tüzük ve 135 program konusu olumlu kanıt veya belirtilen soruyla sınırlı incelenmiş kapsamla ele alındı. Tüzük paketinde 210 kanıt alanı ve 54 kapsam kaydı; programda 170 kanıt alanı ve 36 kapsam kaydı vardır. 470 gerekçeli semantik karar ajan incelemesidir, bağımsız insan kabulü değildir.
- Metin katmanı bulunmayan 38 sayfalık Yargıtay PDF'si sayfa görüntülerinden okundu. İlk dört sayfa 6. Kongreye sunulan değişiklik önerisidir; sonraki program ve tüzük gövdesi bu önerinin kabulünü veya kronolojik sıralamayı kanıtlamaz. Öneri `supplement`, gövdeler kendi türleriyle gösterildi. Örneğin öneri aidatı 10–500 TL, gövde 5–250 YTL, HTML 20–1000 TL belirtir; iş süresi ve yönetim kurulları da farklıdır. Bunlar kendiliğinden önce/sonra veya kabul edilmiş değişiklik olarak sunulmadı.
- HTML programı, tüzük maddelerinden ayrı okundu. İşini kaybeden emekçi ve hayatını kaybeden emekçinin bakmakla yükümlü olduğu yakınlarına yönelik gelir desteği, tüm yurttaşlara koşulsuz temel gelir sayılmadı. Öneride çalışamayan engellilere aylık ve işsiz, yaşlı, malullere aylık ayrı kapsamlarla gösterildi. 1996 tarihli TBMM kitabındaki ayrı Emek Partisi kimliği sessizce güncel EMEP ile birleştirilmedi. Görseldeki 2017, yayın tarihi 2019 ve web güncellemesi 2020 birbirinden ayrı tarih türleridir; kabul tarihi çıkarılmadı.
- Tüzük sürümü `d57131ee0f5b4c9dae1c09e3c704de3d`, raporu `data/releases/d57131ee0f5b4c9dae1c09e3c704de3d/index.html`; son program sürümü `69d1054dc6ce45a7bb45eca3ca37b4c1`, raporu `data/releases/69d1054dc6ce45a7bb45eca3ca37b4c1/index.html`. İkisi yerel immutable sürümlerdir; önceki kaynak baytları ve Faz 2 teslim öneki korunmuştur.

## Doğrulama

- Her iki paket `COMPARISON_INPUT_OK`, yükleme `COMPARISON_LOAD_OK`, kendi sürümünde Faz 3 kısmi denetim `PHASE3_AUDIT_OK` verdi. Son sürümde Faz 2 denetimi `PHASE2_AUDIT_OK` verdi.
- Son raporda 262 tüzük ve 206 program satırının iki görünümdeki bulgu ve kaynak hedefleri ayrı ayrı doğrulandı (`REPORT_LINK_CHECK_OK`). Son veritabanında EMEP için `not_researched` satırı yoktur; 377 kanıt ve 90 sınırlı açık ifade yokluğu satırı vardır.
- HTML kaynağı SHA-256 `16e8971e7cc015b0134f7836a9930200f04e9a298803f58801cf2261e3593329`, Yargıtay PDF `82a0ec082d33e31eeb3ad2e3f0955b851f2d2fc4e9e417fac3bd148bd805f171`, tarihsel kitap `2bad4f7822b5f4b5adda6646ea5309a65d231f93cb6aae538b9a57c3467e706c` olarak doğrulandı. Tüzük ve program girdilerinin özetleri sırasıyla `8fdc69451527ad4232915a680eb83075835c51dbf91b33c116b49b0ac28c7711` ve `cdc67459d4600fc9b10faf3f1d0e8c72ec67da09affb1f5e152bcb91ee8d1812`.
- `actuals.tokens`, plan başlangıcı ile iki görev commit'i arasındaki 65.854.747 karakterlik Git farkının dörde bölünmesidir; model tüketimi değildir. Kaynak anlamını değerlendirme araştırma yargısı gerektirir; otomatik doğrulama bunun yerini almaz.

## Task Commits

1. Tüzük: `730895f62a3c71430bdb74b0114c35aaac964992`.
2. Program: `b8c3cb6ce7b803c48001afceb3fcb4fff71ac7fa`.

## Deviations from Plan

### Auto-fixed Issues

1. **[Rule 1 - Bug] Kanonik tüzük satırı çakışması düzeltildi.** İlk taslak doğrulamada iki aynı konu/düzey/organ/sürüm anahtarı çatıştı. Aynı gerçek organın hükümleri tek satırda ayrı alan ve kaynaklarla birleştirildi; organ adına madde kimliği eklenmedi. Düzeltilmiş girdi denetlendi ve ilk görev commit'inde teslim edildi.

## 03-14, 03-15 ve 03-16 aktarımı

- 03-14 geri taraması için somut adaylar: seçilmişlerin kalifiye işçi ortalamasıyla sınırlanan ücreti, çalışamayan engellilerin önerilen aylığı ve herkese yeterli ücretsiz su önerisi. Bunların öneri/gövde ve koşul sınırları korunmalıdır.
- 03-15/03-16 için açık ifade yokluğu yalnız belirtilen HTML bölümü ve özgül soru ile sınırlıdır; ilişkili bağlam alıntıları, aranan özel soruya olumlu yanıt olarak yorumlanmamalıdır. Faz 3 gereksinimleri bu kısmi plandan sonra bütün faz tamamlanmış sayılarak kapatılmaz.

## Self-Check: PASSED

Paketler, iki yerel sürüm/rapor ve görev commit'leri doğrulandı.
