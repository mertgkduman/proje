---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
reviewed: 2026-11-11T23:49:29Z
depth: standard
files_reviewed: 26
files_reviewed_list:
  - .gitignore
  - README.md
  - src/arsiv.py
  - src/arsiv_gorunum.py
  - src/dosyalar.py
  - src/kaynaklar.py
  - src/rapor.py
  - src/rapor_v10.py
  - src/rapor_v11.css
  - src/rapor_v11.py
  - src/rapor_v12.py
  - src/rapor_v8.py
  - src/rapor_v9.py
  - tests/archive_browser.cjs
  - tests/browser_probe.py
  - tests/test_acceptance.py
  - tests/test_archive_views.py
  - tests/test_dates.py
  - tests/test_documents.py
  - tests/test_dossiers.py
  - tests/test_finance.py
  - tests/test_matches.py
  - tests/test_publication.py
  - tests/test_report.py
  - tests/test_scope.py
  - tests/test_source_policy.py
findings:
  critical: 6
  warning: 0
  info: 0
  total: 6
status: issues_found
---

# Faz 02: Kod İnceleme Raporu

**İnceleme zamanı:** 2026-11-11T23:49:29Z  
**Derinlik:** standard  
**İncelenen dosya:** 26  
**Durum:** issues_found

## Özet

Pasif arşiv, kaynak künyesi ve alıntı üretiminde altı doğrulanmış hata bulundu. Bunlar belirli girdilerde kaynak metnini eksiltiyor veya değiştiriyor, yanlış künye gösteriyor ya da istenmeyen bir ağ isteğine yol açıyor. Örnekler geçici dizin ve yerel HTTP sunucuları kullanılarak çalıştırıldı; uzun süren teslim zinciri denetimleri tekrarlanmadı.

## Narrative Findings (AI reviewer)

### CR-01: Varlık yönlendirmesi doğrulanmadan hedefe istek gönderiliyor

**Sınıflandırma:** BLOCKER  
**Dosya:** `src/arsiv_gorunum.py:42-45`  
**Sorun:** `urlopen` HTTP yönlendirmelerini otomatik izliyor; son ana makinenin izinli olup olmadığı ancak istek tamamlandıktan sonra denetleniyor. Kötü niyetli veya ele geçirilmiş bir kaynak sayfasındaki izinli ana makineye ait görsel/CSS adresi, yerel ağdaki bir servise yönlendirerek arşivi üreten makineden istek gönderebilir. Yerel tekrarda `localhost` üzerindeki izinli varlık `127.0.0.1` üzerindeki farklı hedefe yönlendirdi; fonksiyon dönüşü reddettiği halde hedef `/private` isteğini aldı. İlk veya ara hedeflerde de özel IP ve DNS yeniden bağlanması değerlendirilmelidir.

**Düzeltme:** Otomatik yönlendirmeyi kapatın; her `Location` adresini istekten önce şema, ana makine ve çözümlenen IP açısından doğrulayın, yerel/özel/bağlantı yerel adresleri reddedin ve yönlendirme sayısını sınırlandırın. DNS doğrulaması ile gerçek bağlantının aynı adrese yapıldığından emin olun. İzinli bir URL'nin yerel hedefe yönlendirilmesinde hedefe hiçbir istek ulaşmadığını test edin.

### CR-02: Kapanış etiketi olmayan embed sonrasındaki içerik siliniyor

**Sınıflandırma:** BLOCKER  
**Dosya:** `src/arsiv_gorunum.py:16`, `src/arsiv_gorunum.py:86-90`  
**Sorun:** HTML'de boş öğe olan `<embed>` `DROP` listesinde ve blok yığınına ekleniyor; normal HTML'de `</embed>` gelmediğinden yığın hiç boşalmıyor. `<p>önce</p><embed src="x"><p>SONRAKI ANA METIN</p>` örneğinde sonraki paragraf ve belgenin kalanı üretilen arşivden kayboldu; görünüm bu veri kaybını bildirmiyor.

**Düzeltme:** `embed` gibi kapanış etiketi olmayan yasak öğeleri yığına sokmadan tek başına atın; içerik taşıyan yasak öğeler için mevcut bloklamayı koruyun. `<embed>` sonrasında belge içeriğinin ve kapanış etiketlerinin korunduğunu doğrulayan test ekleyin.

### CR-03: UTF-8 dışındaki HTML belgeleri bozuk metne dönüştürülüyor

**Sınıflandırma:** BLOCKER  
**Dosya:** `src/arsiv_gorunum.py:148-154`  
**Sorun:** Özgün belgenin gerçek karakter kümesi dikkate alınmadan baytlar iki kez `utf-8` ve `errors='replace'` ile çözülüyor. Yerel tekrarda `charset=windows-1254` bildiren ve bu kodlamayla kaydedilen “Türkiye İşçi Partisi”, pasif görünümde “T�rkiye ���i Partisi” oldu. Üretilen UTF-8 meta etiketi kaybolmuş karakterleri geri getirmiyor; bu da eski Türkçe parti belgelerinin yanlış okunmasına yol açıyor.

**Düzeltme:** Yakalama sırasında HTTP karakter kümesini saklayın ve HTML meta bildirimi/BOM ile birlikte güvenilir kodlama belirleme uygulayın; özgün baytları değiştirmeden yalnız doğrulanmış çözümlemeyi UTF-8 türevine dönüştürün. Windows-1254 ve UTF-8 belgeleri, Türkçe karakter ve kaynak hash'i açısından test edin; çözülemeyen kodlamayı açık hata veya sınırlama olarak bildirin.

### CR-04: Görünüm kimliği manifestteki kaynak adresini kapsamıyor

**Sınıflandırma:** BLOCKER  
**Dosya:** `src/arsiv_gorunum.py:167-177`  
**Sorun:** `view_id` yalnız kaynak hash'i ve üretilmiş dosya hash'lerinden hesaplanıyor; değişmez manifest ayrıca `source_url`, `asset_sources` ve `limitations` içeriyor. Aynı HTML baytları ve çıktısı farklı iki URL'den geldiğinde iki üretim aynı dizine düşüyor ama manifestleri farklı oluyor ve ikinci üretim `Değişmez arşiv görünümü farklı` hatasıyla duruyor. Bu durum aynı belgenin farklı URL'lerden veya farklı indirme sınırlamalarıyla arşivlenmesini engelliyor.

**Düzeltme:** Kimliği, manifestin kimlik ve özeti dışındaki bütün anlamlı alanlarını içeren kanonik bir girdiden türetin veya URL'ye özgü kayıtları içerik adresli görünümden ayrı tutun. Aynı baytların iki farklı URL ve farklı varlık sınırlamasıyla ardışık oluşturulmasını test edin; mevcut sürümlerin biçim kimliğini korumak için formatı sürümleyin.

### CR-05: Yazar tamamlama başka sürümün tüm künyesini kullanıyor

**Sınıflandırma:** BLOCKER  
**Dosya:** `src/rapor.py:160-166`  
**Sorun:** Bir sürümün yazarı boşsa aynı belge ve hash'e sahip başka sürümün yalnız yazarı yerine bütün atıf sözlüğü kullanılıyor. Böylece ilk sürümün yayıncısı, yayın tarihi ve atıf gerekçesi başka kaydın değerleriyle sunulabiliyor. Geçerli rapor verisinin bellek içi kopyasında ilk sürümün tarihi bilinmezken aynı hash'li ikinci sürüme `2000-01-01` tarihi ve yazar eklenince ilk kaynağın künyesinde de bu tarih gösterildi. Kaynak baytlarının eşit olması künye alanlarının eşit olduğunu kanıtlamaz.

**Düzeltme:** Sürümün kendi atıf kaydını koruyun; yazarın başka kayıttan devralınması destekleniyorsa yalnız açıkça doğrulanmış yazar alanını kopyalayın ve bu ilişkinin dayanağını saklayın. Aynı hash'li sürümlerin farklı tarih ve yayıncılarıyla kendi künyelerini koruduğunu test edin.

### CR-06: HTML entity çözümlemesi PDF'deki birebir alıntıyı değiştiriyor

**Sınıflandırma:** BLOCKER  
**Dosya:** `src/rapor.py:59-62`, `src/rapor.py:225`  
**Sorun:** Kaynak türünden bağımsız `unescape`, doğrudan alıntı ve pasajdaki gerçek karakter dizilerini HTML karakter başvurusu sayıyor. Örneğin PDF metnindeki gerçek `literal &copy; 2026` alıntısı `literal © 2026` olarak gösteriliyor. PDF pasajları `pdf_page_text` ile doğrudan karşılaştırıldığından bu metin geçerli bir birebir alıntı olabilir; okuyucuya ve kaynak künyesine farklı bir metin sunulması kaynak sadakatini bozuyor.

**Düzeltme:** Metin kökenini dikkate alın: PDF ve zaten düz metin olarak saklanan pasajları yalnız HTML çıktısı için escape edin; HTML kaynaklarındaki entity çözümlemesini kaynağı ayrıştırırken tek ve tutarlı bir aşamada yapın. PDF'de literal `&copy;`, `&amp;` ve sayısal entity benzeri dizelerin aynen görüntülendiğini test edin.

---

_İnceleyen: gsd-code-reviewer_  
_Derinlik: standard_
