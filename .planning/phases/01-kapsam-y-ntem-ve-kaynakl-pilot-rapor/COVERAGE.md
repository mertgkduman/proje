# Faz 1 — Kaynak kapsamı ve varsayım denetimi

No external API integration: Bu faz Python stdlib ile kamusal kaynak belgelerini arşivleyip yerel SQLite snapshot'ından statik HTML üretir; harici API/SDK/servis bağlamaz.

Deterministik API detector, altı PLAN gövdesi ve Faz 1 ROADMAP bölümünde gerçek girdiyle çalıştırıldı: `detected=false`, `signals=[]` (çıkış 1 bu negatif sonucun sözleşmesidir). Assumption-delta taraması da `detected=false`, `signals=[]` verdi. ORM şema-push örüntülerinden hiçbiri seçilmedi; SQLite şeması gerçek scratch DB'ye uygulanır ve kapat/yeniden-aç/FK testleriyle doğrulanır. Paket kurulumu yoktur; bu nedenle package-legitimacy install kapısı uygulanmaz. Yeni paket seçilirse yürütme bu kapsama sessizce ekleyemez; araştırma/meşruiyet protokolü gerekir.

## Multi-Source Coverage Audit

Her satır kaynak sözleşmesini uygulayan görevi gösterir. COVERED planlandığı anlamındadır; uygulama veya doğrulama başarısı değildir.

| SOURCE | ID | Feature/Requirement | Plan/görev | Status | Notes |
|---|---|---|---|---|---|
| GOAL | G-01 | Kapsam/yöntem görünür, kaynaklı beş başlıklı pilot ortak kayıttan HTML ve arşive izlenir | 01-01–01-06 | COVERED | Gerçek tracer, içerik ve son kabul |
| REQ | KAPS-01 | Tarihli TBMM listesi/arşivi | 01-02-01 | COVERED | Dokuz onaylı ad korunur |
| REQ | KAPS-02 | CHP/ittifak ve açık dışlamalar | 01-02-01 | COVERED | Kapsam kararı siyasi bulgu yapılmaz |
| REQ | KAPS-03 | Hukuki parti/üye/grup ayrımı | 01-02-01 | COVERED | Registry ve kaynak ilişkileri ayrı |
| REQ | KAPS-04 | Kuruluştan dönem, olay/ortak yöntem | 01-02-02, 01-03-01, 01-04-02, 01-05-01 | COVERED | Dondurulmuş kesim, zincir, bütün uygun eşleşmeler |
| REQ | KAY-02 | Künye/tarih/sürüm/pasaj/erişim/doğrulama | 01-01-01, 01-04-01, 01-06-02 | COVERED | Bütün gerçek bulgulara genişler |
| REQ | KAY-03 | Özgün/arşiv geri izlenebilirliği | 01-01-01, 01-01-02, 01-06-01 | COVERED | Hash, güvenli türev ve ham dosya |
| REQ | MET-01 | Siyah tırnaklı değişmez alıntı | 01-01-01, 01-04-01, 01-06-01 | COVERED | Exact pasaj ve siyah CSS |
| REQ | MET-02 | Koyu mavi kaynaklı özet | 01-01-01, 01-04-01, 01-06-02 | COVERED | Pasaj incelemesi de gerekir |
| REQ | MET-03 | Tırnak yapısı, görünür tür etiketsiz, köken exportta | 01-01-01, 01-06-01 | COVERED | quote/summary ayrı alan |
| REQ | MET-04 | Olgu/beyan/yorum | 01-04-01, 01-05-01, 01-06-01 | COVERED | Epistemik tür görünür |
| REQ | EKS-01 | Üç ayrı durum | 01-03-02 | COVERED | Girişim türü/sonucuyla doğrulanır |
| REQ | EKS-02 | Parti/konu/tarih/gerekçe; eksik sıfır/sonuç olmaz | 01-03-02, 01-05-02, 01-06-01 | COVERED | Başlık içi ve ayrıntılı liste |
| REQ | VER-01 | Ortak parti/belge/bulgu/karşılaştırma ilişkileri | 01-01-01, 01-06-02 | COVERED | Gerçek DB ve çok kaynaklı karşılaştırma FK round-trip testi |
| RESEARCH | R-01 | Güncel Yeni Parti /sipar/365, kuruluşu tekrar doğrula | 01-01-01, 01-02-01 | COVERED | Araştırma gözlemi arşiv yerine geçmez |
| RESEARCH | R-02 | TBMM arşivi, onaylı liste/dışlamalar/kimlik farkları | 01-02-01 | COVERED | Sessiz kapsam değişikliği yok |
| RESEARCH | R-03 | Eski aynı adlı AYM belgesinin mali kimliğini ayır | 01-05-02 | COVERED | Güncel pilota eklenmez |
| RESEARCH | R-04 | Alan adı ve tüzük/program otoritesi henüz doğrulanmadı | 01-03-02, 01-04-01 | COVERED | Gerçek girişim ve kaynak zinciri |
| RESEARCH | R-05 | Stdlib/SQLite/statik HTML, yerel gösterim | 01-01-01, 01-06-02 | COVERED | Yeni framework/paket/hosting yok |
| RESEARCH | R-06 | NFS aktif DB sınırı, tek kanonik snapshot ve kurtarma | 01-01-02 | COVERED | Staging + son atomik pointer |
| RESEARCH | R-07 | Kimlik, belge/sürüm/pasaj, çoklu kanıt, provenance/epistemik tür | 01-01-01, 01-02-01, 01-04-01 | COVERED | Foreign keys ve parametreli SQL |
| RESEARCH | R-08 | Girişim/eksik ve incelenmedi ayrımı | 01-03-02 | COVERED | Üç gerçek durum |
| RESEARCH | R-09 | Ayrı tarihler ve reproducible cutoff | 01-02-02 | COVERED | İlk doğrulanmış TBMM capture UTC |
| RESEARCH | R-10 | Kaynaklı sürümlü ortak konu sözlüğü | 01-04-02 | COVERED | Öneriler belgesiz parti özelliği olmaz |
| RESEARCH | R-11 | URL/hash/döngü/yeni sürüm/ilgili uç/kapanma/reopen | 01-03-01 | COVERED | Blocked uçlar görünür |
| RESEARCH | R-12 | Bütün uygun eşleşmeler, aktör/oluş kanıtı ayrımı | 01-05-01 | COVERED | Olay kotası ve sessiz kesme yok |
| RESEARCH | R-13 | Mali NULL/0, dönem/currency/örgütsel kapsam | 01-05-02 | COVERED | Kuruluş sonrası gerçek dönemler |
| RESEARCH | R-14 | Özgün bayt/MIME/hash, PDF basılı/sıra sayfa ve HTML exact selector | 01-01-01, 01-04-01 | COVERED | Otomatik ve manuel pasaj doğrulama ayrılır |
| RESEARCH | R-15 | Metin içi/sekme altı kaynak, deep link/geri/fokus/klavye | 01-06-01 | COVERED | Gerçek tarayıcı probu |
| RESEARCH | R-16 | Escaping, güvenli URL/path, raw HTML etkinleştirmeme | 01-01-01, 01-01-02, 01-06-01 | COVERED | İlgili STRIDE kayıtları |
| RESEARCH | R-17 | Wave 0, sıfır-test reddi, scratch/test fixture ve release audit | 01-01-01, 01-01-02, 01-06-02 | COVERED | Testler yürütmede yaratılır |
| RESEARCH | R-18 | Browser keşfi, çevrimdışı/dar ekran ve gerçek kaynak incelemesi | 01-01-01, 01-06-01, 01-06-02 | COVERED | Test başarısı içerik yargısının yerine geçmez |
| CONTEXT | D-01 | Pilot Yeni Parti | 01-01-01, 01-02-01 | COVERED | Kullanıcı seçimi |
| CONTEXT | D-02 | Hukuki kimlik/kuruluş, benzer ad/üye/grup ayrımı | 01-01-01, 01-02-01, 01-05-02 | COVERED | Registry ve kanıt |
| CONTEXT | D-03 | Her partinin kuruluşundan başla | 01-02-02 | COVERED | Başka yıl varsayılmaz |
| CONTEXT | D-04 | Ayrı tarih/dönem/kapsam; açık kesim | 01-02-02, 01-05-02 | COVERED | Kesim planlayıcı kuralıdır |
| CONTEXT | D-05 | Dokuz parti/dışlama/TBMM/fark gerekçesi | 01-02-01 | COVERED | Onaylı liste değişmez |
| CONTEXT | D-06 | Tüzük/programdan ortak konular | 01-04-02 | COVERED | Pasaj ve taxonomy sürümü |
| CONTEXT | D-07 | Bütün uygun kanıtlı eşleşmeler | 01-05-01 | COVERED | Kimlik kümesi eşitliği |
| CONTEXT | D-08 | Kurum/yetkili/bireysel MP ayrımı | 01-05-01 | COVERED | Actor.kind ve yetki kaynağı |
| CONTEXT | D-09 | Beyan/olgu/yorum ve ayrı gerçekleşme kanıtı | 01-04-01, 01-05-01 | COVERED | Epistemik tür |
| CONTEXT | D-10 | İlgili belge/çelişki zinciri | 01-03-01 | COVERED | Açık iş kuyruğu |
| CONTEXT | D-11 | Birincil öncelik, girişim/link sonuç kaydı | 01-03-01 | COVERED | Sabit liste bitişi yeterli değil |
| CONTEXT | D-12 | Engelli uç, kapanma sınırı/reopen | 01-03-01 | COVERED | Kaynak tamlığı iddiası yok |
| CONTEXT | D-13 | Parti ana sekmeleri + özet | 01-06-01 | COVERED | İşlev ana sekmesi yok |
| CONTEXT | D-14 | Beş ortak başlık | 01-04-01, 01-05-02, 01-06-01 | COVERED | Gerçek pilotta tamamlanır |
| CONTEXT | D-15 | Gerçek pilot; diğerleri/karşılaştırma henüz hazırlanmadı | 01-06-01 | COVERED | İleriki faz kapsamı korunur |
| CONTEXT | D-16 | Kapsam/yönteme erişim | 01-02-01, 01-06-01 | COVERED | Üst bağlantı/bölüm |
| CONTEXT | D-17 | Metin içi ve sekme altı kaynak | 01-01-01, 01-06-01 | COVERED | Aynı kaynak kimliği |
| CONTEXT | D-18 | Link kaynak kaydını açar, pasaj/orijinal/arşiv/tarihler | 01-01-01, 01-06-01 | COVERED | Deep link dahil |
| CONTEXT | D-19 | Kısa özet ve alıntı birlikte | 01-01-01, 01-04-01, 01-06-01 | COVERED | Gizli alıntı değil |
| CONTEXT | D-20 | Siyah tırnak/koyu mavi, görünür tür etiketsiz | 01-01-01, 01-06-01 | COVERED | CSS ve yapı |
| CONTEXT | D-21 | Son karar üstün; köken kayıtta/exportta | 01-01-01, 01-06-01 | COVERED | Eski görünür etiket kararı uygulanmaz |
| CONTEXT | D-22 | Kaynak/epistemik/eksik açıklığı ve kaynak sınırı | 01-04-01, 01-06-01, 01-06-02 | COVERED | Kaynak yargısı ayrı |
| CONTEXT | D-23 | Eksik başlıkta gerekçe/tarihle | 01-03-02, 01-06-01 | COVERED | Ayrıca sekme altı liste |
| CONTEXT | D-24 | Girişim zorunlu, incelenmedi ayrı, eksik sıfır/sonuç değil | 01-03-02, 01-05-02, 01-06-02 | COVERED | Değer/yorum kontrolü |

Kapsam dışı sayılmayan sonraki-faz işleri: gerçek dokuz parti dosyaları, bütün parti karşılaştırmaları ve nihai güncelleme/paylaşma yetenekleri yalnız ilgili sonraki fazların gereksinimleridir; burada yapılmış gösterilmez. Yeni ertelenen Faz 1 kararı yoktur.

## Bağımlılık, sahiplik ve tahmin

| Plan | needs | creates | has_checkpoint | Wave |
|---|---|---|---|---|
| 01-01 | Planlama kaynakları, mevcut Python/tarayıcı | Gerçek tracer, writer/render, test runner ve release protokolü | false | 1 |
| 01-02 | 01-01 writer/kaynak yolu | Kapsam/kimlik ve dönem/kesim | false | 2 |
| 01-03 | 01-02 kimlik/kesim | Zincir, girişim ve eksik durumu | false | 3 |
| 01-04 | 01-03 arama/eksik motoru | Gerçek belge ve kaynaklı konu sözlüğü | false | 4 |
| 01-05 | 01-04 konu/pasajlar | Bütün uygun olay ve mali pilot | false | 5 |
| 01-06 | 01-05 tam pilot | Sekmeler/tarayıcı ve son kabul | false | 6 |

Her plan aynı `src/arsiv.py`/`src/rapor.py` ve kanonik release üzerinde yazıcıdır. Bu nedenle sahte paralellik kurulmadı; aynı dalgada dosya veya mutable DB kaynağı çakışması yoktur. Üretilen release/objects dosyaları writer'ın hesapladığı değişmez çıktılardır; elle düzenlenen yeni veri dosyaları yaratılmaz. İlk tracer beş yeni kaynak dosyasını kapsar; diğer her görev en çok beş kaynak dosyasını değiştirir. Her plan iki görevdir.

`estimate-calibration` sonucu factor=1, sample_count=0, confidence=low. Ham/kalibre tahminler sırayla 40000, 32000, 34000, 38000, 44000, 32000 token'dır. Bunlar yürütme maliyeti öngörüsüdür; gerçek kullanım ölçümü değildir.

## Spec-less Edge Coverage — flagged assumptions

SPEC ve Edge Coverage bölümü yok; varsayılan-ON fallback çalıştı. Deterministik rapor 13 satırın tamamını `category=unclassified`, `status=unresolved`, `verification=null`, `resolution=null`, `reason=null`, `probe="unclassified — review manually"` olarak verdi. Aşağıdaki satırların hiçbiri otomatik çözülmüş/dismissed/backstop sayılmaz. Sağdaki normal kabul kontrolleri gereksinimden ayrıca türetilmiştir; motorun sınıflandırılamayan uçlarını çözmüş oldukları iddia edilmez.

| Requirement | category | status | verification | Flag ve normal kabul dayanağı |
|---|---|---|---|---|
| KAPS-01 | unclassified | unresolved | null | flagged; test_scope: tarihli TBMM hash ve dokuz ad |
| KAPS-02 | unclassified | unresolved | null | flagged; test_scope: bütün dışlamalar ve karar kökeni |
| KAPS-03 | unclassified | unresolved | null | flagged; test_scope: parti/üye/grup FK ayrımı |
| KAPS-04 | unclassified | unresolved | null | flagged; test_dates/chain/topics/matches: dönem, kapsam, kapanma |
| KAY-02 | unclassified | unresolved | null | flagged; test_documents/acceptance: tüm kaynak/locator/tarih alanları |
| KAY-03 | unclassified | unresolved | null | flagged; test_tracer/publication: özgün bayt/hash/güvenli yerel arşiv |
| MET-01 | unclassified | unresolved | null | flagged; test_report/documents: siyah tırnaklı exact pasaj |
| MET-02 | unclassified | unresolved | null | flagged; test_report + pasaj incelemesi: koyu mavi, kaynak sınırı |
| MET-03 | unclassified | unresolved | null | flagged; test_report/acceptance: tırnak yapısı, köken exportta |
| MET-04 | unclassified | unresolved | null | flagged; test_matches/report: epistemik ayrım ve gerçekleşme kanıtı |
| EKS-01 | unclassified | unresolved | null | flagged; test_missing: üç ayrı girişim türü/sonucu |
| EKS-02 | unclassified | unresolved | null | flagged; test_missing/finance: parti/konu/tarih/gerekçe, NULL/0 |
| VER-01 | unclassified | unresolved | null | flagged; test_tracer/acceptance: gerçek close/reopen, kanıt FK ve karşılaştırma round-trip |

Koruma eşitliği: motor 13 applicable = 0 otomatik resolved + burada açıkça yüzeye çıkarılan 13 flagged assumption. `01-06-02` ve verify-work manuel incelemesinde her biri ele alınır. Bu belgenin yazımı manuel inceleme sayılmaz.

## Spec-less Prohibition Recall → Precision

Her gereksinim için 'özellik yazarın istemediği neye sessizce dönüşebilir?' sorusu uygulandı. Tekrarlar birleştirildi; rutin yanlış/boş girdi, dosya tanıtıcısı, kaçış, timeout, keşif ve kaynak linki bozulması gibi mühendislik sorunları edge/test/threat kayıtlarına ayrıldı. OWASP enjeksiyon/path traversal ve genel güvenlik kanonu `$gsd-secure-phase` + ilgili T-01/T-06 tehdit denetimlerine yönlendirildi; bespoke prohibition yapılmadı. Genel siyasi tarafsızlık kanonu yerine projeye özgü kapsam/olay seçimi/kanıt/eksik anlamı tutuldu.

| Girdi gereksinimleri | Tutulan özel niyet | Sonuç |
|---|---|---|
| KAPS-01, KAPS-02, KAPS-03 | Kapsam seçiminin siyasi başarısızlık/destek/sıralamaya dönüşmesi | P-01; KAPS-02 altında tekilleştirildi |
| KAPS-04 | Olumlu/olumsuz sonuca göre uygun eşleşme gizleme | P-02 |
| KAY-02, KAY-03, MET-01, MET-02, MET-03, MET-04 | Kaynaksız olgu/beyan ile gerçekleşmiş uygulamayı karıştırma | P-03; MET-02 altında tekilleştirildi; rutin renk/link/file sorunları testlere ayrıldı |
| EKS-01, EKS-02 | Eksik/araştırılmamışı sıfır veya siyasi sonuç yapma | P-04; EKS-02 altında tekilleştirildi |
| VER-01 | Bağımsız ek bespoke değer yasağı yok | Yukarıdaki kanıt/eksik niyeti korunur; FK/veri kaybı normal test konusudur |

Dört tutulan item `probe-core.cjs` içindeki tek `projectProhibitions` serializer'ı ile projekte edilmiştir. Çıktının statement/status alanları aynen `01-06-PLAN.md` içindeki `must_haves.prohibitions` sibling bloğundadır; hiçbiri truths'a taşınmadı. Dördü de `unresolved` ve descriptor-less'tır; check_kind/check_target/check_rule/check_violation_fixture/check_clean_fixture üretilmedi. Sonuç flagged-unverified'dır; normal kontrollerin geçmesi otomatik yeşil karar vermez. İnsan yargısı önerilir; bu aşamada sessiz dismissal yoktur.

## Gerçek kaynak/çevre belirsizlikleri

- Yargıtay kuruluş alanı ve TBMM gözlemi yürütmede özgün baytlarla tekrar doğrulanacaktır; burada yeni olgusal doğrulama yapılmadı.
- Parti alan adları, tüzük/program otoritesi ve erişilebilirliği henüz kesin değildir; 01-03/01-04 gerçek arama ve gerekçeli durumları üretir. D-06 kaynaklı konu sözlüğüne hiçbir yetkili tüzük/program dayanağı bulunamazsa 01-04-02 açık engel verir; kaynak uydurup tamamlanma iddiası üretmez.
- Tarayıcı yolu yürütmede yeniden keşfedilir; yokluğu test atlanarak gizlenmez. Paket kurulumu veya kullanıcıya özgü cache yolu zorunlu tutulmaz.
- Otomatik testler ve gerçek veri incelemeleri henüz çalışmadı. `01-VALIDATION.md` draft/false durumları korunur.
