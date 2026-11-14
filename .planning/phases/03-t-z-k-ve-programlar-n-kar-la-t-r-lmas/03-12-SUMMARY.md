---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "12"
subsystem: kaynakli-karsilastirma
tags: [demokrat, tuzuk, dyp, tarihce, kaynak-atfi]
requires:
  - phase: 03-11
    provides: Denetlenmiş karşılaştırmalar ve önceki yerel sürüm
provides:
  - Demokrat üyelik, organ seçimi, denetim, görüş ve disiplin karşılaştırmaları
  - Erişilen DYP dönemi metinlerinden kaynaklı tarihsel pasaj çiftleri
affects: [03-13, 03-14, 03-15, 03-16]
actuals:
  tokens: 24846452
  tasks: 2
  commits: 2
plan_head_before: 621e65b14e9f5b993ad76eefc07f14208f481ad4
tech-stack:
  added: []
  patterns: [sinirli-kapsam-incelemesi, taranmis-kaynak-sayfa-kontrolu, degismez-yerel-yayin]
key-files:
  created:
    - data/comparisons/03-demokrat-charter-1.json
    - data/comparisons/03-demokrat-charter-2.json
    - data/comparisons/03-demokrat-semantic.json
  modified:
    - data/current.json
key-decisions:
  - "Arşiv yakalama tarihi kabul tarihi veya son yürürlükteki sürüm kanıtı değildir."
  - "Madde 20 ve 25 hükümlerinin uygulanma ilişkisi kaynakta açıklanmadığından hukuki sonuç varsayılmaz."
  - "Tarihsel farklar iki gerçek pasajla, bilinmeyen ara sıra ve tarih sınırları korunarak verilir."
requirements-completed: []
requirements-addressed: [TUZ-01, TUZ-02, TUZ-03, TUZ-04, KAR-01, RAP-02]
duration: unknown
completed: 2026-11-14
status: complete
---

# Phase 03 Plan 12: Demokrat Tüzüğü Karşılaştırması Özeti

**Demokrat tüzüğünün üyelik, seçim, denetim ve disiplin hükümleri ile erişilen DYP metinlerindeki tarihsel farklar kaynaklı karşılaştırmalara eklendi.**

## Teslim ve kaynak sınırı

- `0210-demokrat-charter-archive-v1` tam 48 sayfalık PDF incelendi; özgün PDF SHA-256 `379499d93d88c2ea209706ed34d337adb8bc22422127c5411bb9fc01dbe809b4`. 18.06.2022 arşiv yakalaması kabul tarihi veya bugün en yeni yürürlükteki metnin kanıtı değildir. Canlı site erişim sorunu eldeki atıflı tam nüshanın kullanımını engellemez.
- Yargıtay kaydındaki `yargitay-3` tüzel kişiliğinin 23.06.1983 kuruluşu ve 27.05.2007 ad değişikliği esas alındı; 1946 Demokrat Parti ve 28.05.2007 tarihli ayrı DYP bu metinlerin sahibi yapılmadı.
- İki paketin birleşimi 166 ortak alt soruyu kapsam kaydı veya kanıtla ele alır. Toplam 310 satır, 312 kaynaklı alan, 47 sınırlı yokluk kapsamı ve 359 gerekçeli ajan semantik kararı vardır; bu kararlar bağımsız insan kabulü değildir. `no_explicit_statement` satırına alan veya ilgisiz olumlu bağlam eklenmedi.
- Madde 20 olağan ilçe kongresi için onda bir delege koşulunu; madde 25 bütün düzeylerde ilk açılış için yarıdan bir fazlayı, çoğunluk sağlanmazsa ertesi gün aynı yer, saat ve gündemde katılanlarla açılışı düzenler. İki pasaj ve koşulları korunur; uygulanma ilişkisi metinde açıklanmadığından hangi hükmün uygulanacağına dair sonuç çıkarılmadı.
- 1983, 1985, 1988 ve 1990 kataloglu erişilebilir DYP nüshalarındaki ilgili hükümler incelendi; 22 gerçek tarihsel karşılaştırmada iki ayrı pasaj ve kısa açıklama korundu. Taranmış 1983, 1985 ve 1988 tüzük bölümleri ile 1990 kataloglu ayrı nüshanın tüzük bölümü sayfa görüntülerinden okundu; diğer 1990 kataloglu nüshalarda karşılaştırmada kullanılan ve ilgili örnek sayfalar ayrıca kontrol edildi. Tarihi veya sırası kanıtlanmayan ara sürümler varsayılmadı. 1988 kapak tarihi 15 Mayıs, metindeki yürürlük tarihi 16 Mayıs olarak ayrı tutuldu; ayrı 1990 kataloglu nüshada 7 Haziran 1989 değişikliklerinin 8 Haziran yürürlüğü kendi sayfasına bağlandı.
- İlk yerel sürüm `fcbea5d01f9f409383b2e506878f8876`, son yerel sürüm `bcd3dd70ea6d4cefb3379b1a59ccf264`; raporları ilgili `data/releases/<sürüm>/index.html` dosyalarıdır. Önceki `945f32db93854c19bd1dd1729ffcd691` sürümü ve Faz 2 teslim sırası korundu. Kamuya yayın yapılmadı.

## Doğrulama

- İki paket için `COMPARISON_INPUT_OK`, `COMPARISON_LOAD_OK` ve ilgili yerel sürümde `PHASE3_AUDIT_OK`; son sürümde `PHASE2_AUDIT_OK` alındı. Son raporda ilk paketin 144 satır/160 alanı ve ikinci paketin 166 satır/152 alanı iki görünümde, bulgu metinleri ve kaynak hedefleriyle kontrol edildi.
- Yeni sürümlerin taban zinciri ve Faz 2 teslim sırası karşılaştırıldı; ilk sürümün dört dosyasının SHA-256 özetleri son yayından sonra tekrar doğrulandı. Paket/sürüm özetleri, günlükler, çıkış kodları ve işlem sahipliği `03-12-checks/` dizinindedir.
- `actuals.tokens`, başlangıç ile iki görev commit'i arasındaki 99.385.811 karakterlik Git farkının dörde bölünmüş ölçüsüdür; model tüketimi değildir. Otomatik kontroller kaynak anlamına ilişkin ajan incelemesinin yerini almaz.

## Task Commits

1. Üyelik ve organ seçimleri: `ee7f710914085d5116364218185390916f6d488e`.
2. Denetim, görüş ve DYP tarihçesi: `d82b0b557cde841348d2768de1b6fbbcf9465952`.

## Deviations from Plan

**[Rule 3 - Blocking issue]** İkinci paket için erken başlatılan resmî `comparison-check`, ilk yayın işleminin etkin yazma kilidi nedeniyle `FileExistsError` ile durdu. Kilidi değiştirmedi; deneme günlüğü korundu. İlk görev denetlenip commit edildikten sonra resmî kontrol yeniden çalıştırıldı ve geçti; ikinci yayın tek yazıcı sırasıyla tamamlandı.

## 03-13, 03-15 ve 03-16 aktarımı

- 03-13 Demokrat programını kendi kaynağı ve kapsamıyla inceler; tüzükteki tarihsel farklar program hükmü sayılmaz.
- 03-15/03-16: Mevcut görüntüleyici `no_explicit_statement` durumunu gösterse de ayrıntılı inceleme kapsamını ve eşlik eden bağlam pasajını iki ana görünümde göstermiyor. Bu sunum sınırı sonraki çalışmaya taşınır; bağlam olumlu hüküm değildir.
- Kısmi Faz 3 denetimi bütün fazın veya ortak gereksinimlerin tamamlandığı anlamına gelmez.

## Self-Check: PASSED

İki paket, semantik kayıtlar, iki yerel rapor, denetim sonuçları, sürüm özetleri ve iki görev commit'i doğrulandı.
