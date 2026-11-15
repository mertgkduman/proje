# Faz 03-16 için ajan kaynak ikinci okuması — ön inceleme

**Sonuç:** Aşağıda sınırları açıklanan risk okumasında yeni bir maddi kaynak→özet hatası saptanmadı. Mevcut belge/sıra belirsizlikleri korunuyor. Bu, formal faz doğrulaması, importer paketi, insan siyasi doğrulaması veya UAT kabulü değildir. Yeni complete kapısının henüz uygulanmamış olması kaynak hatası olarak raporlanmadı.

**Reviewer:** `agent`, `/root/precheck_03_sources`. Parent'ın CLI çözümlemesi `gpt-6.1-sol/xhigh`; bu alt görev model değiştirmedi, Astra veya başka ajan başlatmadı. Aktif kök GSD yürütümü içinde yalnız bu klasöre yazıldı. İlk yazıdan önce literal proje kökünde `/tmp/gsd-03-root-pin.sh` başarılı oldu. Commit, veri/kod değişikliği, importer, audit, publish veya global test yok.

**Gerçek zaman:** Kaynak okuması sırasında saat `2026-11-15T12:38:37Z` olarak gözlendi; yapılandırılmış paket `2026-11-15T12:52:48.199108+00:00` anında kaydedildi. JSON'daki kontrol `recorded_at` değerleri paketleme zamanıdır; geçmiş 13–14 Kasım incelemelerinin zamanı değildir. Eski inceleme tarihleri kendi provenance kayıtlarında aynen bırakıldı.

## Sabit giriş ve kapsam

`data/current.json` → `27033583248b4951b3fe8e5fd6d77b9f`. Renderer22, taxonomy4, schema6, policy2, comparison validation2/synthesis2/view1. JSON SHA256:

`65a522a9e7aba2625e87d8436059dc5a7a11c1bf06b7afb50b09b36dcf14a773`

SQLite SHA256:

`74d6c47aa44d51e1e9f185190393540191992623a774c8400d262c0e4fd4ae87`

Paketleme sırasında her iki dosyanın gerçek SHA'sı manifestle ve current kimliğiyle yeniden eşlendi. Bu bütünlük denetimi anlam kanıtı olarak kullanılmadı.

- Seçili v4: 305 konu, 4.935 satır, 3.941 alan, 854 sentez; dokuz parti ve 141 toplam belge sürümü.
- Yeni risk örneklemi: 24 kontrol grubu; 113 benzersiz seçili satır, 93 alan ve 24 açıkça incelenmiş sentez kaydı bağlandı. Bunlar sabit kabul kotası değildir.
- Bağlı kapsam: 169 pasaj, 36 gerçek scope, altı missing ve altı gerçek attempt. `source-second-reading.json` her kontrolü gerçek topic/row/field/finding/change/synthesis kimlikleriyle, scope/missing/attempt ve version/passages zinciriyle verir.
- 25 bağlı kaynak sürümünün 24'ünde bu koşuda ilgili özgün bağlam/sayfa/görüntü okundu. `0207-dbp-bdp-program-wordpress-v1` için önceki ayrı kaynak okuması ve mevcut kopya/pasaj bağı yeniden kullanıldı. Hiçbir sürüm için kitabın tamamının bu koşuda yeniden okunduğu iddia edilmiyor.
- `source_versions[]` her kaynak için köke göre gerçek özgün yol, URL, sürüm etiketi, kayıtlı ve yeniden hesaplanan tam SHA, kendi sürümüne ait publisher/byline atfı ve okuma provenance'ı içerir. `passages[]` gerçek madde/bölüm/index/basılı sayfa ve alıntıyı; `scopes[]`, `missing[]`, `attempts[]` tam araştırma sınırını verir.

Örneklem, geçmiş tam okumaları gereksizce tekrarlamak yerine koşul kaybı, organ/düzey aktarımı, kopya/sıra karışması, görüntüde olup metin katmanında olmayan içerik ve eksiklikten tutum üretme risklerini hedefledi. Charter/program/supplement/historical kaynak rolleri; merkez/il/ilçe/diğer organlar; üyelik, seçim, denetim, görüş/disiplin/itiraz; ilke/hedef/araç; farklı yararlanıcı, eşik ve sektör koşulları kapsandı. Az-partili başlıklarda gerçek tek-olumlu/durum yapısı ayrıca incelendi.

## Dokuz parti paketinin kapanış izi

Tablodaki sayılar araştırma kayıtlarını sayar; siyasi başarı, kalite veya tercih puanı değildir. Seçili v4 durumları sorgulandı; ID'deki `v3` parçasından taxonomy sürümü çıkarılmadı.

| Parti | Seçili satır | evidence | Dar açık-ifade yokluğu | Gerçek belge açığı | Alan | Eski semantic kararları |
|---|---:|---:|---:|---:|---:|---:|
| Yeni Parti | 496 | 419 | 77 | 0 | 430 | 496 |
| TİP | 689 | 500 | 189 | 0 | 504 | 687 |
| DEM | 822 | 529 | 154 | 139 | 530 | 677 |
| İYİ | 427 | 350 | 77 | 0 | 376 | 513 |
| Yeni Yol | 305 | 0 | 0 | 305 | 0 | 0; iki gerçek arama günlüğü |
| DBP | 717 | 471 | 107 | 139 | 479 | 571 |
| EMEP | 476 | 379 | 97 | 0 | 381 | 470 |
| Saadet | 538 | 435 | 103 | 0 | 715 | 507 + program319 |
| Demokrat | 465 | 378 | 87 | 0 | 526 | 359 + program241 |

Her partinin gerçek seçili konusu 305. Seçili satırlarda `not_researched`/`in_progress` yok. Seçili kaynak envanterinin 1.729 bölüm/soru kaydında `unmatched_headings` boş. Bu sonuç tek başına tüm anlamın doğru olduğunu göstermez; aşağıdaki maddi okuma ayrı kanıttır.

Dokuz partiye ait 11 semantic/program-semantic dosyasının **4.840 kararının tamamı** sonuç, boş olmayan özgül gerekçe, gerçek subject ve listelenmiş pasaj kimlikleri bakımından denetlendi; bozuk referans veya `reviewed` dışı karar saptanmadı. Dosyaların tarihsel üst `status: in_progress` etiketleri bugünkü satır durumu yapılmadı; `complete` etiketi de anlam onayı sayılmadı. Yeni Yol'un sıfır olumlu kararı belge açığına uygundur; 03-07'deki iki arama günlüğü bütünüyle okundu.

Seçili 3.941 alanda eski inceleme provenance'ı ayrıca izlendi: 15 doğrudan field semantic kaydı, 3.905 aynı summary/quote finding çiftini koruyan önceki field semantic kaydı, 21 finding-review yoluyla izlenen alan. Son 21 kimlik ve gerçek review gerekçeleri `coverage-map.json` içinde açıkça listelenir. Mekanik soy yeni yapılmış anlam incelemesi veya yeni insan onayı değildir. `v3-v4-row-lineage.json`, önceki soy ve son yerine-geçme/bağımlı-sentez denetimleri yeniden kullanılabilir kanıttır; sıfır-işlem kapsam kapanışı gibi yorumlanmadı.

## Gerçek risk okuması

Aşağıdaki kısa tablo kararın nedenini verir. Kontrol başına tam gerçek kimlikler, kaynak yolu/SHA, pasaj, kısa alıntı, koşul ve kapsam kayıtları JSON'un aynı `SRxx` nesnesindedir. `dependent_claim_ids_for_trace_not_blanket_reapproval`, ilgili alanı kullanan diğer cümleleri izlemek içindir; bütün bu cümlelerin otomatik yeniden onayı değildir.

| Kontrol | Kaynak bağlamı ve doğrudan sonuç |
|---|---|
| SR01 Yeni Parti PM/üyelik | Özgün HTML Madde8,22/7,22/11-f. Genel oy yasağının yanında hükümet konularında yalnız TBMM grup yöneticilerinin özel oyu korunuyor. Sıfır-oy çevresindeki kayıt silme MYK'nın karar verebilme yetkisi; gerçekleşmiş olay değil. `0314-v4-yeni-pm-katilim-row` ve `04-03-v3-0303-epm-uyeligin-sona-ermesi-row`. |
| SR02 TİP PDF | Index8/basılı7 ve22/basılı21 gerçek görüntüleri. Aday belirleme ve merkez adayları aynı kaynak bağlamında; toplantının PDF listesine HTML'deki komite üyeleri eklenmemiş. `04-03-v3-0304-tip-pdf-aday-yetki-field`, `04-03-v3-0304-tip-pdf-genisletilmis-field`. |
| SR03 DEM/HEDEP | İki nüshanın Madde17'si ayrı özgün sayfalardan. Altı yeni başkan seçim satırında ilk iki tur delege tam sayısı salt çoğunluğu ve üçüncü tur en çok oy alan iki kişi korunuyor. Uzlaşma cinsiyet temsili ve disiplin itirazının kapsamı ayrı. HEDEP'in uzlaşma/itiraz tam sayfalarında önceki ayrı okuma yeniden kullanıldı. |
| SR04 İYİ defter/48 | Index5/basılı6 ile48/basılı49 birlikte; kayıt defteri yalnız ilçede. 2020/2026 index31 karşılıklı: seçilen50/25→60/30 ve gündem1/10→1/5 ayrı. Saadet index23/basılı24'teki kendi ilçe istisnası da yeniden okundu. |
| SR05 İYİ üyelik/aidat | Eski index7 ile yeni index7,45,49. Toplu kayıt yenileme gerekçeli ve koşullu; disiplinle aynı işlem değil. Mali durumun müsait olması aidatın ödenmemesine ilişkin **uyarma** hükmünün koşulu; genel ödeme yükümlülüğü Madde80'de ayrı. `04-0314-iyi-membership-record-reset-f` ve aidat tarihçesi birlikte incelendi. |
| SR06 Demokrat yerel/yan kuruluş | Tüzük index12/basılı12 görüntüsü. Büyükşehir merkez ilçe mahallelerinde seçim, öteki yerlerde atama ayrımı; başlık komşuluğundan kesin münhasırlık/genellik çıkmıyor. STK yan kuruluşunun ilçe/il/Genel Merkez üç kademesi korunuyor. Aynı paragraftan türeyen üç temsilcilik alanının tümü okundu. |
| SR07 Demokrat yeter sayı/hesap | Index14,16–17. Madde20 ilçe1/10 ve Madde25 her-kademe ilk-açılış yarı+1/ikinci toplantı ayrı mevcut; alan131 ilişkinin açıklanmadığını söylüyor. `0314-v4-demokrat-kongre-hesap-komisyon-row` gerçek yerel hesap komisyonunu dar bağımsız-kurul yokluğuyla birlikte tutuyor. |
| SR08 Denetleme | TİP HTML5.1 ve PDF index23 görüntüsü; Saadet index6; Demokrat index16–17. TİP örgütsel kurulunun6 ay/yıl farkı, Saadet Büyük Kongre hesap komisyonu ve Demokrat il/ilçe kongre hesabı aynı kurum gibi sunulmuyor. Dört ilgili sentezin bütün olumlu tarafları incelendi. |
| SR09 DBP görüş/kota | Güncel HTML4/97 ve iki tarihsel BDP tüzük kopyası. Bilgiye cevap/üst başvuru, meşru parti içi eleştiri ve disiplin itirazı ayrı. Blogspot `%40`; WordPress `@`: oran ikinci nüshaya aktarılmıyor. Güncel eşit-temsil ifadesi tarihsel oranla birleştirilmiyor. |
| SR10 Engelli koordinasyonu | Saadet index12/basılı13'te kurabilir ve değiştirilebilir7/5/3 gerçek. Üç kademe tek olumlu parti; TİP iki nüsha iki parti değil. Dokuz tarafın scope/missing bağları ve iki sentez kontrol edildi; diğer tüzüklerin tamamı bu koşuda yeniden okunmadı. |
| SR11 Siyasi etik | İYİ index37/basılı38 iki tam paragraf. Oluşturulabilirlik, Genel Başkana bağlılık, şikâyet ve yönetmelik zinciri korunuyor. Disiplin cezası/fiilen kurulmuş yapı iddiası yok. Diğer sekiz tarafın kapsamları önceki bağımsız okumayla sınırlı biçimde yeniden kullanıldı. |
| SR12 Kampanya | DEM index27/basılı28 Madde50 ve EMEP HTML22. Afet dayanışması/katılım şartları ile parti finansmanı kampanyası farklı. EMEP'in olumlu mali kampanya hükmü dar afet-usul yokluğuna çevrilmemiş. Üç ilgili sentezde tüm tipli taraflar incelendi. |
| SR13 Temel gelir | Saadet program index37 genel ilke ve40/basılı41 somut ödeme; Demokrat index44/basılı51. Saadet'in doğum/çalışma/vergi koşulları silinmiyor; Demokrat her vatandaş der ama eşit tutar/periyot/icra koşulu eklenmiyor. |
| SR14 Nitel yaşam/nakit | TİP sosyalist çalışma-bölüşüm özgün paragrafı ve İYİ tam HTML'nin gerçek çiftçi/afet pasajları. İnsanca yaşam güvencesi/ücretsiz hizmet nakit vaadine çevrilmiyor. İYİ genç çiftçi maaşı ve fark primi gözden kaçırılmamış; dar asgari/düzenli gelir sorusu tüm parti politikasına yokluk olarak yayılmıyor. |
| SR15 BDP gelir | Blogspot sosyal güvenlik/sosyal politika özgün paragrafları; WordPress ayrı önceki okuma. `2022 sayılı kanun` yıl değil numara. Yaşlı aylığı ve çocuk/yaşlı yoksulluğuna öncelikli düzenli nakit farklı araçlar; güncel DBP program açığı ayrıca sürüyor. |
| SR16 Saatler | DEM kongre emek paragrafı; EMEP HTML; tarama öneri index1 ve gövde index16 görüntüsü. DEM ücret kaybı olmadan6 saat; EMEP HTML7 saat/5 günlük hafta, ağır-tehlikeli5 saat; öneri7/35 ile gövde<8/<40 ve ücret kaybı yok ayrı. Gün dönüşümü ve kabul/sıra icat edilmiyor. |
| SR17 EMEP eğitim | Öneri13 gerçekten index1/basılı2. İki yeni seçili alan `04-0314-emep-education-correct-access-f`/`...language-f` doğru `0314-emep-education-proposal-correct-page-p` ile bağlı. Eski iki yanlış locator tarihselde kalır. 17 manuel locator için önceki tek tek görsel tablo yeniden kullanıldı. |
| SR18 Su/ihtiyaç | DEM kongre ekonomi3'te ihtiyaç sınırına kadar kamu kaynaklı ücretsiz hizmet; EMEP tarama index2 öneri14'te herkese yeterli parasız su. Koşullar birbirine aktarılmıyor; öneri kabul edilmiş metin sayılmıyor. Aynı DEM paragrafından üç türev alan incelendi. |
| SR19 Temsilci ücreti | TİP sosyalist demokrasi ve EMEP halk demokrasisi bağlamı özgün HTML'den. Ortalama işçi ile kalifiye işçi ortalaması ayrı. Bugünkü maaş/fiilî uygulama/siyasi sıralama değil. |
| SR20 Demokrat görüntü | Ana program PDF8/index7/basılı14 gerçek önsöz devamı. Senato ve seçim barajını temsilde-adalet sağlayacak orana indirme gerçekten var. Boş metin katmanı yokluk sayılmadı, baraj oranı üretilmedi. |
| SR21 Demokrat iklim | Index74–75/basılı81–82 kesintisiz. 2020 hedefi değişiklik yapılmazsa öngörülen düzeyden%20; mutlak salım/net-sıfır değil. İthalat karbon vergisi emisyonlarını kısıtlamayan ülkelere bağlı; iki sayfa dayanağı korunuyor. Aynı paragrafın dört hedef/araç alanı birlikte okundu. |
| SR22 DYP1985 açık | Gerçek index102/basılı98 görüntüsünden hemen sonraki index103/basılı101'e geçiş görüldü. Basılı99–100 bu nüshada fiziksel eksik. `0314-dyp-1985-income-pages-missing`→`0314-dyp-1985-income-page-check` gerçek. Başka kopyadan tamamlama veya bütün parti gelir politikası yokluğu yok. |
| SR23 DYP üç çift | Ayrı hâkim/savcı kurulları↔Bakanlık vesayetinden çıkış; zorunlu hizmet yetersizliğinde gerektiğinde bütçe yardımı↔öz yerel gelir; yoksulun sigorta primi↔katkı payı alınmaması. Üç tarihsel görüntü ve üç ana program karşılığı yeniden okundu. Ara sıra/kabul bilinmiyor; prim ve katkı payı aynı araç değil. |
| SR24 Yeni Yol | Yargıtay331 kimliği, KARAR taslak onayı paragrafı ve iki03-07 arama günlüğü. Haber maddeleri sağlamaz; başka partinin programı/grup konuşması aktarılmıyor.305 konunun iki gerçek belge açığına bağlanması sahte hücre başı arama gerektirmez. |

## Belirsizlik, genişletme ve kalan iş

Yeni desteklenmeyen içerik bulunmadığından yeni immutable finding/row/passage önerisi yok. Şüpheli iki durumda inceleme tek örnekte bırakılmadı: İYİ'de aidat, yükümlülük, yaptırım ve önce/sonra; Demokrat'ta aynı konunun iki maddesi ve bütün ilgili yeter-sayı alanları birlikte okundu. Ayrıca EMEP eğitim hatasının iki gerçek ardılı, Demokrat temsilciliğinin üç türevi, DEM ihtiyaç paragrafının üç türevi ve Demokrat iklim paragrafının dört alanı birlikte incelendi.

Gerçek kaynak sınırları:

1. DEM/HEDEP, TİP HTML/PDF, DBP tarihsel kopyalar ve EMEP öneri/gövde için bilinmeyen sıra/kabul hukuki güncellik güvencesine çevrilemez.
2. DEM, DBP ve Yeni Yol bağımsız tam program edinim açıkları sürer. Kongre eki/tarihsel kopya aynı görünümde olumlu içerik taşısa da ana belge açığını kapatmaz. İYİ'nin tam HTML programı mevcut; PDF açığı tam program açığı değildir.
3. DYP1985 basılı99–100 yalnız o nüshanın gerçek açığıdır. Demokrat17/II başlığı münhasırlık kararı vermiyor; Madde20/25 önceliği metinde açıklanmıyor.
4. Saadet program/tüzük çiftlerinde farklı URL'ler aynı SHA baytlarını taşıyor. `same_hash_copy_facts` bunu tam sürüm künyeleriyle verir; kopya ne değişiklik ne sıra/yürürlük kanıtıdır.
5. Dar kapsam kayıtları ve eski tam okumalar sınırlı kanıttır. Bu koşu bütün4.935 satırın her özgün sayfasını yeniden okumuş değildir. Aynı finding çiftinin soyla korunması yeni anlam onayı değildir.

Bu ön incelemede yarım bırakılmış, destekli diye işaretlenen yeni bir kaynak okuması yok. WordPress programının bütününün ve diğer partilerin bütün yokluk kapsamlarının yeniden baştan okunması bu örneklemin iddiası değildir; hangi kanıtın yeniden kullanıldığı kontrol bazında açık. Sekiz ham `unclassified/unresolved/null` tanı ve üç descriptor-less prohibition değerlendirilmedi, `resolved` yapılmadı.

Root'un formal03-16 yürütümünde yapacağı iş: bu ajan paketini incelemek ve gerekirse resmi `03-source-review` sözleşmesine açıkça eşlemek; complete kapısı/negatif testleri ve son kabul kanıtlarını kendi aşamasında üretmek; insan UAT/ham tanı/prohibition kararlarını ayrı tutmak. Bu dosyaları importer'a vermek veya mevcut insan kabulü gibi yazmak uygun değildir. Kamu dağıtımı yapılmadı.

## Dosyalar

- `source-second-reading.json` — yeni özgül ajan kararları, bütün gerçek bağlar ve kaynak künyeleri.
- `coverage-map.json` — dokuz parti/current kapanış sayımları, bütün11 eski semantic paketi ve21 finding-review-only alanın ayrıntısı.
- `authored_checks.json` — betiğin üretmediği, ajan tarafından yazılmış24 anlam/kapsam kararı.
- `inspect_sources.py`, `materialize_precheck.py` — salt okunur girdilerden yalnız bu klasörde paket/görüntü üretimi.
- Bu klasördeki13 PNG ve03-14'ten yeniden açılan iki TİP locator PNG'si — kaynak ve hash listeleri JSON'da. Görüntüler gerçek özgün PDF'lerden üretilmiştir; HTML ekran görüntüsü değildir.

`03-VERIFICATION.md`, SUMMARY, STATE, ROADMAP, REQUIREMENTS, UAT, `data/`, `src/` ve current bu alt görevde değiştirilmedi.
