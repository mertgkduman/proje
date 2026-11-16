---
quick_id: 261116-mgh
status: passed
review_scope: incremental_source_and_test_changes
review_mode: inline
---

# Artımlı kaynak incelemesi

Kullanıcının açık talebiyle altı kabul kontrolü kapatıldı; ayrı tekil kullanıcı yanıtları veya yeni kaynak anlamı incelemesi uydurulmadı. Kabulün kaynak raporu `3a3021c8e81749c3834462d1a0d81231` olarak kaydedildi. Kamusal açıklamalar ajan özeti, örnekler mevcut kaynak bulguları olarak ayrı köken alanlarıyla korunur.

- **Rapor:** Yeni sekme yalnız gerçek insan kabul kaydından üretilir. Ajan kararı kullanıcı kabulüne dönüşmez. Açıklama/etiket/alıntı kaçışı, koşul ve kaynak bağları korunur. Örnekler mevcut hedeflere bağlanır; satır kimliklerini çoğaltmaz. Beş yeni ve on bir mevcut rapor testi geçti.
- **Tarihsel sürümler:** Renderer23 ve stili donduruldu; eski kapalı HTML bire bir yeniden üretildi. Yeni rendererversion dispatch'i eski sürümleri tanır.
- **SQLite:** Değişmez kip yalnız manifesti bulunan kapalı release yolundadır. Workspace, staging ve manifesti olmayan aday aynı bağlantıda yeni commit'i görür. Gerçek snapshot'ın olağan salt okunur sorgularıyla sonuçlar eşit, özgün hash aynı. Üç okuyucu ve iki tarihsel denetim testi geçti.
- **Yayın sözleşmesi:** On bir yayın testi; hata enjeksiyonları, eski taban, ikinci yazıcı, FK ve kaynak/manifest bozulması, yol/URL güvenliği ve işaretçi öncesi kabul kontrolleriyle geçti. Fixture'a canlı kilit/aday kopyalanması düzeltildi; sınamalar kaldırılmadı.
- **Kamu paketi:** Kod yalnız raporun bağlı dosyalarını ve yerel arşiv varlıklarını mevcut gh-pages ağacına ekler; var olan arşiv dosyalarının hash farkında durur. Kaynak/veri üretimi standart archive API'sindedir; native audit kapıları atlanmaz.

Toplam 32 test ve 360/1365 px gerçek Chromium kontrolleri başarılıdır. İnceleme mevcut ajan tarafından yapıldı; bağımsız alt ajan incelemesi iddia edilmez. Gerçek yeni sürüm ve başarılı canlı dağıtımın kabul kanıtları `publication.json`, `pages-bundle.json`, `deployment.json`, `live-checks.json` ve `browser-live.json` içindedir. Canlı 14 dosyanın baytları yerel paketle eşleşti.
