---
status: testing
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
source: [01-VERIFICATION.md]
started: 2026-11-10T17:51:15.896090+00:00
updated: 2026-11-10T17:51:15.896090+00:00
---

## Current Test

number: 1
name: H1 — Kapsam, hukuki kimlik ve dönem: arşivli TBMM/Yargıtay kopyalarını karşılaştır.
expected: |
  Dokuz ad ve yedi kapsam dışlama kararı doğru kökenle gösterilir; parti/üyelik/grup ayrımı korunur. Yeni Parti kuruluşu ve TİP yargitay-208 ile tarihsel TBMM tanımlayıcısının bağlantısı kaynak anlamıyla doğrulanır; kesim ve tarih belirsizlikleri doğru yorumlanır.
awaiting: user response

## Tests

### 1. H1 — Kapsam, hukuki kimlik ve dönem: arşivli TBMM/Yargıtay kopyalarını karşılaştır.
expected: Dokuz ad ve yedi kapsam dışlama kararı doğru kökenle gösterilir; parti/üyelik/grup ayrımı korunur. Yeni Parti kuruluşu ve TİP yargitay-208 ile tarihsel TBMM tanımlayıcısının bağlantısı kaynak anlamıyla doğrulanır; kesim ve tarih belirsizlikleri doğru yorumlanır.
result: [pending]

İnsan incelemesi gerekçesi: FK, adres, anahtar ve metin eşleşmesi hukuki kimlik veya tarih alanının anlamını tek başına ispatlamaz. Yalnız ilk 01-01 tracer onaylanmıştır.

### 2. H2 — Bütün önemli bulguları, tüzük/program yetki sınırını, eşleşmeleri ve mali araştırmayı özgün pasajlarıyla oku.
expected: 21 bulgunun özet/alıntısı kaynağa sadıktır; 18 eşleşmenin aktörü, bağlamı ve ayrı oluş dayanağı uygundur. TİP taranmış PDF sıra 5 sayfası ve organ seçimi dayanağı doğru okunmuştur. Yeni Parti tüzük/program yetkisi ve mali tutarlar doğrulanmış gibi sunulmaz.
result: [pending]

İnsan incelemesi gerekçesi: 22 review kaydı agent türündedir; insan kaynak incelemesi değildir. Taranmış PDF pasajı için otomatik metin doğrulaması yoktur.

### 3. H3 — Yerel HTML akışını klavye, gerçek dar/mobil görünüm, yakınlaştırma ve çevrimdışı arşivle tamamla.
expected: On sekme/panel erişilebilir; kaynak ve girişim bağlantısı doğru kapalı bölümü açar; geri/odak tutarlıdır. Siyah tırnaklı alıntı ve koyu mavi özet birlikte okunur; içerik kaybı ve görünür üretim türü etiketi yoktur.
result: [pending]

İnsan incelemesi gerekçesi: Tam sekme/geri/odak testi bu turda çalıştırılmadı. Masaüstü pencere görüntüleri gerçek mobil veya insan erişilebilirlik kanıtı değildir; tek kaynak tıklaması bu akışın tamamını kanıtlamaz.

### 4. H4 — Kapsamın siyasi sıralama veya destek sonucuna dönüşmediği yasağını tek tek karara bağla.
expected: Kapsam/pilot seçimi yöntem ve kullanıcı kararı olarak kalır; partiler hakkında başarı, başarısızlık veya oy yönlendirmesi sonucu üretilmez.
result: [pending]

İnsan incelemesi gerekçesi: 01-06 PLAN prohibition maddesi unresolved ve verification alanı yok; bağlamsal tarafsızlık için insan kararı gerekir.

### 5. H5 — Sonucun yönüne göre uygun eşleşme gizlenmediği yasağını karara bağla.
expected: İlan edilen aramalar, 26 aday ve kaynak uçları incelendiğinde uygun hiçbir eşleşme sonuç yönünden dolayı çıkarılmamıştır; 18 kayıt bağımsız olay toplamı sayılmaz.
result: [pending]

İnsan incelemesi gerekçesi: DB/JSON/HTML küme eşitliği yalnız kayda geçirilmiş uygun adayları korur; keşif ve uygunluk kararlarının tarafsızlığını kanıtlamaz. Prohibition unresolved kalır.

### 6. H6 — Kaynak dışı olgu eklenmediği ve beyanın gerçekleşmiş olguya dönüştürülmediği yasağını karara bağla.
expected: Özetler ve yorumlar kaynak sınırındadır; haberin veya partinin beyanı ve bağımsız olay doğrulaması ayırt edilir.
result: [pending]

İnsan incelemesi gerekçesi: Ayrı passage_id, source_kind ve epistemic_type alanları içerik anlamı için bağımsız bir oracle değildir. Prohibition unresolved kalır.

### 7. H7 — Eksik/araştırılmamış bilginin sıfır veya siyasi sonuca dönüşmediği yasağını karara bağla.
expected: Üç eksik durumu girişimin kapsamıyla sınırlıdır; Henüz incelenmedi ayrıdır; doğrulanmış mali satır yokluğu gelir/gider yokluğu veya parti lehine/aleyhine sonuç değildir.
result: [pending]

İnsan incelemesi gerekçesi: NULL/0 testi ve girişim FK'ları kayıt davranışını ispatlar; bütün anlatının okuyucuda ürettiği anlamı karara bağlamaz. Prohibition unresolved kalır.

### 8. H8 — COVERAGE.md içindeki 13 unclassified/unresolved uç satırını ayrı ayrı incele.
expected: KAPS-01–04, KAY-02–03, MET-01–04, EKS-01–02 ve VER-01 için varsayım ya açık gerekçeyle çözülür ya da açık bırakılır; normal test başarısı otomatik çözüm sayılmaz.
result: [pending]

İnsan incelemesi gerekçesi: Motor her satırda verification/resolution/reason=null ve unclassified — review manually üretmiştir; bu rapor yeni sınıflandırma veya insan onayı uydurmaz.

## Summary

total: 8
passed: 0
issues: 0
pending: 8
skipped: 0
blocked: 0

## Gaps

Henüz UAT sonucu yoktur. Bu dosya teknik boşluk iddiası veya insan onayı değildir.

## İnceleme çıktısı

Yerel rapor: `data/releases/7b69e39259214749b36bd655e60c7e66/index.html`.
İlk 01-01 tracer için önceki kullanıcı onayı korunur; buradaki sekiz kontrolün yerine geçmez.
