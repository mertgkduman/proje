---
quick_id: 261116-mgh
title: Faz 3 doğrulama sekmesi ve GitHub Pages yayını
status: complete
---

# Amaç

Kullanıcının altı Faz 3 kontrolü için verdiği kabulü kaydetmek; aynı kontrolleri gerçek karşılaştırma örnekleri ve kaynak bağlantılarıyla yeni rapor sekmesinde sunmak; güncel sürümü mevcut GitHub Pages yayınına göndermek.

## Görevler

1. `03-UAT.md` dosyasını 6/6 kullanıcı kabulüyle tamamla. Ajanın teknik doğrulaması ve kullanıcının toplu kabulü ayrı kaydedilir; ham tanılar değiştirilmez. Kanonik doğrulama ve faz takibini bu kabul doğrultusunda güncelle.
2. Renderer 23'ü dondur, renderer 24 ve yeni stil sürümü oluştur. İnsan kabulü mevcut `review` tablosunda sürüme bağlı yapılandırılmış kayıt olarak tutulur. “3. Faz Doğrulama” sekmesi altı başlığı, kullanıcı kabul tarihini ve kaynaklı somut örnekleri gösterir. Geliştirme talimatları arayüze aktarılmaz. Eski yayın ve kaynak baytları korunur.
3. Rapor/sekme/kaynak bağlantılarını dar ve geniş ekranda gerçek Chromium ile kontrol et; yeni sürümü normal `workspace`/`publish --refresh` yoluyla üret ve mevcut arşiv denetimlerini çalıştır.
4. Kaynak kodu ve takip kayıtlarını GitHub'a normal push ile gönder. `gh-pages` dalının mevcut geçmişinden ayrı yayın ağacı oluştur; yeni raporu ve bağlı kaynak/varlıkları ekle, kök yönlendirmeyi güncelle. Dağıtım ve canlı sayfa doğrulanmadan yayımlandı denmez.

## Doğrulama

- UAT: altı pass, sıfır pending/issue; kullanıcının gerçek mesajına atıf.
- Rapor testleri, örnek bağlantılarının hedef ve kaynak doğruluğu; mevcut renderer23 sürümünün bire bir yeniden üretimi.
- Yeni sekme ve örnek → karşılaştırma → kaynak gezinmesi; klavye ve mobil görünüm.
- Yeni değişmez sürümün mevcut ordinary/P2/P3 kabul yolu; eski yayınlar ve teslim makbuzları korunur.
- GitHub dal uçları, dağıtım sonucu ve sunulan HTML/örnek kaynakları yerel paketle eşleşir.

## Yürütme

Codex skill adapter'ın alt ajan sınırlaması doğrultusunda planlama, uygulama ve inceleme mevcut ajan tarafından sıralı yürütülür. Kullanıcı push ve yayını açıkça yetkilendirmiştir.

## Yürütmede gerekli dar düzeltme

Kapalı SQLite dosyalarında ağ dosya sistemi kilit/değişiklik kontrolleri yayını aşırı yavaşlattı. Aynı gerçek snapshot üzerinde 40 sorgu normal salt okunur kipte 0.1113s, değişmez kipte 0.00369s ve aynı dokuz parti sonucunu verdi (`readonly-benchmark.json`). [SQLite URI sözleşmesi](https://www.sqlite.org/uri.html) uyarınca `immutable=1` yalnız `data/releases/<32 hex>/records.sqlite3` ve manifesti bulunan değişmez kopyalara uygulanır; çalışma alanı ve staging değişiklik algısını korur. Üç gerçek okuma/yazma-gözleme testi ve iki tarihsel audit testi geçti. Native audit kapıları atlanmaz; ilerlemeleri günlüğe yazılır.

Ek yayın testleri canlı yazıcının kilidini kendi fixture kopyasına taşıdığı için `FileExistsError` verdi. Fixture yalnız kökteki operasyonel `.write.lock` ve `.staging` durumunu kopyalamayacak şekilde düzeltildi; kendi kilit, rollback, bozuk kaynak ve eski taban sınamaları aynen korunur.
