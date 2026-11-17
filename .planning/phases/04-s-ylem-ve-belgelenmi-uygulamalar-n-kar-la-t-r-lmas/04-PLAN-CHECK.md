## ISSUES FOUND

**Faz:** 04 — Söylem ve belgelenmiş uygulamaların karşılaştırılması  
**Kontrol:** Yürütüm öncesi, salt okunur plan denetimi  
**Planlar:** 15 plan, 30 görev, 7 dalga  
**Sonuç:** 3 BLOCKER, 0 WARNING, 0 INFO

Hedef: Okur, ilan edilen ilke ve vaatlerin belgelenmiş uygulamalarla ilişkisini ortak yöntem ve olay bağlamı içinde değerlendirebilir.

### Bulgular

**1. BLOCKER — Kaynaklı ortak olay kararları, tekrar üretilebilir birleştirme yolunun girdisi olmalı.**

04-03-02, `practice-merge` komutunun ortak olay çakışmalarında açık kaynak/örtüşme kararı istemesini öngörüyor. Ortak yürütüm sözleşmesi:25 komuta yalnız `--inventory`, `--inputs`, `--out` tanımlıyor. 04-13:61 ve görev 04-13-01:69 kararları `04-shared-events.json` içine yazdırıyor; fakat bu dosyanın komut, paket veya doğrulayıcı tarafından okunacağı bir bağlantı yok. Aynı görevin doğrulaması (:71), yalnız dokuz özgün parti paketini girdi vererek `04-merged.json` dosyasını yeniden üretiyor. Böylece karar kayıtlarının kanonik olay kimliklerine ve onlara bağlı bütün ilişki/katkı/kanıt kayıtlarına uygulanması ve yeniden üretimde korunması planlanmış değil. Ortak anahtarın aday olduğu, nihai kimlik olmadığı sözleşmede özellikle belirtiliyor.

Bağlayıcı olmayan bir çözüm örneği: Karar kaydını belgeli bir birleştirme girdisine bağlamak; aynı girdiler ve kararlarla yeniden üretimin aynı kanonik olayları ve bütün başvuruları koruduğunu, kararsız çakışmanın reddedildiğini doğrulamak. Yeni bir CLI argümanı tek olası çözüm değildir.

**2. BLOCKER — Olay bulunmayan geçerli bir konuda eksik sentezi, gerçek arama ve kapanış kanıtıyla temsil edilebilmeli.**

04-14:55 eksik sentezinde gerçek `attempt/closure` kanıtı kullanılmasını istiyor; görev 04-14-01:65 kaynaklı karşılaştırılabilir çift bulunmazsa eksik sentezini kullanıyor ve 04-14-02:77 her konuya bu tür bir açıklama gerektiriyor. Buna karşılık kanonik sözleşme:36, `practice_synthesis_evidence` için yalnız `synthesis_id`, `relation_id veya unmatched_id`, `passage_id` tanımlıyor. Aynı sözleşmede hem relation hem unmatched bir `event_id` gerektiriyor. Gerçek araştırmanın hiçbir olay saptayamadığı bir konuda geçerli arama/kapanış kayıtları bulunabilir; relation/unmatched veya olay pasajı bulunması gerekmez. Bu durumu sahte olay/pasaj üretmeden yükleme→export→audit→render yolundan geçirecek kanıt çeşidi ve başvurular tanımlanmamış.

Bağlayıcı olmayan bir çözüm örneği: Sentez dayanağının olay/ilişki kanıtı ile kapsam/arama/kapanış kanıtını ayırabilmesi ve aynı doğrulayıcıda uygun başvuruları denetlemesi. Hiç olay bulunmayan fakat gerçek girişimlerle kapanmış konu için tam yol kabul testi ve dayanağı olmayan eksik çıkarımına ret testi bu özelliği kanıtlayabilir.

**3. BLOCKER — Araştırmadaki planlama soruları açık çözüm veya yürütüm disposition kaydı taşımalı.**

04-RESEARCH.md:335 başlığı hâlâ `## Open Questions`; :337–341 içindeki beş maddenin hiçbirinde `RESOLVED` veya açık çözüm kaydı yok. Checker dimension 11, bu durumda geçişi başarısız saymayı zorunlu kılıyor. Planlar bunların çoğunu fiilen ele alıyor: kaynak hacmi için kuyruk/12k okuma dilimleri ve devam koşulu, ortak kaynak sahipliği için `practice_source_party`, pilot örtüşmesi için 04-04/04-13, tarih belirsizliği için 04-02 ve gerçek browser için 04-15. Ancak araştırma belgesi bu karşılıkları kaydetmediği için hangi tasarım sorusunun kapandığı ve hangi ampirik sonucun yürütümde öğrenileceği açıkça ayrılmıyor.

Bu bulgu, bilinmeyen olay hacmini veya kaynak erişimini biliniyor gibi yazma talebi değildir. Bağlayıcı olmayan çözüm örneği: Her maddeye alınmış teknik kararı veya yürütümdeki sorumlu görev, üretilecek kanıt, devam ve kapanış koşulunu bağlayan açık disposition eklemek; gerçek ampirik sonuçları araştırma öncesinde çözülmüş diye göstermemek. Sözleşmede henüz tamamlanmamış merge ve eksik-sentez bağlantıları önce giderilmeli.

### Gereksinim ve karar kapsamı

| Gereksinim | Somut karşılık | Sonuç |
|---|---|---|
| UYG-01 | 04-01–03 veri/iki görünüm; 04-04–12 gerçek dokuz parti araştırması; 04-13 birleşim; 04-14 sentez | Görev kapsamı var; birleşim ve olaysız konu dayanağı düzeltilmeli |
| UYG-02 | 04-01–02 ayrı oluş kanıtı, aşama, tarih, aktör/yetki, ihtilaf; bütün parti görevlerinde gerçek kaynak okuması; 04-15 son inceleme | Kapsanıyor; ortak olay kimliğinin korunumu 1. bulguya bağlı |
| KAR-03 | 04-03 kanonik envanter; 04-04–12 aynı ölçüt; 04-13 bütün-parti geri tarama; 04-14 farklı dönemli kaynaklı sentez | Görev kapsamı var; 1 ve 2. bulgular giderilmeli |

Bütün planların `requirements` alanında üç kimlik de var. PROJECT.md'nin bu faza ilişkin kaynak, tarafsızlık, bütün uygun eşleşmeler, kuruluş başlangıcı, metin kökeni ve gerçek eksik ayrımı görevlerde karşılık buluyor; mali araştırma ve kamuya yayın faza eklenmiyor.

D-01–D-16 yalnız ad olarak değil görev eylemleri üzerinden kontrol edildi. D-08 kaynak zincirinde bulunan yanıtlarla sınırlı kalıyor; yeni zorunlu hedefli yanıt araması eklenmiyor. D-10 hedef/sonuç ilk sırada. D-13 görünür ilişki enum başlığı yok. D-15 bütün uygun olaylar kronolojik açık akışta; sayfalama, olay kotası veya sonuç lehine/aleyhine örnek eleme yok. D-16 farklı dönem kıyasını dönem/yetki/kapsam sınırlarıyla koruyor. Bu içerik kararlarında sessiz kapsam azaltımı saptanmadı; eksik kalan iki bağlantı yukarıda ayrı bulgu olarak gösterildi.

### Yapı, bağımlılık ve bütçe

| Plan | Görev | Dosya/dizin hedefi | Dalga | Tahmin token | Bütçe | Güven |
|---|---:|---:|---:|---:|---:|---|
| 04-01 | 2 | 7 | 1 | 48.000 | 100.000 | low |
| 04-02 | 2 | 5 | 2 | 44.000 | 100.000 | low |
| 04-03 | 2 | 6 | 3 | 45.000 | 100.000 | low |
| 04-04 | 2 | 4 | 4 | 42.000 | 100.000 | low |
| 04-05 | 2 | 4 | 4 | 42.000 | 100.000 | low |
| 04-06 | 2 | 4 | 4 | 42.000 | 100.000 | low |
| 04-07 | 2 | 4 | 4 | 42.000 | 100.000 | low |
| 04-08 | 2 | 4 | 4 | 42.000 | 100.000 | low |
| 04-09 | 2 | 4 | 4 | 42.000 | 100.000 | low |
| 04-10 | 2 | 4 | 4 | 42.000 | 100.000 | low |
| 04-11 | 2 | 4 | 4 | 42.000 | 100.000 | low |
| 04-12 | 2 | 4 | 4 | 42.000 | 100.000 | low |
| 04-13 | 2 | 4 | 5 | 44.000 | 100.000 | low |
| 04-14 | 2 | 6 | 6 | 42.000 | 100.000 | low |
| 04-15 | 2 | 8 | 7 | 44.000 | 100.000 | low |

`estimate-check --calibrated` ile dört farklı tahmin değeri kontrol edildi: tümü `over_budget=false`, recommendation=null, sample_count=0. Bunlar henüz proje gerçekleşenleriyle kalibre edilmiş hassas ölçümler değil; ortak sözleşme tahminlerin bütün tarihsel kaynak hacmini değil bir olağan çalışma bağlamını temsil ettiğini açıkça söylüyor. 12k kaynak okuma dilimleri siyasi olay/kaynak kotası olarak yorumlanmadı; kuyruk bitmeden complete yasağı ve devam konumu kaydı korunuyor.

Bağımlılık grafiği çevrimsiz; bütün başvurular var ve dalgalar bağımlılıkların en büyüğünden bir fazla. Aynı dalgadaki 04-04–12 paket/review/tranches/capture/preview kökleri ayrı; global current, release, lock, ortak SQLite ve envanter salt okunur. Aynı dalga dosya çakışması veya ayrıca bildirilecek somut paylaşılan yazılabilir kaynak bağlantısı saptanmadı. 04-13 kanonik aktarımı seri tek yazıcıyla yapıyor.

### Diğer boyutlar ve kullanılan kanıt

- Sağlanan `04-PLAN-STRUCTURE-CHECKS.json` okundu: 15/15 geçerli, her planda 2 görev; bütün files/action/verify/done alanları var. Tracer görev türü yürütüm akışında destekleniyor.
- Şema6/renderer24 byte uyumu; şema7/renderer25 dispatch, manifest/downgrade engeli; Faz2 prefix ve Faz3 complete/taxonomy4/selection korunumları görev ve olumsuz testlere bağlanmış.
- Mimari sorumluluk haritası korunuyor: anlam kararları araştırma/CLI, veri kuralları Python/SQLite, değişmez snapshot yayıncı, içerik HTML üretici, hash/odak tarayıcı katmanında.
- AGENTS.md okundu; bu kontrol aktif `$gsd-plan-phase 4` akışında. Model/yayın/kaynak politikasıyla çelişki yok. `.codex/skills` ve `.agents/skills` yok; `agent_skills` boş. PATTERNS.md ve plan bağlamındaki analog/yardımcılar değerlendirildi.
- Dimension 8: SKIPPED (`nyquist_validation=false`); VALIDATION.md eksikliği bulgu değildir. Normal anlamlı otomatik kontroller ve gerçek kaynak incelemesi sürüyor.
- `04-VERIFY-PATHS.json` tam dosyası okundu: status=not_applicable, 68/68 not_applicable, blocker=0, warning=0, readError=null. Bu sonuç Python hedeflerinin dosya sistemi çözümlemesi yapıldığı anlamına gelmez; yeniden türetilmedi.
- `04-VERIFY-FAILURE-DIRECTIONS.json` tam dosyası okundu: status=ok, 68/68 ok, blocker=0, warning=0, readError=null. Yeni başarısızlık cümlesi üretilmedi. Sayısal grep/başarılı varsayılanla hata yutma gibi format sorunları saptanmadı.
- UI gate block=false girdisi korundu; UI-SPEC, API coverage, SPEC, REVIEWS veya AI-SPEC için yeni engel türetilmedi.
- ASVS 5 L1/high etkinliği ve her planın proportionate threat_model içeriği mevcut. Geri dönüş dereceleri iç sürümlü adapter/immutable release gerekçesine dayanıyor; kanıtsız geri döndürülemez checkpoint istenmedi.
- Üç ham unclassified/unresolved edge ve üç descriptor-less prohibition, açık flagged olarak son kabul kaydına devrediliyor. Bunlar teknik test başarısıyla çözülmüş sayılmıyor; yeni per-source insan kabulü kapısı yok.
- Uygulama başlatılmadı, implementation testleri çalıştırılmadı, gerçek parti araştırması yeniden yapılmadı. Bu rapor dışında plan veya uygulama dosyası değiştirilmedi.

### Structured Issues

```yaml
issues:
  - plan: "04-13"
    dimension: key_links_planned
    severity: blocker
    task: 1
    required_property: "Kaynaklı ortak olay özdeşlik/ayrılık kararları kanonik birleştirme yolunda tüketilmeli ve yeniden üretimde bütün olay/ilişki/katkı/kanıt başvurularıyla korunmalı."
    description: "04-03-02 karar isteyen merge üretir; EXECUTION-CONTRACT:25 komuta yalnız --inventory/--inputs/--out verir. 04-13:61,69 kararları 04-shared-events.json'a yazar, fakat bu artefaktı merge girdisine veya paket sözleşmesine bağlayan görev yoktur. 04-13:71 doğrulaması yalnız dokuz özgün paketle 04-merged.json'ı yeniden üretir; yazılan kararların uygulanması ve korunması tanımlanmamıştır."
    fix_hint: "Örneğin karar kaydını belgeli bir merge girdisine bağlayıp aynı kararlarla yeniden üretimde kanonik kimlikleri ve bütün başvuruları koruyan kabul/ret doğrulaması tanımlamak."
  - plan: "04-14"
    dimension: cross_plan_data_contracts
    severity: blocker
    task: 1
    required_property: "Hiç belgelenmiş olay bulunmayan geçerli kapalı konuda eksik sentezi, sahte olay/pasaj gerektirmeden gerçek scope/attempt/closure dayanağıyla aynı load/export/audit/render yolunda temsil edilebilmeli."
    description: "04-14:55 eksik sentezinde attempt/closure kanıtı, :65 olaylı çift bulunmazsa eksik sentezi, :77 her konu için dayanaklı açıklama ister. Kanonik EXECUTION-CONTRACT:36 practice_synthesis_evidence için yalnız relation_id veya unmatched_id ile passage_id tanımlar; ikisi de event_id gerektirir. Gerçek aramayla kapanmış olaysız konuda bu kimlikler yoktur ve arama/kapanış kanıtı için tanımlı başvuru çeşidi bulunmaz."
    fix_hint: "Örneğin olay/ilişki dayanağı ile gerçek kapsam/arama/kapanış dayanağını ayırt eden bir kanıt sözleşmesi ve olaysız konu için tam yol kabul testi tanımlamak."
  - plan: null
    dimension: research_resolution
    severity: blocker
    required_property: "Araştırmanın planlama soruları açık çözüm veya görev/sorumlu/kanıt/devam-kapanış koşuluna bağlı dürüst yürütüm disposition kaydı taşımalı."
    description: "04-RESEARCH.md:335 hâlâ Open Questions başlığını taşır; :337–341'deki beş maddede RESOLVED veya açık çözüm kaydı yoktur. Plan/sözleşme çoğuna teknik karşılık verse de araştırma kaydı kapanmış tasarım kararlarını yürütümde öğrenilecek ampirik sonuçlardan ayırmamıştır; checker dimension11 bu durumda geçişi başarısız sayar."
    fix_hint: "Örneğin alınmış kararları ve yürütümde öğrenilecek konuların sahip görev/kanıt/kapanış koşullarını araştırma maddelerine bağlamak; bilinmeyen kaynak hacmi veya erişimi biliniyor gibi göstermemek."
```

### Öneri

Üç bağlayıcı özellik giderildikten sonra yeniden plan kontrolü yapılmalı. Kaynak kapsamını veya D-01–D-16 kararlarını daraltmak gerekmez; düzeltmeler veri bağlantıları ve açık araştırma disposition kayıtları üzerindedir.
