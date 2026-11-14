---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "08"
subsystem: kaynakli-karsilastirma
tags: [dbp, bdp, tuzuk, program, kaynak-atfi]
requires:
  - phase: 03-07
    provides: Denetlenmiş ortak sözlük ve önceki yerel sürüm
provides:
  - DBP tüzüğünün kaynaklı organ ve madde karşılaştırmaları
  - Tarihsel BDP program nüshaları ve bağımsız güncel DBP programı araştırması
  - Sürümün kendi yayıncısını gösteren ve eski sürümleri koruyan rapor üreticisi
affects: [03-14, 03-15, 03-16]
actuals:
  tokens: 14252700
  tasks: 2
  commits: 3
plan_head_before: 8044a07061a6418f650d4b88712297a9041e66ca
tech-stack:
  added: []
  patterns: [surum-bazli-yayinci-atfi, esit-belirsiz-alternatifler, degismez-yerel-yayin]
key-files:
  created:
    - data/comparisons/03-dbp-charter.json
    - data/comparisons/03-dbp-program.json
    - data/comparisons/03-dbp-semantic.json
    - src/rapor_v17.py
    - tests/test_source_labels.py
  modified:
    - data/current.json
    - src/arsiv.py
    - src/rapor.py
    - tests/test_comparison_content.py
key-decisions:
  - "Sırası kanıtlanmayan farklı tüzük hükümleri iki görünümde eşit kaynaklı alternatiflerdir; önce ve sonra ilişkisi uydurulmaz."
  - "Tarihsel BDP programı ve yayıncıları, bağımsız güncel DBP programı aramasından ayrıdır."
  - "Aynı belge kimliğinde her sürümün kendi yayıncısı ve sürüm etiketi gösterilir; üretici 17 dondurulur."
patterns-established:
  - "Okunamayan kaynak değeri başka nüshadan tamamlanmadan belirsiz bırakılır."
requirements-completed: []
requirements-addressed: [TUZ-01, TUZ-02, TUZ-03, TUZ-04, PRG-01, KAR-01, KAR-02, RAP-02]
coverage:
  - id: D1
    description: DBP tüzüğünün 166 ortak konuda kaynaklı karşılaştırılması ve farklı nüshaların gösterimi
    verification:
      - kind: integration
        ref: python3 src/arsiv.py audit --release 6f05d704dbda4333ab93c4bf1687999f --phase 3 --stage partial
        status: pass
    human_judgment: true
    rationale: Maddi hükümlerin ve bağlamın değerlendirilmesi araştırma yargısı içerir; tekil kaynak için insan kabulü ön koşulu değildir.
  - id: D2
    description: Tarihsel BDP program nüshalarının 135 konuda incelenmesi ve bağımsız güncel DBP programı araması
    verification:
      - kind: integration
        ref: python3 src/arsiv.py audit --release 9f6ba77edd7041e18c72954640c6fff4 --phase 3 --stage partial
        status: pass
      - kind: integration
        ref: python3 src/arsiv.py audit --release current --phase 2
        status: pass
    human_judgment: true
    rationale: Kaynak araması ve hükümlerin anlamı araştırma yargısı içerir; tekil kaynak onayı ön koşulu değildir.
  - id: D3
    description: Her belge sürümünde doğru yayıncı ve sürüm etiketinin iki görünümde sunulması ve eski üretici uyumluluğu
    verification:
      - kind: unit
        ref: tests/test_source_labels.py ve tests/test_comparison_content.py odaklı testleri
        status: pass
      - kind: integration
        ref: renderer18 yayın testi ve renderer17 eski current Faz 2 denetimi
        status: pass
    human_judgment: false
duration: 214min
started: 2026-11-13T21:37:40Z
completed: 2026-11-14
status: complete
---

# Phase 03 Plan 08: DBP Tüzük ve Program Karşılaştırması Özeti

**DBP'nin tüzük nüshaları ve tarihsel BDP programları ortak konularda kaynaklarıyla karşılaştırıldı; bağımsız güncel program açığı ve bilinmeyen sürüm sırası açık korundu.**

## Teslimler ve kaynak sınırı

- Güncel HTML tüzüğün 114 maddesi, Yargıtay taramasının 49 sayfası ve erişilebilir iki tarihsel BDP tüzük nüshası 166 konu, ilgili organ ve düzeyler bakımından incelendi. 240 semantik karar, 209 kanıt alanı ve 31 sınırlı kapsam kaydı üretildi; 217 kaynak pasajı arasında görsel okunan 14 PDF pasajının yöntemi ve sıfır tabanlı sayfa indeksi ile basılı sayfa ayrımı korundu.
- HTML ile tarama arasındaki 12 maddi fark grubu iki görünümde eşit kaynaklı sunuldu. Kaynakların sırası bilinmediğinden önce/sonra değişikliği veya kendiliğinden güncel sürüm seçimi üretilmedi. 11.07.2014 ad değişikliği ve DBP madde 112 kaynakları korundu; başka bir tüzel parti DBP ile birleştirilmedi.
- Blogspot tüzüğünde doğrulanan kota %40'tır. WordPress metninde kota hükmü vardır, ancak bozuk karakter nedeniyle kendi kaynağındaki sayı doğrulanamamıştır; bu durum hüküm yokluğu veya diğer nüshanın sayısı olarak gösterilmedi.
- Tarihsel BDP programının tüm bölümleri, `0207-dbp-bdp-program-v1` ve erişilen diğer nüsha dahil, 135 konuda incelendi. 98 konuda somut kanıtlı değerlendirme, 37 konuda kapsamı sınırlı açık ifade yokluğu ve ayrıca 135 konuda bağımsız güncel DBP programı açığı kaydedildi. 257 pasaj kendi özgün kaynak metninde eşleştirildi; 331 yeni semantik karar kaydedildi. Tarihsel kaynak rolü, bilinmeyen kabul tarihleri ve `BDP adlı Blogspot yayını` yayıncı atfı korundu.
- 2026-11-13 22:17:38 ve 22:44:18 UTC'de yapılan iki araştırma turunda dört'er gerçek arama kaydedildi. Güncel program için bulunan akademik yönlendirmeler tüzük adreslerine çıktı; bağımsız tam program bulunmadı. Tarihsel metin güncel programın yerine geçirilmedi.
- Görev 1 yerel sürümü `6f05d704dbda4333ab93c4bf1687999f`; son yerel sürüm `9f6ba77edd7041e18c72954640c6fff4`. Faz 2'nin tamamlanmış teslim öneki değişmedi. Özgün kaynak baytları ve önceki yayınlar korundu; yeni Blogspot pasif yerel görünümü eklendi.

## Doğrulama

- Tüzük ve program paketleri ayrı ayrı `COMPARISON_INPUT_OK` ve `COMPARISON_LOAD_OK`, güncel tabanlı çalışma alanında Faz 2 ön kontrolü, yayımdan sonra `PHASE3_AUDIT_OK` verdi. Sabit son girdi SHA-256 değerleri sırasıyla `4729ac4c57a9b6565d53a93b7dc47f6e518a2664c4932776d2ac29ebb9444837` ve `66ae23926476ed8222531c24b1a6b1a11a0511db16c6e2baa3d53a3712d648a7`.
- Son sürümde `python3 src/arsiv.py audit --release current --phase 2` çıkış 0 ve `PHASE2_AUDIT_OK 9f6ba77edd7041e18c72954640c6fff4` verdi. Tüzüğün 240, programın 466 satırının iki görünümde karşılıklı bağlantıları, kaynak hedefleri ve atıfları kontrol edildi; 514 program kaynak etiketi kendi yayıncısıyla doğrulandı. DBP ortak konu kayıtlarında `not_researched` kalmadı.
- Üretici düzeltmesinin 11 odaklı testi ve gerçek yayın/yenileme testi geçti; mevcut gerçek üretici 17 yayını kendi dondurulmuş üreticisiyle Faz 2 denetimini geçti. Veri incelemesi için önceki 124 testlik tam takım gereksiz yere tekrar çalıştırılmadı.
- `actuals.tokens`, başlangıç HEAD'inden üç görev/düzeltme commitine gerçekleşen 57.010.798 karakterlik Git farkının dörde bölünmesiyle ölçüldü; model token tüketimi değildir.

## Task Commits

1. Tüzük karşılaştırmaları: `c35d126eeccc041b6f0bef2f763d5c84ddeafb6a`.
2. Kaynak sürümü başlığı düzeltmesi: `7e49d3dc22d4623daa032928c8be33a43b422c29`.
3. Tarihsel program ve güncel program araştırması: `f3365d02bbfe9848bcf319edb35d4c0f549a0c7d`.

## Deviations from Plan

### Auto-fixed Issues

1. **[Rule 1 - Bug] Yeni Blogspot tüzük sürümünün dosya kaynağı bağlantısı:** İlk yayın denemesinde `dossier_source` bağlantısı eksikti ve yayın kabul edilmedi. Paket düzeltildi, girdi yeniden dondurulup kontrol ve yükleme tekrarlandı; başarılı görev commiti `c35d126`. Başarısız hazırlık `/tmp/gsd-03-08-failed-staging-1c1dd6ff7c7f4c37956499b9c6e10d66` altında korundu.
2. **[Rule 1 - Bug] Ortak belge başlığının yanlış yayıncı atfetmesi:** Aynı belge kimliğindeki Blogspot ve WordPress sürümlerinin yayıncıları kendi `source_attribution.publisher` ve `version_label` alanlarından gösterilecek şekilde genel düzeltme yapıldı. Eski üretici 17 davranışı `src/rapor_v17.py` içinde donduruldu; canlı üretici 18 oldu, CSS ve kaynak kimlikleri değişmedi. Gerçek aynı-belge örnekleri iki görünümde, yerel hedeflerle ve kaçış güvenliğiyle test edildi; commit `7e49d3d`.

## Issues Encountered

Bir çalışma alanı açılışı metadata yazılmadan 143 ile kesildi. Yalnız kendi bayat yazıcı kilidi, süreç, host ve token sahipliği doğrulanarak orkestratörün açık kurtarma kararıyla temizlendi; milestone kilidine dokunulmadı. Önceki başarılı giriş kontrolü korundu ve yalnız kesilen adım tekrarlandı. Kalıcı süreç ve kontrol kayıtları `/tmp/gsd-03-08-*` altındadır.

## 03-14, 03-15 ve 03-16 aktarımı

- 03-14 için bütün partilerde geri taranabilecek somut adaylar: tarihsel programdaki kamu/özel finansmanlı ücretsiz çocuk bakımı, askerî kâr amaçlı işletmeler ve yaş koşullu 2022 emeklilik önerisinin evrensel gelirden ayrımı.
- Farklı belge kimliklerini kapsayan alternatif grubu mevcut şemada kurulamadığından farklı hükümler eşit görünür ayrı satırlarda, sıra bilinmezliği içerikte ve seçim gerekçesinde açık tutularak verildi. Kapsam satırında genel yokluk gösterimi ve ona eşlik eden kaynaklı bağlam satırı sınırı 03-15/03-16 değerlendirmesine taşınır; kimlikler klonlanmadı. 03-15, yeni üretici değişikliğinden önce o zamanki canlı üretici 18'i dondurmalıdır.
- Sekiz ortak gereksinim diğer planlar ve son faz doğrulaması tamamlanıncaya kadar beklemede kalır.

## User Setup Required

None - no external service configuration required.

## Self-Check: PASSED

Üç karşılaştırma paketi, iki yerel rapor, üç görev/düzeltme commiti, dondurulmuş üretici ve kaynak etiketi testleri mevcut; iki Faz 3 denetimi ve son Faz 2 denetimi başarılı, yazıcı kilidi yok.
