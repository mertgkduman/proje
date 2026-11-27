---
phase: 05-finansman-ve-harcamalar-n-belgelenmesi
verified: 2026-11-27
status: passed
score: 3/3
verified_against: d42dff690de26fefd1af3aa05ba19b24157e7c92
release_id: c426b97652d1447d97041685f1261e2b
---

# Faz 5 ilk teslim doğrulaması

| Gereksinim | Sonuç | Dayanak |
|---|---|---|
| MAL-01 | Geçti | Yedi kesin hesapta kaynaklı gelir ve kapsam kayıtları. Dokuz partinin 27 hedef dönemi ve dört ek eski dönem. |
| MAL-02 | Geçti | Karar pasajına bağlanan harcama kalemleri, bölüm toplamları ve gerekçeli eksikler. |
| MAL-03 | Geçti | 264 kayıt için ayrı hesap dönemi, TRY, örgüt kapsamı, yayım tarihi ve pasaj. 19 eksik kayıt tutardan ayrı. |

Sekiz özgün AYM yanıtının SHA-256 özeti ve karar kimliği eşleşti. SQLite hızlı bütünlük ve dış anahtar kontrolleri geçti. Önceki sürümdeki 14.754 karşılaştırma satırı, 428 uygulama ilişkisi ve 255 söylem kaydı SQLite tabanıyla karşılaştırıldı. Altı mali kayıt testi geçti.

Canlı mali sayfada dokuz parti, 264 tutar, sekiz resmî karar bağlantısı ve klavyeyle açılan pasajlar Chromium’da 360 pikselde doğrulandı. Birleşik sürümde sekmeler ve odak, siyah alıntı ile koyu mavi özet, mali kayıttan pasif kaynak görünümüne bağlantı aynı genişlikte denetlendi.

GitHub Release farkı indirildi ve SHA-256 özeti eşleşti. Faz 4 tabanından geri yüklenen üç çıktı sürüm manifestiyle eşleşti. Geri yüklenen SQLite, 264 tutar kaydıyla açıldı.

[Veri ve tarayıcı makbuzu](05-01-checks/finance-review.json) · [Faz 5 teslimi](05-01-SUMMARY.md)
