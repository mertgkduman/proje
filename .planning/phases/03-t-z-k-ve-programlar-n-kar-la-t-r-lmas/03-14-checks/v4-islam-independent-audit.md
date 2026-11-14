# İslam kurumları sorusu v4 — bağımsız kaynak ve yöntem denetimi

Denetlenen paket: `data/comparisons/03-backfill-v4.json`. Karşılaştırılan ön inceleme: `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-14-checks/v4-islam-authored-review.json`. Yeni tanım ve mekanik soy: `data/comparisons/03-taxonomy-v4.json`; v3 taban arşivi: `data/releases/4da93e2c64914eecb875c66cca14ea57/records.json`.

**Sonuç:** Dokuz partiye ait 13 kaynak-durum satırının belge rolleri ve gerçek kanıt bağlantıları korunuyor. Yeni Parti ve Saadet'in yeni dar kapsamları, İYİ Parti'nin de dar kapsam sonucu özgün belirtilen bölümlerde yaptığım okumayla destekleniyor. **İYİ Parti scope gerekçesindeki “laik hukuk devleti” ifadesinin bölüm atfı düzeltilmeli:** açık ifade scope'un belirttiği 1/2/4 bölümlerinin dışında, 5. İç ve Dış Güvenlik bölümünde yer alıyor. Bu yer düzeltmesi dar kapsam sonucunu tersine çevirmiyor. Diğer satırlarda aşağıda belirtilen anlam sınırlarıyla maddi bir yanlış bulmadım.

Bu bir bağımsız yeniden okumadır. Ön incelemedeki `reviewed` sonuçlarını delil saymadım ve gerekçelerini kendi onayım olarak kopyalamadım. Metinleri, koşulları ve aşağıdaki değerlendirmeleri kendim okudum/yazdım. Betikler yalnız kayıt, kimlik ve bağ listeleme; HTML'nin görünen metnini sunma; PDF sayfa metni sunma ve birebir eşleşme kontrolü yaptı. Bir betik yokluk, anlam veya inceleme kararı üretmedi. Yeni web araması yapıldığı iddia edilmiyor; eksik durumlarında arşivdeki gerçek girişim ve kaydedilmiş sonucu denetlendi. Yalnız bu `/tmp` raporu yazıldı; repo, veritabanı, yayın ve lock değiştirilmedi.

## Yeni soru ve sayımın sınırı

v4 tanımı şöyledir:

> İslam inanç örgütlenmesine özgü program veya tamamlayıcı belge yaklaşımı ve tüm dinsel devlet kurumları veya kamu finansmanına ilişkin açık genel hükümler ayrı incelenir; özel inanç örgütleri için genel yasak veya fiilî uygulama çıkarılmaz.

Bu tanım iki ayrı kabul yolu açıyor: adlandırılmış İslam kurumu/örgütlenmesine ilişkin özgül yaklaşım; tüm dinsel **devlet** kurumlarına veya dinî kurumların kamu finansmanına ilişkin açık genel hüküm. Genel inanç özgürlüğü, inançlara saygı veya laik eğitim ilkesi tek başına bu ikinci yolun kurumsal/finansal aracına dönüşmez. Bununla birlikte bir kurumun açık yeniden düzenlenme önerisi, bütün dinî kurumları kapsamadığı gerekçesiyle dışlanamaz; ilk yola ait somut yanıt olabilir.

13 satır; 7 `evidence`, 3 `no_explicit_statement`, 3 `document_missing` içeriyor. Yedi evidence satırından İYİ Parti'nin genel ilke satırı **bağlamdır**, olumlu kurumsal araç değildir. İki BDP kopyası aynı tarihsel yaklaşımın iki kaynağıdır. Böylece 13 satır, 13 ayrı politika veya 13 olumlu yanıt anlamına gelmez. Belge rolleri 10 `program`, 1 `supplement`, 2 `historical` olarak korunmuş; `program` rolü tek başına belgenin bugün yürürlükte olduğunu kanıtlamaz.

## On üç satırın karşılığı

| Parti ve v4 satırı | Kaynak/durum | Doğrudan okunan yer | Bağımsız değerlendirme |
|---|---|---|---|
| TİP — `04-03-v3-0304-tip-program-din-kurum-row` | `0203-tip-program-v1`, program, evidence | HTML: Mezhepçiliğe Karşı Eşit Yurttaşlık | Diyanet'in kapatılması **ve** din işlerinin tüm din/mezheplere eşit mesafeli kurumda yeniden düzenlenmesi birlikte korunmalı. |
| DEM — `04-03-v3-0305-dem-program-islam-row` | `0204-dem-policies-v1`, supplement, evidence | 4. Olağanüstü Büyük Kongre kararları: Demokratik İslam Hareketi | DİK ile ilişkiyi canlandırma ve çalışmasını destekleme kararı yeterli özgül içerik; Diyanet eleştirisi fesih/finansman vaadi değil. |
| DEM — `04-03-v3-0305-dem-program-missing-islam-inanc-orgutlenmesi` | Program, document_missing | `0204-dem-missing-current-program` → `0204-dem-search-program` | Güncel bağımsız ana programın gerçek edinme açığı; kongre eki bu belgenin yerine geçmez. |
| İYİ — `04-03-v3-0306-iyi-program-scope-islam-inanc-orgutlenmesi-context-row` | `0205-iyi-program-page-v1`, program, evidence/bağlam | HTML: 1. İyi Bir Türkiye / Amacımız | İnançlara saygı amacı gerçek; kurum feshi, kurumsal tasarım veya kamu finansmanı aracı olarak sınıflandırılmamalı. |
| Yeni Yol — `04-03-v3-0307-yeni-yol-islam-inanc-orgutlenmesi-program` | Program, document_missing | `0307-yeni-yol-missing-program` → `0307-yeni-yol-search-program-20261113` | Tam program edinme açığı; kurucu partilerin veya ortak Meclis grubunun görüşleri aktarılmaz. |
| DBP — `04-03-v3-0308-dbp-current-islam-inanc-orgutlenmesi` | Program, document_missing | `0207-dbp-missing-current-program` → `0207-dbp-search-current-program` | Bağımsız güncel DBP programı için açık; tarihsel iki kopya bunun cevabı değildir. |
| DBP — `04-03-v3-0308-dbp-program-097-0-row` | `0207-dbp-bdp-program-v1`, historical, evidence | Blogspot BDP kopyası: Laiklik | Diyanet'in demokratik düzenlenmesi ve din/inanç işlerinin **tedricen** gruplara bırakılması; derhal fesih çıkarılmaz. |
| DBP — `04-03-v3-0308-dbp-program-097-1-row` | `0207-dbp-bdp-program-wordpress-v1`, historical, evidence | WordPress BDP kopyası: Laiklik | Aynı iki cümle ikinci kopyada da gerçek; güncel DBP programı veya ikinci bağımsız parti politikası sayılmaz. |
| Demokrat — `04-03-v3-0313-demokrat-islam-inanc-orgutlenmesi` | `0210-demokrat-program-archive-v1`, program, evidence | PDF index 3, basılı 10: Demokrat Parti, İnsanı Merkez Alır | Diyanet'in değişik inanç gruplarına hizmet verecek biçimde yeniden yapılandırılması açık; kapatma veya finansmanı kesme değildir. |
| EMEP — `0314-v4-emep-din-kurum-row` | `0208-emep-program-charter-v1`, program, evidence | Birleşik HTML yayınının programı: G / A / 7 | Tüm dinsel devlet kurumlarının feshi ve dinî kurum/cemaatlerin devlet finansmanının sona ermesi ayrı nesnelere sahip iki araçtır; alan inananlara bırakılır. |
| Yeni Parti — `0314-v4-yeni-din-kurum-scope-row` | `epm-program-v1`, program, no_explicit_statement | Düşünsel Temellerimiz ve Siyasi Kimliğimiz; Demokratik, Şeffaf, Kamucu Eğitim Sistemi | Dar kapsam bu bölümlerde destekleniyor; eğitim sorumluluğunun devredilmemesi ve laik eğitim bağlamı saklı kalmalı. |
| İYİ — `0314-v4-iyi-din-kurum-scope-row` | `0205-iyi-program-page-v1`, program, no_explicit_statement | Tam 1. İyi Bir Türkiye, 2. Demokrasi ve Hukuk, 4. Kamu Yönetimi bölümleri | Bu üç bölüm için dar sonuç uygun; gerekçedeki açık “laik hukuk devleti” ifadesinin yer atfı düzeltilmeli. |
| Saadet — `0314-v4-saadet-din-kurum-scope-row` | `0209-saadet-current-program-v1`, program, no_explicit_statement | PDF index 4–6 ve 10, basılı 5–7 ve 11 | Ayrım yapmayan hak ve hizmet ilkeleri var; bu sayfalarda yeni genel soruya ayrı kurum/finansman aracı bulmadım. Sonuç bu sayfaları aşmamalı. |

## Yeni Parti: eğitimdeki araç ile genel kurum sorusu

Kaynak [parti programı](https://yenipartiyiz.biz/parti-programi), `epm-program-v1`, SHA `58fa220ab814bd82a4c8d0d233bf55ab268eb9f856750cd88abc544e17ceba1b`. Yayın kaydı 24 Temmuz 2026, arşiv erişimi 10 Kasım 2026; bütün hükümlerin yürürlük başlangıcı olarak kullanılmadı.

“Düşünsel Temellerimiz ve Siyasi Kimliğimiz” başlığını gövdedeki başlangıcından Bölüm II'ye kadar, “Demokratik, Şeffaf, Kamucu Eğitim Sistemi” başlığını da “Yaşayan, Nitelikli, Güvenli Okullar” başlangıcına kadar bütünüyle okudum. İlkinde Altı Ok ve laiklik benimseniyor; bu, dinî kurumların kuruluş/tasfiye düzenini veya kamu finansmanını ayrıca tanımlamıyor. İkincisinde şu açık araç var:

> Devletin kamusal eğitim sorumluluğu hiçbir cemaat, tarikat, vakıf, dernek ve siyasi yapılara devredilmeyecektir. Karma, laik ve bilimsel eğitim temel ilke olacaktır.

Bu, kamusal **eğitim sorumluluğunun devredilmemesi** kuralıdır. Dinsel devlet kurumlarının tümünün feshi, Diyanet tasarımı veya dinî kurum/cemaatlere bütün kamu ödemelerinin sona ermesi olarak genişletilemez. `0314-v4-yeni-din-kurum-scope` bu iki gerçek başlıkla sınırlı kaldığında anlamı uygun. Bunun “programın tamamında hiçbir ilgili araç yok” biçiminde sunulması uygun olmaz. Önceki I–V taramasının İslam'a özgü dar sorusu, genişleyen yeni soru için yapılmış tam program incelemesi sayılmamalı.

Kaynakta eğitim aracı bulunduğu için scope okura “hiçbir ilgili içerik yok” izlenimi vermemeli. Mevcut gerekçenin bu aracı somut olarak anması bu bakımdan yerinde. Bu eğitim içeriği ayrıca gösterilecekse kendi gerçek eğitim pasajı ve konu alanıyla sunulmalı; mevcut dar scope olumlu kurumsal yanıt olarak kullanılmamalı.

## İYİ Parti: dar sonuç uygun, gerekçe yer atfı düzeltilmeli

Kaynak [Ankara teşkilatı sitesindeki program](https://iyipartiankara.org.tr/parti-programi/index.php), `0205-iyi-program-page-v1`, SHA `7165cd05b2643134a6a8fc4910f312915c59c52a31561ec6f657d89f2a493f9a`; kesin yayın/kabul günü bilinmiyor. İncelediğim özgün HTML'de 1. bölümün başından 2. bölümün sonuna ve 4. Kamu Yönetimi bölümünün tamamına döndüm; 3. Toplum ve 5. İç ve Dış Güvenlik başlangıçlarını bölüm sınırı olarak kullandım.

1. bölüm “İnançlara saygı ve ifade özgürlüğünü sağlamak” amacını açıkça içeriyor. `0306-iyi-program-scope-islam-inanc-orgutlenmesi-passage` bunu doğrudan destekliyor. 2. bölüm haklar, hukuk düzeni, yargı, parlamento ve seçimler; 4. bölüm kamu hizmetleri, merkezi/yerel yönetim ve personel rejimini düzenliyor. 4. bölümde kamu bürokrasisi için ehliyet, liyakat, kariyer, tarafsızlık ve eşitlik ilkeleri var. Bu tam bölümlerde, yeni sorunun gerektirdiği dinsel devlet kurumu tasarımı veya dinî kurumlara kamu finansmanı için özgül araç saptamadım. `0314-v4-iyi-din-kurum-scope` sonucu yalnız bu sınırla destekleniyor.

**Somut düzeltme:** Scope reason'daki “İncelenen amaçlar, haklar ve kamu yönetimi bölümlerinde ... laik hukuk devleti bağlamları bulunur” ifadesi, belirtilen bölümlerdeki açık bir ifadeye atıf gibi okunuyor. Oysa şu açık metin 5. İç ve Dış Güvenlik bölümünde, Türk ordusunun yapılanması anlatılırken bulunuyor:

> Yeniden tesis edilecek laik, demokratik, sosyal, hukuk devleti ve parlamenter rejimle birlikte Genelkurmay Başkanlığı Millî Savunma Bakanlığına, Kuvvet Komutanlıkları da Genelkurmay Başkanlığına bağlanacaktır.

Dar kapsamı genişletmeden gerekçe şöyle kesinleştirilebilir: “İncelenen 1, 2 ve 4. bölümlerde inançlara saygı, demokratik hukuk düzeni ve kamu yönetiminde tarafsızlık/eşitlik ilkeleri bulunur; bu belirli bölümlerde dinsel devlet kurumlarının yapısı veya dinî kurumların devlet finansmanı için ayrıca açık araç belirtilmez.” Aynı yer kesinliği authored-review'daki `0314-v4-iyi-din-kurum-scope-row` explanation ve bu ifadeyi tekrarlayan semantic review gerekçesinde de korunmalı. Burada yeni bir karşıt politika bulgusu yok; düzeltilecek olan gerekçenin bölüm atfıdır.

Eski context alanının sekiz bölüm için **İslam kurumsal yapısı** hakkında kurduğu sınırlı yokluk açıklaması yeni genel finansman sorusuna otomatik taşınmamalı. Bu denetimde yeni soruya ilişkin yeniden okuduğum yokluk sınırı 1/2/4'tür; sekiz bölümün tamamını yeni soruyla yeniden taradığımı iddia etmiyorum.

## Saadet: dört gerçek sayfayla sınırlı sonuç

Kaynak [parti belge dizininin program PDF'si](https://admin.saadet.org.tr/dosyalar/K-D-1751227555.pdf), `0209-saadet-current-program-v1`, SHA `6718b7ca1b2997d0d1f0e52999c8c5ce852af648be7e83cb26c5a7eef060805c`. Nüsha 3 Kasım 2019, Ankara ve 70 PDF sayfası bilgisiyle kayıtlı. Dizin güncelliği her hükmün yeni kabul edildiği anlamına gelmiyor.

PDF index 4/basılı 5 Giriş'i; index 5/basılı 6 siyaset anlayışının kucaklayıcılık ve birleştiricilik alt başlıklarını; index 6/basılı 7 hak, hizmet, adalet ve liyakat bölümlerini; index 10/basılı 11 Demokrasi, İnsan Hakları ve Özgürlükler sayfasını tam okudum. Özgün ifadeler etnik/dinî/mezhepsel kimliği nedeniyle baskı görmeme; kamu hizmetinden din/dil/cinsiyet/etnik köken ayrımı olmadan yararlanma; devletin din ve mezhep gözetmeden hak ve özgürlükleri garanti etmesi üzerinedir.

Bu dört sayfada Diyanet veya diğer dinsel devlet kurumlarının yeniden düzenlenmesi/tasfiyesi yahut dinî kurum ve cemaatlerin kamu finansmanı için ayrı bir araç yok. Bu sonuç `0314-v4-saadet-din-kurum-scope` içindeki belirtilmiş sayfalarla sınırlı tutulmalı. Devletin hiçbir vatandaşı öteki görmemesi veya inanca bakmadan insan haklarını teslim etmesi, dinî kurum finansmanının belirli bir modeline eşitlenemez. Önceki 1–70 taraması eski İslam'a özgü soruya aittir; yeni soru için bütün PDF'yi yeniden okuma sonucu gibi gösterilemez. Saadet'in bu başlıkta bir politikası bulunmadığı veya kurumları reddettiği sonucuna varmadım.

## EMEP: fesih nesnesi devlet kurumları, finansman nesnesi kurumlar ve cemaatler

Kaynak [birleşik program/tüzük yayını](https://www.emep.org/emek-partisi-program-ve-tuzugu), `0208-emep-program-charter-v1`, SHA `16e8971e7cc015b0134f7836a9930200f04e9a298803f58801cf2261e3593329`. Burada kullanılan içerik tüzük kısmı değil **program gövdesindeki G / A — Halk İktidarı ve Halk Demokrasisi İçin / 7** maddesidir. Yayının 2019/2020 web tarihleri programın kesin kabul günü sayılmamalı.

Madde 7'nin tamamını, 6 ve 8–10. maddelerin bağlamıyla okudum. `0314-v4-emep-din-kurum-p` tam 7. maddeyle özgün HTML görünen metninde birebir eşleşiyor. İki farklı nesne açık:

1. “Eğitim alanındakiler dahil **devletin tüm dinsel kurumlarının feshi**”: tüm sözcüğü devletin dinsel kurumlarına aittir. Bütün özel dinî örgütlerin feshini söylemez.
2. “**dini kurumlar ve cemaatlerin devlet tarafından finansmanına son verilerek** dinsel alanın bütünüyle inananlara terk edilmesi”: burada kamu finansmanına son verme, dinî kurumlar ve cemaatleri kapsayan ayrı araçtır; bu grupların var olmasının yasaklanması değildir.

İnanma ve inanmama hakkı, devletin din/mezhep/inanç toplulukları karşısında yansızlığı ve dinsel alanın inananlara bırakılması aynı maddenin anlam sınırını güçlendirir. Bu nedenle summary `0314-v4-emep-din-kurum-s` ve field `0314-v4-emep-din-kurum-f` yeni tanıma doğrudan uygundur. Özel İslam kurumu adı, tüm özel cemaatlere genel yasak veya uygulanmış fesih sonucu eklenmemiştir. Eski yalnız İslam'a özgü yokluk kapsamının bu yeni genel hüküm yerine kullanılması uygun olmaz; v4'ün bunu değiştirmesi gerekçelidir.

## TİP: kapatma ile yeni kurum birlikte

Kaynak [HTML parti programı](https://tip.org.tr/parti-programi), `0203-tip-program-v1`, SHA `6aa8a0087e2426e808defbc8e427281f08862b1206fdad2ae847fd294854c7e0`; sürümün kesin kabul günü belirtilmemiş. “Mezhepçiliğe Karşı Eşit Yurttaşlık” başlığını, Alevilere ilişkin önceki paragrafı ve sonraki Kadın Mücadelesi başlığının sınırını okuyarak kontrol ettim.

`0304-tip-program-diyanet-p1` aynı paragrafta zorunlu din derslerinin kaldırılmasını, Diyanet'in kapatılmasını, tarikatlaşmayla mücadeleyi ve din işlerinin tüm din/mezheplere eşit mesafeli bir kurumda yeniden düzenlenmesini içeriyor. `0304-tip-program-diyanet-q` son cümleyi ayrıca taşır. Seçili summary hem kapatmayı hem yeniden düzenlemeyi koruduğundan yeterli. “Tüm dinsel devlet kurumları kaldırılır” ya da “devletin bütün din hizmetleri sona erer” denemez; metin yeni bir kurum hedefini de açıkça korur. Kamu finansmanını sonlandıran bir araç bu pasajda yazılı değildir. V4'ün ilk kabul yolunda somut kurum yaklaşımı olarak kullanılabilir.

## DEM: eleştirinin öznesi ve somut kararın öznesi ayrı

Kaynak [4. Olağanüstü Büyük Kongre kararları](https://www.demparti.org.tr/tr/4-uncu-olaganustu-buyuk-kongre-kararlari/20375/), `0204-dem-policies-v1`, SHA `0ba81cd43ab9b5455db4a77ca66fc4bdf08df72a3dcb4fd40405ab977cc8ec45`; yayın günü bilinmeyen kongre eki, **supplement** rolündedir.

“Demokratik İslam Hareketi” başlığını Demokratik Alevi Hareketi başlığına kadar tam okudum. Başta, iktidarların İslam'ı siyasete alet ettiği ve Diyanet'i manipülasyon/kutuplaştırma amacıyla kullandığı ileri sürülür. Bunlar belgenin siyasal eleştirileridir; tarafsız doğrulanmış uygulama olgusu veya Diyanet'i feshetme taahhüdü değildir. Sonraki somut kararın öznesi partidir: DİK'le ilişkileri canlandırmak, çalışmalarını desteklemek, ortak etkinlikler yapmak, yerel din âlimleriyle temas geliştirmek ve komisyon çalışmalarını güçlendirmek.

Seçili `0305-dem-program-islam-passage` ve `0305-dem-program-islam-context-passage` bu özgül örgütsel ilişkinin ilk iki cümlesini taşır. Summary bunları aşarak bir devlet kurumu tasarımı veya kamu finansmanı vaadi eklemiyor. V4 tanımının İslam'a özgü tamamlayıcı belge yolu bakımından uygun; genel devlet kurumları veya kamu finansmanı sorusunda ayrıca olumlu yanıt gibi sayılmamalı.

İkinci DEM satırındaki `0204-dem-missing-current-program` gerçek `0204-dem-search-program` girişimine bağlıdır. Menü, site içi ve web aramasında bağımsız güncel tam ana program bulunamadığı kayıtlıdır. Kongre ekinin varlığı bu edinme açığını kapatmaz. Eksik kayıt ayrıca tarihsel 2012 basın aktarımını ayrı tür/tarihle anıyor; bu aktarım seçili güncel program kanıtı olarak kullanılmıyor. Bu denetim yeni bir program araması değildir.

## DBP/BDP: iki tarihsel kopya ve güncel belge açığı

İki kaynağın özgün “Laiklik” bölümlerini ayrı okudum:

- [Blogspot kopyası](https://bdpgenelmerkez.blogspot.com/p/roportajlar.html), `0207-dbp-bdp-program-v1`, SHA `bd00c00dddbf2011987243257252ea3bf2dc47998bb3d1b7443fb732ec46bdbc`.
- [WordPress kopyası](https://bdpblog.wordpress.com/parti-programimiz/), `0207-dbp-bdp-program-wordpress-v1`, SHA `1db73a2c13c009691839920cad0824ee700df9dabd1ccad858165d464192fbde`.

İkisinde de `0308-dbp-program-097-{0,1}-passage` metni gerçekten vardır: Diyanet'in demokratik düzenlenmesi ve din/inanç işlerinin **tedricen** tümüyle inanç gruplarına bırakılması. Kaynakta öncesinde çoğunluğun din/mezhebini temel alan idari yapılanmanın değiştirileceği; devamında inanç gruplarının eğitim kurumları ve ibadethanelerinin engellenmeyip tümüne eşit koşullarda destek verileceği belirtilir. Bu geniş bağlam, metni derhal Diyanet feshi veya inanç gruplarına destek verilmemesi şeklinde okumayı engeller.

Seçili iki summary kurumsal düzenleme ve kademeli geçişi doğru koruyor. Devamındaki “eşit koşullarda destek” cümlesi, bağımsız bir nakit ödeme, belirli kamu bütçesi veya finansman kesintisi aracı diye etiketlenmemeli; desteğin türünü bu cümle açıklamaz. Daha geniş finansman sentezi yapılırsa bu bağlam da gösterilmeli; mevcut iki cümlede finansman yokluğu ileri sürülmediğinden burada bir yanlış özet saptamadım.

İki kopyanın kabul/yayın tarihi, birbirine sırası ve güncel DBP programıyla birebir ilişkisi kanıtlanmış değil; **historical** rolü zorunlu. `0207-dbp-missing-current-program` → `0207-dbp-search-current-program` bağlantısı güncel DBP adına bağımsız tam program aramasında bulunamama sonucunu taşır. İki BDP kopyasının varlığı, bu üçüncü satırdaki güncel belge açığını veya güncel tutumu çözmez.

## Demokrat Parti: arşiv programında yeniden yapılandırma

Kaynak [29 Aralık 2021 arşiv yakalamalı PDF](https://web.archive.org/web/20211229025938id_/https://www.dp.org.tr/storage/DP.Yeni.Program.pdf), `0210-demokrat-program-archive-v1`, SHA `6554ec05b00d37f62159e1d722f4464ff8b32569ddf7455108530cc772747da2`. 83 PDF sayfalı nüshanın kesin kabul ve güncellik tarihi bilinmiyor.

PDF index 3/basılı 10'un tamamı okundu. “Demokrat Parti, İnsanı Merkez Alır” altında laiklik, devletin din kuralları yerine halk iradesiyle yönetilmesi; inançlara eşit uzaklık ve kamusal sorumlulukların din/mezhep farkı gözetilmeden yerine getirilmesi çerçevesinde açıklanıyor. `0313-demokrat-025-islam-inanc-orgutlenmesi-p` bu bağlamda Diyanet'in değişik inanç gruplarına hizmet verecek şekilde yeniden yapılandırılmasını tam cümle olarak taşıyor.

Seçili summary yeniden yapılandırma hedefini doğru aktarır. Devletin bütün dinsel kurumlarını kapatma veya kamu finansmanını kesme anlamı yok; bunlar eklenmemeli. Arşiv yakalama tarihi program kabul tarihi yapılmamalı. `program` rolü belgenin türünü, seçili satırın açıklaması ise arşiv nüshası ve güncellik sınırını birlikte koruyor.

## Yeni Yol: gerçek belge açığı

`0307-yeni-yol-missing-program` → `0307-yeni-yol-search-program-20261113` kaydını okudum. Sonuç `Bulunamadı`; girişim Yargıtay kimlik sayfasında program bağlantısı olmamasını, diğer sayfanın zaman aşımını ve 10 Ocak 2025 kuruluş haberinin taslak onayını aktarıp metni yayımlamamasını ayrı kaydediyor. Aynı adlı eski oluşum, ortak Meclis grubu ve diğer partilerin belgeleri dışlanmış.

Bu, programın var olmadığı veya partinin din kurumları hakkında görüşü bulunmadığı tespiti değildir. Özgün parti programı edinilemediğinden yeni sorunun iki kabul yoluna da kaynaklı bir yanıt verilemiyor. Yeni soruya geçirilirken gerçek missing ve girişim bağı korunmuş; metin açığını scope yokluğu gibi sunan bir değişiklik görmedim.

## Bağ denetimi ve yapılacak tek düzeltmenin sınırı

13 `row_reviews` kaydı, dokuz gerçek parti, v4 satır soyları, her alanın kendi finding_evidence pasajları, pasaj-sürüm sahipliği, üç scope'un parti/sürüm/satır bağları ve üç missing→attempt bağı kontrol edildi: **bağ hatası yok**. V3'ten gelen authored-review anahtarlarının `03-v3-...`, paket satırlarının `04-03-v3-...` olması açık `row_mappings` ile eşleşiyor; yeni dört satır kendi kimliğini taşıyor. Bu mekanik eşleşme anlam onayı üretmek için kullanılmadı.

Uygulanması gereken somut düzeltme, İYİ Parti dar scope gerekçesinin bölüm atfıdır. `0314-v4-iyi-din-kurum-scope`, ona bağlı row semantic review ve authored-review explanation aynı gerçek 1/2/4 bölüm sınırına uygun biçimde kesinleştirilmeli; özgün baytlar ve eski inceleme kaydı değiştirilmemeli. Kapsamı bütün programa genişletmek veya yeni bir karşıt tutum yazmak gerekmiyor. Diğer sonuçlar bu raporda açık tutulan kaynak, rol, kademeli geçiş ve belge açığı sınırlarıyla kullanılabilir.
