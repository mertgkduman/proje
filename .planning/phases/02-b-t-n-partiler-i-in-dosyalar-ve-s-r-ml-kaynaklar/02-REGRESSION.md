# Faz 02 regresyon kapısı

**Sonuç: geçti; tek başarısız test düzeltilip yeniden çalıştırıldı.**

Tam koşu 91 testte 90 başarılı ve 1 başarısız sonuç verdi (1583.953 sn, 1800 sn sınırı içinde). Hata, TİP entegrasyon testinin yeni rapor üreticisinden hâlâ sabit 13 beklemesiydi. 8b85586 ile beklenti etkin sürüme bağlandı; eski 13 için ayrı bayt eşitliği testi korundu. İlgili gerçek yayın/audit/makbuz entegrasyon testi tekrar çalıştırıldı ve 1/1 geçti (13.225 sn).

İkinci turda değişen arşiv/rapor yolları 25/25, kaynak-atıf yolu iki ilgili testte 2/2 geçti. Başarılı süitler gereksiz yere tekrar çalıştırılmadı. Tam paketin tek seferde bütünüyle yeşil çalıştığı iddia edilmez.

İlk koşunun gerçek hata dökümü [02-REGRESSION.log](02-REGRESSION.log), komut/sonuç geçmişi [02-REGRESSION.json](02-REGRESSION.json) ve düzeltmeler [02-REVIEW-FIX.md](02-REVIEW-FIX.md) içindedir. Testler, kaynakların siyasi içeriğine insan kabulü değildir.

Son SC3 yöntem açıklaması için üretici14 bayt olarak donduruldu; üretici15 kapalı yöntem paragrafını güncelledi (c2415da). Tarihsel13/14 eşitliğini kapsayan iki odaklı test geçti. Resmî publish --refresh yeni ac4b8fdec02f4a9ebb666036ed251683 sürümünde faz1, tam dokuz dosya ve audit_release kontrollerini işaretçi değişiminden önce başarıyla uyguladı. Kayıtların release_id dışındaki tam eşitliği ve değişmeyen teslim künyesi doğrulandı; yalnız metin açıklaması için ayrıca tam süit veya sekiz makbuz yeniden çalıştırılmadı.
