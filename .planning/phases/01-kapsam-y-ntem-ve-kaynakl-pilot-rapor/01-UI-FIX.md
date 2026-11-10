# Faz 1 arayüz düzeltmesi — uygulama kanıtı

2026-11-10 tarihinde `01-UI-REVIEW.md` içindeki üç öncelikli bulgu ve ilgili kaynak gezinmesi giderildi. Yerel sürüm `7b69e39259214749b36bd655e60c7e66`, üretici sürümü 7'dir; önceki `6fd06aa1a6c643ed99b2b1c95f32822d` üretici sürümü 6 olarak korunur.

- Genel rapor başlığı, viewport meta bilgisi, seçili panel başlıkları, okuma genişliği, satır aralığı, kayıt aralıkları ve sekme dokunma alanları eklendi.
- Aktör, uygunluk, aday, arama, kaynak ve tarih kesinliği kodları okura Türkçe karşılıklarla gösterilir. Kimlikler, durum ve köken değerleri veri/DOM kayıtlarında korunur; özgün alıntılar çevrilmedi. Kaynak bağlantılarının erişilebilir adları belge başlığını içerir.
- Kapsam ve girişim bağlantıları kapalı yöntem ayrıntısını açar; hash ile doğrudan girişim açılışı da denetlendi. Önceki kaynak sekmesi, geri ve odak davranışı korunur.
- `python3 tests/run.py --pattern test_report.py`: 2 test geçti. `python3 tests/run.py`: `TESTS_OK count=44`, 34.546 saniye. Faz denetimi `PHASE1_AUDIT_OK 7b69e39259214749b36bd655e60c7e66`; önceki sürüm `AUDIT_OK` verdi. Önceki tam çalışmada geçmiş eksik kimliğinin artık görünür metinde olmamasına bağlı test beklentisi başarısızdı; test, gerçek geçmiş gerekçesi ve kanıt bağlantısını ve veri kaydındaki kimliği kontrol edecek biçimde güncellendi.
- Chromium ile `/tmp/proje-ui-narrow.png` (390×844 pencere) ve `/tmp/proje-ui-wide.png` (1440×900 pencere) üretildi ve görüntüler incelendi. Bunlar masaüstü Chromium pencere boyutlarıdır; gerçek mobil cihaz emülasyonu veya insan erişilebilirlik/okunabilirlik incelemesi değildir. Kaynak doğruluğu ve tarafsızlık için insan incelemesi açık kalır.
