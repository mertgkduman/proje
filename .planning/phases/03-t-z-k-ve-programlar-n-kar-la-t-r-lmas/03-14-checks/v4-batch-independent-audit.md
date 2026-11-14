# v4 toplu kaynak düzeltmeleri — bağımsız kapsam ve soy denetimi

**Sonuç:** Son okunan taslakta 13 yerine-geçme kaydının parti, sürüm, konu, alan ve kanıt soyları tutarlı. İki DEM/HEDEP nüshasının seçim turu istisnası, İYİ Parti üye kayıt defterinin ilçe koşulu, Demokrat Parti yan kuruluşlarının üç kademesi ve Yeni Parti PM oy istisnası özgün kaynaklarla destekleniyor. Demokrat Parti mahalle hükmünün yeni özeti, kaynakta bulunduğu “Kadın ve Gençlik Kolları” başlığını izleyen konumu açıkça taşıdığı ve üç türevin düzeyi yerel olduğu son haliyle ihtiyatlıdır. Bu metinden bütün ana parti mahalle temsilcilikleri için genel bir seçim kuralı veya yalnız kollara ait kesin münhasırlık çıkarılamaz. EMEP 22. maddedeki finansman kampanyası içeriği korunmuş; dar afet/dayanışma yokluğuna dönüştüren replacement son dosyalarda bulunmuyor.

Bu rapordaki kaynak okumalarını, kapsam kararlarını ve gerekçeleri kendim yaptım/yazdım. Paket içindeki `reviewed` kayıtlarını otomatik onay olarak benimsemedim. Betikler yalnız kayıtları listeledi, özgün PDF/HTML metnini veya sayfa görüntüsünü sundu ve kimlik/bağ/birebir metin denetimi yaptı; anlam veya inceleme kararı üretmedi. Yalnız bu `/tmp` raporuna yazdım. Repo, veritabanı, yayın ve lock mutasyonu yapılmadı.

## Denetlenen dosyalar ve son okuma

- `/tmp/gsd-0314-v4-batch-lineage.json` — SHA256 `ac72e9073a48769302bbf0a29e95ba08335e9d339e8f1fc0947063140e71fe13`; 12 yerine-geçme.
- `/tmp/gsd-0314-03-backfill-v4-batch.json` — SHA256 `19c51aac7738bd4b28cd86c5b774d50a07b6d43986f30a239f3a61741fdca81f`; yeni kaynak ve bulguların okunduğu taslak.
- `/tmp/gsd-0314-v4-pm-voting-lineage.json` — SHA256 `5dba825db4548f65129e9712e0c484743ed6e30399d956185cd943ee96c87b9a`; genişletilmiş toplantı konusundaki ayrı PM yerine-geçmesi.

Eski satır, alan ve bulguların kaynağı `data/releases/4da93e2c64914eecb875c66cca14ea57/records.json`. Rapor 12+1 yerine-geçmeyi ve korunması kararlaştırılan EMEP 22. madde kaydını kapsar. İslam konusu için bağımsız denetim `/tmp/gsd-0314-v4-islam-independent-audit.md` dosyasında ayrı yapılmıştır.

## On üç yerine-geçmenin kimlikleri

Yeni alanların tamamı kendi satırına, aşağıda açıklanan yeni bulgu çiftine ve aynı parti/sürümün gerçek pasajlarına bağlıdır.

| Eski v3 satırı | Yeni v4 satırı | Yeni alan |
|---|---|---|
| `03-v3-0305-dem-baskan-secim-dem-row` | `0314-v4-fix-dem-1` | `0314-v4-fix-dem-1-f` |
| `03-v3-0305-dem-baskan-secim-to-es-genel-baskan-dem-row` | `0314-v4-fix-dem-2` | `0314-v4-fix-dem-2-f` |
| `03-v3-0305-dem-baskan-secim-also-organ-secim-yontemi-dem-row` | `0314-v4-fix-dem-3` | `0314-v4-fix-dem-3-f` |
| `03-v3-0305-dem-baskan-secim-hedep-row` | `0314-v4-fix-hedep-1` | `0314-v4-fix-hedep-1-f` |
| `03-v3-0305-dem-baskan-secim-to-es-genel-baskan-hedep-row` | `0314-v4-fix-hedep-2` | `0314-v4-fix-hedep-2-f` |
| `03-v3-0305-dem-baskan-secim-also-organ-secim-yontemi-hedep-row` | `0314-v4-fix-hedep-3` | `0314-v4-fix-hedep-3-f` |
| `03-v3-0306-iyi-parti-defterleri-row` | `0314-v4-fix-iyi-defter-1` | `0314-v4-fix-iyi-defter-1-f` |
| `03-v3-0312-demokrat-1-015-mahalle-koy-temsilciligi-row` | `0314-v4-fix-dp-mahalle-1` | `0314-v4-fix-dp-mahalle-1-f` |
| `03-v3-0312-demokrat-1-015-parti-temsilcilikleri-row` | `0314-v4-fix-dp-mahalle-2` | `0314-v4-fix-dp-mahalle-2-f` |
| `03-v3-0312-demokrat-2-039-parti-temsilcisi-row` | `0314-v4-fix-dp-mahalle-3` | `0314-v4-fix-dp-mahalle-3-f` |
| `03-v3-0312-demokrat-2-082-sivil-toplum-iliskileri-row` | `0314-v4-fix-dp-sivil-1` | `0314-v4-fix-dp-sivil-1-f` |
| `03-v3-0303-epm-detail9-organ-toplanti-parti-meclisinde-oy-hakk-olmayan-kat-l-m-row` | `0314-v4-yeni-pm-organ-toplanti-row` | `0314-v4-yeni-pm-organ-toplanti-row-f` |
| `03-v3-0303-epm-genisletilmis-toplanti-row` | `0314-v4-yeni-pm-katilim-row` | `0314-v4-yeni-pm-katilim-f` |

## DEM ve HEDEP: iki gerçek nüsha, üçer konu

**DEM kısa adlı nüsha:** `0204-dem-charter-v1`; SHA `97f552324d044a6a0ec4ad9d1dd99ac66ba50540a3ad397ebefaa3fbd7e1a471`; [özgün PDF](https://www.demparti.org.tr/Images/UserFiles/Documents/Editor/Parti%20metinleri/dem-parti-tuzuk.pdf). Madde 17, PDF index 12/basılı 13 sayfasının tamamını okudum. `0314-dem-cochair-selection-rounds-full-p` şu tam seçim paragrafını kendi nüshasından taşıyor:

> Eş Genel Başkanlar, Kongre’de delege tam sayısının salt çoğunluğu ile seçilir. Seçim, gizli oy açık sayım yöntemiyle yapılır. İlk iki oylamada yeterli oy sağlanamazsa, üçüncü oylamada en çok oy alan iki üye, Eş Genel Başkan seçilirler.

**HEDEP kısa adlı nüsha:** `0204-dem-charter-older-v1`; SHA `7c54e58c28d9e0bfadc72a5be640169a15137dc8aca8c93b4c1b6a1fc16470c4`; [ayrı özgün PDF](https://www.demparti.org.tr/Images/UserFiles/Documents/Editor/Parti%20metinleri/tuzuk.pdf). Madde 17, PDF index 11/basılı 10 sayfasını ayrıca okudum. `0314-hedep-cochair-selection-rounds-full-p` bu ikinci nüshanın noktalama ve satır düzenini koruyan gerçek paragrafıdır. Aynı içerik varsayılıp DEM pasajı HEDEP'e kopyalanmış değildir; iki pasaj da kendi özgün sayfasıyla birebir eşleşir.

Yeni `0314-v4-dem-s/q` ve `0314-v4-hedep-s/q` çiftleri başlangıçtaki salt çoğunluk, gizli oy/açık sayım ve ilk iki turda yeterli oy sağlanamazsa üçüncü turdaki en çok oy alan iki üye koşulunu birlikte koruyor. Böylece eski koşulsuz salt çoğunluk özetindeki eksiklik gideriliyor. Aynı öznenin üç ayrı soruda kullanılması kaynak anlamını değiştirmiyor: `genel-baskan-secimi`, `es-genel-baskan`, `organ-secim-yontemi`.

Bu altı alan altı farklı seçim usulü değildir; aynı partinin iki kaynak nüshasındaki birer hükmün üç ortak soruya bağlanmasıdır. Yeni alanlar nüsha sürümünü ayrı tutuyor; kabul/yürürlük günü veya hukuki sıra kanıtlanmadığı için “eski hükmün yerine yürürlüğe girmiş yeni hüküm” sonucu çıkarılmıyor. Aynı sayfalardaki görevden ayrılma ve vekâlet hükümleri ayrı konudur; seçim paragrafına karıştırılmamış.

**Değerlendirme:** Altı yeni özet ve alan, bu kaynak/özne/tur sınırıyla uygun. Her varyantın kendi finding_evidence bağı var; başka nüshanın pasajı kullanılmıyor.

## Demokrat Parti mahalle hükmü: açık bağ ve belirsiz bağ

Kaynak `0210-demokrat-charter-archive-v1`; SHA `379499d93d88c2ea209706ed34d337adb8bc22422127c5411bb9fc01dbe809b4`; [18 Haziran 2022 arşiv yakalamalı PDF](https://web.archive.org/web/20220618225341id_/https://www.dp.org.tr/storage/DP.T%C3%BCz%C3%BCk.2022.pdf). Dosya adı ve arşiv tarihi her maddenin kabul veya güncel yürürlük tarihi sayılmadı.

Madde 17'nin başladığı PDF index 11/basılı 11, ilgili index 12/basılı 12 ve devam index 13/basılı 13 sayfalarını okudum. Index 12'nin **gerçek sayfa görüntüsünü de** Poppler/Cairo ile bellekte açıp başlık, girinti ve blok konumlarını gördüm; yeni görüntü dosyası yazılmadı.

Metnin açık yapısı:

- 17/I “Temel Teşkilat” ilçe, il, merkez ve grupları tanımlar.
- 17/II “Yan Kuruluşlar”, kadın kolları, gençlik kolları ve 3. bentte başka yan kuruluşlarla beraber köy/mahalle temsilciliklerini sayar.
- Ardından ayrı, kalın “KADIN VE GENÇLİK KOLLARI” başlığı ve ilçe/il/merkez organ listesi gelir.
- “Ayrıca, Büyükşehir Belediye...” ve seçim/atama paragrafları bu başlık/listeden sonra, yeni 17/III “Yurt Dışı Temsilcilikleri” başlığından önce yer alır.

Bu konum, paragrafın kadın ve gençlik kolları bağlamında okunmasını kuvvetle destekler. Cümlelerde kadın/gençlik öznesi yeniden yazılmamış, atama bölümünde “partiyi temsil edecek parti üyeleri” denmiştir. Üstteki II/3 de köy/mahalle temsilciliklerini genel yan kuruluş listesinde sayar. Bu nedenle yalnız bu maddi metinden iki kesin sonuç kurulamıyor: kuralın bütün ana parti mahalle temsilciliklerine uygulandığı; kuralın münhasıran kadın/gençlik kollarıyla sınırlı olduğu. Açık olan, **kaynağın başlık altındaki konumu** ve aşağıdaki coğrafi/usul ayrımıdır.

Coğrafi/usul ayrımı doğrudan metinde var:

1. Büyükşehir belediyesi statüsünün uygulandığı şehirlerin **merkez ilçelerindeki mahalleler**: mahallede oturan üyelerin katıldığı kongrede bir başkan ve dört üyelik yönetim seçilir.
2. Bunun dışındaki il ve ilçeler: temel teşkilat yönetim kurulu kararıyla köy/mahalle temsilciliği kurulur; ilçe yönetimi parti üyeleri arasından bir temsilci atar; temsilci bir yardımcı seçer. Temsilci ve yardımcısının görevi bağlı ilçe yönetiminin görev süresi kadardır.

Bu iki yol “bütün mahalle temsilcileri atanır” veya “bütün mahalle temsilcileri kongrede seçilir” diye tekleştirilemez. Kaynakta büyükşehir statüsündeki bütün ilçeler denmiyor; merkez ilçesi koşulu korunmalı.

Son taslakta `0314-v4-dp-mahalle-s` şu ihtiyatlı başlangıcı kullanıyor: “Tüzüğün 17/II bölümünde Kadın ve Gençlik Kolları başlığını izleyen temsilcilik hükmünde...”. Bu, kaynak konumunu saptar; münhasır kapsam veya bütün ana parti organlarına yayılım iddiası kurmaz. Kalan özet seçim/atama ayrımını ve üye bileşimini doğru aktarır. Kısa özetin taşımadığı kuruluş kararı, parti üyeleri arasından atama ve görev süresi ayrıntıları tam alıntıda görünür; bunları ortadan kaldıran bir hüküm ileri sürülmemiştir.

Yeni tam `0314-demokrat-mahalle-secim-atama-full-p`, artık başlığı, üç kademe listesini ve seçim/atama paragraflarını **kesintisiz** içeriyor; index 12 metniyle birebir eşleşiyor. Kısa `0314-demokrat-mahalle-kollar-heading-p` de gerçek başlıktır. Aynı yeni `0314-v4-dp-mahalle-s/q` çifti üç konuya bağlanır: `mahalle-koy-temsilciligi`, `parti-temsilcilikleri`, `parti-temsilcisi`. Son dosyada üç satırın `level` değeri `yerel`; üçüncü satırın önceki `merkez` mirası giderilmiş.

**Değerlendirme:** Son kaynak konumlu özet ve kesintisiz pasajla üç türev kullanılabilir. Gelecekte yapılacak sentezde bu cümleyi “ana partinin bütün mahalle örgütleri için seçim zorunludur” biçimine dönüştürmek yeni bir anlam hatası olur. Kesin münhasırlık için bu metnin dışında yeni, açık yetkili kaynak gerekir; bu denetim böyle bir dış doğrulama yapmış değildir.

## Demokrat Parti yan kuruluşları: üç kademe ve iki farklı karar bağı

Aynı `0210-demokrat-charter-archive-v1` nüshasının index 12/basılı 12 sayfasındaki 17/II/3 bendini ve devamını tam okudum. `0314-demokrat-yan-kurulus-kademeleri-full-p` şu tam bendi taşır:

> 3. Genel İdare Kurulu kararı ile Genel Merkeze bağlı olarak yurt dışı temsilcilikler ile gerek görülen yerlerde temel teşkilat yönetim kurulları kararı ile İlçe, İl ve Genel Merkez Teşkilatına bağlı olarak köy ve mahalle temsilcilikleri, Demokratik Kitle Örgütleri Temsilciliği, İşçi ve Sosyal Güvenlik Kurulları ile diğer yan kuruluşlar kurulabilir.

Yeni `0314-v4-dp-sivil-s/q` çifti ve `0314-v4-fix-dp-sivil-1-f`, Demokratik Kitle Örgütleri Temsilciliğini yalnız Genel Merkezin kurabileceği bir organ olarak sunmuyor. Gerekli görülen yer ve temel teşkilat yönetim kurulu kararı koşulları ile ilçe, il ve Genel Merkez bağlantısı birlikte korunuyor. Kaynaktaki yurt dışı temsilcilikleri için GİK/Genel Merkez bağı, diğer yan kuruluşların üç kademeli bağlantısına gelişigüzel aktarılmıyor.

Buradaki Demokratik Kitle Örgütleri Temsilciliği bir parti yan kuruluşudur; dışarıdaki bütün sivil toplum örgütlerinin partiye tabi olduğu anlamı yoktur. “Kurulabilir” yetkisi gerçekleşmiş kuruluş kanıtı veya her yerde kuruluş zorunluluğu değildir. Kaynak devamı bu kuruluşların bulundukları yerdeki temel teşkilat kademelerine bağlı çalışacağını da açıklar.

**Değerlendirme:** `sivil-toplum-iliskileri` sorusundaki yeni alanın üç kademe ve koşullu kuruluş kapsamı uygun; yeni satırın `ilçe, il ve merkez` düzeyi kaynakla uyumlu.

## İYİ Parti defterleri: ilçe koşulu yalnız üye kayıt defterine ait

Kaynak `0205-iyi-charter-download-v1`; SHA `f35b00a3991e45bca3ac4ecffb6b4a8537574570ef873a50bd6a2e7f7e68e02e`; [54 sayfalık PDF](https://www.iyiparti.org.tr/wp-content/uploads/2026/05/IYI-PARTI-TUZUGU-YENI_4.olagan-kurultay.pdf?download=1), 18 Ocak 2026 değişiklikleri işlenmiş nüsha.

Madde 5'in index 5/basılı 6 sayfasını ve Madde 78'in index 48/basılı 49 sayfasını ayrı ayrı bütünüyle okudum. Madde 5 üyelik başvurusunu, ilçe yönetiminin kabulünü ve üyeliğin köy/mahalle esaslı deftere işlenmesini anlattıktan sonra açıkça “Üye kayıt defteri sadece ilçe teşkilatlarında bulundurulur” der. `0314-cm-x06-part1-p` bu gerçek cümledir.

Madde 78'in genel listesi ise her kademede üye kayıt, üye başvuru, karar, gelen-giden evrak, gelir-gider ve demirbaş defterlerini sayar; `0306-iyi-parti-defterleri-passage` bu genel listeyi taşır. Yeni özet, diğer defterlerin genel yükümlülüğünü koruyup üye kayıt defterine ilişkin özel ilçe hükmünü ayrıca bildiriyor. Böylece “bütün bu defterler yalnız ilçede tutulur” veya “üye kayıt defteri her kademede ayrıca bulundurulur” sonucuna gitmiyor.

İki maddenin genel/özel ifade gerilimi özgün metinde vardır; yeni yorumla bir madde silinmiş sayılmamalı. Mevcut yeni `0314-v4-iyi-defter-s` hem genel listeye hem özel cümleye bağlıdır; `0314-v4-iyi-defter-q` ilçe cümlesini aynen gösterir. Bu, arşivin kaynakları birlikte sunmasıdır; bir hukuki uygulanma sırası kararı değildir.

**Değerlendirme:** `0314-v4-fix-iyi-defter-1-f` bu açık kaynak ayrımıyla uygun. Satırın genel teşkilat düzeyini taşıması, özet ilçe istisnasını açık tuttuğundan tek başına kapsam hatası yaratmıyor.

## Yeni Parti PM: genel katılım ve hükümet toplantısı oy istisnası

Kaynak `epm-charter-v1`; SHA `b3709f52e07f6d65797d021f571c2b97eca5ac02771a633fe55aafec4130518e`; [HTML tüzük](https://yenipartiyiz.biz/parti-tuzugu). Madde 22/7'yi çevresindeki toplantı hükümleriyle, 22/11-f'yi görev/yetki listesiyle birlikte özgün metinden okudum.

Genel kural `0303-epm-detail9-organ-toplanti-parti-meclisinde-oy-hakk-olmayan-kat-l-m-p` pasajında: TBMM grup başkanvekilleri, grup yönetim kurulu üyeleri, kadın ve gençlik kolları genel başkanları PM toplantısına katılabilir, söz alabilir ve öneride bulunabilir; oy kullanamaz.

Özel hüküm `0314-v4-yeni-pm-hukumet-oy-istisna-p` pasajında tamdır:

> Hükümet kurma, hükümete katılma, hükümetten çekilme konularında karar verir. Bu konuların görüşüldüğü Parti Meclisi toplantısına, TBMM Grup Başkanvekilleri ve Grup Yönetim Kurulu üyeleri katılır ve oy kullanırlar.

Bu istisnanın kişi grubu ilkinden daha dardır: TBMM grup başkanvekilleri ve grup yönetim kurulu üyeleri. Kadın/gençlik kolları genel başkanları özel oy cümlesinde sayılmıyor. Konu da sınırlıdır: hükümet kurma, katılma ve çekilme. Kaynak iki gruba bütün PM toplantılarında genel oy hakkı vermiyor; kadın/gençlik kolları başkanlarına aynı özel oy hakkını eklemiyor.

Yeni `0314-v4-yeni-pm-katilim-s` iki hükmü birlikte ve doğru kişi/konu sınırıyla aktarır. Summary kendi finding_evidence zincirinde hem genel hem özel pasajı taşır; quote genel kuralı kendi gerçek pasajından gösterir. Aynı bulgu çifti `genisletilmis-toplanti` ve `organ-toplanti` sorularındaki iki yeni alana bağlanmış. İki alan iki farklı hüküm üretmiyor; aynı genel/özel koşul çiftinin iki ortak sorudaki görünümüdür.

**Değerlendirme:** İki yeni alanın kaynak ve kapsamı uygun. “Oy hakkı olmayan katılım” organ etiketi, özetin açıkladığı özel hükümet toplantısı koşulundan bağımsız mutlak kural gibi kullanılmamalı; sentezler yeni çiftin tamamını okumalı.

## EMEP madde 22: finansman kampanyası içeriği korunmalı

Kaynak `0208-emep-program-charter-v1`; SHA `16e8971e7cc015b0134f7836a9930200f04e9a298803f58801cf2261e3593329`; [birleşik program/tüzük yayını](https://www.emep.org/emek-partisi-program-ve-tuzugu). Buradaki içerik program değil **tüzük** kısmının “Partinin Mali Kaynakları”, 22. maddesidir. 21–23 çevresindeki başlık ve madde sınırlarını okudum. `0309-emep-html-064-0-passage` tam maddeyi taşır:

> Partinin mali kaynakları üyelerinin aidatları ve bağışlar, belirli zamanlarda açılan kampanyalar ve diğer gelirlerdir.

`03-v3-0309-emep-html-064-0-row` / `03-v3-0309-emep-html-064-0-field` ve `0309-emep-html-064-0-summary/quote` gerçek parti gelir kampanyası içeriğine dayanır. Konu tanımı “Yardım kampanyaları hakkında tüzük düzenlemeleri” olup yalnız afet veya dış yararlanıcıya dayanışma yardımıyla sınırlandırılmamıştır. Bu nedenle bu kaydın finansman anlamını korumak, afet/dayanışma amacına dair dar yoklukla yer değiştirmesinden daha uygundur.

Metnin açık söylediği parti mali kaynağı olarak dönemsel kampanyalardır. Afet mağduru, yardım alıcısı, kampanya yönetimi, denetim usulü veya dışa yardım amacı bu maddede açıklanmaz; bunlar eklenmemeli. Maddenin böyle bir ayrıntı içermemesi, başka maddelerde/başka belgelerde yardım politikası olmadığı sonucuna da dönüşmez. İçerik okura “parti gelir kaynakları arasında belirli zamanlarda açılan kampanyalar” olarak gösterildiğinde gerçek kapsam nettir.

Son okunan batch-lineage içinde EMEP 064-0 satırının replacement kaydı yok. Son batch içinde de `0314-v4-emep-yardim-md22-scope` ve ona bağlı no_explicit_statement satırı yok. Mevcut kaynaklı finansman satırının mekanik soyla korunması kararıyla dosyalar bu bakımdan uyumlu. Bu rapor, finansman kampanyasını afet yardımına dönüştürmeyi veya maddenin açık gelir içeriğini bir yokluk kaydıyla görünmez kılmayı desteklemiyor.

## Yapısal ve birebir metin denetiminin kanıtı

12 batch soyu ve ayrı PM soyuyla toplam 13 eski/yeni satır için şu ilişkiler denetlendi: eski alanın eski satıra sahipliği; yeni alanın yeni satıra sahipliği; parti, sürüm, konu ve belge rolünün devamı; yeni finding çiftinin lineagedeki kimliklerle eşleşmesi; her finding'in kendi gerçek pasajının aynı kaynak sürümüne ait olması. **Bağ hatası bulunmadı.** Aynı kaynak bulgusunun ilgili üç veya iki soruda tekrar kullanılması bağımsız kanıt sayısı artırmak için kullanılmamalı.

Son batch'in sekiz passage kaydı kendi özgün PDF/HTML metninde **birebir exact** eşleşti: DEM seçim paragrafı; HEDEP seçim paragrafı; İYİ Madde 5 cümlesi; Demokrat kesintisiz başlık/listeler/mahalle paragrafı; Demokrat yan kuruluşlar bendi; Demokrat başlık pasajı; Yeni Parti PM istisnası; daha önce ayrıca denetlenen EMEP G/A/7 program pasajı. Bu mekanik kontrol yalnız metin doğruluğuna kanıttır; yukarıdaki anlam değerlendirmelerinin yerine geçmez.

Son yeniden üretilen dosyada önceki kısa gerçek pasajlar da yeni bulguların kanıt zincirine eklenmiş. Denetlenen 13 alanın kullandığı toplam 23 benzersiz pasajın tamamı kendi belirtilen PDF sayfası/HTML kaynağında birebir bulundu; DEM ve HEDEP kısa pasajları kendi farklı nüshalarının index 12 ve 11 sayfalarında kaldı. Önceki kısa parçalar, yeni tam paragraftaki koşulları kaldıran bağımsız özetler olarak kullanılmamalı.

Denetim sırasında saptanan DP üçüncü satırın merkez düzeyi ve mahalle paragrafının başlıksız genelleştirilmesi son taslakta giderilmiş. İncelenen son hallerde ayrıca bir kaynak veya soy hatası saptamadım. Arşiv nüshalarının kesin yürürlük sırası, Demokrat mahalle hükmünün bütün ana teşkilata uygulanıp uygulanmadığı ve finansman maddesinde söylenmeyen kampanya ayrıntıları bu raporla çözülmüş sayılmamalı. Bu sınırlar yeni özetlerde korunduğunda kaynak temelli değişiklikler incelemeye elverişlidir.
