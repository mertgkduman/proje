# Phase 03 navigasyon test gözlemcisi düzeltmesi

**Durum:** Hedef testler geçti; bağımsız yeniden inceleme, yeni commit üzerinde tam regresyon ve insan doğrulaması açık. **Commitler:** `f70504e`, `6e59f35`.

Önceki tam koşu 158 testte tek hata verdi (`root-tests.exit` 1): `%ZZ` alt testinde Node, geçici Chromium profilini silerken `ENOTEMPTY` aldı. Hata kaydı `03-15-checks/nav-percentzz/root-tests-failure.log` içinde korunmuştur; o koşu başarılı değildir.

Altı gerçek Chromium kapanışında `Browser.close` yanıtı geldiğinde süreç hâlâ yaşıyordu; exit 24–30 ms sonra gerçekleşti. Eski probe bu aralıkta profili siliyordu. Düzeltilmiş probe sahip olduğu Chromium sürecinin exit olayını bekler; gerektiğinde sınırlı süre sonra onu sonlandırır ve geçici profil silinmesinde sınırlı retry kullanır. Navigasyonun 19 assertionı ve gerçek uygulama olayları değişmedi.

Kontrollü gecikmiş profil yazımında eski probe çıkış sonrası profil bıraktı, yeni probe bırakmadı (`late-write-test.json`, exit 0). Bu, kapanış sıralaması kusurunu yeniden üretir; ilk `ENOTEMPTY` hatasının aynı anda yazan tam dosyası kaydedilmemiştir.

Gerçek yayın ve arşiv üzerinde dört hedef test 97.534 saniyede geçti (`fixed-tests.log`, exit 0). File/HTTP × 360/1365 modlarının her birinde 19 kontrol ve arşiv alıntısı geçti; gerçek kaynaklı `%`, `%20`, `%ZZ` önizlemeleri dahil. Girdi özetleri `fixed-inputs.sha256` ile doğrulandı. `node --check` geçti. Root'un yeni girdilerle tüm testleri yeniden çalıştırması gereklidir; plan 03-16 ve faz kapanışı bu sonuçla tamamlanmış sayılmaz.

## WR-01: Kapatma yanıtı gelmezse süreç çıkışı ve timeout beklenememesi

Bağımsız inceleme `f70504e` sürümünde close isteği yanıt beklerken exit/kill sınırına hiç ulaşılmadığını saptadı. Bu nedenle root'un sonraki tam regresyonu yalnız kendi test süreç grubunda durduruldu; exit 143, geçiş değildir.

`6e59f35`, Browser.close isteğinin yanıtını beklemeksizin owned child exit ve timeout yoluna geçer; CDP pipe kapanması veya hatası bekleyen istekleri reddeder. Close isteği sonrası beş saniye içinde exit yoksa yalnız o child `SIGKILL` alır; beş saniye daha çıkmazsa hata verilir. Önceki sınırlı profil silme retry korunur.

Gerçek Chromium kullanan, yalnız close yanıtını bastıran kontrollü proxy deneyinde eski probe, hem child çıkışı hem de canlı kalan owned proxy durumunda 12 saniye sınırını aştı ve profil bıraktı. Yeni probe iki durumda da yaklaşık 6.9 saniyede exit 0 ile tamamlandı ve profil bırakmadı (`wr01-red-{exit,hang}.json`, `wr01-green-{exit,hang}.json`). Deney kendi process group'unu kullandı; profile ve süreçlere ilişkin sonuçlar kanıt kayıtlarındadır. Bu lifecycle deneyi 19 kontrollü gerçek navigasyon kabulünün yerine geçmez.

Yeni commit'in gerçek testi 4 testi 119.246 saniyede geçti (`wr01-real-tests.log`, exit 0). Dört file/HTTP × 360/1365 modunun her birinde 19 kontrol ve gerçek arşiv alıntısı geçti; `%`, `%20`, `%ZZ` önizlemeleri de geçti. Hashler `wr01-fixed-inputs.sha256`, sonuçlar `wr01-real-navigation.json` içindedir. Tam global koşudan önce bağımsız yeniden inceleme gereklidir.
