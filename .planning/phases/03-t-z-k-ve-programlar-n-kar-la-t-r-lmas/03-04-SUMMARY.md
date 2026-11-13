---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "04"
subsystem: kaynakli-karsilastirma
tags: [tip, tuzuk, program, semantik-inceleme, renderer17]
requires:
  - phase: 03-03
    provides: ortak kaynaklı konu sözlüğü, envanter ve önceki parti karşılaştırmaları
provides:
  - TİP HTML ve PDF tüzük sürümlerinin kaynaklı ve sırası belirsiz karşılaştırması
  - TİP programının koşulları korunmuş kaynaklı ortak konu karşılaştırması
affects: [03-14, 03-15, 03-16]
actuals:
  tokens: 11255958
  tasks: 2
  commits: 2
plan_head_before: 9512c2c252a84708cecf9b07300d3c38135f01a1
tech-stack:
  added: []
  patterns: [degismez-yerel-yayin, kaynakla-ajan-anlam-incelemesi, kapsamli-yokluk]
key-files:
  created:
    - data/comparisons/03-tip-charter.json
    - data/comparisons/03-tip-semantic.json
    - data/comparisons/03-tip-program.json
  modified:
    - data/current.json
key-decisions:
  - "HTML ve PDF tüzük metinleri arasında kabul veya yürürlük sırası kanıtlanmadığından gerçek farklı hükümler eşit alternatiflerdir."
  - "PDF Türkçe metin katmanındaki kayıplar sayfa görüntülerinden doğrudan okunarak sayfa ve yöntem bilgisiyle kaydedildi."
  - "Programdaki sosyalist toplum koşulu ve nicel ayrıntısı bulunmayan nitel araçlar korunur; yokluk yalnız incelenen kaynak ve somut alt soru içindir."
requirements-completed: []
requirements-addressed: [TUZ-01, TUZ-02, TUZ-03, TUZ-04, PRG-01, KAR-01, KAR-02, RAP-02]
duration: yaklaşık 205min
completed: 2026-11-13
status: complete
---

# Phase 03 Plan 04: TİP Tüzük ve Program Karşılaştırması Özeti

**TİP'in tam arşivli tüzük sürümleri ve programı, özgün pasajları ve koşullarıyla iki rapor görünümüne bağlandı; sürüm sırası belirsizliği ve incelenen alt soruların sınırları korundu.**

## Teslimler ve kaynaklar

- Tüzük HTML `0203-tip-charter-v1`, özgün SHA-256 `3618e6ebefa371e469d2d34b4c92cacf479ed8bff6da34cdc21bd1dab2a4b28c`; PDF `0203-tip-charter2022-v1`, SHA-256 `e86237895eda1cec2e66ac388ce7b9cd7096e86dfc9f1cccdd93ab1a298e4a60`. PDF'nin 32 sayfası görsel okundu; metin katmanının Türkçe karakter kayıpları erişimsizlik sayılmadı. Elle doğrulanan pasajlarda gerçek sayfa, yöntem ve gerekçe vardır. Dosya adındaki 2022 kabul veya yürürlük tarihi değildir.
- Üyelik, haklar, adaylık, seçimler, kotalar, süreler, merkez/il/ilçe ve diğer organlar, denetim, görüş ve öneriler, disiplin ve itirazlar kaynak yetki ve koşullarıyla incelendi. 166 ortak tüzük konusu; 459 satır, 347 kanıt alanı ve somut alt soruya sınırlandırılmış 114 yokluk satırıyla karşılandı. Görünür kaynaklı açıklamalar kapsamları belirtir. Önceki izleyici bulgusu ve araştırılan eski yer tutucu kimliği yeniden kullanıldı.
- HTML ve PDF'de Parti Meclisi bileşimi sırasıyla 35 asıl/5 yedek ve 45 asıl/5 yedek; başka örneklerde kongre delegeleri, kadın kotası, disiplin süreleri ve denetim raporu sıklığı farklıdır. Gerçek hükümler sürümlerine bağlı, eşit belirsiz alternatifler olarak gösterildi; hukuki öncelik veya kronoloji uydurulmadı. Önceki `tip-charter-v1` ile 0203 HTML'nin yedi bölümünün etiket ve boşluk normalleştirilmiş metinleri eşittir; özgün baytlar ise ayrıdır.
- Tüzük son yerel sürümü `d538799da191453abba729858fb28529`, rapor `data/releases/d538799da191453abba729858fb28529/index.html`, görev commit'i `57fbc35`. Ara doğrulanmış yerel sürümler `13376e6322f84e0d9fffb7a48e46bf5b` ve `e949c9e621224584a669fa1f0bf9c407` geçmişte korunur.
- Program `0203-tip-program-v1`, özgün SHA-256 `6aa8a0087e2426e808defbc8e427281f08862b1206fdad2ae847fd294854c7e0`; kabul tarihi bilinmiyor. Giriş ve 32/32 bölüm, 135 ortak konu ve 226 satırla incelendi: 155 ilke/hedef/araç alanı ve 71 somut soruya bağlı yokluk satırı. 204/204 yeni pasaj kaynak metniyle birebir eşleşir. Güncel mücadele önerileri ile sosyalist toplum modeline bağlı hükümler ayrıdır. Önceki demokrasi açılışı yinelenmeden yeniden kullanıldı.
- Program son yerel sürümü `b54b8fe4805741d4bd6b87b5dd81da4c`, rapor `data/releases/b54b8fe4805741d4bd6b87b5dd81da4c/index.html`, görev commit'i `e4da6f3`. Yazılı hedef ve kurallar gerçekleşmiş davranış olarak sunulmaz; kaynak anlamı kararları ajan incelemesidir, insan incelemesi değildir.

## 03-14 geri tarama aktarımı

- TİP programından kaynaklı adaylar: tohum genetik kaynaklarının korunması ve tohum üretim merkezleri; hayvanların eşya yerine canlı olarak tanınması; sosyalist demokrasi modelinde yönetici ve temsilci ücretinin ortalama işçi ücretine bağlanması; eşit işe eşit ücret. TİP tüzüğünde bakım sorumluluğu taşıyan üyelerin katılımını kolaylaştırma ayrıca kaynaklı adaydır. Bunlar yayımlanmış ortak tanımları değiştirmeden paketlerde işaretlendi.
- 03-03'ten devreden zorunlu temel yurttaşlık geliri tanım incelemesi korunur: mevcut ortak tanım geliri olmayanlara odaklanırken Yeni Parti kaynağı her yurttaşı kapsar. TİP'in aynı kanonik satırında incelenen programda düzenli nakit temel gelire ilişkin somut soru için kapsamlı yokluk kaydedilir; programın sosyalist toplumda çalışamayacak durumdakilerin insanca yaşamını güvenceye alan nitel hükmü ayrı ve kendi koşuluyla korunur. Bu farklı kapsamlar 03-14'te bütün partiler için yeniden değerlendirilmelidir.

## Doğrulama ve sınırlar

- Her iki görevde `COMPARISON_INPUT_OK`, `COMPARISON_LOAD_OK`, geçerli current tabanından scratch ve `publish --refresh`; tüzükte `PHASE3_AUDIT_OK d538799da191453abba729858fb28529`, programda `PHASE3_AUDIT_OK b54b8fe4805741d4bd6b87b5dd81da4c` ve son sürümde `PHASE2_AUDIT_OK b54b8fe4805741d4bd6b87b5dd81da4c`. Paket hashleri yükleme ve yayın boyunca değişmedi, yazıcı kilidi görevler arasında bırakıldı.
- Tüzük 459/459 ve program 226/226 satır için iki HTML görünümünün kimlikleri ve karşılıklı bağlantıları doğrulandı; programdaki 226/226 anlam kararı karşılık gelen kanonik incelemeyle eşleşti. Önceki kod dalgasındaki 123 benzersiz test bu veri çalışmasında tekrarlanmadı.
- Renderer 17 kapsamlı yokluk satırında kapsamı doğrudan göstermiyor. Her somut yokluğa kaynak ve alt soruyu belirten ayrı görünür mavi açıklama bağlandı; kapsam ve sürüm kanonik inceleme kaydında saklanır. Satır içi sunum sınırı 03-15/03-16 için sürer; yayımlanmış renderer sürümü değiştirilmedi.
- `actuals.tokens`, başlangıç commit'inden iki görev commit'ine gerçekleşen 45.023.832 karakterlik git farkının dörtte biridir; model tüketimi değildir. Faz genelindeki gereksinimler henüz tamamlanmış sayılmadı, kamuya yayın yapılmadı.

## Sapmalar

Yayınlanmış ara tüzük bulgusundaki af istisnasına atıf fazla kısa kaldığından, değişmez geçmiş korunarak aynı satıra HTML ve PDF'den suç türlerini ve kesin çıkarma koşulunu açıkça belirten kaynaklı alanlar eklendi. Her iki metnin 5.8 maddesi ayrı incelendi; yeni yerel sürüm bütün denetimlerden geçirildi. Uygulama kodu veya yayımlanmış renderer değiştirilmedi.

## Self-Check: PASSED

İki görev commit'i, üç kaynak paketi, son rapor ve üç başarılı faz denetimi dosya ve commit olarak doğrulandı.
