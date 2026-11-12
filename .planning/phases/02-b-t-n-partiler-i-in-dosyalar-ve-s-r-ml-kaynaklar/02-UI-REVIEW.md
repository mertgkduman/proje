# Faz 02 — Arayüz İncelemesi

**Tarih:** 2026-11-11  
**Ölçüt:** UI-SPEC bulunmadığından altı genel tasarım ilkesi ve özellikle D-13–D-16.  
**İncelenen çıktı:** Dokuz partilik yerel renderer 13 sürümü; Yeni Parti pilotunun mevcut 1365 ve 360 piksel ekran görüntüleri.  
**Görüntüler:** Yeni yakalama yapılmadı; 3000, 5173 ve 8080 portlarında sunucu yanıt vermedi. Mevcut görüntüler yalnızca Yeni Parti pilotunu gösterir; diğer partiler ve tablet bu incelemede görsel olarak yeniden doğrulanmadı. Önceki parti kontrol kayıtları ve tarayıcı testleri yeniden çalıştırılmadı. Görüntü alınmadığı ve görev yalnızca bu rapora yazma yetkisi verdiği için ekran görüntüsü dizini oluşturulmadı; gelecekte yakalamadan önce `.planning/ui-reviews/.gitignore` oluşturulmalıdır.

## Puanlar

| İlke | Puan | Temel bulgu |
|---|---:|---|
| Metin | 3/4 | Dokuz partilik rapor hâlâ “pilot rapor” adını kullanıyor. |
| Görsel düzen | 3/4 | Açık hiyerarşi var; mobil sekme şeridinin devamı az fark ediliyor. |
| Renk | 3/4 | Alıntı ve özet ayrımı doğru; renkler değişkenlerle tam merkezileştirilmemiş. |
| Tipografi | 2/4 | Çok sayıda birbirine yakın küçük metin boyutu ve ağırlık var. |
| Boşluk | 3/4 | Mobil kaynak ve bölüm bağlantılarında dokunma alanları dar. |
| Deneyim | 3/4 | Sekmeler klavyeyle çalışacak şekilde kodlanmış; mobilde diğer partileri keşfetmek zor. |

**Toplam: 17/24**

## Öncelikli üç düzeltme

1. **UYARI — Mobil parti gezintisi:** Yatay şeritte sonraki partiler kesiliyor; 360 piksel görüntüsünde kaydırma çubuğu dışında devam işareti yok. Bir kenar geçişi veya görünür ileri/geri kontrolleri ekleyin ve klavye ile dokunmayı sınayın (`src/rapor_v11.css:87`).
2. **UYARI — Kaynak bağlantılarının hedefi:** Tekrarlanan küçük `[Kaynak]` bağlantıları dokunma ve taramayı zorlaştırıyor. Görünür metni kısa tutarak tıklanabilir alanı büyütün ve mevcut kaynak başlığını erişilebilir adda koruyun (`src/rapor_v13.py:178`, `src/rapor_v11.css:56`).
3. **UYARI — Tipografi ölçeği:** Meta bilgiler ve bağlantılar için birbirine çok yakın çok sayıda küçük boyut kullanılıyor. Okunabilir bir alt sınır ve birkaç tutarlı metin/başlık ağırlığı belirleyin (`src/rapor_v11.css:28`, `:37`, `:64`, `:71`).

## Ayrıntılı bulgular

### 1. Metin — 3/4

- **UYARI:** Başlık “kaynaklı pilot rapor” diyor; dokuz partilik mevcut sunumun kapsamını olduğundan dar anlatabilir. Üst başlığı kapsamı ifade eden güncel bir adla değiştirin (`src/rapor_v13.py:237`).
- **UYARI:** Kaynak listesi beş başlığı içerik olmasa da basıyor; boş başlıklar açıklamasız kalıyor. Kaydı olmayan grupları kısa bir durum metniyle açıklayın veya gizleyin (`src/rapor_v13.py:410`).
- “Henüz incelenmedi” ve karşılaştırmanın henüz hazırlanmadığını söyleyen metinler bu fazın bilinçli kapsamıdır; eksiklik olarak puanlanmadı (`src/rapor_v13.py:400`, `:424`).

### 2. Görsel düzen — 3/4

- **UYARI:** 360 piksel pilot görüntüsünde sonraki parti adı kısmen kesiliyor. Şeridin yatay kaydırılabildiği daha açık gösterilmeli (`src/rapor_v11.css:91`).
- **UYARI:** Kaynak künyeleri uzun belge adı, tür, tarih ve sürümü aynı özet satırına sıkıştırıyor. Küçük ekranda satırları ve aralıkları gözden geçirerek taranabilirliği artırın (`src/rapor_v13.py:223`).
- Masaüstü pilot görüntüsünde parti adı, kuruluş kartı ve okuma sırası belirgin; ikon-only kontrol saptanmadı.

### 3. Renk — 3/4

- **UYARI:** Koyu mavi özet ve siyah tırnaklı alıntı D-14'e uygun; ancak bunlar ve bazı odak, durum, kenarlık renkleri doğrudan CSS içinde tanımlı. Anlamsal renk değişkenlerine taşıyarak tutarlılığı kolaylaştırın (`src/rapor_v11.css:19`, `:48`, `:49`, `:62`).
- Sekiz temel renk değişkeni var; yeşil bağlantılarda ve seçili sekmede kullanılıyor (`src/rapor_v11.css:1`, `:17`, `:30`, `:66`). Ekran görüntüsünden kesin 60/30/10 alan oranı ölçülmedi; dağılım hakkında kesin uygunluk iddia edilmez.

### 4. Tipografi — 2/4

- **UYARI:** CSS'de 15 farklı `font-size` ifadesi ve yedi sayısal ağırlık var; `.78rem`–`.95rem` arasında çok sayıda yakın değer bulunuyor. Özellikle kaynak türü ve dip bilgi metinlerini büyütüp ölçeği sadeleştirin (`src/rapor_v11.css:28`, `:37`, `:64`, `:71`). Sayılar ifade çeşitleridir, hesaplanan tarayıcı boyutları değildir.
- **UYARI:** Küçük ekran görüntüsünde parti şeridi büyük harfli ve sıkışık; uzun yasal adların taranması zor. Sekme metnini daha okunabilir bir ağırlık ve boyutla deneyin (`src/rapor_v11.css:28`, `:92`).

### 5. Boşluk — 3/4

- **UYARI:** Bölüm bağlantılarının düşey dolgusu `.26rem`, kaynak bağlantılarında ise ayrı hedef dolgusu yok; dar ekranda bitişik bağlantıları seçmek zorlaşabilir. Görsel aralığı bozmadan dokunma hedeflerini artırın (`src/rapor_v11.css:39`, `:40`, `:72`).
- **UYARI:** Boşluklar `.25`, `.26`, `.3`, `.35`, `.4`, `.45`, `.55`, `.65`, `.7`, `.75`, `.8`, `.85` ve `.9rem` gibi yakın değerlerle dağılmış. Küçük bir ortak ölçek bakım ve görsel ritmi iyileştirir (`src/rapor_v11.css:27`, `:39`, `:41`, `:67`, `:72`).
- 920 ve 600 piksel kırılma noktaları mevcut; tablet görünümü bu turda test edilmedi (`src/rapor_v11.css:87`, `:96`).

### 6. Deneyim — 3/4

- **UYARI:** Mobil sekme listesinde yatay kaydırma var ancak görünür ileri/geri yönlendirmesi yok; dokuz partinin tamamını keşfetmek kolay olmayabilir (`src/rapor_v11.css:91`).
- **UYARI:** Kaynaklara gidildiğinde geri dönüş için bağlantıyı kapatma veya tarayıcı geçmişine güveniliyor; belirgin bir “Metne dön” bağlantısı uzun kaynak kartlarında yön bulmayı kolaylaştırır. Mevcut odak iadesi kaynak kapatılınca çalışmak üzere kodlanmış (`src/rapor_v13.py:511`, `:537`).
- Sekmelerin ok/Home/End tuşları, odak görünümü, içeriğe atlama bağlantısı ve açılır kaynak kayıtları kodda mevcut (`src/rapor_v13.py:242`, `:487`; `src/rapor_v11.css:19`). Bu turda yeni etkileşim testi yapılmadı. Statik raporda yükleme durumu ve yıkıcı eylem gerekmemektedir.

## İncelenen dosyalar

- `AGENTS.md`, `02-CONTEXT.md`, 02-01–02-10 PLAN ve SUMMARY belgeleri.
- `src/rapor.py`, teslim edilen sürümle eşleşen `src/rapor_v13.py`, `src/rapor_v11.css`.
- `data/releases/bcc67d04d9d741e191589d0f5ac173ca/index.html` ve mevcut `/tmp/proje-epm-browser-public/report-1365.png`, `report-360.png` görüntüleri.

`components.json` yok; üçüncü taraf bileşen kayıt defteri denetimi uygulanmadı. Bu inceleme kaynakların gerçekliğine insan onayı vermez.
