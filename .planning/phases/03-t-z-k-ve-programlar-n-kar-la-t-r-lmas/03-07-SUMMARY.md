---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "07"
subsystem: kaynakli-karsilastirma
tags: [yeni-yol, tuzuk, program, belge-acigi]
requires:
  - phase: 03-06
    provides: Denetlenmiş ortak sözlük ve önceki yerel sürüm
provides:
  - Yeni Yol'un ayrı tüzel kimliği için güncel tüzük ve program araştırma zinciri
  - Ortak konularda belgelenmiş iki bağımsız belge açığı
affects: [03-14, 03-15, 03-16]
actuals:
  tokens: 15434402
  tasks: 2
  commits: 2
plan_head_before: b349990521e515509a038bcb3da9f9fec1e12c47
tech-stack:
  added: []
  patterns: [ortak-belge-acigi, degismez-yerel-yayin]
key-files:
  created:
    - data/comparisons/03-yeni-yol-charter.json
    - data/comparisons/03-yeni-yol-program.json
    - data/comparisons/03-yeni-yol-semantic.json
    - .planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-07-CHECKS.json
  modified:
    - data/current.json
key-decisions:
  - "Kuruluş haberindeki taslak onayı tüzük veya program metni sayılmadı."
  - "Ayrı Yeni Yol tüzel kişiliğinin belge açığı ortak grup ve başka partilerin metinleriyle kapatılmadı."
requirements-completed: []
requirements-addressed: [TUZ-01, TUZ-02, TUZ-03, TUZ-04, PRG-01, KAR-01, KAR-02, RAP-02]
coverage:
  - id: D1
    description: Yeni Yol tüzük araştırması ve 166 ortak konuda belgelenmiş açık
    verification:
      - kind: integration
        ref: python3 src/arsiv.py audit --release 4dfc60953674424cb459da498ee71eaa --phase 3 --stage partial
        status: pass
    human_judgment: true
    rationale: Kaynak aramasının kapsamı ve belge türü değerlendirmesi araştırma yargısı içerir; bu tekil kaynak onayı ön koşulu değildir.
  - id: D2
    description: Yeni Yol bağımsız program ve ek belge araştırması, 135 ortak konuda açık ve karşılıklı bağlantılar
    verification:
      - kind: integration
        ref: python3 src/arsiv.py audit --release current --phase 2
        status: pass
    human_judgment: true
    rationale: Arama kapsamı ve kaynak türü otomatik bütünlük denetiminin dışında ayrıca değerlendirilir; tekil kaynak kabulü ön koşulu değildir.
duration: 84min
started: 2026-11-13T20:07:02Z
completed: 2026-11-13
status: complete
---

# Phase 03 Plan 07: Yeni Yol Tüzük ve Program Araştırması Özeti

**Yeni Yol'un ayrı sicil kimliği için tüzük ve program aramaları yenilendi; 301 ortak konu, elde edilemeyen belgelerin gerçek arama zincirleriyle iki rapor görünümünde gösterildi.**

## Teslimler ve kaynak sınırı

- Yargıtay `yargitay-331` kaydı 13 Ocak 2025 kuruluşunu ve ayrı Yeni Yol kimliğini gösterir. `0206-yeni-yol-registry-v1`, `0206-yeni-yol-registry-page-v1`, `0206-yeni-yol-founding-v1` ve `0206-yeni-yol-mutabakat-v1` önceki özgün yakalamalar olarak korundu. Sicilde erişilen kimlik sayfasında tüzük veya program indirme bağlantısı yok; ikinci sayfanın güncel erişimi zaman aşımına uğradı.
- KARAR'ın 10 Ocak 2025 kuruluş haberinde taslakların onayı aktarılır; içerikleri verilmez. DHA'nın haberi ortak grup kuruluşunu anlatır. Bu haberler tüzük maddesi, tam program veya kendi başına parti ilkeler bildirgesi yerine geçirilmedi. Aynı adlı eski parti, ortak Meclis grubu ve Saadet/DEVA/Gelecek belgeleri ayrı tutuldu.
- Tüzük için 166 ortak konu mevcut veya yeni ortak belge açığına bağlandı; önceki sürümdeki merkez yönetimi yer tutucusu aynı kimlik, düzey ve organla kapatıldı. Tüzük sürümü `4dfc60953674424cb459da498ee71eaa`, rapor `data/releases/4dfc60953674424cb459da498ee71eaa/index.html`; görev commiti `4aceb24`.
- Program için 135 ortak konu mevcut veya yeni ortak belge açığına bağlandı. Bağımsız tam program veya partiye ait ilkeler/kuruluş metni bu taramada bulunmadı; ek belge uydurulmadı. Son sürüm `b27a1387425c40889313e92dfc91739e`, rapor `data/releases/b27a1387425c40889313e92dfc91739e/index.html`; görev commiti `4f23ad0`.
- Gerçek sorgular, ziyaret edilen adresler, zamanlar, sonuçlar ve kapanış gerekçeleri paketler ve semantik araştırma kaydındadır. Aynı gerçek belge açığı birçok konuya bağlandı; hücre başına sahte arama yapılmadı. Tam metin edinilmediğinden hiçbir politika veya organ hükmü, alıntı ya da incelenmiş metinde açık ifade yokluğu üretilmedi.

## Doğrulama

- Her iki paket `COMPARISON_INPUT_OK`, current tabanlı ayrı çalışma alanlarında `COMPARISON_LOAD_OK` ve kendi yerel sürümünde `PHASE3_AUDIT_OK` verdi. Son sürüm `PHASE2_AUDIT_OK` verdi; Faz 2 teslim öneki önceki sürümle aynı kaldı.
- Son sürümde 166 tüzük ve 135 program konusu belge eksikliğiyle kayıtlı, Yeni Yol için `not_researched` satırı ve eksik satırına bağlanmış politika alanı yok. 301 güncel satırın iki görünümde karşılıklı hedefleri doğrulandı. Ayrıntılı sonuçlar `03-07-CHECKS.json` içindedir.
- Mevcut kod ve dondurulmuş üreticiler değiştirilmedi; önceki 124 testlik kod tabanı bu veri planında tekrar çalıştırılmadı. Yeni sorgu ve belge türü incelemesi ajan değerlendirmesidir; bağımsız insan kabulü veya hukuki yürürlük kanıtı iddiası değildir.
- `actuals.tokens`, başlangıç HEAD'inden iki görev commitine 61.737.609 karakterlik gerçekleşen farkın dörde bölünmesiyle ölçüldü; model token tüketimi değildir.

## 03-14, 03-15 ve 03-16 aktarımı

- Bu planda yeni kaynaklı ortak konu adayı çıkmadı. Bağımsız tüzük, program veya ilgili partiye ait ek metin sonradan bulunursa kimlik ve belge türü korunarak bütün ortak konularda yeniden taranmalıdır.
- Renderer 17'nin açık ifade yokluğu kapsamını tek başına göstermeme sınırı 03-15/03-16 için geçerlidir; bu planda açık ifade yokluğu kaydı üretilmedi. Sekiz ortak gereksinim diğer planlar ve son faz doğrulaması tamamlanana kadar beklemede kalır.

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

Üç paket, iki görev commiti, iki yerel rapor ve her iki Faz 3 ile son Faz 2 denetimi doğrulandı; yazıcı kilidi yok.
