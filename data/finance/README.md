# Kesin hesap verileri

İlk teslim dokuz partinin 2023–2025 hesap dönemlerini ve daha eski son doğrulanmış hesapları kapsar. Dönemler Anayasa Mahkemesi Kararlar Bilgi Bankasının yayımlanmış siyasi parti mali denetim kararlarında arandı. Her dizin sorgusunun sıkıştırılmış yanıtı ve SHA-256 özeti Faz 5 kontrol kayıtlarındadır.

`phase05-mali.json` dönem kapsamını, karar künyelerini, tutarları, örgüt kapsamını, kaynak pasajlarını ve eksik bilgi gerekçelerini içerir. `sources/` içindeki gzip dosyaları sekiz karar için AYM'nin özgün JSON yanıtını içerir. Kaynak künyesindeki SHA-256, sıkıştırılmamış yanıta aittir. Arşiv görünümünün özgün HTML baytları yanıttaki `icerik` alanının UTF-8 kodlamasıdır.

Sonuçlar kaynakta yayımlanan tutarları gösterir. Parti genel toplamı, genel merkez ve il örgütleri ayrı kapsamlardır. Karar yılı, hesap yılı ve yayım tarihi ayrı ayrı izlenir. Dizin taramasında karar bulunmaması, bu dizindeki arama sonucunu belirtir. Aynı tüzel kişinin kuruluşundan önceki yıllar ayrı gösterilir.

## Yeniden üretim

Kendi tarayıcınızda açacağınız bağımsız HTML sayfasını üretin.

```sh
python3 src/finansman_html.py --input data/finance/phase05-mali.json --output kesin-hesaplar.html
```

Faz 4 tabanından açılmış arşiv çalışma alanında mali paketi yükleyin ve tam raporu üretin.

```sh
python3 src/finansman.py --data data --workspace CALISMA_DIZINI --input data/finance/phase05-mali.json
python3 src/arsiv.py publish --workspace CALISMA_DIZINI --refresh
python3 src/arsiv.py audit --release current --check finance
```
