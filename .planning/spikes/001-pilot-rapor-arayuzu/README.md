---
spike: "001"
idea: pilot-rapor-arayuzu
name: pilot-rapor-arayuzu
type: standard
validates: "Pilot raporu masaüstü ve telefonda açıldığında parti, bulgu ve kaynaklar arasında gezinilebilir."
verdict: VALIDATED
related: []
tags: [html, erişilebilirlik]
---

# Pilot rapor arayüzü

## Araştırma

[Survey BP](https://github.com/mertgkduman/survey_bp/tree/main/web/research) arayüzünden koyu sol menü, açık renkli kartlar, mobil yatay sekme şeridi ve açılır ayrıntı düzeni referans alındı. Raporun CSS ve JavaScript'i HTML'ye gömülür. Böylece aynı HTML dosyası yerel arşivde ve GitHub Pages'te çalışır.

## Deneme

Yerelde `python3 src/arsiv.py serve --host 127.0.0.1 --port 8000` komutuyla sunucuyu başlatın. Ardından `/releases/26de2a4efc584b5b9f81ea67dcb8d65c/index.html` adresini açın. [Çevrimiçi pilot rapor](https://mertgkduman.github.io/proje/)

## İnceleme

- TİP ikinci sekmeye taşındı. Parti sırası rapor üreticisinde tanımlıdır.
- Tekrarlanan eksikler ilgili başlıkta bir kez listelendi. Durumlar kısa etiketlerle, kaynak ve araştırma ayrıntıları açılır kayıtlarla gösterildi.
- Bölüm bağlantıları eklendiğinde eski tarayıcı testi kuruluş bölümünü kaynak bağlantısı olarak seçti. Test seçicisi kuruluş pasajına giden kaynak bağlantısına daraltıldı.

## Sonuç

Chromium'da 360, 390, 768, 1024 ve 1440 piksel genişlikte sekme sırası, klavye, karşılaştırma, kapsam ve başka sekmedeki kaynak kaydına erişim doğrulandı. Yeni sürümün SQLite dosyası öncekiyle bayt düzeyinde aynı. Arşiv denetimi geçti ve rapordaki 76 yerel kaynak dosyası yayın dalındaki kopyalarla eşleşti.
