---
status: resolved
trigger: "Standart yerel yayın komutu Yeni Parti'nin önceki fazdan gelen uygulama kanıtlarında parti dosyası denetimini geçemiyor."
created: 2026-11-27
updated: 2026-11-27
---

## Current Focus

hypothesis: Faz 2 dosya denetimi Faz 4 başlığına ait atıflı kanıt bağlarını tanımıyor.
test: Faz 4 tabanı ve Faz 5 çalışma verisinde kaynak sahibi, atıf ve bulgu incelemesini karşılaştır. Aynı sürüm zincirinde standart yayını tekrar çalıştır.
expecting: Yalnız doğrulanmış uygulama bağları kabul edilir. Dosya başlıklarındaki mevcut kaynak denetimleri sürer.

## Evidence

- İki SQLite kopyasında Yeni Parti'nin aynı 763 kanıt bağlantısında Faz 2 dosya satırı eksik. Bunlar 215 ayrı belge sürümüne ait.
- 763 bağlantıda da belge Yeni Parti kapsamına ait. Kaynak atfı ve kayıtlı bulgu incelemesi var.
- Faz 4 arşivinin değişmez baytları ve yayımlanmış HTML/JSON dosyaları doğrulama girdisi olarak kullanılacak.
- Eski kodun odak testi kaynak başlığı hatasını verdi. Düzeltilmiş test eksik atfı, incelemesiz bulguyu, yanlış parti sahipliğini ve tüzükteki eksik dosya kaydını reddetti.
- Dokuz partinin dosya denetimi Faz 4 tabanında ve yayımlanan Faz 5 verisinde geçti. Sürüm soyundaki 55 arşivde kullanılan 2.730 özgün ve okunabilir dosya yerinde bulundu.
- Standart yayın denemesi yeniden HTML, SQLite ve JSON üretti. İlk iki dosya Faz 5 arşivine bayt düzeyinde eşit. JSON kayıtları da yeni sürüm kimliği dışında eşit.
- Parti dosyası, yayın komutu ve birleştirme motoruna yönelik 25 test geçti. Kod cfe7c43f ve a3f35df3 commitleriyle çalışma dalına gönderildi.
- Yeni yerel aday sürümü 9c9875d93188491b977a3d561c6a5cc9. Dört sürüm dosyası oluşturuldu ve manifestteki üç çıktı özeti eşleşti. İçerik ve karşılaştırma bağlantı kontrolleri tamamlandı. Etkinleştirme öncesi geçmiş denetimi devam ediyor.

## Resolution

- Faz 4 uygulama bulgularında belge sahipliği, kaynak atfı, kayıtlı bulgu incelemesi ve tam pasaj bağı birlikte denetlenir.
- Yayın sırasında doğrulanmış aday verisi tekrar kullanılır. Birleştirme kaynakları ve kayıt eşitliği indekslenir.
- Standart `publish --refresh` yalıtılmış veride 55 geçmiş sürümün ve yeni sürümün denetimini bitirdi. Çıkış kodu sıfır. Etkin sürüm `9c9875d93188491b977a3d561c6a5cc9`.
- Etkin SQLite hızlı bütünlük ve dış anahtar kontrollerinden geçti. Dokuz parti, 264 mali kayıt ve üç manifest özeti doğrulandı. Yazıcı kilidi bırakıldı.
- Parti dosyası, yayın komutu, birleştirme motoru ve kayıt doğrulamasına yönelik 27 test geçti. İkinci tam arşiv turu, standart yayın denemesi tamamlandıktan sonra sonlandırıldı.
