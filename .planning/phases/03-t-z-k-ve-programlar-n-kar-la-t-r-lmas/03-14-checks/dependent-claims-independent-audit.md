# Son v4 kaynak düzeltmeleri — bağımlı sentez denetimi

**Sonuç:** İstenen dört konudaki 15 v4 cümleyi ve eski `0314-charter-last-es-genel-baskan-1` cümlesini kaynaklarıyla karşılaştırdım. Kaynak anlamını aşan yeni bir cümle saptamadım. Yeni Parti'nin genel/özel PM oy ayrımı, Demokrat Parti mahalle hükmünün başlık konumu ve yerel koşulu, İYİ Parti üye kayıt defteri istisnası, Demokrat Parti yan kuruluşlarının üç kademesi ve DEM üçüncü tur koşulu korunmuş. Eski DEM/DBP cümlesinin v4'te kullanılacağı durumda gereken iki güncel taraf adresi aşağıda açıklandı; eski v3 kayıt kendi halinde korunmalı.

Denetlenen dosyalar: `data/comparisons/03-synthesis-final-groups-v4.json`, `data/comparisons/03-synthesis.json`, `data/comparisons/03-taxonomy-v4.json`, `data/comparisons/03-backfill-v4.json`; özgün arşiv ve eski alan tabanı `data/releases/4da93e2c64914eecb875c66cca14ea57/records.json`. Son v4 soyunda **4.917 taşınan satır ve 18 yerine-geçen eski satır** var. Bu sayım fiziksel kaynak veya bağımsız politika sayısı değildir.

Bu rapordaki cümle/kaynak/koşul incelemesini ve özgül gerekçeleri kendim yaptım. Paketlerdeki önceki inceleme kararlarını bağımsız onay yerine kullanmadım. Betikler yalnız pasaj ve kayıt listeleme, özgün metni/görüntüyü sunma, kimlik ve bağ denetimi yaptı; anlam gerekçesi, yokluk veya onay kararı üretmedi. Yalnız bu `/tmp` raporu yazıldı; repo, veritabanı, yayın ve lock değişmedi.

## Değişikliklere doğrudan bağımlı beş cümle

### 1. Yeni Parti genel ve özel PM oyu

`0314-v4-charter-more-genisletilmis-toplanti-1` cümlesi Yeni Parti'de söz/öneriyle katılımın genel oy yasağını ve hükümet kurma, katılma, çekilme konularındaki TBMM grup yöneticilerine ait özel oy hakkını birlikte söylüyor. `epm-charter-v1` özgün HTML Madde 22/7 ve 22/11-f aynı koşulları taşıyor. Genel cümlede kadın ve gençlik kolları genel başkanları da var; özel cümlede yalnız TBMM grup başkanvekilleri ve grup yönetim kurulu üyeleri sayılıyor. Sentez bu özel hakkı kadın/gençlik kolları başkanlarına veya bütün PM gündemlerine yaymıyor.

Yeni seçili taraf `0314-v4-yeni-pm-katilim-row`; kendi bulgusunun kanıtları hem `0303-epm-detail9-organ-toplanti-parti-meclisinde-oy-hakk-olmayan-kat-l-m-p` hem `0314-v4-yeni-pm-hukumet-oy-istisna-p`. İki pasaj sentezin evidence listesinde de mevcut. Cümledeki DBP ve DEM tarafları ayrı kurallardır: DBP HTML Madde 59, DEM PDF index 13/basılı 14 Madde 18, bilgi alma/görüşme için daveti ve PM üyesi olmayanın oy kullanamamasını açıklar. `0314-cm-x09-part1-p` ve `0314-cm-x10-part1-p` tam paragrafları, kısa davet parçalarında eksik kalan oy koşulunu gerçekten tamamlıyor. Yeni Parti'nin özel hükümet oyu bu iki partiye aktarılmamış.

**Karar:** Cümle ve üç tarafın ayrı kanıt/kapsamı uygun; eski oy yasağı özetinden kalan eksiklik yeni cümlede sürmüyor.

### 2. İYİ Parti defter istisnası

`0314-v4-charter-more-parti-defterleri-2`, İYİ Parti ve Saadet'in genel defter listelerini aktardıktan sonra üye kayıt defterinin yalnız ilçede tutulacağını açıkça ayırıyor. İYİ `0205-iyi-charter-download-v1` Madde 78, PDF index 48/basılı 49 genel listeyi; Madde 5, index 5/basılı 6 “Üye kayıt defteri sadece ilçe teşkilatlarında bulundurulur” cümlesini taşıyor. Bunların ikisini de özgün sayfalarda okudum. Yeni seçili `0314-v4-fix-iyi-defter-1`, hem `0306-iyi-parti-defterleri-passage` hem `0314-cm-x06-part1-p` bağını gerçekten taşıyor.

Saadet'in `0209-saadet-current-charter-v1` Madde 62, PDF index 23/basılı 24 ilk paragrafında aynı sayfa içinde genel liste ve “Üye Kayıt Defterleri yalnız İlçe Yönetim Kurulları tarafından mahalle ve köy esasına göre tutulur” istisnası var. Sentezde kullanılan Saadet context pasajı bu cümleyi içeriyor. İYİ'deki üye başvuru defteri Saadet'e eklenmemiş; ilçe istisnası da bütün defterlere yayılmamış.

**Karar:** Cümle iki partinin kaynaklarını ayrı tutarak istisnayı doğru koruyor. İYİ'nin genel/özel iki madde ifadesini bir hukuki yürürlük sırası kararı vermeden birlikte sunuyor.

### 3. Demokrat Parti başlık konumu ve yerel seçim/atama ayrımı

`0314-v4-charter-more-mahalle-koy-temsilciligi-1`, Demokrat Parti tarafını “17/II Kadın ve Gençlik Kolları başlığını izleyen temsilcilik hükmü” diye sınırlar. `0210-demokrat-charter-archive-v1` PDF index 11–13'ü ve özellikle index 12/basılı 12'nin gerçek görüntüsünü önceki bağımsız kaynak denetiminde okudum; bu denetimde son kesintisiz pasaj ve sentez birlikte kontrol edildi.

Açık koşullar korunmuş: büyükşehir statüsü uygulanan şehirlerin **merkez ilçelerindeki mahalleler**, mahallede oturan üyelerin katıldığı kongre, bir başkan ve dört üye; bunun dışındaki yerler için ilçe yönetiminin bir temsilci ataması ve temsilcinin bir yardımcı seçmesi. Cümle “bütün mahalle temsilcileri seçilir” veya “hepsi atanır” demiyor. Kaynağın başlık konumunu ifade ediyor; yalnız kadın/gençlik kollarına kesin münhasırlık veya bütün ana parti temsilciliklerine genellik ilan etmiyor.

Yeni seçili taraf `0314-v4-fix-dp-mahalle-1`, düzeyi `yerel`. `0314-demokrat-mahalle-secim-atama-full-p` başlık, üç kademe listesi ve devamdaki hükmü kesintisiz taşıyor; aynı kaynak sahibinin finding_evidence zincirinde ve sentez kanıtlarında var. Önceki kısa atama parçası yeni coğrafi şartın yerine tek başına kullanılmıyor.

İYİ tarafının atayan ilçe yönetimi ve temsilcinin bu yönetimle sınırlı görev süresi, ayrı `0205-iyi-charter-download-v1` Madde 20, PDF index 14/basılı 15'te okundu. `0314-cm-x13-part1-p` ikinci paragraftaki süreyi de gerçekten taşır. Demokrat Parti'nin seçim koşulu İYİ'ye aktarılmamış.

**Karar:** Son kaynak konumlu ve koşullu cümle uygun. Kaynaktaki kapsam belirsizliğini kesin bir genel kural olarak çözmüyor.

### 4. Demokrat Parti yan kuruluşları: ilçe, il ve Genel Merkez

`0314-v4-charter-final-sivil-toplum-iliskileri-2`, DBP'nin ortak amaç/hedefle STK işbirliğini ve Demokrat Parti'nin kendi yan kuruluşunu kurma yolunu ayırıyor. DBP `0207-dbp-charter-v1` HTML Madde 41/d, halkı siyasetin öznesi yapmaya çalışan STK'larla ortak amaç ve hedef doğrultusunda eşgüdümü belirtir; bütün STK'larla koşulsuz birlik söylemez.

Demokrat Parti `0210-demokrat-charter-archive-v1`, Madde 17/II/3, PDF index 12/basılı 12'de gerekli görülen yer, temel teşkilat yönetim kurulu kararı ve **ilçe, il, Genel Merkez** bağlantılarını birlikte sayar. Yeni seçili `0314-v4-fix-dp-sivil-1` ve sentez `0314-demokrat-yan-kurulus-kademeleri-full-p` tam bendine bağlı. “Kurulabilir” ifadesi korunmuş; sadece merkezde zorunlu/fiilen kurulmuş bir organ veya bütün sivil toplumun partiye bağlılığı iddia edilmemiş.

**Karar:** Üç kademe ve karar koşulu doğru; farklı partilerin araçları tek bir ortak kuruluş modeli yapılmamış.

### 5. Eski DEM/DBP eş genel başkan cümlesi

`data/comparisons/03-synthesis.json` içindeki `0314-charter-last-es-genel-baskan-1` hâlen taxonomy 3 kaydıdır. Metni, DEM'de ilk iki turda salt çoğunluk sağlanamazsa üçüncü turda en çok oy alan iki üyenin seçileceğini; DBP'de Büyük Kongre'nin bir kadın ve bir erkek seçeceğini söylüyor.

DEM `0204-dem-charter-v1` Madde 17, index 12/basılı 13'te başlangıç eşiği delege tam sayısının salt çoğunluğu, yöntem gizli oy/açık sayım ve üçüncü turda en çok oy alan iki üyedir. `0314-dem-cochair-selection-rounds-full-p` bu tam paragraftır ve eski sentezin evidence listesinde de bulunuyor. DBP `0207-dbp-charter-v1` HTML Madde 51'de program, tüzük, PM kararları ve ilgili mevzuat doğrultusunda partiyi temsil/yönetmek üzere bir kadın ve bir erkeğin Büyük Kongrece seçileceği yazılı; `0308-dbp-draft-095-passage` bunu gerçekten taşıyor.

Cümle DEM'de kadın/erkek koşulu bulunmadığını veya DBP'de tur kuralı olmadığını söylemiyor; iki ayrı somut seçim ayrıntısını karşılaştırıyor. DEM ve HEDEP iki nüshası birbirine karıştırılmıyor; bu cümle yalnız DEM kısa adlı nüshaya ait.

v4 kaynak düzeltmeleriyle **güncel taraf rotası** şöyledir:

- Eski DEM tarafı `03-v3-0305-dem-baskan-secim-to-es-genel-baskan-dem-row` → 18 superseded kaydı içinden `0314-v4-fix-dem-2`.
- Eski DBP tarafı `03-v3-0308-dbp-draft-095-row` → 4.917 mapping içinden `04-03-v3-0308-dbp-draft-095-row`.

Bu iki güncel satırın kendi bulguları, eski sentezin kullandığı gerçek pasajları da sahipleniyor. Böylece v4'e taşınması için doğru bağlantı mevcut. Eski dosyadaki v3 adresleri kendi tarihsel kayıt bağlamında geçerlidir; v4'te yeniden kullanılacak sentezin tarafları bu açık rotadan çözülmeli. Bu rapor eski v3 kaydını değiştirmeyi veya v4'e kopyasının zaten yayımlandığını iddia etmiyor.

**Karar:** Cümlenin kaynak anlamı doğru; üçüncü tur eksikliği cümlede yok. V4 kullanımında yukarıdaki iki taraf rotası uygulanmalı.

## Diğer on bir cümlenin gerçek kaynak kontrolü

| Sentez kimliği | Kaynak ve özgül koşul kontrolü | Değerlendirme |
|---|---|---|
| `0314-v4-charter-more-parti-defterleri-1` | DEM Madde 53, PDF index 30/basılı 31 tam organ listesini, işletme hesabını ve asıl/fahri üye ayrımını içerir. TİP HTML 7.2 her kademedeki organın üye, karar, evrak, gelir/gider ve demirbaş defterlerini ayrı sayar. `0314-cm-x04-part1-p` DEM öznesini gerçekten tamamlıyor. | Organlar ve iki partinin farklı defter adları karışmamış. |
| `0314-v4-charter-more-parti-defterleri-3` | DBP HTML 103 kararların tarih/numara sırası ve oylamaya katılanların imzası; Yeni Parti HTML 59/2 defter biçimi/basımı/dağıtımı için Hesap Yönetmeliği; Demokrat PDF index 8/basılı 8 Madde 10 merkezden hazırlama/gönderme, seçim kuruluna onaylatma ve ilçe yönetiminin tutmasını ayırır. | Üç farklı görev zinciri doğru; seçim kurulu defteri tutan organ yapılmamış. |
| `0314-v4-charter-more-parti-defterleri-4` | Yeni Yol gerçek missing `0307-yeni-yol-missing-charter` ve girişimi `0307-yeni-yol-search-charter-20261113`. | Belge açığı; fiilî defter tutulmadığı sonucu değil. |
| `0314-v4-charter-more-genisletilmis-toplanti-2` | Demokrat PDF index 20/basılı 20 Madde 31/o, il/ilçe kurullarının kendi delegeleriyle yılda en az iki danışma toplantısını belirtir. TİP HTML 4.10'da komite ve büro üyeleri; 2022 dosya adlı PDF index 22/basılı 21'de büro üyeleri sayılır. PDF'nin 4.10 paragrafını bu denetimde görüntüden ayrıca okudum. | Toplantı sıklığı ve iki TİP nüshasının liste farkı doğru. Nüshaların yürürlük sırası çıkarılmıyor. |
| `0314-v4-charter-more-genisletilmis-toplanti-3` | EMEP HTML tüzük 53 danışma/bilgi için çağrılmayı; Saadet PDF index 10/basılı 11 Madde 23 Genel Başkanın GİK'e davet yetkisini; İYİ PDF index 30/basılı 31 Madde 47 Genel Başkanın birleşik toplantı çağrısı/başkanlığını belirtir. | Davet, seçilmiş organ üyeliğine veya oy hakkına dönüştürülmemiş. |
| `0314-v4-charter-more-genisletilmis-toplanti-4` | Yeni Yol'un aynı gerçek tüzük açığı; farklı ortak Meclis grubuna ait haberler bu tüzük hükmü yerine kullanılamaz. | Kaynak açığı doğru sınırlı. |
| `0314-v4-charter-more-mahalle-koy-temsilciligi-2` | DBP HTML 32 komisyon/meclis kurulmamış olması, iletişim amacı ve önce yerel delege, yoksa partili üye koşulunu verir. DEM PDF index 21/basılı 22 Madde 36 ilçe örgütünün açma yetkisi, en az bir kişi ve ilçeye bağlılığı ayrı mahalle/köy paragrafında taşır. `0314-cm-x12-part1-p` bu tam paragraftır. | Koşullar ve yetkili organlar ayrı korunmuş; il/belde örgütü kurulmamış yerlere ait önceki paragraf bu cümleye karıştırılmıyor. |
| `0314-v4-charter-more-mahalle-koy-temsilciligi-3` | Saadet PDF index 13/basılı 14 Madde 30/a bir temsilci/yardımcı, beldede belde-ilçede ilçe seçimi ve büyüklüğe göre artışı belirtir. TİP HTML 3.18 örgütlü yerde yerel talep+MYK onayı, örgütsüz yerde MYK kararı ve MYK fesih yetkisini ayırır. | İki kişilik bileşim değişmez sayı yapılmamış; TİP'in yerel talep koşulu örgütsüz yere taşınmamış. |
| `0314-v4-charter-more-mahalle-koy-temsilciligi-4` | Yeni Yol aynı gerçek missing+attempt; kuruluş kimliği temsilcilik usulünü vermez. | Karşılaştırılamama, temsilcilik bulunmadığına çevrilmemiş. |
| `0314-v4-charter-final-sivil-toplum-iliskileri-1` | Yeni Parti HTML 23/13-e'de MYK ilişki düzenleme/karar yetkisi; İYİ PDF index 33/basılı 34 Madde 51'de Başkanlık Divanı meslek odası/STK/medya koordinasyonu. Özgün başlık ve özne de okundu. | Görev doğru organlara ait; gerçekleşmiş ortaklık veya STK üzerinde yönetim yetkisi çıkarılmıyor. |
| `0314-v4-charter-final-sivil-toplum-iliskileri-3` | Yeni Yol'un tam tüzük kaynağı açığı; kurucu partilerin organ yetkileri aktarılamaz. | Sadece kaynak/organ yetkisi açığı ifade ediliyor. |

## Kanıt ve taraf zincirinin son kontrolü

Toplam **16 cümle: 12 multi_positive, 4 status_only**. Multi-positive kayıtların her birinde en az iki ayrı gerçek parti pasaj sahibi var; iki TİP nüshası tek başına iki taraf sayılmadı. Dört status-only kayıt aynı Yeni Yol belge açığının farklı sorulardaki etkisini gösteriyor; dört farklı belge eksikliği gibi sayılmamalı.

Bu 16 cümlede kullanılan **46 benzersiz pasaj** için tarafın parti/konu eşleşmesi, kaynak sürümü, seçili satırın kendi finding_evidence sahipliği ve sentezin comparison_synthesis_evidence bağı kontrol edildi. Eski v3 cümlenin iki tarafı kontrol sırasında yukarıdaki v4 rotalarından çözüldü. Dört Yeni Yol durumunda gerçek missing→attempt bağlantısı ve parti sahipliği de doğrulandı. **Bağ hatası bulunmadı.**

Metinlerin hüküm, izin, davet ve belge açığı olarak ayrılmasına ilişkin kararlar yukarıdaki gerçek kaynak okumalarına dayanır. Bağ sayısı ve betik sonucu bu anlam kararlarının yerine kullanılmadı. Özgün nüshaların tarihi/yürürlük sırası, Demokrat mahalle hükmünün kesin münhasır kapsamı ve fiilî uygulama bu cümlelerle belirlenmiş sayılmamalı.
