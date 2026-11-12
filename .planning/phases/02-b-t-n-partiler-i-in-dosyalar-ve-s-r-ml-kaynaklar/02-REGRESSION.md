# Faz 02 regresyon kapısı

**Sonuç: geçti; tek başarısız test düzeltilip yeniden çalıştırıldı.**

Tam koşu 91 testte 90 başarılı ve 1 başarısız sonuç verdi (1583.953 sn, 1800 sn sınırı içinde). Hata, TİP entegrasyon testinin yeni rapor üreticisinden hâlâ sabit 13 beklemesiydi. 8b85586 ile beklenti etkin sürüme bağlandı; eski 13 için ayrı bayt eşitliği testi korundu. İlgili gerçek yayın/audit/makbuz entegrasyon testi tekrar çalıştırıldı ve 1/1 geçti (13.225 sn).

İkinci turda değişen arşiv/rapor yolları 25/25, kaynak-atıf yolu iki ilgili testte 2/2 geçti. Başarılı süitler gereksiz yere tekrar çalıştırılmadı. Tam paketin tek seferde bütünüyle yeşil çalıştığı iddia edilmez.

İlk koşunun gerçek hata dökümü [02-REGRESSION.log](02-REGRESSION.log), komut/sonuç geçmişi [02-REGRESSION.json](02-REGRESSION.json) ve düzeltmeler [02-REVIEW-FIX.md](02-REVIEW-FIX.md) içindedir. Testler, kaynakların siyasi içeriğine insan kabulü değildir.
