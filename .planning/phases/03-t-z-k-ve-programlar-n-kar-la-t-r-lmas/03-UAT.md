---
status: testing
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
source: [03-VERIFICATION.md]
started: 2026-11-16T04:49:40.790193+00:00
updated: 2026-11-16T04:49:40.790193+00:00
---

# Faz 03 — İnsan değerlendirmesi

Yerel sürüm `3a3021c8e81749c3834462d1a0d81231`: [raporu açın](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html). Üç kontrol grubu ve üç ayrı değer değerlendirmesi aşağıda altı pending madde olarak izlenir. Ajan kaynak okuması insan kabulü değildir; münferit kaynak kullanımı için ön izin istenmez.

## Current Test

number: 1
name: Tüzük, haklar ve tarihçe
expected: |
  Gereksinimler: TUZ-01, TUZ-02, TUZ-03, TUZ-04, KAR-01. Üyelik hak ve koşullarının, seçim usulünün, merkez/il/ilçe/diğer organların, denetimin, görüş ve disiplin/itiraz güvencelerinin kaynak kapsamıyla tutarlı sunulmasını inceleyin. Örnekler: Yeni Parti Parti Meclisi genel katılım ve özel oy koşulu [Yeni Parti katılım kaydı](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html#comparison-0314-v4-yeni-pm-katilim-row); [Demokrat il/ilçe kongresi hesap komisyonu](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html#comparison-0314-v4-demokrat-kongre-hesap-komisyon-row). Tarihi bilinmeyen sürümler için kesin hukuki sıra veya fiili uygulama varsayılmamalıdır.
awaiting: user response

## Tests

### 1. Tüzük, haklar ve tarihçe
expected: Gereksinimler: TUZ-01, TUZ-02, TUZ-03, TUZ-04, KAR-01. Üyelik hak ve koşullarının, seçim usulünün, merkez/il/ilçe/diğer organların, denetimin, görüş ve disiplin/itiraz güvencelerinin kaynak kapsamıyla tutarlı sunulmasını inceleyin. Örnekler: Yeni Parti Parti Meclisi genel katılım ve özel oy koşulu [Yeni Parti katılım kaydı](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html#comparison-0314-v4-yeni-pm-katilim-row); [Demokrat il/ilçe kongresi hesap komisyonu](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html#comparison-0314-v4-demokrat-kongre-hesap-komisyon-row). Tarihi bilinmeyen sürümler için kesin hukuki sıra veya fiili uygulama varsayılmamalıdır.
result: [pending]

### 2. Program, koşullar ve kaynaklı sentez
expected: Gereksinimler: PRG-01, KAR-02. Konu birleşimini, az partili konuları, ilke/hedef/araç ve koşul ayrımını, bütün kanıtların ve kaynaklı sentezin korunmasını inceleyin. Örnekler: Demokrat iklim ve koşullu ithalat aracı [Demokrat iklim kaydı](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html#comparison-04-03-v3-0313-demokrat-doga-ekoloji); EMEP eğitim önerisi [eğitim kaydı](../../../data/releases/3a3021c8e81749c3834462d1a0d81231/index.html#comparison-04-0314-emep-education-access-correct-page-row). DEM/DBP/Yeni Yol tam program açığı, ek veya tarihsel belge içeriğiyle kapatılmış sayılmamalıdır.
result: [pending]

### 3. Rapor, kaynak yolu ve ortak değerler
expected: Gereksinim: RAP-02. Karşılaştırma ve parti dosyası arasında iki yönde gidin; bir kaynağı ve yerel arşivini açın. Dokuz partinin sabit sırasını, yönlendirme yapılmamasını, eksiklik ve güncellik sınırlarını, ayrı tüzel kimlikleri kontrol edin. Yeni Parti tüzüğünün gerçek yerel arşivi: [Yeni Parti tüzüğü](../../../data/views/5ad0d30f04d349ca9c6e55a913f9d4b1/index.html).
result: [pending]

### 4. Değer 1 — Puanlama ve siyasi yönlendirme
expected: Kapsam ve sabit parti sırası siyasi destek veya başarı sıralaması olarak sunulmaz; puanlama, oy yönlendirmesi veya araştırmacı tercihi üretilmez.
result: [pending]

### 5. Değer 2 — Eksiklik ve belirsizlik
expected: Belge açığı, dar ifade yokluğu ve bilinmeyen sürüm sırası; karşıt tutuma, olumsuz performansa veya hukuki güncellik güvencesine dönüşmez.
result: [pending]

### 6. Değer 3 — Mekanizma, belge türü ve tüzel kimlik
expected: Yazılı mekanizma gerçekleşmiş uygulama; ek/tarihsel metin bağımsız güncel program; ayrı tüzel partinin belgesi başka partiye ait sayılmaz. EMEP önerisi, DEM eki, tarihsel BDP ve Yeni Yol açığı bu sınırlarla okunur.
result: [pending]

## Summary

total: 6
passed: 0
issues: 0
pending: 6
skipped: 0
blocked: 0

## Gaps

Henüz kullanıcı sonucu alınmadı. Otomatik testler teknik kabul kanıtıdır; altı insan değerlendirmesinin sonucu yerine geçmez.

## Ham tanılar ve kapsam sınırı

Sekiz ham gereksinim kaydı `data/comparisons/03-probe-record.json` içinde `unclassified`, `unresolved`, verification/resolution/reason null olarak korunur. Üç descriptor-less prohibition kaydı da unresolved kalır. Normal UAT kabulü bu ham kayıtları otomatik yeniden sınıflandırmaz veya eksik descriptor alanını doldurmuş sayılmaz. Yukarıdaki son üç madde proje ilkelerine dayalı insan değer değerlendirmesidir; yapılmış bir teknik doğrulama veya uydurulmuş insan kabulü değildir.

Bağımsız doğrulama: teknik 14/14; toplam 14/17 (üç prohibition uncertain). Faz, altı gerçek insan yanıtı olmadan kapatılmaz.
