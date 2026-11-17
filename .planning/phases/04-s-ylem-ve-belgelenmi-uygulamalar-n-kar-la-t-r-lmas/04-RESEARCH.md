# Faz 4: Söylem ve belgelenmiş uygulamaların karşılaştırılması — Araştırma

**Araştırma tarihi:** 2026-11-17
**Alan:** Kaynaklı olay araştırması; Python/SQLite kayıt sözleşmesi; değişmez snapshot ve Türkçe statik HTML
**Genel güven:** MEDIUM — yerel kod/veri doğrudan okundu; dış belge bulguları araştırma seam’inin MEDIUM sonucuyla sınırlandı.

<user_constraints>
## User Constraints (from CONTEXT.md)

[VERIFIED: 04-CONTEXT.md:15-64,130-135] Aşağıdaki kararlar bağlam belgesinden kelimesi kelimesine aktarılmıştır.

<!-- DATA_7mF2qR8p_START -->
### Locked Decisions

### Söylemle olayın eşleştirilmesi

- **D-01:** Eşleştirme için kaynaklarla açıklanabilen konu ve kapsam bağı yeterli olabilir. Belgeler aynı somut meseleyi ilgilendiriyorsa neden karşılaştırılabilir oldukları açıkça yazılır. Kaynağın eylemi ilgili vaade açıkça bağlaması zorunlu değildir; eylemin o vaadi gerçekleştirmek amacıyla yapıldığı varsayılmaz.
- **D-02:** Aynı ilke veya vaade bağlı bütün uygun uygulamalar tek ilke/vaat altında tarih sırasıyla gösterilir. Söylem bir kez sunulur; her olay kendi tarihi, kaynakları ve karşılaştırma açıklamasıyla yer alır.
- **D-03:** Bir olay birden fazla ilkeyle ilgiliyse ilgili her ilkenin altında kısa olay kaydı ve o ilkeye özgü ilişki açıklaması bulunur. Diğer eşleşmelere bağlantı verilir. Ortak olay kimliği ve bağlantıları aynı olayın ayrı ayrı gerçekleşmiş olaylar gibi değerlendirilmesini önler.
- **D-04:** Belgelenmiş bir uygulama bulunur, fakat ilişkilendirilebilecek ilke/vaat bulunamazsa uygulama ilgili konunun içinde ayrı gösterilir. Söylem aramasının sonucu belirtilir; söylem–uygulama ilişkisi hakkında sonuç çıkarılmaz. Söylem araması yapılmamışsa “Henüz incelenmedi” kalır; denenmiş aramaya dayanan gerçek eksik durumuyla karıştırılmaz.

### Uygulama kanıtı ve çelişen kaynaklar

- **D-05:** Birincil uygulama belgesine ulaşılamadığında, somut dayanağı yeterli olan tek haber veya bağımsız rapor kullanılabilir. Kaynağın olayı nasıl saptadığı, hangi iddiayı/olayı desteklediği ve belirsizlikleri açıklanır. İki bağımsız kaynak zorunluluğu seçilmedi. Birincil kaynak önceliği korunur; yalnız parti açıklamasını tekrarlayan haberler uygulamanın gerçekleştiğine ayrı kanıt sayılmaz.
- **D-06:** “Karar veya girişim”, “Fiilen yapılan” ve “Belgelenmiş sonuç” ayrı alanlarda gösterilir. Önerge verilmesi, kabul edilmesi ve hedefin gerçekleşmesi birbirinin yerine geçmez; belgede bulunmayan aşama tamamlanmış gösterilmez.
- **D-07:** Çelişen kaynaklarda ilk görünüm, desteklenen ve ihtilaflı noktaları kısa ve kaynaklı biçimde açıklar. Hangi noktanın hangi kanıta dayandığı, kaynakların nerede ayrıştığı ve neyin çözülemediği belirtilir; ilgili anlatımlar ve pasajlar birlikte sunulur. Kaynağın iddiası sırf yayımlanmış olmasıyla doğrulanmış olguya dönüşmez.
- **D-08:** Partinin veya aktörün yayımlanmış yanıtları mevcut kaynak zincirinde bulunduğu ölçüde kullanılır. Her ihtilaflı olay için ayrıca hedefli yanıt araması yapılması zorunluluğu getirilmez. Bulunan ilgili yanıtlar kaynak zinciri ve atıf kurallarıyla korunur. Yanıta rastlanmaması “yanıt vermedi” sonucuna dönüştürülmez. Kullanıcı bu soruda önerilen hedefli arama yerine açıkça bu yaklaşımı seçti.

### Zaman, yetki ve değişen tutumlar

- **D-09:** Olay, kendi dönemine ait ilgili söylemle karşılaştırılır; sonraki tutum değişiklikleri ayrıca gösterilir. Söylemin tarihi veya ilgili sürüm belirlenemiyorsa belirsizlik açıklanır. Sonradan açıklanan vaat geçmişte ihlal edilmiş gibi sunulmaz. Bu karar olay karşılaştırmalarına aittir; Faz 3'ün tüzük/program ana görünümünde en yeni saptanan sürümü öne çıkarma kararı korunur.
- **D-10:** Vaadin gerçekleşmesi partinin tek başına yetkisinde olmasa da karşılaştırmanın odağı ilan edilen hedefin gerçekleşme durumudur: önce hedef ve belgelenmiş sonuç gösterilir; partinin yetkisi, katkısı ve sorumluluk sınırları yanında kaynaklı açıklanır. Hedefin gerçekleşmemesi tek başına partinin sorumluluğunu kanıtlamaz. Kullanıcı bu soruda önerilen “önce partinin kendi adımları” yerine açıkça hedef/sonuç odağını seçti.
- **D-11:** Birden fazla partinin ortak karar veya girişimine dayanan sonuç, ortak kapsamı ve her partinin belgelenmiş katkısıyla birlikte sunulur. Destek, itiraz ve üstlenilen görev birbirinden ayrılır; belirlenemeyen katkı açık bırakılır. Bir yapıya ortak olmak bütün kararlarını desteklediğinin kanıtı sayılmaz.
- **D-12:** Aynı mesele ve karşılaştırılabilir koşullara ilişkin tarihli önceki/sonraki belgeler yeterince destekliyorsa tutum değişikliği açıklanabilir; partinin bunu ayrıca ilan etmesi şart değildir. Kaynakta bulunmayan değişiklik nedeni veya niyet varsayılmaz. Farklı koşullara ilişkin ifadeler yalnız sözcükleri farklı diye tutum değişikliği sayılmaz.

### Karşılaştırmanın okunma biçimi

- **D-13:** Söylem ile uygulama arasındaki ilişki, hangi yönlerden örtüştüklerini/ayrıştıklarını ve kanıtın sınırını somut biçimde açıklayan kısa, kaynaklı cümlelerle anlatılır. Aynı olayın farklı yönleri birlikte açıklanabilir. Okur görünümünde “Benzerlik / Farklılık / Belirlenemiyor” ilişki başlığı seçilmedi; iç veri temsili planlama ayrıntısıdır. Bu karar eksik bilgi durumlarının açık gösterilmesini kaldırmaz.
- **D-14:** İlke/vaat tüzük veya programdan geliyorsa hem Faz 3'teki ilgili konu incelemesine hem özgün pasajın kaynak kaydına doğrudan bağlantı bulunur. Kaynak kaydı, özgün belge ve arşiv zinciri korunur.
- **D-15:** Bir ilke/vaat altındaki bütün uygun olaylar tarih sırasıyla tek akışta gösterilir; sayfalama seçilmedi. Kısa olay kayıtları, kısa özet, kısa özgün alıntı ve kaynak bağlantıları açık görünür. Uzun açıklamalar ve ek belgeler açılır ayrıntılardadır. Sayısal olay kotası veya yalnız seçilmiş örnekleri gösterme yaklaşımı uygulanmaz.
- **D-16:** Partiler arası kısa özet farklı dönem ve koşullardaki kayıtları karşılaştırılabilir yönleriyle birlikte anlatabilir. Dönem, yetki ve kapsam farkları açıklamada belirtilir; doğrudan karşılaştırılamayan yönler ayrı tutulur. Ortak değerlendirmeyi yalnız aynı olay veya döneme ait kayıtlarla sınırlama seçilmedi. Birbirinden farklı tarama kapsamlarından siyasi sıralama veya kanıtsız genelleme üretilmez.

### Önceki fazlardan devreden kararlar

- Onaylı dokuz parti ve dışlama kuralları korunur. İnceleme her partinin kendi kaynaklı kuruluşundan başlar. Parti tüzel kimliği, milletvekili üyeliği ve ortak Meclis grubu ayrı tutulur; kapsam kararı siyasi değerlendirme değildir.
- Tüzük/programlardan türetilmiş ortak konular araştırma için temeldir. Tarama sırasında bulunan bütün uygun, yeterli kanıtlı eşleşmeler kaydedilir; uyum veya farklılık sonucuna göre eleme yapılmaz. İlgili belge bağlantıları ve çelişkiler izlenir; takip edilecek ilgili kaynak kalmadığında konu taraması gerekçesiyle kapanır ve yeni belgelerle yeniden açılabilir.
- Kurumsal kararlar ve parti adına hareket ettiği belgelenen yetkili temsilcilerin eylemleri esas alınır. Milletvekillerinin bireysel oy ve açıklamaları kendi aktörleriyle ayrı tutulur; kurumsal tutuma bağlanmaları kanıta dayanır.
- Parti yayınları, atıflı haberler ve sosyal paylaşımlar kullanılabilir. Faz 2 D-13–D-16 geçerlidir: alan adı için sicil kanıtı, tarihsel yürürlük kanıtı veya her kaynakta insan kabulü içerik kullanımının ön koşulu değildir. Sicil kimliği kendi kaynağıyla tutarlı kalır. Olay dönemi ilişkisi açıklanır; belirsiz tarihler ve belge sıraları uydurulmaz.
- Kaynak beyanı, doğrulanmış olgu ve yorum ayrılır. Partinin kendi açıklaması söylemin yapıldığına kanıt olabilir; uygulamanın gerçekleşmesi ayrıca desteklenir. Yapay zekâ modelinin bilgisi kaynak olarak kullanılmaz.
- Doğrudan alıntı siyah ve tırnak içinde; kaynaklı özet/düzenleme koyu mavidir. Görünür metin kökeni etiketleri kullanılmaz; metin kökeni kayıtlarda korunur. Kısa özet ve kısa alıntı kaynak bağlantılarıyla birlikte görünür.
- Belge tarihi/sürümü, söylem ve olay tarihleri, erişim ve doğrulama tarihleri ayrı tutulur. Her bulgu kendi pasajına ve belge sürümüne bağlıdır; erişim tarihi belge sürümünün tarihsel sırasını tek başına kanıtlamaz.
- “Bulunamadı”, “Erişilemedi” ve “Doğrulanamadı” belgelenmiş girişime dayanır; “Henüz incelenmedi” ayrıdır. Eksik kanıt uyum, çelişki veya parti lehine/aleyhine sonuç değildir.
- Ana sekmeler ve ortak konu içinde partilerin alt alta sunumu korunur. Parti sırası Yeni Parti → TİP → DEM Parti → İYİ Parti → Yeni Yol Partisi → DBP → EMEP → Saadet Partisi → Demokrat Parti'dir. Karşılaştırma ile ilgili parti dosyası arasında doğrudan karşılıklı bağlantılar bulunur.
- Okur önce gerçek parti içeriğini görür; teknik yöntem ve eski girişimler kapalı ayrıntılardadır. Özgün baytlar, pasif yerel arşivler ve önceki değişmez rapor sürümleri korunur. Puanlama ve siyasi sıralama yapılmaz.


### the agent's Discretion


- Kullanıcı “sen karar ver” seçeneği kullanmadı; yukarıdaki 16 içerik/sunum tercihi açık seçimlerdir. Teknik yapı ve somut araştırma işi mevcut iş akışında araştırmacı/planlayıcı tarafından belirlenir.
- Mevcut Faz 3 konu sözlüğüyle olay/ilke ilişkilerinin nasıl kurulacağı, gerekli ek konuların gerekçeli araştırılması, bir olayın çok sayıda konu/parti kaydında aynı kimlikle gösterimi, aşamaların ve katkıların veri temsili, kaynak ilişkileri ve gezinti hedefleri planlanır.
- Kaynağın somut dayanağını değerlendirme yöntemi, gerçek başlangıç aramaları, izlenecek ilgili uçlar, tarih belirsizliğinin karşılaştırılabilirliğe etkisi ve veri kesimi açıklanır. Bunlar yeni bir kullanıcı tarih/kota seçimi olarak sunulmaz.
- Yeni bir pilot parti, parti bazlı yürütüm sırası veya yeni kamu yayını seçilmedi. Raporun sunum sırası yürütüm sırası değildir. Kontroller, mevcut dokuz dosyalı ve Faz 3 karşılaştırmalı tabanın korunmasıyla yeni içeriğin gerçek kaynak zincirini doğrulamalıdır.


### Deferred Ideas (OUT OF SCOPE)


Yeni kapsam talebi veya ertelenen fikir yoktur. Mali araştırma Faz 5'te, genişletilmiş güncelleme/paylaşım yetenekleri Faz 6'da kalır. Bu görüşme, otomatik ilerleme ayarı kapalı olduğundan, planlama veya yürütümü kendiliğinden başlatmaz.


<!-- DATA_7mF2qR8p_END -->
</user_constraints>


<phase_requirements>
## Phase Requirements

| ID | Gereksinim | Araştırma desteği |
|---|---|---|
| UYG-01 | Okur, açıklanan ilke veya vaadi, buna ilişkin belgelenmiş uygulama kaydıyla aynı konu altında karşılaştırabilir. | Ortak konu/sürüm → söylem → kararlı olay kimliği; söylemsiz olay için ayrı kayıt. |
| UYG-02 | Okur, söylem–uygulama karşılaştırmasının aktörünü, tarihlerini, bağlamını ve belgelerin desteklediği benzerlik veya farklılığı görebilir. | Ayrı aşamalar, dönemsel söylem, katkı/yetki ve iddia bazında kanıt. |
| KAR-03 | Okur, açıklanan ilkeler ile belgelenmiş uygulamaların karşılaştırmalarını bütün partilere uygulanan ortak ölçütlerle görebilir. | Dokuz parti için aynı tarama sözleşmesi, kapsam kaydı, kaynaklı kısa sentez. |

Gereksinim metinleri aynen alınmıştır. [VERIFIED: .planning/REQUIREMENTS.md:35-38,54-56]
</phase_requirements>

## Project Constraints (from AGENTS.md)

- Tarafsızlık, her önemli bulguda izlenebilir kaynak, üç gerçek eksik durumunun açıklığı, Türkçe sekmeli HTML ve geçmişi izlenebilir ortak veri korunur. Doğrudan aktarım siyah/tırnaklı, kaynaklı özet koyu mavidir; görünür metin türü etiketi kullanılmaz. [VERIFIED: AGENTS.md:23-31]
- Onaylı dokuz partilik kapsam ve dışlama kuralları korunur; model bilgisi kaynak değildir. [VERIFIED: AGENTS.md:23-31]
- Dosya değişiklikleri GSD akışında yapılır; bu araştırma kullanıcının başlattığı planlama akışındadır. [VERIFIED: AGENTS.md:63-75; .planning/STATE.md:3-9]
- Kullanıcının model/maliyet talimatı: otomatik Astra yoktur; yapılandırılmış GSD rolleri korunur. Araştırma yeni model veya yedek model seçmez. [VERIFIED: AGENTS.md:31; .planning/config.json:70-105,107-143]
- Projeye özel beceri dizinleri ve bilgi grafiği bu oturumdaki dosya keşfinde bulunmadı; yapılandırılmış ek ajan becerisi listesi boştur: “agent_skills”: {}. Bu gözlem, başka ortamlar hakkında yokluk iddiası değildir. [VERIFIED: .planning/config.json:61-64; 2026-11-17 yerel dosya keşfi]

## Summary

Mevcut uygulamayı genişletin; yeni uygulama çatısı veya bağımsız veri deposu kurmayın. Pilot eşleştirme, arşiv ve yayın zinciri vardır; dokuz partiyi kapsayan yeni olay araştırması henüz bunlardan türetilemez. Geçerli sürüm “9003e475ee5d49b29a1310c0bfe2007d”, veri şeması “6”, üretici “24”, karşılaştırma sözleşmesi “2”, sözlük “4” ve aşama “complete” değerlerini taşır. [VERIFIED: data/current.json:1; data/releases/9003e475ee5d49b29a1310c0bfe2007d/manifest.json:1; aynı sürüm records.json:5777-5782]

Salt okunur sayımda 16 action ve 18 match vardır; action kayıtlarının tamamı Yeni Parti'ye bağlıdır. Bunlar mevcut arşiv kayıtlarıdır. Testteki amaçlı olaylar farklıdır: kaynak testinin kendi açıklaması “Purpose-made fixtures: neither source is asserted to be a real event.” şeklindedir. Test pasajları siyasi araştırmaya taşınmamalıdır. [VERIFIED: 2026-11-17 güncel records.json sayımı; tests/test_matches.py:22-40]

**Ana öneri:** Eski action/match kayıtlarını koruyan eklemeli bir olay katmanı, açık bir Faz 4 sözleşmesi ve ayrı kabul denetimi kurun. Aynı olayın parti/ilke bazlı yorumlarını olayın kendisinden ayırın; kaynak → pasaj → sürüm → yerel rapor zincirini mevcut yayıncı üzerinden sürdürün. Bu, D-01–D-16'nın teknik karşılığı olan tasarım önerisidir.

## Architectural Responsibility Map

Aşağıdaki dağılım önerilen görev sahipliğidir; mevcut kaynak/snapshot/HTML ayrımını sürdürür. [VERIFIED: src/arsiv.py:2670-2812,3165-3247; src/rapor.py:163-210]

| Yetenek | Birincil katman | İkincil katman | Planlama kararı |
|---|---|---|---|
| Kaynağı değerlendirme, olay ve karşılaştırma yazma | Araştırmacı/yerel CLI | Kaynak arşivi | Anlam kararını tarayıcı üretmez. |
| Olay, aktör, dönem, aşama, katkı ve tarama bütünlüğü | Python doğrulayıcı | SQLite | Aynı kurallar yükleme ve export sırasında çalışır. |
| Değişmez snapshot ve geri üretim | Python yayıncı | Dosya sistemi | Denetimden sonra atomik current geçişi. |
| Ortak konu ve parti görünümü | Statik HTML üretici | Tarayıcı | Tek veriden iki görünüm ve karşılıklı bağlantı. |
| Sekme, odak, hash ve ayrıntı açma | Tarayıcı | — | Siyasi yorum ve kaynak yeterliliği kararı içermez. |

## Standard Stack

| Bileşen | Doğrulanan durum | Kullanım |
|---|---|---|
| Python standart kitaplığı | Oturumda “3.12.2”; uygulama sqlite3/json/urllib/argparse kullanıyor. [VERIFIED: 2026-11-17 ortam probu; src/arsiv.py:2-20] | Mevcut CLI ve doğrulayıcılar. |
| SQLite | Python bağında “3.41.2”. [VERIFIED: 2026-11-17 sqlite3.sqlite_version probu] | Yerel scratch üzerinde tek yazıcı; kapalı snapshot. |
| Mevcut HTML/CSS/JavaScript | “RENDERER_VERSION = 24”; “rapor_v24.css”. [VERIFIED: src/rapor.py:11-20] | Yeni üretici sürümü; tarihsel üretici ve stil korunur. |
| unittest + gerçek Chromium | Çalıştırıcı unittest keşfi yapıyor; bulunan tarayıcı “Google Chrome for Testing 156.0.8078.4”. [VERIFIED: tests/run.py:1-18; 2026-11-17 tarayıcı probu] | Sözleşme ve gezinti kontrolleri. |
| Poppler/GObject/GLib/Cairo | Dört kütüphane bu oturumda bulundu ve ctypes ile yüklendi. [VERIFIED: 2026-11-17 yerel native yükleme probu] | PDF pasaj denetimi. |

**Kurulum / Package Legitimacy Audit:** Yeni harici paket önerilmiyor; kurulum ve paket meşruiyeti kapısı uygulanmaz. Sistem araçlarının mevcut olması yeni sürüm kurulmasını gerektirmez. Sürümler yukarıdaki ortam ölçümleridir; yayımlanma tarihi iddiası değildir.

## Architecture Patterns

### Sistem akışı

~~~mermaid
flowchart TD
  A[Arşivli konu ve dönemsel söylem] --> B[Ortak araştırma kapsamı]
  C[TBMM / kurum / parti / haber / bağımsız rapor] --> B
  B --> D[Kaynak zinciri ve pasaj doğrulaması]
  D --> E{Kanıt hangi aşamayı destekliyor?}
  E --> F[Karar veya girişim]
  E --> G[Fiilen yapılan]
  E --> H[Belgelenmiş sonuç]
  F --> I[Ortak olay kimliği + aktör katkıları]
  G --> I
  H --> I
  D --> J[Belgeli eksik / ihtilaf / açık uç]
  I --> K[Dönemsel söylemle kaynaklı ilişki]
  J --> K
  K --> L[Kapalı SQLite → JSON → HTML]
  L --> M[Parti dosyası ↔ ortak konu ↔ kaynak/arşiv]
~~~

Bu diyagram önerilen Faz 4 akışıdır; kaynağın yayımlanması tek başına iddiayı olguya dönüştürmez. [VERIFIED: 04-CONTEXT.md:20-44,48-57]

### Değişecek bileşenler ve sınırlar

| Bileşen | Mevcut bulgu | Yapılacak iş |
|---|---|---|
| src/arsiv.py::check_match | “2026-07-24” başlangıcı sabit; aynı parti, tek aktör ve ayrı beyan/oluş pasajı arıyor. [VERIFIED: src/arsiv.py:2384-2416] | Pilot sabitini kaynaklı parti kuruluşuyla değiştirin; eski sözleşmenin anlamını yeniden yazmayın. |
| src/dosyalar.py::foundation_for_party | “entity_kind='party'” ve tek “valid_from” kaydını check_identity ile denetliyor. [VERIFIED: src/dosyalar.py:59-72] | Bütün parti dönemlerinin tek otoritesi olarak yeniden kullanın. |
| src/arsiv.py::record / export_db | event_date zaten foundation_for_party kullanıyor. [VERIFIED: src/arsiv.py:2246-2256,2724-2731] | Match ve yeni olay denetimlerini bu semantiğe hizalayın. |
| src/arsiv.py::comparison_render_data | Aktif revision.selection ile konuları/satırları/sentezleri seçiyor; yalnız belirli tablolardaki finding referanslarını koruyor. [VERIFIED: src/arsiv.py:2817-2852] | Yeni olay/söylem referanslarını koruyun; tarihsel bir pasaj görünüm filtresiyle kaybolmasın. |
| src/rapor.py::add_matches | Olay ve söylem details içinde; “relation” metni görünür. [VERIFIED: src/rapor.py:408-438] | D-13/D-15 için yeni gruplu açık kısa kart görünümü; ilişki sınıfı başlığı gösterilmez. |
| src/rapor.py::render_report | Parti ve Karşılaştırmalı Özet ayrı üretiliyor; citation/fragment yardımcıları var. [VERIFIED: src/rapor.py:207-210,440-445,537-573] | Tek sunum fonksiyonunu iki görünümde farklı DOM kimlikleriyle kullanın. |
| src/dosyalar.py::validate_delivery_prefix | Tamamlanmış Faz 2 teslimi refresh ile korunuyor. [VERIFIED: src/dosyalar.py:75-100] | Yeni parti sırası/receipt oluşturmayın; yerel refresh kullanın. |

### Önerilen eklemeli veri sözleşmesi

Aşağıdaki isimler **yeni tasarım önerileridir**; mevcut tablo/enum oldukları ileri sürülmez. Yeni modülü önerilen src/uygulamalar.py altında tutun; yalnız CLI/export/yayın bağlantılarını arsiv.py'ye ekleyin.

| Önerilen kayıt | İçerik ve zorunlu bağlar |
|---|---|
| Faz 4 sözleşmesi | Sözleşme sürümü, aşama, temel release, yöntem kesimi, konu sözlüğü; partial/complete geçişinin kanıtı. |
| Olay | Parti/konudan bağımsız kararlı kimlik; konu, yer, olay zamanı/kesinliği ve kapsamı. Bir URL ya da bir match, olay kimliği değildir. |
| Olay aşaması | Karar/girişim, fiilen yapılan ve belgelenmiş sonuç için ayrı bulgu + alıntı/özet + pasajlar; bilinmeyen aşama için gerçek eksik veya incelenmeme kaydı. |
| Olay katılımcısı | Parti, kişi veya ortak grup; olay dönemindeki rol, destek/itiraz/görev, kaynaklı yetki ve katkı sınırı. Ortak sonuç bir kere tutulur. |
| Söylem | Bulgu çifti, tarih/kesinlik, belge sürümü, koşullar/hedef; varsa Faz 3 konu satırı ve özgün pasaj. |
| Söylem–olay ilişkisi | Söylem, olay, parti, ortak konu+sürüm; karşılaştırılabilir kapsam, hedef/sonuç açıklaması, yetki/katkı sınırı, tarih belirsizliği ve yorumun kaynakları. |
| İhtilaf / yanıt | Hangi iddianın hangi pasajla desteklendiği veya ihtilaflı olduğu; mevcut zincirde bulunan yanıt; çözülemeyen nokta. |
| Söylemsiz olay | İlgili konu, olay ve söylem aramasının gerçek sonucu; sahte söylem üretmeden aynı görünümde sunum. |
| Tutum değişikliği | Tarihli önce/sonra pasajlar, aynı mesele/karşılaştırılabilir koşullar ve kaynaklı açıklama; kaynakta olmayan niyet eklenmez. |
| Araştırma kapsamı/kapanışı | Parti + konu+sürüm + dönem + araştırma türü; başlangıç sorguları, ilgili uçlar, girişimler, adaylar, kapanma gerekçesi ve yeniden açılma. |
| Pilot köprüleri | Eski action/match/aday kimliğinden yeni olay/ilişkiye açık bağlantı; örtüşen ulusal/yerel kapsamlar için gerekçeli ilişki. |

Mevcut çekirdek kayıtlar bunun tamamını ifade etmez: “action” anahtarı “finding_id”, actor için tek “party_id”, match için “statement_finding_id” zorunludur. Yeni ortak olayı dokuz parti için dokuz ayrı olay gibi çoğaltmayın. Aynı arşiv belgesinin ortak kullanımını açık kaynak-kapsam ilişkileriyle doğrulayın; bütün sahiplik denetimlerini gevşetmeyin. [VERIFIED: src/arsiv.py:56-61,99-106,2391-2413]

### Tarama sözleşmesindeki kritik fark

Mevcut tanım “topic_search”: “topic_id TEXT PRIMARY KEY, method_version INTEGER NOT NULL, state TEXT NOT NULL”; kapanma tüm lead kayıtlarını yalnız topic_id ile topluyor. Bu nedenle bir partinin tamamlanması diğer sekiz partinin aynı konusu incelendi anlamına gelmez. Faz 4 için ayrı kapsam kimliği ve parti/konu/dönem anahtarı ekleyin; eski kapanışları yeniden adlandırmayın. [VERIFIED: src/arsiv.py:79-87,2495-2519]

Kapsam envanteri, aday listesi ve sonuç listesini ayrı tutun. Bütün uygun eşleşmeler listede kalmalı; dışlanan adayın gerekçesi, çözülemeyen ucun gerçek durumu bulunmalıdır. Kapanma, ilgili takip ucu kalmamasıyla gerekçelendirilir; tarih boyunca her olayın bulunduğu iddiası değildir. [VERIFIED: 01-CONTEXT.md:25-34; 04-CONTEXT.md:48-55]

### Şema / snapshot / üretici geçişi

Öneri: eklemeli tabloları açık bir yeni veri şeması ve Faz 4 sözleşmesiyle etkinleştirin; mevcut şema 6 snapshot'larının export biçimini değiştirmeyin. Yeni numara olarak şema 7 ve üretici 25 kullanılabilir; bunlar **önerilen yeni değerlerdir**, mevcut sabit değildir. Geçiş kararı ilk teknik planda tek yerde sabitlensin.

Önce mevcut üretici 24'ü ayrı tarihsel modül olarak dondurun ve mevcut stilini koruyun. Denetim renderer dispatch'i, geçerli üretici listesi, kaynak politikası şema dalları, Faz 3 denetimi ve manifest üretimi birlikte güncellenmelidir; yalnız RENDERER_VERSION artırmak eski sürümü yeniden üretemez. Mevcut kodda “(5,6)” ve “schema_version == 6” dalları vardır. [VERIFIED: src/arsiv.py:2885-2941,3104-3108,3218-3236]

Migration yalnız workspace kopyasında: SQLite backup → transaction → yeni tablolar → integrity/foreign_key denetimi → commit; hata durumunda rollback ve current korunması. Mevcut örnek bu sırayı kullanır. [VERIFIED: src/dosyalar.py:30-56; src/arsiv.py:397-422] SQLite'ın ADD COLUMN kısıtları nedeniyle eski NOT NULL ilişkileri kaldırmaya çalışmak yerine yeni tablolar kullanın. [CITED: https://www.sqlite.org/lang_altertable.html] Python backup API bu işlem için mevcuttur. [CITED: https://docs.python.org/3.12/library/sqlite3.html#sqlite3.Connection.backup]

Faz 3 sözlüğü ve complete kabulü ayrı kalmalıdır. Yeni olay araştırması için Faz 3 sözleşmesini partial'a düşürmeyin. Yeni konu gerekirse kaynaklı gerekçe, bütün partilerde geri tarama ve mevcut sözlük/soy geçişi ayrı iştir. Eski karşılaştırma verilerinin silinmesi/yeniden yorumlanması descent denetimlerine takılır. [VERIFIED: src/arsiv.py:2103-2161]

## Dönem ve dokuz parti için gerçek başlangıçlar

Geçerli yöntemin kesimi “2026-11-10T14:38:46.154751+00:00”, dayanağı “tbmm-scope-v1”dir. Yeni erişim tarihi bu kesimi kendiliğinden değiştirmez. Aynı yöntemi koruyun; kesim sonrası erişilen belge kesim öncesi olayı destekleyebilir. [VERIFIED: güncel records.json:637856-637865; src/arsiv.py:2643-2665; README.md:34-36]

Aşağıdaki kuruluş tarihleri **mevcut arşivin valid_from değerleridir**; bu araştırmada yeniden yapılmış tarihsel kimlik kararı değildir. Tarih/sicil çiftleri aynen aktarılmıştır. [VERIFIED: güncel records.json:633973-634045]

| Parti | Kaynaklı başlangıç / sicil değeri | Somut kaynak başlangıcı ve araştırma yönü |
|---|---|---|
| Yeni Parti | “2026-07-24” / “yargitay-365” | [Tüzük](https://yenipartiyiz.biz/parti-tuzugu), [program](https://yenipartiyiz.biz/parti-programi); mevcut pilot ön seçim kaynak zinciriyle başlayın. Ulusal/yerel örtüşmeyi ve ön seçim–kongre ayrımını koruyun. |
| TİP | “2017-11-07” / “yargitay-208” | [Program](https://tip.org.tr/parti-programi); sitedeki MYK/Parti Meclisi değerlendirmeleri ve kanun teklifi/soru önergesi bağlantılarını TBMM asıllarına izleyin. |
| DEM | “2012-11-30” / “yargitay-157” | [Kongre kararları](https://www.demparti.org.tr/tr/4-uncu-olaganustu-buyuk-kongre-kararlari/20375/); önerge/teklif/başvuru ve grup konuşması menüleri. Ek kongre belgesini tam program diye yeniden adlandırmayın. |
| İYİ Parti | “2017-10-25” / “yargitay-207” | [Kurumsal kaynak](https://www.iyiparti.org.tr/iyi-parti/), arşivli program ve eski tüzükler; dönemsel TBMM tutanak/teklifleriyle eşleyin. |
| Yeni Yol | “2025-01-13” / “yargitay-331” | [TBMM tutanak kaydı](https://www.tbmm.gov.tr/Tutanaklar/TutanakGoster/5242), [grup imzalı önerge](https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T7/WebOnergeMetni/7ee84bf0-e6ea-4715-a53b-26a6afb2c760.pdf); grup, tüzel parti ve imzacı üyeliği ayrı araştırın. |
| DBP | “2008-05-02” / “yargitay-117” | [Tüzük](https://dbp.org.tr/parti/tuzuk); basın açıklaması/rapor menüleri ve arşivli tarihsel BDP nüshaları. Ad değişikliğini yeni kuruluş veya ayrı HDP kimliğiyle karıştırmayın. |
| EMEP | “1996-11-25” / “yargitay-52” | [Program ve tüzük](https://www.emep.org/emek-partisi-program-ve-tuzugu); tarihli kongre metinleri, TBMM teklif/konuşma asılları. Ayrı 1996 Emek Partisi belgesi otomatik aynı kimlik sayılmaz. |
| Saadet | “2001-07-20” / “yargitay-70” | Arşivli [program](https://admin.saadet.org.tr/dosyalar/K-D-1751227555.pdf), [tüzük](https://admin.saadet.org.tr/dosyalar/K-D-1751227541.pdf); TBMM kaynakları ve dönemsel kurumsal açıklamalar. Yeni Yol ortaklığı her olaya destek kanıtı değildir. |
| Demokrat | “1983-06-23” / “yargitay-3” | Arşivli [program](https://web.archive.org/web/20211229025938id_/https://www.dp.org.tr/storage/DP.Yeni.Program.pdf), [tüzük](https://web.archive.org/web/20220618225341id_/https://www.dp.org.tr/storage/DP.T%C3%BCz%C3%BCk.2022.pdf), TBMM açık erişim tarihsel DYP belgeleri. Ad/kimlik devamını kaynakla izleyin. |

Erişim: 2026-11-17. Yeni Parti tüzüğü, TİP programı, DEM kongre sayfası, İYİ kurumsal sayfası, DBP tüzüğü ve EMEP metni bu oturumda açıldı; yukarıdaki menüler bu sayfalarda görüldü. Yeni Yol başlangıçları resmî TBMM kaynaklarıdır. Bunlar yeni kabul edilmiş siyasi olay/sonuç değildir. [CITED: https://tip.org.tr/parti-programi] [CITED: https://www.demparti.org.tr/tr/4-uncu-olaganustu-buyuk-kongre-kararlari/20375/] [CITED: https://dbp.org.tr/parti/tuzuk] [CITED: https://www.emep.org/emek-partisi-program-ve-tuzugu] [CITED: https://www.tbmm.gov.tr/Tutanaklar/TutanakGoster/5242]

Saadet ana sayfası bu oturumda okunabilir metin döndürmedi; dp.org.tr isteği zaman aşımına uğradı. Bu araç gözlemleri “belge yok” sonucu değildir. Son iki partinin tabloda verilen belge adresleri mevcut arşiv envanterinden başlangıçtır; bu oturumda yeniden indirilmiş oldukları ileri sürülmez. [VERIFIED: 2026-11-17 web erişim çıktıları ve güncel dossier_source/document_version okuması]

Ortak birincil başlangıçlar: [TBMM tutanak sorgusu](https://tbmm.gov.tr/Tutanaklar/TutanakSorgu), [kanun teklifleri](https://tbmm.gov.tr/yasama/kanun-teklifleri), [sorgu açıklamaları](https://tbmm.gov.tr/Sayfa/Kanun-Teklifleri-Sorgu-Formu-Kullanim-Bilgileri). Teklif formunda dönem, teklif sahibi, tarih ve son durum alanları; aşama/metin bağlantıları vardır. Her parti/konuda dönem ve aktör adlarını kullanarak arayın, bulunan resmî belge numaralarını takip edin. [CITED: https://tbmm.gov.tr/yasama/kanun-teklifleri] [CITED: https://tbmm.gov.tr/Sayfa/Kanun-Teklifleri-Sorgu-Formu-Kullanim-Bilgileri]

## Kanıt kabulü ve Don't Hand-Roll

| Problem | Önerilen yaklaşım |
|---|---|
| Bir haberden olay çıkarmak | Kaynağın somut dayanağını, hangi aşamayı desteklediğini ve sınırını kaydedin. Tek yeterli haber kabul edilebilir; parti açıklaması tekrarı oluş kanıtı değildir. [VERIFIED: 04-CONTEXT.md:25-30] |
| Haber için epistemik tür seçmek | Kaynak politikası gazetecilik/parti/sosyal bulgusunu “claim” veya “comment” ister. Haber dayanaklı olay desteğini bunu “fact”e çevirerek sağlamayın; olay incelemesi ile kaynağa atfı ayrı tutun. [VERIFIED: src/kaynaklar.py:93-106] |
| Siyasi doğruluk puanı / otomatik niyet | Kaynaklı kısa açıklama kullanın; benzer sözcüklerden niyet veya vaat gerçekleştirme amacı türetmeyin. [VERIFIED: 04-CONTEXT.md:20,34-44] |
| Kaynak arşivi / PDF çıkarımı / güvenli HTML | Mevcut capture, pasaj, atıf, pasif görünüm ve citation yardımcılarını kullanın. Yeni scraper/HTML çalıştırıcısı kurmayın. [VERIFIED: src/arsiv.py:2738-2772; src/arsiv_gorunum.py:16-23; src/rapor.py:207-210] |
| Güncelleme / sürümleme | Mevcut workspace + transaction + değişmez publish/refresh akışını kullanın. Üretilmiş JSON/HTML'yi elle değiştirmeyin. [VERIFIED: src/arsiv.py:3165-3247] |

## Common Pitfalls

1. **Kuruluş ve dönem:** Pilot tarihi bütün partilere uygulanırsa eski uygun olaylar dışlanır. Kuruluş günü dahildir; yalnız gün bilinen kesim-günü olayı “uncertain”, kesin an kesimi aşmıyorsa “inside” olur. Belirsizliği otomatik ihlal/uyum sonucuna çevirmeyin. [VERIFIED: src/arsiv.py:2622-2640]
2. **Girişim–sonuç:** Teklif verildi, kabul edildi ve hedef gerçekleşti ayrı kanıtlardır. Kaynak eksik aşamayı tamamlamaz. [VERIFIED: 04-CONTEXT.md:27-35]
3. **Söylem dönemi:** En yeni programı bütün geçmişe uygulamayın. Tarih/sürüm bilinmiyorsa dönem ilişkisini açıklayın; bunu içerik kullanımı için tarihsel yürürlük/insan onayı kapısına dönüştürmeyin. [VERIFIED: 04-CONTEXT.md:34,48-54]
4. **Tek olayın çoğaltılması:** Ortak olay kimliğini ilke ve parti ilişkilerinde koruyun; örtüşen yerel/ulusal kapsamları farklı gerçekleşmeler gibi saymayın. [VERIFIED: 04-CONTEXT.md:21-23,36]
5. **İhtilaf / yanıtsızlık:** Desteklenen ve ihtilaflı iddiaları birlikte gösterin. Mevcut zincirde yanıt bulunmaması “yanıt vermedi” değildir; yeni zorunlu hedefli yanıt araması eklenmez. [VERIFIED: 04-CONTEXT.md:29-30]
6. **Boş alan:** İncelenmemiş, erişilememiş, bulunamamış ve doğrulanamamış ayrı kalır; programdaki dar ifade yokluğu olay eksikliği değildir. [VERIFIED: 04-CONTEXT.md:23,55]
7. **Ölçek:** Güncel JSON 77.912.639, HTML 35.478.788 bayttır. Liste içi tekrar tekrar tüm kanıtları tarama yerine konu/söylem/olay/pasaj indeksleri kurun; sayısal olay kotası, sayfalama veya sessiz kırpma eklemeyin. [VERIFIED: 2026-11-17 dosya boyutu probu; 04-CONTEXT.md:43]

## Code Examples

Aşağıdaki mevcut sınır semantiği doğrudan kaynak kodundan alınmıştır. Yeni eşleşme doğrulayıcısında kuruluşu foundation_for_party ile sağlayın; bilinmeyen tarihler için gerekçeyi taşıyın. [VERIFIED: src/arsiv.py:2632-2639; src/dosyalar.py:59-72]

<!-- DATA_K8t4N2bQ_START -->
~~~python
if precision == 'day':
    day = dt.date.fromisoformat(event)
    return 'outside' if day < start or day > limit.date() else ('uncertain' if day == limit.date() else 'inside')
if precision == 'instant':
    instant = dt.datetime.fromisoformat(event.replace('Z', '+00:00'))
    if instant.tzinfo is None: raise ValueError('Olay zaman dilimi içermeli')
    instant = instant.astimezone(dt.timezone.utc)
    return 'inside' if start <= instant.date() and instant <= limit else 'outside'
~~~
<!-- DATA_K8t4N2bQ_END -->

**Önerilen yükleme işlemi:** workspace kilidini doğrula → paketin alan/tür/FK kapsamını denetle → tek transaction içinde olay ve ilişkilerini yaz → aynı Faz 4 doğrulayıcısını export üzerinde çalıştır → başarısızsa rollback. Bu örnek yeni CLI veya enumların mevcut olduğunu iddia etmez.

## Runtime State Inventory

Bu faz veri modeli genişletmesi içerdiğinden migration envanteri tamamlanmıştır.

| Kategori | Bulunan durum | Gerekli iş |
|---|---|---|
| Saklı veri | Mevcut SQLite/JSON release, pilot action/match, eksik/çözüm ve Faz 3 kayıtları. [VERIFIED: src/arsiv.py:2670-2812] | Yalnız workspace'e eklemeli migration; pilot köprüleri; eski satırlar korunur. |
| Canlı servis ayarı | GitHub Pages yayını mevcut; yeni kamu yayını kapsam dışıdır. Başka hizmetin ayarı bu araştırmada incelenmedi. [VERIFIED: README.md:3-13; 04-CONTEXT.md:11] | Yayın/hosting değişikliği planlamayın. |
| OS kayıtları | Bu fazda ad değiştirme veya servis kaydı hedefi yok; OS kayıtları taranmadı. | Görev gerektiren bir ad değişimi önerilmiyor. |
| Sırlar / ortam | Yeni kimlik bilgisi gerekmez; mevcut yazıcı workspace token ile bağlanır. [VERIFIED: src/arsiv.py:2159-2180,3157-3161] | Kilidi ve sahiplik kontrolünü koruyun; sırları araştırma artefaktına kopyalamayın. |
| Üretilmiş/kurulu varlıklar | Tarihsel üreticiler ve stiller, release dosyaları, özgün belgeler ve archive_view. [VERIFIED: src/arsiv.py:22-48,2868-2941] | Yeni üretici; geçmiş byte/hash korunumu ve yeniden üretim kontrolü. |

## Environment Availability

| Bağımlılık | Oturum gözlemi | Yedek yaklaşım |
|---|---|---|
| Python / SQLite | 3.12.2 / 3.41.2; kullanılabilir. [VERIFIED: 2026-11-17 ortam probu] | Mevcut standart kitaplık akışı. |
| Native PDF kütüphaneleri | Poppler-glib, GObject, GLib, Cairo bulundu/yüklendi. [VERIFIED: 2026-11-17 ctypes probu] | Başka ortamda README kontrolü; PDF içeriğini tahmin etmeyin. |
| Chromium / Node | Gerçek headless Chromium bulundu; Node “v24.21.0”. [VERIFIED: 2026-11-17 ortam/tarayıcı probları] | Mevcut browser_probe.browser veya BROWSER_BIN. |
| Context7 | MCP ve ctx7 CLI bu oturumda kullanılamadı. [VERIFIED: 2026-11-17 araç keşfi ve command -v probu] | Resmî Python/SQLite/OWASP/TBMM belgeleri web aracıyla okundu. |

Engelleyici eksik bağımlılık saptanmadı. Haber/parti sayfası erişim hatalarını belge yokluğu gibi işlemeyin.

## Doğrulama ve CLI stratejisi

Nyquist bölümü oluşturulmaz: yapılandırmada “nyquist_validation”: false. Bu, normal test ve gerçek kaynak incelemesini kaldırmaz. [VERIFIED: .planning/config.json:20-24,39-53]

- Mevcut CLI: workspace, capture, record, publish --refresh, audit --phase 1/2/3. Faz 4 audit seçeneği henüz yoktur: parser “choices=('1','2','3')” kullanır. İlk teknik dilimde yeni Faz 4 check/load ve audit aşamasını ekleyin; bunlar **önerilen yeni komutlardır**. [VERIFIED: src/arsiv.py:3262-3275]
- UYG-01: bir söylem–çok olay, bir olay–çok ilke/parti ve söylemsiz olay senaryolarını DB → JSON → iki HTML görünümüyle sınayın; bulunan bütün uygun kimliklerin korunmasını denetleyin.
- UYG-02: ayrı aşama ve kanıtlar, tek dayanaklı haber, salt parti tekrarı reddi, yanlış dönem, temsil yetkisi, ortak katkı, ihtilaf ve tutum değişikliği için anlamlı kabul/ret örnekleri kurun.
- KAR-03: dokuz partinin aynı kapsam matrisi; her kapanışın gerçek girişim/uç listesi; farklı dönem/yetki kapsamlarını açıklayan kaynaklı sentez. Hiçbir partiye olay sayısı hedefi koymayın.
- Tarihsel güvence: migration/yükleme hatasında rollback; eski renderer24'ün byte eşitliği; Faz 2 prefix ve Faz 3 complete sözleşmesinin korunması; yeni sözleşmenin manifestten kaldırılarak audit atlatılamaması.
- Gezinti: doğrudan hash, karşılıklı parti/konu bağlantısı, aynı olayın diğer ilişkileri, Faz 3 satırı, kaynak pasajı ve pasif arşiv; file/HTTP, dar/geniş ekran ve klavye odağı.
- Mevcut komutlar: “python3 tests/run.py --pattern test_matches.py”, “python3 tests/run.py --pattern test_comparisons.py”, “python3 tests/run.py --pattern test_comparison_content.py”, “python3 tests/run.py --pattern test_comparison_navigation.py”; kapsamlı kapı “python3 tests/run.py”. Seçili test çalıştırma parserı bunları destekler. [VERIFIED: tests/run.py:6-18; tests/test_matches.py:54-153; tests/test_comparison_navigation.py:83-155]
- Bu araştırmada yalnız mevcut tarih testi çalıştırıldı: “Ran 1 test in 22.151s”, “OK”, “TESTS_OK count=1”. Tam suite veya Faz 4 doğruluğu iddia edilmez. [VERIFIED: 2026-11-17 test_dates.py çalıştırma çıktısı]

## Plan dilimleri

Aşağıdaki teknik bağımlılık sırasını kullanın; parti tablosunun sırası yürütüm sırası kararı değildir.

1. **Kaynaklı sözleşme ve ilk dikey dilim:** yeni olay/katkı/tarama modeli, kuruluş semantiği, kilit/migration/rollback, pilot köprüleri; mevcut gerçek kayıt üzerinden yeni yerel görünüm. Yeni pilot parti seçmeyin.
2. **İki görünüm ve yeni denetim:** açık kısa kartlar, hedef/sonuç önceliği, aşamalar/yetki, karşılıklı bağlantılar, üretici dondurma ve yeni manifest/audit entegrasyonu.
3. **Dokuz parti için dönemsel söylem ve tarama envanteri:** Faz 3 ortak konu/koşullarını başlangıç alın; tarihsel belge erişimi ve söylem açıklarını gerçek girişimlerle kaydedin. Program/tüzük içeriğini uygulama saymayın.
4. **Belgelenmiş olay araştırma paketleri:** kurumsal kararlar ve temsilci eylemleri; TBMM girişimleri; belgelenmiş fiilî sonuçlar ve ortak olaylar. İşi kaynak/konu/dönem büyüklüğüne göre sınırlı paketlere bölün; bütün uygun olaylar eklenir, kota uygulanmaz.
5. **Kapsam kapanışı ve ortak sentez:** açık uç/çelişki takibi, söylemsiz olaylar, kaynaklı tutum değişimleri, dokuz parti kapsam kontrolü ve yeniden açılma yolu.
6. **Maddi kaynak ve kullanıcı kabulü:** teknik testlerden ayrı anlam incelemesi; önceki dokuz dosya/Faz 3/regresyon ve gerçek tarayıcı kontrolü; yalnız yerel yeni release.

## Security Domain

Güvenlik etkin: “security_enforcement”: true, “security_asvs_level”: 1, “security_block_on”: “high”. [VERIFIED: .planning/config.json:48-50] ASVS sürümünü açık yazın: resmî güncel 5.0.0 kaynağında kategori numaraları eski şablondan farklıdır. [CITED: https://asvs.owasp.org/]

| ASVS 5.0 alanı | Fazdaki kapsam / kontrol |
|---|---|
| V1 Encoding and Sanitization | Yeni bütün metin ve kimliklerde escape; URL fragment encoding; SQL değerlerinde placeholder. |
| V2 Validation and Business Logic | Parti/dönem/pasaj/sürüm bütünlüğü, transaction ve tek yazıcı; zayıf sözleşmeye geri düşme engeli. |
| V3 Web Frontend Security / V5 File Handling | Pasif arşiv, yerel varlık, kaynak script/form/frame çalıştırmama, yol/kaynak hash denetimi. |
| V6 Authentication / V7 Session Management / V8 Authorization | Yeni hesap/oturum sistemi bu fazda yok; yerel yazıcı kilidi ve dosya kökü sınırları korunur. |
| V11 Cryptography | Mevcut hashlib/standart hash kullanımı; yeni kriptografi tasarımı yok. |

Kategori adları resmî makine okunur ASVS 5.0 kaynağından doğrulandı. [CITED: https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/docs_en/OWASP_Application_Security_Verification_Standard_5.0.0_en.cdx.json] Yukarıdakiler bu faz için uygulanabilirlik önerisidir; bütün standarda uygunluk sertifikası değildir.

Başlıca tehditler: kaynak metninden XSS (Tampering/Elevation), JSON/yol girdisinden kök dışına erişim (Tampering/Information Disclosure), geçersiz paketle kısmi veya zayıflatılmış yayın (Tampering), büyük girdilerle bellek yükü (DoS). Mevcut escape/fragment, safe_path/safe_url, parametreli SQL ve pasif CSP kontrollerini yeni yollara taşıyın. [VERIFIED: src/rapor.py:33-46,207-210; src/arsiv.py:214-226,2290-2299; src/arsiv_gorunum.py:16-28]

## State of the Art

Bu fazda dış teknoloji yenilemesi gerekmez. Mevcut pilotun tek eşleşme kartından, tek olay kimliği altında dönemsel çoklu ilişki ve aşama/katkı modeline geçiş **proje içi tasarım önerisidir**. ASVS 5.0 adlandırmasını kullanın; eski kategori şablonunu sürüm belirtmeden kopyalamayın. [CITED: https://asvs.owasp.org/]

## Assumptions Log

Doğrulanmamış siyasi olay, yeni başlangıç tarihi veya kullanıcı adına seçilmiş parti yürütüm sırası eklenmedi. Teknik tablo/komut/sürüm isimleri öneri olarak işaretlendi; mevcut değer diye kullanılmamalıdır. Bu raporda [ASSUMED] düzeyinde kilitlenecek yeni bir olgusal karar yoktur.

## Araştırma soruları — planlama disposition kaydı

2026-11-17 hedefli plan revizyonu: Aşağıdaki RESOLVED işareti yalnız alınmış **tasarım/iş dağıtımı kararına** aittir. Kodun çalıştığı, bütün kaynakların erişilebilir olduğu veya siyasi/ampirik sorunun çözüldüğü anlamına gelmez. Ampirik sonuçlar belirtilen yürütüm görevi ve kanıt oluşana kadar PENDING/UNKNOWN kalır. Kanonik alanlar 04-EXECUTION-CONTRACT.md'dedir; revizyon kanıtı 04-REVISION-1.md'de izlenir.

1. **Q1 — Gerçek olay hacmi ve tarihsel erişim. Planlama disposition: RESOLVED (araştırma kuyruğu ve devam yöntemi). Ampirik sonuç: UNKNOWN; hacim ve erişilebilirlik henüz bilinmiyor.** 04-03-01 yürütücüsü bütün konu×parti×dönem×statement/event envanterinin sahibidir. 04-04-01/02 Yeni Parti, 04-05-01/02 TİP, 04-06-01/02 DEM, 04-07-01/02 İYİ, 04-08-01/02 Yeni Yol, 04-09-01/02 DBP, 04-10-01/02 EMEP, 04-11-01/02 Saadet ve 04-12-01/02 Demokrat yürütücüleri kendi bütün kaynak/konu kuyruğunu araştırır; 04-13-02 çapraz kaynak/yeni konu geri taramasını kapatır. Kanıt: 04-inventory.json, her 04-PARTY-tranches.json ve -review.json, gerçek query/URL/attempt, kaynak bölümleri, lead/closure/reopen ve SUMMARY devam konumu. Yaklaşık 12k token okuma dilimi sonunda kuyruk kaldıysa GSD continue ile yeni bağlamdan devam edilir; olay kotası veya zaman aşımı araştırma sonucu değildir. Kapanış: bütün hücre/dilimler gerçek gerekçeli kapanış veya belgelenmiş erişim/doğrulama sınırı taşır, pending uç kalmaz ve --complete coverage geçer. Sonuç bütün tarihsel olayların bulunduğu iddiası değildir.

2. **Q2 — Ortak kaynak sahipliği. Planlama disposition: RESOLVED (alanlar ve denetim sınırı). Uygulama/ampirik sonuç: PENDING.** practice_source_party(version_id,party_id,passage_id,scope_reason), kaynağın ortak kullanımını açık ve dar kapsamla yetkilendirir; başka parti kanıtını genel kabul etmez. Sahip: 04-01-01 alan/yükleme/export bağlantısı; 04-02-02 kabul/ret ve gerçek dönemsel aktör/katkı denetimi. Kanıt: src/uygulamalar.py ve test_practice_tracer.py/test_practice_contract.py'de ortak kaynak kabulü, yetkisiz başka-parti kanıtı reddi; gerçek araştırma paketlerinin source_review kayıtları. Başarısız kontrol varsa aynı görevde düzeltip devam edilir. Kapanış: aynı sahiplik kuralı load/export/audit/iki görünümde korunur ve gerçek paylaşılan kaynağın kullanım gerekçesi varsa kaydedilir; gerçek ortak kaynak bulunacağı peşinen ileri sürülmez.

3. **Q3 — Pilot toplu/yerel olay örtüşmesi. Planlama disposition: RESOLVED (maddi inceleme ve tekrar üretilebilir karar yolu). Ampirik özdeşlik/ayrılık sonucu: UNKNOWN.** Sahip: 04-04-01/02 bütün mevcut pilot kaynaklarını inceler; 04-13-01 kaynaklı same/distinct/unresolved kararlarının ve 04-13-02 yeni backscan kararlarının sahibidir. 04-03-02 teknik yürütücüsü --event-decisions girdisi, practice_event_decision/alias ve digest bağlı merge_provenance'ı kurar. Kanıt: gerçek pasaj/sürüm/bağlam, 04-shared-events.json, dokuz özgün paket+gerektiğinde 04-backscan.json, merged DB/JSON/manifest ve iki görünüm. Adayda kanıt yetmiyorsa ayrı kayıtlarla unresolved ve kaynaklı belirsizlik korunur; otomatik özdeşlik veya kesin ayrılık üretilmez. Yeni ilgili uç varsa araştırma/reopen devam eder. Kapanış: bütün adaylar dayanaklı karar veya dürüst unresolved disposition taşır; aynı girdiler+kararlar aynı kimlik/ilişki/katkı/kanıt başvurularını üretir ve audit bunları korur. Eski action/match satırları yeniden onaylanmış gibi sunulmaz.

4. **Q4 — Tarih/sürüm belirsizliği. Planlama disposition: RESOLVED (kaynak bazlı dönem açıklaması; yeni yürürlük kapısı yok). Ampirik belge sırası/karşılaştırılabilirlik: UNKNOWN.** Sahip: 04-02-02 tarih/kapsam doğrulayıcısı ve görünümü; 04-04–12'nin her iki araştırma görevi gerçek söylem/sürüm ilişkisi; 04-14-01/02 sentez; 04-15-01 son maddi inceleme. Kanıt: statement_at/date_precision/version_id/period_basis/uncertainty_reason, tarihli pasajlar, source_review ve sentezde dönem/yetki/kapsam farkları. İlgili tarihsel belge ucu varsa takip edilir; ulaşılamıyorsa gerçek girişim ve belirsizlik yazılır, gün/sıra/niyet uydurulmaz. Kapanış: bilinen tarih ilişkileri kaynaklı, bilinmeyenler açık sınırlı; sonraki vaat geçmiş ihlal diye kullanılmaz. Hiç olay saptanmayan kapalı konu 04-14'te record|scope kanıt ayrımıyla gerçek scope/attempt/closure dayanağı taşır. Yeni tarih/kota/pilot seçimi gerekmez. [VERIFIED: 04-CONTEXT.md:34,48-64]

5. **Q5 — Tarayıcı/UI ve teslim yetkisi. Planlama disposition: RESOLVED (mevcut UI gate block=false, gerçek browser ve yalnız yerel teslim). Yürütüm kabul sonucu: PENDING.** Sahip: 04-15-02 yürütücüsü gerçek final release üzerinde file/HTTP×360/1365 px, hash/odak, parti↔konu, olay/kanıt ve olaysız scope dayanağı yollarını doğrular; orkestratör insan UAT yanıtını kendi akışında toplar. Kanıt: test_practice_navigation.py/practice_navigation_probe.cjs, 04-acceptance.json gerçek release/hash/browser kayıtları ve 04-UAT.md. Başarısız browser olgusu düzeltilip tekrar doğrulanır; kullanıcı yanıtı yoksa human_acceptance=pending devam eder. Kapanış: gerçek teknik kanıt tamamdır, insan kabulü ancak gerçek yanıta göre kaydedilir; üç unclassified/unresolved edge ve üç descriptor-less prohibition flagged kalır. Kamu yayını/hosting yetkisi ve yeni kaynak ön onayı türetilmez. [VERIFIED: 04-CONTEXT.md:11,64]

## Sources

- **Yerel birincil kaynaklar:** AGENTS, PROJECT/STATE/ROADMAP/REQUIREMENTS, 01–04 CONTEXT; src/arsiv.py, rapor.py, dosyalar.py, kaynaklar.py, arsiv_gorunum.py; ilgili test dosyaları ve current release. Satır atıfları yukarıdadır.
- **Dış birincil belgeler, erişim 2026-11-17:** [Python 3.12 sqlite3](https://docs.python.org/3.12/library/sqlite3.html), [SQLite ALTER TABLE](https://www.sqlite.org/lang_altertable.html), [ASVS](https://asvs.owasp.org/), yukarıdaki resmî TBMM ve parti girişleri.
- Araştırma seam soruları 04-research-questions.json içinde; beş digest research-store'a kaydedildi. Context7 kullanılamadığından resmî web belgesine geçildi. classify-confidence --provider websearch --verified sonucu “MEDIUM”; dış bulgular bu seviyede tutuldu. [VERIFIED: 2026-11-17 seam çıktıları]
- Dosya Read/Write bağlayıcısı “Unknown tool” hatası döndürdü; dosyalar numaralı yerel okuma araçlarıyla açıldı, araştırma çıktısı yerel patch aracıyla yazıldı. Bu araç uyarlaması kaynakları yalnız grep üzerinden doğrulama anlamına gelmez. [VERIFIED: 2026-11-17 araç çıktıları]

## Metadata

| Alan | Güven | Gerekçe |
|---|---|---|
| Mevcut yığın ve bağlantı noktaları | MEDIUM | Kod/veri ve ortam doğrudan incelendi; yeni modelin uygulaması bu araştırmada yapılmadı. |
| Mimari öneri | MEDIUM | Kilitli kararlar ve mevcut snapshot sınırlarından türetildi; alan adları teknik planda sabitlenecek. |
| Kaynak başlangıçları / riskler | MEDIUM | Resmî girişler ve arşiv envanteri doğrulandı; geniş olay araştırması yürütüm işidir. |

**Geçerlilik:** Teknik bulgular kod değişene kadar; canlı erişim gözlemleri bu oturuma aittir ve yürütümde yeniden kontrol edilir. Araştırma tamamlandı; uygulama ve kamu yayını yapılmadı.

