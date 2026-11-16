---
status: complete
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
source: [03-VERIFICATION.md]
started: 2026-11-16T04:49:40.790193+00:00
updated: 2026-11-16T21:12:18.364185+00:00
---

# Faz 03 — İnsan değerlendirmesi

Yerel sürüm `3a3021c8e81749c3834462d1a0d81231`: [raporu açın](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html). Üç kontrol grubu ve üç ayrı değer değerlendirmesi aşağıda altı madde olarak izlenir. Ajan kaynak okuması insan kabulü değildir; münferit kaynak kullanımı için ön izin istenmez.

## Current Test

[testing complete]

## Tests

### 1. Tüzük, haklar ve tarihçe
expected: Gereksinimler: TUZ-01, TUZ-02, TUZ-03, TUZ-04, KAR-01. Üyelik hak ve koşullarının, seçim usulünün, merkez/il/ilçe/diğer organların, denetimin, görüş ve disiplin/itiraz güvencelerinin kaynak kapsamıyla tutarlı sunulmasını inceleyin. Örnekler: Yeni Parti Parti Meclisi genel katılım ve özel oy koşulu [Yeni Parti katılım kaydı](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html#comparison-0314-v4-yeni-pm-katilim-row); [Demokrat il/ilçe kongresi hesap komisyonu](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html#comparison-0314-v4-demokrat-kongre-hesap-komisyon-row). Tarihi bilinmeyen sürümler için kesin hukuki sıra veya fiili uygulama varsayılmamalıdır.
result: pass
acceptance_note: Kullanıcı, geliştirme talimatlarının kullanıcı arayüzüne aktarılmaması koşuluyla bu kontrolü kabul etti. Bu talimatlar iç kayıtlarda tutulur.
user_response: 'Bu tür "developer" mesajlarımı lullanıcı arayüzünr yansıtmafığın sürece sorun yok'

### 2. Program, koşullar ve kaynaklı sentez
expected: Gereksinimler: PRG-01, KAR-02. Konu birleşimini, az partili konuları, ilke/hedef/araç ve koşul ayrımını, bütün kanıtların ve kaynaklı sentezin korunmasını inceleyin. Örnekler: Demokrat iklim ve koşullu ithalat aracı [Demokrat iklim kaydı](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html#comparison-04-03-v3-0313-demokrat-doga-ekoloji); EMEP eğitim önerisi [eğitim kaydı](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html#comparison-04-0314-emep-education-access-correct-page-row). DEM/DBP/Yeni Yol tam program açığı, ek veya tarihsel belge içeriğiyle kapatılmış sayılmamalıdır.
result: pass
acceptance_note: Kullanıcının 2026-11-16 tarihli açık toplu kabulüyle geçti; ayrı ayrı test yanıtı veya otomatik kaynak doğrulaması iddia edilmez.

### 3. Rapor, kaynak yolu ve ortak değerler
expected: Gereksinim: RAP-02. Karşılaştırma ve parti dosyası arasında iki yönde gidin; bir kaynağı ve yerel arşivini açın. Dokuz partinin sabit sırasını, yönlendirme yapılmamasını, eksiklik ve güncellik sınırlarını, ayrı tüzel kimlikleri kontrol edin. Yeni Parti tüzüğünün gerçek yerel arşivi: [Yeni Parti tüzüğü](../../../data/views/5ad0d30f04d349ca9c6e55a913f9d4b1/index.html).
result: pass
acceptance_note: Kullanıcının 2026-11-16 tarihli açık toplu kabulüyle geçti; ayrı ayrı test yanıtı veya otomatik kaynak doğrulaması iddia edilmez.

### 4. Değer 1 — Puanlama ve siyasi yönlendirme
expected: Kapsam ve sabit parti sırası siyasi destek veya başarı sıralaması olarak sunulmaz; puanlama, oy yönlendirmesi veya araştırmacı tercihi üretilmez.
result: pass
acceptance_note: Kullanıcının 2026-11-16 tarihli açık toplu kabulüyle geçti; ayrı ayrı test yanıtı veya otomatik kaynak doğrulaması iddia edilmez.

### 5. Değer 2 — Eksiklik ve belirsizlik
expected: Belge açığı, dar ifade yokluğu ve bilinmeyen sürüm sırası; karşıt tutuma, olumsuz performansa veya hukuki güncellik güvencesine dönüşmez.
result: pass
acceptance_note: Kullanıcının 2026-11-16 tarihli açık toplu kabulüyle geçti; ayrı ayrı test yanıtı veya otomatik kaynak doğrulaması iddia edilmez.

### 6. Değer 3 — Mekanizma, belge türü ve tüzel kimlik
expected: Yazılı mekanizma gerçekleşmiş uygulama; ek/tarihsel metin bağımsız güncel program; ayrı tüzel partinin belgesi başka partiye ait sayılmaz. EMEP önerisi, DEM eki, tarihsel BDP ve Yeni Yol açığı bu sınırlarla okunur.
result: pass
acceptance_note: Kullanıcının 2026-11-16 tarihli açık toplu kabulüyle geçti; ayrı ayrı test yanıtı veya otomatik kaynak doğrulaması iddia edilmez.

## Summary

total: 6
passed: 6
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

Şu ana kadar kullanıcı tarafından sorun bildirilmedi. Otomatik testler teknik kabul kanıtıdır; insan değerlendirmelerinin sonucu yerine geçmez.

## Ham tanılar ve kapsam sınırı

Sekiz ham gereksinim kaydı `data/comparisons/03-probe-record.json` içinde `unclassified`, `unresolved`, verification/resolution/reason null olarak korunur. Üç descriptor-less prohibition kaydı da unresolved kalır. Normal UAT kabulü bu ham kayıtları otomatik yeniden sınıflandırmaz veya eksik descriptor alanını doldurmuş sayılmaz. Yukarıdaki son üç madde proje ilkelerine dayalı insan değer değerlendirmesidir; yapılmış bir teknik doğrulama veya uydurulmuş insan kabulü değildir.

Bağımsız teknik doğrulamanın özgün sonucu 14/14; descriptor-less ham kayıtların özgün toplamı 14/17 olarak korunur. Altı insan değerlendirmesi kullanıcı tarafından 2026-11-16 tarihinde açıkça kabul edildi; tek tek yanıt alınmış gibi gösterilmez.

## Kullanıcı kabul kaydı — 2026-11-16

İlk kontrol arayüze geliştirme talimatı taşınmaması tercihiyle kabul edildi. Kalan beş kontrol, kullanıcının şu açık toplu kabulüyle geçti olarak kaydedildi:

> hepsi gecti olsun, github'a push edelim ki yayinlansin. Bu verify edilen maddeler ornekleriyle yeni bir sekmede olsun, 3. faz verify maddelerini orneklerle gorebilelim.

Kabul, incelenen `3a3021c8e81749c3834462d1a0d81231` raporuna aittir. Örnekli yeni sekme ve kamu yayını quick task `261116-mgh` kapsamında ayrıca uygulanır ve teknik olarak kontrol edilir. Ham probe ve descriptor kayıtları yeniden sınıflandırılmaz.
