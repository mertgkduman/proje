# Phase 03 navigasyon test gözlemcisi düzeltmesi

**Durum:** Hedef testler geçti; yeni commit üzerinde tam regresyon ve insan doğrulaması açık. **Commit:** `f70504e`.

Önceki tam koşu 158 testte tek hata verdi (`root-tests.exit` 1): `%ZZ` alt testinde Node, geçici Chromium profilini silerken `ENOTEMPTY` aldı. Hata kaydı `03-15-checks/nav-percentzz/root-tests-failure.log` içinde korunmuştur; o koşu başarılı değildir.

Altı gerçek Chromium kapanışında `Browser.close` yanıtı geldiğinde süreç hâlâ yaşıyordu; exit 24–30 ms sonra gerçekleşti. Eski probe bu aralıkta profili siliyordu. Düzeltilmiş probe sahip olduğu Chromium sürecinin exit olayını bekler; gerektiğinde sınırlı süre sonra onu sonlandırır ve geçici profil silinmesinde sınırlı retry kullanır. Navigasyonun 19 assertionı ve gerçek uygulama olayları değişmedi.

Kontrollü gecikmiş profil yazımında eski probe çıkış sonrası profil bıraktı, yeni probe bırakmadı (`late-write-test.json`, exit 0). Bu, kapanış sıralaması kusurunu yeniden üretir; ilk `ENOTEMPTY` hatasının aynı anda yazan tam dosyası kaydedilmemiştir.

Gerçek yayın ve arşiv üzerinde dört hedef test 97.534 saniyede geçti (`fixed-tests.log`, exit 0). File/HTTP × 360/1365 modlarının her birinde 19 kontrol ve arşiv alıntısı geçti; gerçek kaynaklı `%`, `%20`, `%ZZ` önizlemeleri dahil. Girdi özetleri `fixed-inputs.sha256` ile doğrulandı. `node --check` geçti. Root'un yeni girdilerle tüm testleri yeniden çalıştırması gereklidir; plan 03-16 ve faz kapanışı bu sonuçla tamamlanmış sayılmaz.
