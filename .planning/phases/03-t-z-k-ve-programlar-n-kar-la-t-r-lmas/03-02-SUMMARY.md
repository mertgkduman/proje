---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "02"
subsystem: kaynakli-karsilastirma
tags: [tuzuk, program, kaynak-envanteri, karsilastirma, renderer17]
requires:
  - phase: 03-01
    provides: surumlu karsilastirma semasi ve kaynakli tracer
provides:
  - 1632 bolum kaydi iceren kaynak envanteri ve 301 dayanakli konu
  - Yeni Parti ve TIP icin ilke, hedef ve arac iceren demokrasi karsilastirmasi
  - DEM kaynak alternatifleri, ek belge ve ortak belge eksigi ornekleri
affects: [03-03, 03-04, 03-05, 03-06, 03-07, 03-08, 03-09, 03-10, 03-11, 03-12, 03-13, 03-14, 03-15, 03-16]
actuals:
  tokens: 2130616
  tasks: 2
  commits: 48
plan_head_before: 51ec70e66ea50b50bb2a9e1d4363ff113f9b069d
tech-stack:
  added: []
  patterns: [surumlu-konu-dayanagi, degismez-renderer, kaynakli-envanter]
key-files:
  created:
    - data/comparisons/03-taxonomy.json
    - data/comparisons/03-source-inventory.json
    - data/comparisons/03-program-opening.json
    - data/comparisons/03-exception-cases.json
    - src/rapor_v16.py
    - tests/test_comparison_content.py
  modified:
    - src/arsiv.py
    - src/rapor.py
    - data/current.json
key-decisions:
  - "Tam kaynak envanteri ayrıntılı parti bulgularının tamamlanmasıyla karıştırılmaz; sonraki parti planları araştırılmamış satırları doldurur."
  - "DEM kongre kararı ek belgedir ve bağımsız program açığını kapatmaz; farklı tüzük nüshaları bilinmeyen sıraları uydurulmadan birlikte gösterilir."
  - "Yeni Yol için aynı gerçek belge açığı yeniden kullanılır; aynı SHA değerli Saadet adresleri maddi değişiklik değildir."
  - "Renderer 16 donduruldu; canlı renderer 17'de eşdeğer alanlar kaynakları korunarak birleştirilir ve farklı koşullar ayrı tutulur."
patterns-established:
  - "Taksonomi 2 konu dayanağı atıflı sürüm ve açık kaynak rolü taşır."
  - "Tam aşama, eşleşmemiş bölüm bırakmayan doğrulanmış kaynak envanterini gerektirir."
requirements-completed: []
requirements-addressed: [TUZ-01, TUZ-02, TUZ-03, TUZ-04, PRG-01, KAR-01, KAR-02, RAP-02]
duration: 192min
completed: 2026-11-13
status: complete
---

# Phase 03 Plan 02: Kaynak Envanteri ve Karşılaştırma Özeti

**Tam erişilebilir belgelerin 1.632 bölümlük envanteri, 301 kaynaklı ortak konu ve gerçek program/istisna kayıtları yerel renderer 17 raporunda birleştirildi.**

## Performans ve kapsam

- Başlangıç: yaklaşık 2026-11-13 05:41 UTC; bitiş: yaklaşık 08:53 UTC.
- İki görev tamamlandı; 17 uygulama ve yerel sürüm dosyası değişti. `actuals.tokens` gerçekleşen git farkının karakter sayısı/4 ölçüsüdür; iki büyük üretilmiş HTML/JSON snapshot'ını içerir ve model tüketimi değildir.
- Sekiz erişilebilir tam tüzük, altı tam program, DEM kongre kararları ve DBP'nin tarihî BDP belgeleri ilgili sürüm ve kaynak türleriyle envanterlendi. 1.632 kayıtta eşleşmeyen başlık kalmadı; dört elde olmayan belge gerçek ortak eksik kayıtlarına bağlandı.
- Yeni Parti ve TİP demokrasi/katılım örneklerinde kaynaklı ilke, hedef ve önerilen araç gösterilir. Diğer partilerin ayrıntılı tüzük/program incelemesi bu envanterin kapanmasından bağımsızdır ve sonraki planlara bırakılmıştır.

## Teslimler

- İlk kapalı partial sürüm: `d85d9c64b68d4c9abfa30d142645361d`, commit `0da6c1f`.
- İstisnaları içeren son yerel sürüm: `d370042ecc23499b9abfd6c11af33120`, commit `4e0c58b`; rapor `data/releases/d370042ecc23499b9abfd6c11af33120/index.html`.
- DEM'in il disiplin kuruluna ilişkin iki farklı tüzük hükmü, iki ayrı atıflı sürüm ve eşit alternatif olarak her iki görünümde yer alır. Kongre kararındaki gerçek yurttaşlık geliri içeriği ek belge olarak gösterilir; bağımsız programın bulunamama kaydı ayrı kalır.
- Yeni Yol'un aynı bağımsız program eksikliği birden çok konuya aynı `missing_id` ile bağlandı. Saadet'in aynı SHA değerli iki adresi değişiklik kanıtı sayılmaz. Tarihi bilinmeyen BDP belgeleri tarihsel, DEM kongre kararı tamamlayıcı kaynak olarak işaretlidir.
- TİP'in 2022 PDF'i sayfa görüntüleriyle de incelendi; farklı nüshalar ve metin çıkarım sınırları envanterde korundu. DEM ve Saadet, İYİ Parti, DBP/BDP ve diğer erişilebilir sürümlerin gerçek madde veya bölüm sınırları ayrı tutuldu.
- `src/rapor_v16.py` canlı renderer 17'den önce donduruldu; `src/rapor_v16.css` SHA-256 `bbf86a55a6134df843aa7acd8644b27daf6039e89239700d08e5b3addbd9c389` olarak korundu. Yeni sürümlerin kamuya dağıtımı yapılmadı.

## Doğrulama

- `python3 tests/run.py --pattern test_comparison_content.py`: **17/17** geçti; aynı içerikli alanların bütün kaynaklarıyla birleşmesi, farklı koşulların ayrılması, sahte/eksik kapsam, sürüm ve kaynak rolü olumsuz durumları sınandı.
- `python3 tests/run.py --pattern test_topics.py`: **3/3** geçti; geçmiş konu sözlüğü ve kaynak dayanağı davranışı korundu.
- Üç son paket için `comparison-check`: **COMPARISON_INPUT_OK**. Açılış paketi son doğrulamasından sonra değiştirilmedi; düzeltilen taksonomi ve istisna paketleri tekrar doğrulandı.
- **269/269** yeni pasaj özgün HTML/PDF kaynaklarıyla birebir eşleşti; 1.632 envanter kaydı partial sözleşme kontrolünden geçti. Son HTML, records JSON'dan bayt düzeyinde yeniden üretildi; DEM alternatifleri iki görünümde kontrol edildi.
- `python3 src/arsiv.py audit --release current --phase 3 --stage partial`: **PHASE3_AUDIT_OK d370042ecc23499b9abfd6c11af33120**.
- Önceki dalgada tüm test takımı 1.800 saniyede zaman aşımına uğramıştı; kökün düzelttiği eski renderer beklentisi hedefli olarak geçmiş olsa da kalan tüm-takım regresyon kapsamı bu plan tarafından geçmiş sayılmamıştır.

## Sapmalar ve düzeltmeler

**[Rule 1 - Bug] Kaynak pasajı konumu ve yayın yeniden üretimi.** Türkçe `casefold` dönüşümünün uzunluk değiştirmesi, 13 yeni dayanağın bazılarında yanlış kaynak aralığı seçti; bir hatalı aralıktaki CRLF ilk yayın adayının HTML yeniden üretim denetimini başarısız kıldı. Gerçek başlık pasajları birebir düzeltildi, anlamlı RED/GREEN testi eklendi, başarısız adayın current veya başka sürüme bağlı olmadığı doğrulanıp yalnız o aday temizlendi. Kusur kaydı 5 `fixed` durumundadır. Commitler `c1c1ac2`, `410caec`.

**[Rule 1 - Bug] Envanter sürüm kimliği.** Aynı bölümün başka bir taksonomi sürümünde aynı anahtarı üretmesi, RED/GREEN testiyle giderildi; sürüm envanter kimliğine dahil edildi. Commitler `e6953db`, `655e6ed`.

**[Rule 2 - Correctness] Kaynak, kapsam ve sunum doğrulamaları.** Aynı SHA'dan maddi değişiklik çıkarılması, tek nüshalı alternatifler, kaynaksız konu ve envantersiz complete aşaması reddedildi; tekrarların kanıtları ve farklı koşullar korundu. Her değişiklik kendi RED/GREEN commitleriyle kaydedildi.

## Görev commitleri

- Kaynak ve şema temeli: `82ffdae`, `d4a1008`, `28a74cc`, `9d8e68c`, `d056d62`, `93d002f`, `226d1c9`, `7370525`, `68c6776`, `1f4fd00`, `f911054`, `7d8e2b8`, `9b114b5`.
- Envanter, kaynak sözleşmesi ve görünüm: `e0e7e72`, `2c7aa44`, `b071b22`, `78d7ee5`, `58a6f20`, `db1caed`, `e25f1af`, `e9a39d7`, `091c69f`, `f170121`, `209b361`, `498b2d9`, `4c00067`, `1f7510b`, `d7757cf`.
- Kaynak birleşimi: `b45aaf6`, `d2bb69a`, `edb2c22`, `4e58732`, `7df68c1`, `f6f3e05`, `3d3338b`, `29052d2`, `95083f6`, `bd85509`, `c468fc9`, `ff8ea2f`.
- Tekrar, envanter kimliği ve kaynak düzeltmesi: `4b7efc9`, `a1987e3`, `e6953db`, `655e6ed`, `c1c1ac2`, `410caec`.
- Yerel yayınlar: `0da6c1f`, `4e0c58b`.

## Self-Check: PASSED

Planın sekiz uygulama dosyası ve iki yerel raporu mevcut; her iki yayın commit'i doğrulandı. Plan düzeyinde tamamlanmış gereksinim işaretlenmedi: ilgili faz gereksinimleri sonraki parti incelemeleri ve faz denetimiyle birlikte değerlendirilecektir.

## Dalga sonu ek regresyon düzeltmesi

Gerçek kapalı yayın kabulü, kaynaklı konu sentezinde geçerli CRLF satır sonuyla çalıştırıldı. RED koşusu `HTML kapalı snapshot ile eşleşmiyor` hatasını yeniden üretti (311.633 saniye; `274fb3d`). HTML denetimi metin okumanın satır sonu dönüşümünü kullanmak yerine renderer UTF-8 baytlarını dosya baytlarıyla doğrudan karşılaştıracak şekilde düzeltildi. Yedi karşılaştırma testi son kodla geçti; eski yayınlar ve kaynak baytları değiştirilmedi. Yeni yayın fixture'ı güncel renderer sürümünü bekler; tarihsel renderer15/16 kabulü ayrı testlerde korunur.

03-03 ön bağımlılık kontrolünün sembolik `parti bölümü ↔ karşılaştırma konusu` hedefi kaynak kodda düz metin olarak aranamadığından otomatik sorgu false verdi. Mevcut kapalı rapordaki 38 kanonik comparison row için iki görünümün kimlikleri ve karşılıklı bağlantıları tek tek doğrulandı; gerçek kablolama açığı bulunmadı.
