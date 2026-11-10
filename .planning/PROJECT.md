# Türkiye Siyasi Partileri: Tüzük, Program, İlke ve Uygulama Araştırması

## What This Is

Türkiye'deki siyasi partilerin kuruluş bilgilerini, tüzüklerini, programlarını, kamuoyuna verdikleri sözleri, finansmanlarını, harcamalarını ve belgelenmiş uygulamalarını inceleyen bağımsız, tarafsız ve kaynak temelli bir araştırma arşividir. Dağınık bilgileri doğrulanabilir kaynaklarla bir araya getirerek herkesin aynı bilgiye erişmesini ve kendi değerlendirmesini yapmasını amaçlar. Standart parti dosyaları ve karşılaştırmalar, sekmelere ayrılmış Türkçe bir HTML raporu ve yeni belgelerle güncellenebilir ortak veri tabanı üzerinden sunulacaktır.

## Core Value

Herkesin siyasi partiler hakkında kendi değerlendirmesini yapabilmesi için kaynağına kadar izlenebilen, karşılaştırılabilir ve eksiklerini açıkça gösteren bilgiye eşit erişim sağlamak.

## Requirements

### Validated

- ✓ Tarihli TBMM kopyası, dokuz partilik kapsam ve dahil etme/dışlama gerekçeleri — Faz 1 (KAPS-01–03).
- ✓ Kuruluştan başlayan inceleme dönemi ve kaynak yakalamasına bağlı veri kesimi — Faz 1 (KAPS-04).
- ✓ Yeni Parti'nin beş başlıklı kaynaklı pilotu; girişim destekli eksikler, metin kökeni ve olgu/beyan/yorum ayrımı — Faz 1 (KAY-02–03, MET-01–04, EKS-01–02).
- ✓ Kapalı SQLite snapshot'ından sürümlü JSON/HTML ve arşiv zinciri — Faz 1 (VER-01).

Kullanıcı `$gsd-verify-work 1 onaylıyorum` yanıtıyla sekiz UAT kontrolünü topluca kabul etti. Bu doğrulama pilot ve ortak yöntemin ilk uygulaması içindir; bütün parti dosyaları ve karşılaştırmalar sonraki fazlardadır.

### Active

- [ ] Her parti için kuruluş ve temel bilgiler, tüzük, program, söylem–uygulama ve finansman–harcamalar başlıkları altında standart bilgi dosyası hazırlamak.
- [ ] Parti üyelerinin haklarını, yönetimin seçilmesini ve denetlenmesini, farklı görüşlerin ifade mekanizmalarını belge maddelerine dayanarak incelemek.
- [ ] Kamuoyuna açıklanan ilke ve vaatleri belgelenmiş uygulamalarla, ilgili aktör, tarih ve bağlam korunarak karşılaştırmak.
- [ ] Finansman kaynaklarını ve harcama kalemlerini erişilebilen belgelere dayanarak incelemek; tutarların kapsadığı dönem ve para birimini kaydetmek.
- [ ] Birincil kaynaklara öncelik vermek; güvenilir gazetecilik, akademik araştırmalar ve bağımsız raporların kullanımını kaynak türüyle birlikte açıkça göstermek.
- [ ] Her önemli bulguya kaynak bağlantısı, belge tarihi, varsa sürüm, ilgili madde veya sayfa, erişim tarihi ve doğrulama tarihi eklemek.
- [ ] Kaynak bağlantılarını ve elde edilen belgeleri, değişiklikleri izlenebilen bir belge arşivinde toplamak.
- [ ] Kaynaktan doğrudan aktarılan metni siyah ve tırnak içinde; yapay zekâ tarafından kaynaklardan özetlenip düzenlenen metni koyu mavi göstermek; metin kökenini veri kayıtlarında korumak.
- [ ] Olgusal bilgi, kaynağın kendi beyanı ve yorum arasındaki ayrımı korumak; kaynakta bulunmayan olgusal iddialar üretmemek.
- [ ] Bulunamayan belgeyi “Bulunamadı”, erişilemeyen belgeyi “Erişilemedi”, doğrulanamayan iddiayı “Doğrulanamadı” olarak kaydetmek ve eksik bilgi listesini sunmak.
- [ ] Bütün partilere aynı araştırma başlıklarını ve doğrulama ölçütlerini uygulayan tüzük, program ve söylem–uygulama karşılaştırmaları hazırlamak.
- [ ] Herkesin okuyabileceği ve paylaşabileceği, sekmelere ayrılmış Türkçe HTML araştırma raporu oluşturmak.
- [ ] Yeni bilgilerle güncellenebilen ve raporun dayandığı kayıtların izlenebildiği ortak veri tabanı oluşturmak.

### Out of Scope

- CHP — kullanıcının ilk proje tanımında açıkça dışlanmıştır.
- Cumhur İttifakı'nın mevcut ve geçmiş ortakları — kullanıcının kapsamı daraltma kararıdır; geçmiş ortakların da dışlanacağı ayrıca onaylanmıştır.
- AKP/AK Parti, MHP, BBP, HÜDA PAR, DSP ve Yeniden Refah Partisi'nin parti dosyaları — onaylanan dışlama kuralı kapsamında ilk incelemede yer almazlar; BBP için ayrıca TBMM'de temsil koşulu değerlendirilir.
- TBMM kayıtlarında araştırmanın esas aldığı tarihte temsil edilmeyen partilerin tam incelemesi — ilk kapsam Meclis'te temsil edilen partilerle sınırlıdır.
- Bağımsız milletvekillerini ayrı bir siyasi parti gibi ele almak — ilk araştırmanın birimi siyasi partidir.
- Kaynaksız bilgiler, uydurma belge veya atıflar, doğrulanmamış iddiaları kesin olgu olarak sunmak — araştırmanın kaynak ve doğrulama ilkeleriyle bağdaşmaz.
- Yapay zekâ özetini doğrudan kaynak aktarımı gibi sunmak — kullanıcı metinlerin kökenini renk ve tür bakımından ayırmayı istemiştir.
- Partilere oy verme yönlendirmesi, siyasi sıralama veya araştırmacının tercihine dayalı puanlama — amaç herkesin kendi değerlendirmesini yapabileceği ortak bilgi kaynağı oluşturmaktır.

## Context

### Çıkış noktası ve yaklaşım

Proje, siyasi partiler ve aktörler değerlendirilirken yeterli, güvenilir ve karşılaştırılabilir bilgiye ulaşma ihtiyacından doğmuştur. Temel yaklaşım “Önce öğrenmek, sonra tanımak, karşılaştırmak ve değerlendirmek”tir. Bilgi eşitliği araştırmanın temelidir; kapsam dışına çıkarma kararları partiler hakkında olumlu veya olumsuz bir araştırma sonucu anlamına gelmez.

### Onaylanan başlangıç kapsamı

Kaynak: [TBMM — 28. Dönem Milletvekilleri Sandalye Dağılımı](https://tbmm.gov.tr/sandalyedagilimi). Başlangıç listesi oluşturulurken sayfa 2026-11-09 tarihinde görüntülenmiştir. Bu erişim tarihi, sayfanın kendi güncelleme tarihi olarak yorumlanamaz. Faz 1 içinde sayfanın özgün baytları arşivlenmiş ve liste yeniden kontrol edilmiştir. İlk doğrulanmış TBMM yakalamasının `2026-11-10T14:38:46.154751+00:00` erişim anı ilk yöntem kesimidir; bu an sayfanın kendi güncelleme tarihi değildir.

TBMM tablosundan elde edilen ve kullanıcının onayladığı ön liste, CHP ve Cumhur İttifakı'nın mevcut/geçmiş ortakları çıkarıldıktan sonra dokuz partidir:

1. Yeni Parti
2. Halkların Eşitlik ve Demokrasi Partisi (DEM Parti)
3. İYİ Parti
4. Yeni Yol Partisi
5. Türkiye İşçi Partisi (TİP)
6. Demokratik Bölgeler Partisi (DBP)
7. Emek Partisi (EMEP)
8. Saadet Partisi
9. Demokrat Parti

Kapsam değişiklikleri tarih ve gerekçeyle izlenmelidir. Ortak Meclis grubu, bir milletvekilinin parti üyeliği ve partinin hukuki kimliği birbirine karıştırılmamalıdır. Özellikle ortak grup yapılarında bireysel TBMM kayıtlarıyla farklı üyelikler saptanırsa bunlar sessizce birleştirilmemeli; kapsam ve kimlik uyuşmazlığı olarak kaydedilmelidir.

2023 seçimindeki ittifak ve seçim işbirliği bilgileri için başlangıç kaynağı: [Anadolu Ajansı — Seçimde 13 siyasi parti tek başına, diğerleri ittifak çatısında yarışacak](https://www.aa.com.tr/tr/gundem/secimde-13-siyasi-parti-tek-basina-digerleri-ittifak-catisinda-yarisacak/2868155). Resmî ittifak ortaklığı ile ortak liste/aday desteği aynı ilişki türü olarak kaydedilmemelidir. HÜDA PAR, DSP ve Yeniden Refah'ın kapsam dışında tutulması kullanıcıyla açıkça netleştirilmiştir; bu karar güncel ittifak üyeliği hakkında ayrıca doğrulanmış bir iddia yerine geçmez.

### Ortak inceleme başlıkları

- **A. Kuruluş ve temel bilgiler:** Partinin kuruluşu, kimliği ve araştırmayı anlamlandırmak için kaynaklardan doğrulanabilen temel bilgiler.
- **B. Parti tüzüğü:** Üyelik hakları, yönetim organları, seçim, denetim ve parti içi görüş ifade mekanizmaları.
- **C. Parti programı:** Açıklanan ilkeler, politika yaklaşımları ve hedefler.
- **D. Söylem ve uygulama:** Açıklamalar/vaatler ile belgelenmiş eylemler arasındaki karşılaştırma.
- **E. Finansman ve harcamalar:** Erişilebilen belgelerde gelir kaynakları ve harcamaların yöneldiği alanlar.

### Temel araştırma soruları

1. Parti neyi savunduğunu söylüyor?
2. Bu ilkeler tüzüğünde ve programında nasıl tanımlanıyor?
3. Parti üyeleri hangi haklara sahip?
4. Yönetim nasıl seçiliyor ve nasıl denetleniyor?
5. Parti içinde farklı görüşlerin ifade edilmesine hangi mekanizmalar olanak tanıyor?
6. Parti, ilan ettiği ilkeleri uygulamaya nasıl yansıtıyor?
7. Söylem ve uygulama arasında belgelenebilir farklılıklar var mı?
8. Hangi bilgiler doğrulanabiliyor, hangileri eksik kalıyor?
9. Partilerin aynı konulardaki düzenlemeleri ve yaklaşımları hangi noktalarda benzeşiyor veya farklılaşıyor?
10. Finansmanları nereden geliyor, harcamaları nereye yapılıyor?

### Kanıt ve kaynak politikası

Birincil kaynaklara öncelik verilir. Güvenilir gazetecilik çalışmaları, akademik araştırmalar ve bağımsız raporlar da kullanılabilir; bunların türü ve dayandıkları belgeler kaydedilir. Bir partinin kendi yayını, partinin ne söylediğine kanıt olabilir; uygulamanın gerçekleştiğine tek başına kanıt olarak değerlendirilmemelidir.

Her önemli bulgunun kaynağı, belge tarihi ve varsa sürümü, ilgili madde veya sayfası, erişim ve doğrulama tarihleri tutulur. Birden fazla kaynağa dayanan bulgularda her kaynakla kurulan ilişki korunur. Belgenin tarihi, incelenen olayın tarihi, erişim tarihi ve doğrulama tarihi birbirinin yerine kullanılmaz.

Finansman ve harcamalarda belge kapsamı, hesap dönemi, tutarın para birimi ve yayımlanma tarihi ayrı tutulur. Açıklanmayan veya bulunamayan tutarlar sıfır gibi gösterilmez. Farklı dönemleri ya da kapsamları olan mali veriler doğrudan eşdeğer kabul edilmez.

### Metin kökeni ve yapay zekâ

Kullanıcının ilk tanımındaki “Yapay zekâ tarafından üretilen bilgiler kabul edilmeyecektir” ilkesi, sonraki açıklamasıyla kaynakta doğrulanmış bilgilerin yapay zekâ tarafından özetlenip düzenlenmesine izin verecek şekilde netleştirilmiştir. Bu izin kaynakta bulunmayan yeni olgular üretmeyi kapsamaz.

- **Doğrudan aktarım:** Kaynaktaki metin, tırnak içinde ve yeri belirtilerek siyah gösterilir. Metin değiştirilirse doğrudan alıntı gibi sunulamaz.
- **Yapay zekâ özeti/düzenlemesi:** Kaynakta doğrulanmış içerik koyu mavi gösterilir. İlgili kaynaklara ve özgün pasajlara ulaşılabilir olmalıdır. Kısa özet ve kısa özgün alıntı birlikte görünür.
- Renkler, doğruluğa ya da güven düzeyine verilen puanlar değildir; metnin nasıl üretildiğini gösterir.
- Kullanıcı 2026-11-09 tarihli Phase 1 görüşmesinde görünür metin türü etiketlerini kaldırmış, alıntılar için tırnak işaretini seçmiştir. Metin kökeni veri kayıtlarında ve dışa aktarımlarda korunur; alıntı yapısı erişilebilirlik ve yazdırmada da anlaşılır olmalıdır.
- Olgusal bilgi ile yorum ayrı tutulur. Kaynağın kendi iddiası, bağımsız olarak doğrulanmış sonuç gibi sunulmaz.

### Eksik bilgi durumları

- **Bulunamadı:** Aranan belge için yapılan taramada belge bulunamamıştır; taranan kaynaklar ve arama tarihi kaydedilir.
- **Erişilemedi:** Belge veya kaynak adresi saptanmış, ancak içeriğine erişilememiştir; erişim denemesi kaydedilir.
- **Doğrulanamadı:** İddia için yeterli doğrulama sağlanamamıştır; mevcut kaynaklar ve eksik kanıt belirtilir.

Bu durumlar birbirinin yerine kullanılmaz ve bilginin yokluğundan parti aleyhine veya lehine sonuç çıkarılmaz.

### Beklenen teslimler

1. Her parti için standart bilgi dosyası.
2. Kaynak bağlantıları ve belge arşivi.
3. Tüzük ve program karşılaştırma tabloları.
4. Açıklanan ilkeler ile belgelenmiş uygulamaların karşılaştırılması.
5. Eksik veya doğrulanamayan bilgilerin listesi.
6. Herkesin okuyabileceği, paylaşılabilir ve sekmelere ayrılmış HTML araştırma raporu.
7. Yeni bilgi ve belgelerle güncellenebilir ortak veri tabanı.

### Teknik başlangıç ve açık noktalar

Çalışma kökü `/hpc/group/pfisterlab/mg551/storage/proje/` olarak onaylanmıştır. Boş klasörde yeni Git deposu başlatılmıştır; devralınmış uygulama, veri tabanı veya kod tabanı yoktur. GSD planlama dosyaları `.planning/` altında tutulacaktır.

Phase 1 görüşmesinde pilot Yeni Parti olarak seçilmiş, incelemenin partinin kuruluşundan başlaması kararlaştırılmıştır. Hukuki kimlik ve kuruluş tarihi kaynakla doğrulanacaktır. Veri kesim tarihi, ortak karşılaştırma dönemleri, belge kapsamları ve mali denetim yayın dönemlerinin karşılaştırmaya etkisi planlamada açıkça belirtilmelidir.

Ortak konu başlıklarında tarama sırasında bulunan bütün uygun ve yeterli kanıtlı eşleşmeler kaydedilir; bulunan belgelerin ilgili bağlantıları ve çelişkiler takip edilir. Takip edilecek ilgili kaynak kalmadığında konu taraması kapanır. Kurumsal kararlar ve parti adına hareket ettiği belgelenen yetkili temsilcilerin eylemleri esas alınır; bireysel oy ve açıklamalar aktörleriyle ayrı gösterilir.

Ana rapor sekmeleri partiler ve Karşılaştırmalı Özet olacaktır; her partinin altında ortak araştırma başlıkları bulunacaktır. Kaynaklar ilgili sekmenin altında listelenir ve metindeki ilgili ifadelerden rapordaki kaynak kaydına bağlantı verilir. Kaynak kaydı künye, ilgili pasaj, özgün bağlantı ve arşiv kopyasını bir araya getirir. Eksik bilgi durumu, gerekçe ve arama/erişim tarihi ilgili araştırma başlığında gösterilir. Ayrıntılı kararlar: [.planning/phases/01-kapsam-y-ntem-ve-kaynakl-pilot-rapor/01-CONTEXT.md](phases/01-kapsam-y-ntem-ve-kaynakl-pilot-rapor/01-CONTEXT.md).

Faz 1 yerel Python/SQLite yazıcısı, değişmez belge arşivi, kapalı release snapshotları ve bunlardan üretilen sekmeli Türkçe HTML ile tamamlandı. Aktif SQLite yerel scratch üzerinde çalışır; kayıt, JSON ve HTML tek atomik release işaretçisiyle birlikte tutulur. PDF denetimindeki mevcut yerel Poppler/Cairo gereksinimleri README içinde belgelenir. Katkı/güncelleme sürecinin genişletilmesi ve barındırma/yayın yeri sonraki çalışmalardır. Kamuya yayın yapılmadı. Pilotun tüzük/program otoritesi ve doğrulanmış mali tutarları bakımından süren kaynak eksikleri raporda korunur; kullanıcı kabulü bu eksikleri yeni olguya dönüştürmez.

## Constraints

- **Tarafsızlık:** Bütün partiler aynı başlıklar ve doğrulama ölçütleriyle incelenir; kapsam kararı araştırma sonucu gibi sunulmaz.
- **Kaynak zorunluluğu:** Her önemli bulgu izlenebilir kanıta dayanır; yapay zekâ modelinin bilgisi kaynak olarak kabul edilmez.
- **Metin sunumu:** Doğrudan aktarım siyah ve tırnak içinde, yapay zekâ özeti/düzenlemesi koyu mavidir; görünür metin türü etiketi kullanılmaz, metin kökeni kayıtlarda korunur.
- **Eksikleri görünür kılma:** “Bulunamadı”, “Erişilemedi” ve “Doğrulanamadı” durumları açıkça gösterilir.
- **İlk kapsam:** TBMM kayıtlarında temsil edilen partiler arasından CHP ve Cumhur İttifakı'nın mevcut/geçmiş ortakları çıkarılır; onaylanan dokuz partilik ön liste esas alınır ve değişiklikler belgelenir.
- **Dil ve teslim biçimi:** Araştırma Türkçe ve herkesin okuyabileceği şekilde sunulur; ana okuyucu çıktısı sekmeli HTML raporudur.
- **Geliştirilebilirlik:** Kaynaklar, belge sürümleri ve bulgu değişiklikleri izlenebilir olmalı; veri tabanı yeni bilgilerle güncellenebilmelidir.
- **Model ve maliyet tercihi:** Kullanıcının 2026-11-09 tarihli seçimiyle kayıtlı Sol ve Terra modelleri 6.1 sürümlerine geçirilmiştir. Belirtilmeyen orkestrasyon ve alt görevlerde GPT-6.1 Terra/high; ağır araştırma, planlama, sentez ve yöntem doğrulamasında yapılandırılmış GPT-6.1 Sol/xhigh rolleri esas alınır. Rol bazında önceden seçilmiş reasoning seviyeleri ve iki rutin Luna rolü korunur. Astra açık kullanıcı seçimi olmadan otomatik model veya yedek model olarak eklenmez.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Mevcut `proje/` klasöründe başlamak | Kullanıcının klasör seçimi | Faz 1 yerel pilotu uygulandı ve kullanıcı kabulü alındı |
| Başlangıç parti listesini TBMM kayıtlarına dayandırmak | Temsil durumunu doğrulanabilir birincil kaynaktan belirlemek | Faz 1 tarihli arşivi ve yeniden kontrolü tamamlandı |
| CHP'yi kapsam dışında tutmak | İlk proje tanımındaki açık sınır | Onaylandı |
| Cumhur İttifakı'nın mevcut ve geçmiş ortaklarını dışlamak | Kullanıcının kapsam daraltması ve geçmiş ortaklar için açık seçimi | Onaylandı; HÜDA PAR, DSP ve Yeniden Refah da dışarıda |
| Dokuz partilik başlangıç ön listesini esas almak | TBMM tablosuna dışlama kurallarının uygulanması | Onaylandı; grup/parti kimlik eşleştirmesi araştırmada doğrulanacak |
| Doğrudan aktarımı siyah, yapay zekâ özetini koyu mavi göstermek | Kullanıcının metin kökenini görünür kılma isteği | Faz 1 HTML ve veri modelinde uygulandı |
| Kaynaklı yapay zekâ özetine izin vermek; kaynaksız olgu üretimini dışlamak | Kullanıcının yapay zekâ ilkesini netleştirmesi | Onaylandı |
| Eksik bilgi için üç ayrı durumu korumak | Bilgi eksikliğini ve erişim/doğrulama sorunlarını gizlememek | Onaylandı |
| Ortak veri tabanından beslenen sekmeli HTML raporu hedeflemek | Paylaşılabilir ve güncellenebilir araştırma çıktısı | Faz 1 yerel Python/SQLite ve sürümlü HTML mimarisinde uygulandı |
| İncelemeyi partinin kuruluşundan başlatmak | Kullanıcının Phase 1 görüşmesindeki açık seçimi | Faz 1 arşivli sicil kaydı ve TBMM yakalamasına bağlı kesimle uygulandı |
| Yeni Parti ile pilotu başlatmak | Kullanıcının açık parti seçimi | Faz 1 pilotu tamamlandı; kaynak sınırlarıyla birlikte kullanıcı kabulü alındı |
| Ortak konularda bütün uygun eşleşmeleri almak ve ilgili belge zincirini takip etmek | Kullanıcının olay seçimi ve arama sonlandırma kararları | Onaylandı; ayrıntılar 01-CONTEXT.md içinde |
| Parti bazlı ana sekmeler ve Karşılaştırmalı Özet kullanmak | Kullanıcının rapor düzeni seçimi | Onaylandı; kaynaklar sekme altında ve metinden bağlantıyla erişilecek |
| Görünür metin türü etiketlerini kaldırıp siyah alıntıda tırnak kullanmak | Kullanıcının önceki etiket kararını açıkça güncellemesi | Onaylandı; koyu mavi özet ve veri kayıtlarındaki metin kökeni korunacak |
| Kayıtlı GSD Sol/Terra modellerini 6.1'e geçirmek | Kullanıcının açık model güncelleme isteği; mevcut rol ve maliyet dağılımını korumak | Uygulandı; Luna seçimi ve reasoning seviyeleri korundu, otomatik Astra eklenmedi |
| Gereksinimlerden önceki teknik ekosistem ön araştırmasını atlamak | Kullanıcı gereksinimlerin mevcut proje tanımından çıkarılmasını seçti | Onaylandı; esas kaynak araştırması ve aşama doğrulama ayarları korunuyor |
| Önce tek partide çalışan örnekle ilerlemek; bütün aşamaları mvp modunda kurmak | Kullanıcı kaynak → veri tabanı → sekmeli HTML akışının önce bir pilotta tamamlanmasını seçti | Onaylandı; 35 gereksinimi kapsayan altı aşamalı yol haritası kullanıcı tarafından onaylandı |

| Yerel scratch ve kapalı snapshot ile sürümlü yayın | NFS üzerinde aktif DB çalıştırmamak ve başarısız üretimde önceki raporu korumak | Faz 1 uygulandı; atomik pointer ve hata testleri mevcut |
| İlk doğrulanmış TBMM yakalamasını veri kesimi yapmak | Tekrarlanabilir dönem ve ayrı erişim/olay/belge tarihleri | 2026-11-10T14:38:46.154751+00:00; kullanıcı tarafından önceden seçilmiş tarih olarak sunulmaz |
| Yeni kanıtla çözülen eksikleri tarihçede korumak | Aday/eksik geçişini ve kanıt değişimini izlemek | Faz 1 aday ledger ve çözüm kayıtlarıyla uygulandı |
| Faz 1 UAT kabulünü toplu kullanıcı yanıtıyla kaydetmek | Kullanıcının açık onayıyla kapanış; yeni test veya kaynak olgusu üretmemek | 8/8 kabul, bildirilen sorun yok; ham 13 uç sınıflandırması ve kaynak eksikleri korunur |

## Evolution

Bu belge aşama geçişlerinde ve kilometre taşı sınırlarında güncellenir.

**Her aşama geçişinden sonra:**
1. Geçersiz kalan gereksinimleri gerekçeleriyle Out of Scope bölümüne taşı.
2. Teslim edilip doğrulanan gereksinimleri aşama referansıyla Validated bölümüne taşı.
3. Yeni gereksinimleri Active bölümüne ekle.
4. Alınan kararları Key Decisions tablosuna işle.
5. What This Is açıklaması mevcut durumu yansıtmıyorsa güncelle.

**Her kilometre taşından sonra:**
1. Bütün bölümleri gözden geçir.
2. Core Value önceliğinin hâlâ doğru olduğunu kontrol et.
3. Kapsam dışı kararların gerekçelerini ve kaynaklarını denetle.
4. Parti kapsamı, kaynaklar, kullanıcı geri bildirimi ve çıktılardaki güncel durumu Context bölümüne işle.

---
*Last updated: 2026-11-10 after Phase 1 UAT acceptance and completion*
