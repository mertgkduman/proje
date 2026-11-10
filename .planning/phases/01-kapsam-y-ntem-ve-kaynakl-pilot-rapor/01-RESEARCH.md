# Faz 1 — Kapsam, yöntem ve kaynaklı pilot rapor: araştırma

**Tarih:** 2026-11-10
**Güven:** Orta; kimlik ve başlangıç kaynakları kontrol edildi, pilotun ayrıntılı belge incelemesi yürütmede yapılacak.
**Üretim kaydı:** Ayrı `gsd-phase-researcher` (GPT-6.1 Sol/xhigh) bulguları; dosya teslimi geciktiği için araştırmacının `RESEARCH COMPLETE` yanıtı orkestratörce kaydedildi. Yargıtay ve TBMM başlangıç kayıtları orkestratörce de açıldı. Bu dosya tam pilot incelemesi veya arşiv teslimi değildir.

## Kullanıcı kararları ve faz sınırı

Bağlayıcı kararlar `01-CONTEXT.md` D-01–D-24'tür. Pilot Yeni Parti; onaylı dokuz partilik liste değişmez. İnceleme her partinin kaynakla doğrulanan kuruluşundan başlar. Aynı ad, bireysel milletvekili üyeliği ve ortak grup farklı varlıklardır. Beş başlık: kuruluş/temel bilgiler, tüzük, program, söylem–uygulama, finansman–harcamalar.

Parti bazlı ana sekmeler ve Karşılaştırmalı Özet kurulur; diğer partilerin dosyaları ve partiler arası gerçek karşılaştırmalar bu fazda üretilmiş gibi sunulmaz. Özet koyu mavi, değişmeden alınan kısa alıntı siyah ve tırnak içinde birlikte görünür; ayrıca görünür üretim türü etiketi eklenmez. Metin kökeni ortak veri/dışa aktarımda korunur. Kaynak türü, olgu/beyan/yorum ve eksik durumları açık kalır.

Gereksinimler: KAPS-01–04, KAY-02–03, MET-01–04, EKS-01–02, VER-01. Uygulama kodu ve test altyapısı henüz yoktur. MVP ve walking skeleton etkin: ilk dilim gerçek kaynaktan kalıcı DB yazma/yeniden okuma ve HTML'de kaynak açma davranışını kanıtlamalıdır. Geliştirme gösterimi yalnız yereldir; kamuya yayın/barındırma yetkisi yoktur.

## Kontrol edilen birincil kaynaklar

| Kaynak | Araştırma bulgusu ve kullanım sınırı |
|---|---|
| [Yargıtay Yeni Parti kaydı](https://www.yargitaycb.gov.tr/sipar/365) | Sayfanın adı YENİ PARTİ, kuruluş alanı 24.07.2026. Yürütmede özgün sayfa baytları ve tarihli arşiv kopyası alınmalı; kayıt kontrolü ve kimlik bağlama tamamlanmalıdır. |
| [Yargıtay siyasi parti listesi](https://www.yargitaycb.gov.tr/sipars) | Kimlik karşı kontrolü için başlangıç kaynağı. |
| [TBMM sandalye dağılımı](https://tbmm.gov.tr/sandalyedagilimi) | Yeni Parti satırı bulunuyor. Tarihli sayfa kopyası, ön liste ve dışlama gerekçeleri ile üyelik/grup ayrımı yürütmede ilişkilendirilmeli. Sayfa erişim tarihi kendi güncelleme tarihi değildir. |
| [AYM 2013/103 mali denetim kararı](https://siyasipartikararlar.anayasa.gov.tr/Dosyalar/Kararlar/KararPDF/2013-103-spmd.pdf) | Araştırmacı, eski aynı adlı oluşumun 2009 hesabı ve 2012 birleşmesiyle ilgili olduğunu bildirdi. Güncel pilota ad benzerliğiyle mali kayıt eklenmemeli; kullanılacaksa içerik/kimlik yeniden kontrol edilmeli. |

`https://yeni-parti.org` ve `https://yeni-parti.org.tr/` araştırmacının erişim girişimlerinde zaman aşımı/okunabilir metin sorunu verdi. Alan adı otoritesi, tüzük/programın özgün dosyası ve sürümü henüz doğrulanmış değildir. Arama dizini bir özgün belge yerine geçmez. Yürütmede Yargıtay/TBMM bağlantıları, doğrulanmış parti kanalları ve bunların belge zinciri izlenmeli; sonuçsuz girişimler kaydedilmelidir. Erişim başarısızlığı belge yokluğu sayılmaz.

## Önerilen teknik yapı

Python standart kitaplığı (`sqlite3`, `json`, `hashlib`, `html`, `unittest`) ve yalın HTML/CSS/JavaScript yeterlidir. Ayrı üretim sunucusu, JS çerçevesi, harici API veya ücretli servis gerekmiyor. Statik rapor göreli yerel arşiv bağlantılarıyla açılabilmeli; geliştirme gösterimi gerekirse yalnız `127.0.0.1` üzerinden yapılır.

Araştırmacı ortamda Python 3.12.2, SQLite 3.41.2, Node 24.21.0 ve npm 11.19.0 ölçtü. Bunlar ortam gözlemidir; plan sözleşmesi tüm sürümleri gereksiz yere sabitlememelidir. [Python sqlite3 belgesi](https://docs.python.org/3.12/library/sqlite3.html).

**NFS:** Araştırmacının `stat -f` gözleminde proje `nfs`, `/tmp` `xfs`. Aktif SQLite DB'si yerel scratch/geçici dizinde tek yazıcıyla işletilmeli; doğrulama ve bağlantı kapanışından sonra kapalı snapshot, JSON dışa aktarımı ve HTML üretilmelidir. Kalıcı snapshot ile JSON arasında hangisinin asıl kayıt olduğu, yükleme/yazma ve hata durumunda yayınlama sırası planlarda açık olmalı; iki bağımsız doğruluk kaynağı oluşmamalı. NFS üzerinde WAL/eşzamanlı yazma kullanılmamalı. [SQLite WAL](https://sqlite.org/wal.html), [kullanım sınırları](https://sqlite.org/whentouse.html).

Önerilen modüller (nihai adları planlayıcı sabitler): DB/şema, veri aktarımı, kaynak arşivleme, kanıt doğrulama, yöntem/kaynak zinciri, statik rapor üretimi ve yerel CLI. Veri, belgeler ve çıktı ayrı dizinlerde; hash'li değişmez belge sürümleri, okunabilir kaynak kayıtları ve göreli bağlantılar kullanılır.

## Veri sözleşmesi

- Parti ve kimlik/kapsam gözlemleri; milletvekili üyeliği ve grup gözlemleri ayrı ilişkiler.
- Belge → değişmez sürüm → özgün arşiv dosyası/güvenli okunabilir türev → pasaj/konumlandırıcı.
- Bulgu ↔ kanıt pasajları çoktan çoğa; konu ↔ bulgular; veri kökeni `quote`/`summary` ile epistemik tür `fact`/`source_assertion`/`comment` ayrı alanlar.
- Arama/erişim/doğrulama girişimi → gerekçeli eksik bilgi kaydı. `not_researched` ile üç gerçek eksik durumu ayrılır.
- Söylem–uygulama eşleşmesi, iki ayrı bulgu ve aktör/tarih/bağlam/kanıt ilişkisine bağlanır. Kurumsal eylem, yetkili temsilci eylemi ve bireysel milletvekili kaydı ayrılır.
- Finansal değer isteğe bağlı; yokluk `NULL`, sıfır ancak belgede açıklanmışsa `0`. Hesap dönemi, para birimi, örgütsel kapsam ve yayımlanma tarihi ayrı.
- Karşılaştırma kayıt yapısı kaynak ilişkilerini koruyabilir; pilotta partiler arası gerçek kayıt uydurulmaz.
- Yabancı anahtarlar her bağlantıda işlem öncesinde etkin; parametreli SQL; eksik kanıt/yanlış kimlik/bozuk arşiv ilişkisi reddedilir. [SQLite foreign keys](https://sqlite.org/foreignkeys.html).

Belge tarihi/sürümü, olay tarihi, hesap dönemi, erişim tarihi ve doğrulama tarihi birbirinin yerine kullanılmaz. Planlama önerisi: ilk başarılı TBMM kapsam arşivinin UTC zamanını veri kesim noktası olarak dondurmak, yöntem kaydı ve raporda göstermek; sonradan elde edilen belgeler geçmiş kesime ilişkin kanıt sağlayabilir, kesim sonrası olaylar sessizce eklenmez. Bu bir teknik/yöntem önerisidir, kullanıcının önceden seçtiği tarih değildir.

## Ortak konu sözlüğü ve kaynak zinciri

Başlangıç sözlüğü önerisi: üyelik hakları, organ seçimi, denetim, görüş ifade mekanizmaları, aday belirleme, demokrasi/hukuk, ekonomi/emek, sosyal politika, eğitim, çevre, dış politika, finansal şeffaflık. Bunlar önceden doğrulanmış parti özellikleri değildir. Erişilebilen tüzük/program pasajlarıyla gerekçelendirilir, yeni konu eklemeleri sürümlenir; beş dosya başlığıyla konu sözlüğü karıştırılmaz.

Belge düğümleri ve ilgili bağlantı/çelişki kenarları tutan bir iş kuyruğu kullanın. URL takma adları ve içerik hash'leri birlikte tekilleştirilir; yönlendirme, döngü ve aynı URL'deki yeni sürüm ayrı ele alınır. Her ilgili uç incelenmiş veya gerekçeli erişim/çözüm engeliyle kaydedilmişse konu taraması kapanabilir. Bekleyen ilgili uç varken kapanamaz. Engelli uçlar görünür kalır; yeni belge taramayı yeniden açar. Kapanma bütün tarihsel belgelerin bulunduğunu veya çelişkinin kesin çözüldüğünü iddia etmez.

Konu bazında başlangıç sorguları, bağlantılar, erişim sonuçları, dışlama gerekçeleri ve kapanma/yeniden açılma kaydedilir. Sayısal olay kotası veya sonuç yönüne göre seçme uygulanmaz: ilan edilen taramada bulunan bütün uygun, yeterli kanıtlı eşleşmeler saklanır ve rapora alınır. Partinin açıklaması, açıklamanın varlığının kanıtıdır; eylemin gerçekleşmesine ayrıca dayanak gerekir.

Eksikler ilgili başlıkta kısa gerekçe ve girişim tarihiyle görünür; ayrıca parti/konu eksik listesinde izlenebilir. `Bulunamadı` arama, `Erişilemedi` saptanan kaynağa erişim, `Doğrulanamadı` yetersiz doğrulama girişimine bağlanır. Hiç girişim yapılmamış alan bu üç durumdan biri olamaz. Eksik veri olumlu/olumsuz siyasi sonuç veya uyumsuzluk değildir.

## Arşiv ve HTML sözleşmesi

PDF'nin özgün baytları, HTML'nin tarihli ham kopyası ve güvenli okunabilir yerel türevi saklanır. Özgün/nihai URL, erişim zamanı, MIME, SHA-256 ve belge sürümü tutulur. PDF sıra sayfası ile basılı sayfa numarası farklıdır; madde, bölüm ve kısa özgün pasaj eklenir. HTML için `exact/prefix/suffix` seçici değişmez arşive bağlanabilir. [hashlib](https://docs.python.org/3.12/library/hashlib.html), [W3C TextQuoteSelector](https://www.w3.org/TR/annotation-model/#text-quote-selector).

Metindeki bağlantı rapordaki kaynak kaydını açar; kayıt künye, ilgili pasaj, özgün URL ve erişilebilen göreli arşiv bağlantısını birlikte gösterir. Her parti sekmesi altında kaynakça da vardır. Derin bağlantıyla kaynak açılışı, görünmeyen paneli açma, geri dönüş/fokus ve klavye hareketi planlanmalı. Kısa özet ve kısa alıntı birlikte görünür. Kapsam/yöntem parti sekmesi yapısını bozmadan erişilir. [ARIA sekme örüntüsü](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/).

Kaynak metni HTML'ye kaçışlanmalı, bağlantı protokolleri doğrulanmalı; ham kaynak HTML'si rapor içinde etkin çalıştırılmamalı. [Python html](https://docs.python.org/3.12/library/html.html). Statik yapı için yerel dosya yolu güvenliği, güvenli URL, kaynak metninden betik çalıştırma ve başarısız üretimde eski çıktının korunması ilgili tehditlerdir. Kimlik doğrulama/oturum altyapısı bu fazın ihtiyacı değildir.

## Validation Architecture

### Test altyapısı ve Wave 0

Yeni repo için Python `unittest`; önerilen hızlı/tam komut `python3 -m unittest discover -s tests -v`. Testler henüz yoktur. Önce keşfin sıfır testle sahte başarı vermemesini sağlayan test sayısı/başarı çıktısı kontrolü, yerel küçük belge fixture'ları, scratch DB düzeni ve statik bağlantı denetimi kurulmalı. Gerçek kaynaktan bir kayıt yazılıp bağlantı kapanmalı, yeniden açılıp HTML'ye taşınmalı. [unittest](https://docs.python.org/3.12/library/unittest.html).

| Katman | Anlamlı kontrol |
|---|---|
| Kapsam/kimlik | Dokuz adın korunması, dışlama gerekçeleri, parti/üye/grup ayrımı, eski aynı adlı mali belgenin reddi |
| DB/kanıt | Gerçek yazma–kapatma–yeniden okuma; yabancı anahtar; kanıtsız bulgu ve yanlış belge sürümü reddi |
| Arşiv | Hash, MIME, özgün URL, yerel dosyanın bulunması, PDF/HTML pasaj doğrulaması ve bozuk kopyanın reddi |
| Yöntem | Ayrı tarihler/kesim; zincir döngüsü, yeni sürüm, kapanma/yeniden açılma; kotasız bütün uygun eşleşmeler |
| Eksikler/mali veri | Girişimsiz eksik kaydının reddi; üç durum ayrımı; `NULL` ile `0` ayrımı |
| Üretim | Kaynak içi/sekme altı bağlantılar; bütün gerekli alanların dışa aktarımı; kaçış/güvenli URL ve göreli arşiv yolları |

Her görevden sonra hedefli test, her dalga sonunda tam paket ve gerçek veri bütünlüğü kontrolü çalıştırılır. Komutlar sonlu olmalı; sıfır test/boş çıktı kabul değildir. Test süresi hedefi hızlı kontrolde 30 saniyenin, tam otomatik kontrolde 60 saniyenin altında; bunlar henüz ölçülmemiş hedeflerdir.

### Tarayıcı ve insan doğrulaması

Araştırmacı PATH'te tarayıcı bulamadı; kullanıcı Playwright önbelleğindeki Chrome for Testing'i başlatıp küçük headless JavaScript tıklama probunu çalıştırdı. Bu ürün doğrulaması değildir. Yürütmede tarayıcı yolu yeniden keşfedilmeli; kullanıcıya özgü mutlak cache yolu uygulamaya gömülmemeli. [Chrome headless](https://developer.chrome.com/docs/automation-and-testing/headless).

Gerçek raporda kaynak bağlantısına tıklama, hash ile doğrudan açılış, geri/fokus, klavye sekmeleri, dar ekran, çevrimdışı arşiv açılışı ve özet/alıntının birlikte görünmesi doğrulanır. Otomatik DOM kontrolleri görsel/pasaj incelemesinin yerine geçmez. Araştırmacı isteğe bağlı Playwright paketini yenilik denetiminde işaretledi; bu yığın harici paket kurulumu gerektirmez. Sonradan seçilecek paketler mevcut GSD denetiminden geçirilmelidir.

### İçerik doğrulaması

Pilotun her önemli bulgusu bağlı özgün pasajla karşılaştırılmalı; kısa alıntı gerçekten değişmeden aktarılmalı, özet kaynak sınırını aşmamalı. Her beş başlık gerçek kaynaklı bulgu veya denenmiş girişime bağlı durum içerir. Gerçek bulunmayan olay/mali veri uydurulmaz. İnsan son incelemesi, yazılım testleri yeşil olsa bile kaynak doğruluğunu ve tarafsız sunumu ayrıca kontrol eder.

## Planlama için açık işler

1. Kimlik ve TBMM kapsamını tarihli özgün kopyalarla arşivlemek; ön liste farklarını gerekçeyle kaydetmek.
2. Tek bir kanonik kayıt/snapshot ve scratch işlem protokolünü belirlemek; DB → JSON → rapor akışını tek gerçek kaynakla uçtan uca kanıtlamak.
3. Veri kesimini, konu sözlüğünü, zincir iş kuyruğunu ve girişime bağlı eksik durumlarını somutlaştırmak.
4. Tüzük/program otoritesini ve özgün sürümleri doğrulamak; pilotun beş başlığını tamamlamak; söylem/uygulama ve mali belgelerde güncel tüzel kimliğe bağlama yapmak.
5. Bütün bulgu/kanıt ilişkilerini ve gerçek tarayıcı davranışlarını doğrulamak; sonraki faz içeriklerini henüz incelenmedi olarak bırakmak.

## Kaynak denetimi ve güven sınırı

Kaynaklar bu dosyadaki doğrudan bağlantılardır; yapay zekâ bilgisi siyasi olgu kaynağı değildir. Yargıtay/TBMM burada okunmuştur, fakat bu okuma yürütmedeki hash'li özgün arşiv kopyası yerine geçmez. Diğer belge yolları ve teknik çevre gözlemleri ayrı araştırmacının dönüşünden kaydedilmiştir. Modelin bildirdiği kuruluş tarihini yürütmede tekrar kontrol edip arşive bağlayın; eski aynı adlı oluşumların belgeleri ayrı kalsın.
