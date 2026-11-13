---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "03"
subsystem: kaynakli-karsilastirma
tags: [yeni-parti, tuzuk, program, semantik-inceleme, renderer17]
requires:
  - phase: 03-02
    provides: 301 kaynaklı ortak konu, tam kaynak envanteri ve program açılışı
provides:
  - Yeni Parti tüzüğünün kaynaklı parti içi işleyiş karşılaştırması
  - Yeni Parti programının ortak konulara bağlı kaynaklı karşılaştırması ve kapsamlı eksiklik kayıtları
affects: [03-14, 03-15, 03-16]
actuals:
  tokens: 4021625
  tasks: 2
  commits: 2
plan_head_before: 2ad828b6d095bf4f64050e9f4d21f85eefab5898
tech-stack:
  added: []
  patterns: [degismez-yerel-yayin, ajanin-kaynakla-anlam-karsilastirmasi, surumlu-inceleme-kapsami]
key-files:
  created:
    - data/comparisons/03-yeni-parti-charter.json
    - data/comparisons/03-yeni-parti-program.json
  modified:
    - data/comparisons/03-yeni-parti-semantic.json
    - data/current.json
key-decisions:
  - "Tüzüğün çelişen gençlik kotası ifadeleri ve geçiş hükümleri kaynak atfıyla birlikte korunur; yürürlük veya gerçek uygulama hakkında hüküm verilmez."
  - "Programın her vatandaş için temel vatandaşlık geliri ifadesi daraltılmaz; ortak konu tanımındaki kapsam farkı 03-14 geri tarama sorunudur."
  - "Kapsamlı yokluk yalnız incelenen program sürümü ve belirtilen alt soru için kaydedilir; sayısal ayrıntının yokluğu nitel bir aracın yokluğu sayılmaz."
requirements-completed: []
requirements-addressed: [TUZ-01, TUZ-02, TUZ-03, TUZ-04, PRG-01, KAR-01, KAR-02, RAP-02]
duration: yaklaşık 144min
completed: 2026-11-13
status: complete
---

# Phase 03 Plan 03: Yeni Parti Tüzük ve Program Karşılaştırması Özeti

**Yeni Parti'nin tam tüzüğü ve programı, ortak konulara bağlı kaynaklı bulgular, ajan semantik incelemeleri ve sınırlandırılmış eksiklik kayıtlarıyla iki değişmez yerel rapora işlendi.**

## Teslimler ve kapsam

- Tüzük: `epm-charter-v1`, kullanıcının kabul ettiği `https://yenipartiyiz.biz/parti-tuzugu`, özgün SHA-256 `b3709f52e07f6d65797d021f571c2b97eca5ac02771a633fe55aafec4130518e`. Üyelik, haklar, seçimler, denetim, görüş, disiplin ve itiraz; merkez, il, ilçe ve düzenlenen diğer organlar için kaynak, yetki ve düzeyleriyle ele alındı. Üye veya ön seçim oyları ile son kurultay seçimi ayrıldı. Paket 335 karşılaştırma satırı ve 324 özgün pasaj içerir.
- Tüzük yerel sürümü `aa5d545f8358406dbe448ef82995ac78`; rapor `data/releases/aa5d545f8358406dbe448ef82995ac78/index.html`; görev commit'i `4368464`.
- Program: `epm-program-v1`, `https://yenipartiyiz.biz/parti-programi`, özgün SHA-256 `58fa220ab814bd82a4c8d0d233bf55ab268eb9f856750cd88abc544e17ceba1b`. Programın ortak ana ve alt konuları, önceden eklenmiş demokrasi açılışı yinelenmeden incelendi. Yeni paket 124 kaynaklı ve 32 sınırlandırılmış açık ifade bulunamadı satırı, 129 ilke/hedef/araç alanı ve 269 özgün pasaj içerir. Tarım, adil enerji dönüşümü, çalışma, sosyal güvenlik, sağlık, eğitim, yargı, ifade ve toplumsal cinsiyet araçlarının ilgili destekleyici pasajları bir arada korunur.
- Program yerel sürümü `4c9b19b8d0c347d6b5b643cc624fa58c`; rapor `data/releases/4c9b19b8d0c347d6b5b643cc624fa58c/index.html`; görev commit'i `271806c`. Pasif program arşivi `data/views/bb13963f4a7945c12f748e1c4f1e1aba/index.html` içindedir.
- `03-yeni-parti-semantic.json` ve paketlerdeki `comparison_semantic_review` kayıtları, özetlerin kaynak anlamı, koşulu ve kapsamına ilişkin ajan kararlarını taşır; insan incelemesi iddia edilmez. Yazılı hedef ve kurallar fiilî uygulama olarak sunulmaz.
- Net sıfır yol haritası, platform çalışanlarının hakları ve enerji yoksulluğu/sosyal tarife, kaynak pasajlarıyla 03-14 ortak geri tarama adayı olarak program paketinde kayıtlıdır. Aynı yerde mevcut `temel-yurttaslik-geliri` tanımının geliri olmayanlara odaklanması ile programın her vatandaşı kapsaması arasındaki fark, tüm parti kayıtlarıyla birlikte 03-14 incelemesine bırakıldı.

## Kaynak koşulları ve açık sınırlar

- Tüzük Madde 36 gençlik kotasında “yüzde yirmi (%25)” biçimindeki tutarsızlığı ve alt kırılımı olduğu gibi içerir. Kadın kotasına ilişkin %33, %35, %40, %45 ve %50 geçiş ifadeleri ve ilk kongre öncesi geçici hükümler koşullarıyla korunur; bunların güncel hukuki etkisi karara bağlanmaz. İmzalı PDF'nin uyuşmazlıkta önceliğine ilişkin kaynak notu, kullanılan HTML sürümünün sınırıdır; yeni bir kabul veya alan adı kanıtı koşulu değildir.
- Kürt sorununa ilişkin çözüm ifadesindeki terörün sona ermesi koşulu, ana dili öğrenme/kullanma hakkı ile ana dilde eğitim arasındaki ayrım ve göçte güvenli, onurlu ve gönüllü dönüş koşulu korunur. Sayısal tutar veya takvim verilmemesi tek başına nitel aracın yokluğu değildir.
- Renderer 17, `no_explicit_statement` satırlarının kayıtlı ayrıntılı araştırma kapsamını ve doğrudan kaynak bağlantısını görünür metinde göstermiyor. İlgili sürüm, alt soru ve gerekçe kanonik `comparison_review_scope` ile bağlıdır; bu sunum sınırı sonraki navigasyon/kabul incelemesine açıktır. Kaynağa dayanmayan alıntı oluşturulmadı.
- Plan tamamlanması Faz 3 gereksinimlerinin tamamlandığı anlamına gelmez; başka partiler, geri tarama ve faz kabulü sonraki planlardadır. Kamuya dağıtım yapılmadı.

## Doğrulama

- Tüzük ve programın son `comparison-check` çalıştırmaları **COMPARISON_INPUT_OK**; her görev geçerli current tabanından scratch yüklenip `publish --refresh` ile yayımlandı. Program paketi `COMPARISON_LOAD_OK`; son paket ve semantik dosyanın SHA-256 değerleri denetim sonrasında değişmedi.
- Her iki yerel sürüm için **PHASE3_AUDIT_OK**; son sürüm için ayrıca **PHASE2_AUDIT_OK** alındı. Son manifestin Faz 2 completed_prefix, party ve stage nesnesi önceki sürümle eşittir; eski teslim zinciri korunur.
- Programın 156/156 satırında iki görünümün kimlikleri ve karşılıklı bağlantıları, 269/269 pasajın kaynak kimliği ve pasif arşiv bağlantısı kontrol edildi. Programın 161 alan/kapsam semantik kararı iki dosyada eşleşir. Tüzüğün 335 satırı ve 324 pasajı da iki görünüm ve özgün metinle kontrol edildi.
- Önceki dalgada son kod/veri üzerinde geçen 123 benzersiz test yeniden çalıştırılmadı; bu veri odaklı planda paket ve yayın denetimleri kullanıldı.
- `actuals.tokens`, iki görev commit'i arasındaki gerçekleşen 16.086.502 karakterlik git farkının dörtte biridir; model tüketimi değildir. Commit sayısı kaydedilmiş plan başlangıcından SUMMARY öncesi ölçülmüştür.

## Sapmalar

Plan kapsamında mimari veya kod değişikliği yapılmadı. Renderer 17 kapsam görünürlüğü sınırı yukarıda açıklandı; mevcut sürüm değiştirilmedi.

## Self-Check: PASSED

İki paket, semantik kayıt, iki yerel rapor ve iki görev commit'i SUMMARY yazılmadan önce doğrulandı.
