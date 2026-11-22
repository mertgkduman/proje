# Özgün parti duyuruları

Partinin sayfaları tarayıcı kabuğu döndürdüğünde, sitede yayımlanan istemcinin kullandığı açık haber adresleri erişildi. `237`, `255`, `274` ve `295` için özgün `application/json` yanıtları HTTP 200 ile alındı. Ham baytlar ve pasif okunabilir kopyalar ayrı dosyalardır. `ab-party-publications.json` gerçek erişim zamanını, kaynak ve görünen sayfa adreslerini, ham zaman alanlarını ve SHA-256 değerlerini taşır. Sürüm ve atıf tarihleri gün kesinliğindedir. Duyurulardaki olay anlatımları partinin açıklamaları olarak kullanılır.

- **21 Ekim 237.** Parti, Özgür Özel ile Aivo Orav ve heyetinin görüşmesini ve eşlik edenleri duyurdu. Aynı görüşme için ayrı ANKA haberi mevcut olay kaydına bağlıdır. [Parti duyurusu](https://yeni-parti.org.tr/haber/237)
- **28 Ekim 255.** Zeynel Emre, AB’nin göç yaklaşımına dair parti görüşünü açıkladı. Kaynak bağlamı göç ve AB ilişkileri söylemidir. [Parti duyurusu](https://yeni-parti.org.tr/haber/255)
- **2 Kasım 274.** Parti sözcüsünün Made in Europe, lojistik ve nakliye yaklaşımı aktarıldı. Bir önceki değerlendirmeye atfın tarih ve içerik izi ayrı araştırılır. [Parti duyurusu](https://yeni-parti.org.tr/haber/274)
- **9 Kasım 295.** Parti sözcüsünün bir dönem için 150 Parti Meclisi üyesi ve 30 yedek açıklaması ile AB Gümrük Birliği ve TIR sürücülerine yönelik önerisi iki ayrı pasajdır. İkisi mevcut `0404-charter-announcement-api-v1` belge sürümüne bağlandı. Kurumsal pasaj `0404-charter-announcement-api-p` kimliğini koruyor. İki yeni AB pasajı aynı SHA-256 değerindeki özgün JSON ile eşleşiyor. [Parti duyurusu](https://yeni-parti.org.tr/haber/295)

Özgün JSON ve ilgili pasajların eşitliği kontrol edildi. Pasif yerel okunabilir kopyalar hazır. Tam paket girdi ve önizleme denetimi bekliyor.
