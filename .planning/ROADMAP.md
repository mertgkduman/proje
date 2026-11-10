# Roadmap: Türkiye Siyasi Partileri Araştırması

## Overview

Önce kapsam ve yöntem görünür hâle getirilir ve kapsam içinden seçilen bir partiyle gerçek kaynak → ortak veri kaydı → sekmeli HTML akışı tamamlanır. Ardından aynı yöntem bütün partilere genişletilir; tüzük/program, söylem–uygulama ve finansman araştırmaları rapora çalışan dilimler olarak eklenir. Son aşamada güncelleme geçmişi ve yeniden üretilebilir, paylaşılabilir rapor tamamlanır. Her aşama mevcut araştırma çıktısına okurun kullanabileceği bir yetenek ekler.

**Status:** Kullanıcı tarafından onaylandı — 2026-11-09.
**Milestone:** v1.0 — Kaynak temelli ilk araştırma arşivi ve rapor.
**Structure:** Kullanıcının seçimiyle bütün aşamalar `mvp` modundadır. Gereksinimlerin onayı tamamlanmıştır; uygulama başlamamıştır.
**Coverage:** 35/35 v1 gereksinimi tam olarak birer aşamaya atanmıştır. Eşleme, gereksinimlerin tamamlandığı anlamına gelmez.

## Phases

**Phase Numbering:** Tam sayı aşamalar ana çalışmayı, gerektiğinde eklenecek ondalık aşamalar ara işleri gösterir. Sıralama 1 → 2 → 3 → 4 → 5 → 6'dır.

- [ ] **Phase 1: Kapsam, yöntem ve kaynaklı pilot rapor** - Okur, kapsamı ve araştırma yöntemini görebilir; seçilen bir partinin beş başlıklı pilot dosyasını ortak kayıttan HTML raporuna ve arşiv belgelerine kadar izleyebilir.
- [ ] **Phase 2: Bütün partiler için dosyalar ve sürümlü kaynaklar** - Okur, onaylanan kapsamdaki bütün partilerin ortak beş başlıklı dosyalarını ve dayandıkları kaynak sürümlerini aynı rapordan inceleyebilir.
- [ ] **Phase 3: Tüzük ve programların karşılaştırılması** - Okur, üyelik haklarını, parti yönetimini ve program ilkelerini bütün partiler için aynı konular üzerinden kaynaklarına ulaşarak karşılaştırabilir.
- [ ] **Phase 4: Söylem ve belgelenmiş uygulamaların karşılaştırılması** - Okur, ilan edilen ilke ve vaatlerin belgelenmiş uygulamalarla ilişkisini ortak yöntem ve olay bağlamı içinde değerlendirebilir.
- [ ] **Phase 5: Finansman ve harcamaların belgelenmesi** - Okur, partilerin erişilebilen gelir ve harcama bilgilerini dönem ve kapsam farklarını anlayarak inceleyebilir.
- [ ] **Phase 6: Güncellenebilir veri tabanı ve paylaşılabilir rapor** - Araştırmacı kaynak ve bulguları geçmişi korunarak güncelleyebilir; okur aynı kayıtlardan üretilen tam, erişilebilir ve paylaşılabilir HTML araştırma raporunu kullanabilir.

## Phase Details

### Phase 1: Kapsam, yöntem ve kaynaklı pilot rapor

**Goal:** Okur, kapsamı ve araştırma yöntemini görebilir; seçilen bir partinin beş başlıklı pilot dosyasını ortak kayıttan HTML raporuna ve arşiv belgelerine kadar izleyebilir.
**Mode:** mvp
**Depends on:** Nothing (first phase)
**Requirements:** KAPS-01, KAPS-02, KAPS-03, KAPS-04, KAY-02, KAY-03, MET-01, MET-02, MET-03, MET-04, EKS-01, EKS-02, VER-01
**Success Criteria**:

1. Okur, tarihli TBMM kaynak kopyasından başlangıç listesini, dahil etme/dışlama gerekçelerini ve parti üyeliği ile ortak Meclis grubu ayrımını görebilir.
2. Okur, incelenecek dönemleri, olay seçimi ve arama sonlandırma ölçütlerini ve kapsam içinden pilot partinin seçilme gerekçesini yöntem bölümünde okuyabilir; henüz onaylanmamış bir başlangıç yılı varsayılmaz.
3. Okur, bir pilot partinin kuruluş, tüzük, program, söylem–uygulama ve finansman–harcamalar başlıklarını gerçek kaynaklı bulgular veya denenmiş aramalara dayanan eksik bilgi durumlarıyla HTML raporunda görebilir; ortak veri kaydından bağlantı, belge tarihi/sürümü, madde/sayfa veya pasaj, erişim/doğrulama tarihleri ve arşiv kopyasına ulaşabilir.
4. Okur, aynı pilot içerikte doğrudan aktarımı siyah ve tırnak içinde, kaynaklı yapay zekâ özetini koyu mavi görebilir; görünür metin türü etiketi kullanılmaz, metin kökeni veri kayıtlarında korunur. Olgu, kaynağın beyanı ve yorum birbirinden ayrılır.
5. Araştırmacı üç eksik bilgi durumunu ayrı kaydedebilir; okur eksik listesinde parti/konu, arama veya erişim tarihi ve gerekçeyi görebilir. Yalnız denenmiş aramalar bu durumlara dönüştürülür; eksikler sıfır veya olumsuz bulgu sayılmaz.

**Plans:** 3/6 plans executed

Plans:
**Wave 1**

- [x] 01-01-PLAN.md — Gerçek kaynak → kapalı SQLite → HTML/kaynak tıklama tracer'ı ve güvenli release/kurtarma

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02-PLAN.md — Dokuz parti kapsamı, ayrı kimlikler ve tekrarlanabilir veri kesimi

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 01-03-PLAN.md — Kaynak zinciri, kapanma/yeniden açılma ve girişime bağlı eksikler

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 01-04-PLAN.md — Pilot tüzük/program belgeleri ve kaynaklı ortak konu sözlüğü

**Wave 5** *(blocked on Wave 4 completion)*

- [ ] 01-05-PLAN.md — Bütün uygun söylem–uygulama eşleşmeleri ve mali pilot

**Wave 6** *(blocked on Wave 5 completion)*

- [ ] 01-06-PLAN.md — Parti sekmeleri, kaynak etkileşimi ve gerçek release kabulü

**UI hint**: yes

### Phase 2: Bütün partiler için dosyalar ve sürümlü kaynaklar

**Goal:** Okur, onaylanan kapsamdaki bütün partilerin ortak beş başlıklı dosyalarını ve dayandıkları kaynak sürümlerini aynı rapordan inceleyebilir.
**Mode:** mvp
**Depends on:** Phase 1
**Requirements:** DOS-01, DOS-02, KAY-01, KAY-04
**Success Criteria**:

1. Okur, onaylanan kapsamdaki her parti için kuruluş, tüzük, program, söylem–uygulama ve finansman–harcamalar başlıklarını aynı şablonda açabilir; başlangıç ön listesi dokuz partidir ve değişiklikler gerekçeyle izlenir.
2. Okur, her partinin resmî adını, kuruluş tarihini ve temel kimlik bilgilerini destekleyen kaynakları veya gerekçeli eksik bilgi durumunu görebilir.
3. Okur, kaynakların birincil belge, gazetecilik, akademik çalışma veya bağımsız rapor türünü görebilir; birincil kaynak önceliği ve ikincil kaynak kullanımı aynı yöntemle açıklanır.
4. Okur, bulgunun hangi belge sürümüne ve döneme dayandığını ve mevcut eski sürümleri görebilir; henüz araştırılmamış bir başlık, denenmiş bir aramanın “Bulunamadı” sonucu gibi gösterilmez.

**Plans:** TBD
**UI hint**: yes

### Phase 3: Tüzük ve programların karşılaştırılması

**Goal:** Okur, üyelik haklarını, parti yönetimini ve program ilkelerini bütün partiler için aynı konular üzerinden kaynaklarına ulaşarak karşılaştırabilir.
**Mode:** mvp
**Depends on:** Phase 2
**Requirements:** TUZ-01, TUZ-02, TUZ-03, TUZ-04, PRG-01, KAR-01, KAR-02, RAP-02
**Success Criteria**:

1. Okur, her partinin üyelik hakları, yönetim seçimi, yönetim denetimi ve farklı görüşlerin ifade mekanizmalarını ilgili tüzük maddeleriyle veya belgelenmiş eksik bilgi durumlarıyla inceleyebilir.
2. Okur, her partinin ilkelerini, hedeflerini ve politika yaklaşımlarını programın ilgili bölümlerine dayanarak veya belgelenmiş eksik bilgi durumlarıyla inceleyebilir.
3. Okur, tüzük ve program tablolarında aynı konu başlıklarını bütün partiler için görebilir; her hücrede dayanak veya eksik bilgi durumu bulunur.
4. Okur, dosyalardaki bulgulardan ve karşılaştırma hücrelerinden doğru kaynak kaydına ve erişilebilen arşiv belgesine ulaşabilir; madde/sayfa veya pasaj bağlantısı korunur.

**Plans:** TBD
**UI hint**: yes

### Phase 4: Söylem ve belgelenmiş uygulamaların karşılaştırılması

**Goal:** Okur, ilan edilen ilke ve vaatlerin belgelenmiş uygulamalarla ilişkisini ortak yöntem ve olay bağlamı içinde değerlendirebilir.
**Mode:** mvp
**Depends on:** Phase 3
**Requirements:** UYG-01, UYG-02, KAR-03
**Success Criteria**:

1. Okur, yöntem aşamasında belirlenen konu ve olay seçimi ölçütleriyle her parti için hazırlanan ilke/vaat–uygulama eşleştirmelerini veya yeterli kanıt bulunamadığı durumları inceleyebilir.
2. Okur, her eşleştirmenin aktörünü, açıklama ve olay tarihlerini, geçerli belge sürümünü ve bağlamını görebilir; parti açıklaması tek başına uygulamanın gerçekleştiğine kanıt sayılmaz.
3. Okur, aynı ölçütlerle hazırlanmış karşılaştırmalarda belgelerin desteklediği benzerlik/farklılıkları, kaynağın beyanını ve araştırmacı/yapay zekâ yorumunu ayrı görebilir; kanıt eksikliği uyum veya çelişki sonucu gibi sunulmaz.

**Plans:** TBD
**UI hint**: yes

### Phase 5: Finansman ve harcamaların belgelenmesi

**Goal:** Okur, partilerin erişilebilen gelir ve harcama bilgilerini dönem ve kapsam farklarını anlayarak inceleyebilir.
**Mode:** mvp
**Depends on:** Phase 4
**Requirements:** MAL-01, MAL-02, MAL-03
**Success Criteria**:

1. Okur, her parti için erişilebilen belgelerdeki gelir kaynaklarını ve açıklanan gelir tutarlarını belge dayanağıyla; açıklanmayan veya bulunamayan alanları gerekçeli eksik bilgi durumlarıyla görebilir.
2. Okur, her parti için erişilebilen harcama kalemlerini ve açıklanan harcama tutarlarını belge dayanağıyla veya gerekçeli eksik bilgi durumlarıyla görebilir.
3. Okur, her mali kaydın hesap dönemini, para birimini ve örgütsel kapsamını görebilir; farklı yıllar/kapsamlar eşdeğer sayılmaz, açıklanmayan tutarlar sıfır gibi gösterilmez.

**Plans:** TBD
**UI hint**: yes

### Phase 6: Güncellenebilir veri tabanı ve paylaşılabilir rapor

**Goal:** Araştırmacı kaynak ve bulguları geçmişi korunarak güncelleyebilir; okur aynı kayıtlardan üretilen tam, erişilebilir ve paylaşılabilir HTML araştırma raporunu kullanabilir.
**Mode:** mvp
**Depends on:** Phase 5
**Requirements:** RAP-01, RAP-03, VER-02, VER-03
**Success Criteria**:

1. Okur, kapsamdaki bütün parti dosyalarını, karşılaştırmaları, kaynak/belge arşivini ve eksik bilgi listesini sekmeli Türkçe HTML raporunda açabilir; rapor alıcının proje geliştirme ortamını kurmasını gerektirmeyen biçimde paylaşılabilir.
2. Okur, rapordaki sekmeleri klavyeyle kullanabilir ve dar ekranda parti dosyaları, kaynaklar ve karşılaştırmaları içerik kaybı olmadan okuyabilir; siyah/koyu mavi ayrımı, tırnaklı alıntı yapısı ve metin kökeni bilgisi korunur.
3. Araştırmacı yeni belge, sürüm ve bulgu ekleyebilir veya bir kaydı düzeltebilir; değişiklik tarihi, gerekçesi ve önceki kayda bağlantı görülebilir.
4. Araştırmacı güncellenen ortak kayıtlardan parti dosyalarını, karşılaştırmaları ve HTML raporunu yeniden üretebilir; kaynak, sürüm, metin kökeni ve eksik bilgi kayıtları çıktılar arasında tutarlı kalır.

**Plans:** TBD
**UI hint**: yes

## Delivery Rules

- Her gereksinimin bir sorumlu aşaması vardır. Kaynak zorunluluğu, ortak ölçütler, metin kökeni ve eksik bilgi kuralları sonraki bütün veri/rapor eklemelerinde de korunur; bir gereksinimin daha önce uygulanmış olması yeni içeriğin kontrolünü kaldırmaz.
- Pilot parti kapsam içinden, önceden açıklanan yöntemle seçilir; bu tercih bir siyasi sıralama veya destek anlamına gelmez. Dokuz partilik ön liste TBMM kaydıyla tekrar kontrol edilir; parti/grup uyuşmazlıkları sessizce kapsam değişikliğine çevrilmez.
- İnceleme başlangıç yılı, karşılaştırma dönemleri ve olay örnekleme/arama sonlandırma kuralları Phase 1 planlanırken netleştirilir. Henüz bir yıl veya olay sayısı varsayılmamıştır.
- Sonraki aşamalarda araştırılacak başlıklar, denenmiş aramalar sonucunda saptanan eksik bilgi durumlarından ayrı izlenir. Boş bir alan otomatik olarak “Bulunamadı” sayılmaz.
- Veri tabanı teknolojisi ve raporun teknik yapısı Phase 1 planlamasında seçilecektir; bu yol haritası belirli bir teknoloji yığını veya barındırma hizmetini zorunlu kılmaz.
- Paylaşılabilir HTML çıktısı hazırlanır; kamuya barındırma/yayın yeri ayrıca kararlaştırılır. Bu aşamalar kendiliğinden dış bir servise yayın yapma işlemi başlatmaz.
- Ayrıntılı PLAN.md dosyaları ilgili aşama planlanırken oluşturulur. `TBD`, plan sayısının henüz belirlenmediğini gösterir.

## Progress

**Execution Order:** 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Kapsam, yöntem ve kaynaklı pilot rapor | 3/6 | In Progress|  |
| 2. Bütün partiler için dosyalar ve sürümlü kaynaklar | 0/TBD | Not started | - |
| 3. Tüzük ve programların karşılaştırılması | 0/TBD | Not started | - |
| 4. Söylem ve belgelenmiş uygulamaların karşılaştırılması | 0/TBD | Not started | - |
| 5. Finansman ve harcamaların belgelenmesi | 0/TBD | Not started | - |
| 6. Güncellenebilir veri tabanı ve paylaşılabilir rapor | 0/TBD | Not started | - |

---
*Last updated: 2026-11-09 after explicit user approval of the six-phase MVP roadmap*
