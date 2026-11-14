---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "10"
subsystem: kaynakli-karsilastirma
tags: [saadet, tuzuk, disiplin, tarihce, kaynak-atfi]
requires:
  - phase: 03-09
    provides: Denetlenmiş dokuz partilik taban ve önceki yerel sürüm
provides:
  - Saadet üyelik, organ, denetim ve disiplin hükümlerinin kaynaklı karşılaştırması
  - 2002 ikinci baskısı ile erişilen sonraki tüzük nüshasının iki pasajlı konu karşılaştırmaları
affects: [03-11, 03-14, 03-15, 03-16]
actuals:
  tokens: 20141255
  tasks: 2
  commits: 2
plan_head_before: c0d5497209046d6d2490fdbcd57195b25235a9cd
tech-stack:
  added: []
  patterns: [kaynak-katmani-ayrimi, sinirli-kapsam-incelemesi, degismez-yerel-yayin]
key-files:
  created:
    - data/comparisons/03-saadet-charter-1.json
    - data/comparisons/03-saadet-charter-2.json
    - data/comparisons/03-saadet-semantic.json
  modified:
    - data/current.json
key-decisions:
  - "Aynı SHA taşıyan tüzük adresleri ayrı maddi değişiklik sayılmaz."
  - "2002 baskısı ile sonraki nüsha iki kaynak pasajıyla karşılaştırılır; kesin yürürlük ve ara sürüm zinciri varsayılmaz."
  - "Dar soruya eşlik eden bağlam kanıtı, o soruya olumlu cevap sayılmaz."
requirements-completed: []
requirements-addressed: [TUZ-01, TUZ-02, TUZ-03, TUZ-04, KAR-01, RAP-02]
duration: unknown
completed: 2026-11-14
status: complete
---

# Phase 03 Plan 10: Saadet Tüzük ve Tarihçe Karşılaştırması Özeti

**Saadet tüzüğünün üyelik, organ, denetim ve disiplin hükümleri kaynaklarına bağlandı; 2002 baskısı ile erişilen sonraki nüsha maddi farkları iki kaynak pasajıyla karşılaştırıldı.**

## Teslimler ve kaynak sınırı

- Erişilen 25 sayfalık tüzük ve 2002 ikinci baskısındaki ilgili karşılıklar incelendi; metin katmanı bulunmayan eski PDF sayfaları görüntülerinden okundu ve görsel inceleme kaydıyla kaynaklandı. Etkin taksonominin 166 tüzük konusu incelenen kapsamda ele alındı. 63 dar soruda açık ifade bulunmaması kendi kapsamıyla kaydedildi; bu kayıtlara eşlik eden kaynaklı bağlam, soruya olumlu yanıt verildiği anlamına gelmez. Tüzükte araştırılmamış satır kalmadı; programa ait iki başlangıç satırı 03-11 kapsamındadır.
- Üyelik, merkez, il, ilçe ve diğer organların koşulları ayrı düzey ve gerçek organ satırlarıyla gösterildi. Ortak hüküm birden fazla düzeye uygulanıyorsa gerçek pasaj her uygulanabilir düzeyde kaynaklandı. 507 gerekçeli semantik karar ajan incelemesidir; bağımsız insan kabulü değildir.
- On dokuz tarihsel karşılaştırmada her iki nüshanın ilgili pasajları ilişkilendirildi. Örneğin olağanüstü Büyük Kongre seçim gündemi için 2002 baskısındaki üçte iki eşiği ile diğer nüshadaki salt çoğunluk; GİK için 50 asil/50 yedek ile 75 asil/30 yedek hükümleri ayrı gösterildi. 2019 değişiklik notu ve 2020 GİK kararı yalnız kendi belirttiği maddeler veya sayılar için dayanak alınır; bütün metne kesin yürürlük tarihi verilmez. Ara sürümler ve uygulamadaki tarihsel sıra kanıtlanmış değildir.
- İki erişim adresindeki aynı SHA'lı güncel tüzük aynı içeriktir; adresler kaynak kökeni olarak korunur ve maddi değişiklik üretilmez. 2002 ve sonraki nüsha farklı belge kimliklerine bağlı olduğundan mevcut şemanın aynı belgeyle sınırlı change/alternative_group ilişkileri zorlanmadı; her iki kaynağa bağlı ayrı karşılaştırma bulguları kullanıldı.
- İlk yerel sürüm `84e26e5102ff49fc98e523ae7830ed17`, son sürüm `4926099ac08b40df96fd4c304064023b`; raporları ilgili `data/releases/<id>/index.html` yollarındadır. Önceki özgün kaynaklar ve Faz 2 teslim öneki korundu; kamuya yayın yapılmadı.

## Doğrulama

- Her iki sabit paket `COMPARISON_INPUT_OK`, yükleme `COMPARISON_LOAD_OK`, ilgili sürümde Faz 3 kısmi denetim `PHASE3_AUDIT_OK` verdi. Son sürüm `PHASE2_AUDIT_OK` verdi. Son raporda 262 satırın iki görünümdeki bulgu ve kaynak hedefleri `REPORT_LINK_CHECK_OK` ile doğrulandı; ilk paketin 156 satırı da kendi sürümünde doğrulandı. Günlükler, çıkış kodları, işlem sahipliği ve sabit girdi SHA'ları `03-10-checks/` içindedir.
- `actuals.tokens`, plan başlangıcı ile iki görev commit'i arasındaki 80.565.021 karakterlik Git farkının dörde bölünmüş ölçüsüdür; model tüketimi değildir. Otomatik kontroller kaynak anlamı üzerine ajan değerlendirmesinin yerini almaz.

## Task Commits

1. Üyelik ve organlar: `86bf873dec457ad960bb67f953320387fdef44ab`.
2. Denetim, disiplin ve tarihçe: `d00a421ad096adc5bba2615be4ec1a010b32ef14`.

## Deviations from Plan

### Auto-fixed Issues

1. **[Rule 1 - Bug] Kaynak konumlandırması ve organ düzeyi kapsamı düzeltildi.** Kaynağın sayfa ve madde dayanakları, ortak hükümlerin gerçek uygulama düzeyleri ve aynı organın kanonik alanları yayın öncesinde düzeltildi; yeniden sabitlenen paket doğrulandı ve ilk görev commit'inde teslim edildi.
2. **[Rule 3 - Blocking issue] Sahipsiz eski yerel çalışma alanı güvenle kapatıldı.** Sahiplik belirteci, ana makine, ölü süreç ve mevcut yayın/veritabanı eşitliği doğrulandıktan sonra kilit bırakıldı; kanıt `03-10-checks/unused-workspace-close.log` içindedir.

## 03-11, 03-14, 03-15 ve 03-16 aktarımı

- 03-11 program incelemesini ve programa ait iki araştırılmamış başlangıç satırını ele alır; bu plan program sonucu üretmez.
- 03-14 geri taramasında yalnız belgelenmiş ve kapsamı açık kaynak adayları kullanılmalıdır.
- 03-15/03-16: Bağlam alıntısı ilgili dar soruda açık hüküm bulunduğunun kanıtı değildir; 63 sınırlı yokluk kaydı ve gerçek olumlu hükümler ayrılmalıdır. Farklı belge kimliklerindeki iki nüshanın çift kaynaklı tarihçesi mevcut ilişkilerin sınırı korunarak sunulmalıdır. Faz 3 gereksinimleri bu kısmi planla tamamlanmış sayılmaz.

## Self-Check: PASSED

İki paket, semantik kayıt, iki yerel sürüm ve rapor, denetim günlükleri ve iki görev commit'i doğrulandı.
