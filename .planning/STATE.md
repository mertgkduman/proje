---
gsd_state_version: "1.0"
milestone: v1.0
current_phase: 03
current_phase_name: Tüzük ve programların karşılaştırılması
current_plan: 12
status: executing
stopped_at: Completed 03-11-PLAN.md
last_updated: "2026-11-14T10:26:17.648Z"
last_activity: 2026-11-14
last_activity_desc: 03-11 Saadet program karşılaştırması tamamlandı
state_head: 3accd1d52c6137e4bbb89b90a97e8b5358b07c4f
progress:
  total_phases: 6
  completed_phases: 2
  total_plans: 32
  completed_plans: 27
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-11-11)

**Core value:** Kaynağına kadar izlenebilen, karşılaştırılabilir ve eksiklerini açıkça gösteren siyasi parti bilgisine eşit erişim.
**Current focus:** Phase 03 — Tüzük ve programların karşılaştırılması

## Current Position

Current Plan: 12
Total Plans in Phase: 16
Phase: 03 (Tüzük ve programların karşılaştırılması) — EXECUTING
Plan: 12 of 16
Status: Ready to execute
Last activity: 2026-11-14 — 03-11 tamamlandı; Saadet program karşılaştırması yerel partial sürümde doğrulandı

Progress: [███░░░░░░░] 33% (2/6 tamamlanan faz); Faz 2: 10/10 plan, 13/13 teknik teslim doğrusu, UAT 3/3; Faz 3: 11/16 plan

## Performance Metrics

**Velocity:**

- Total plans completed: 17
- Average duration: Kesin toplam ölçülmedi; plan bazlı yaklaşık süreler SUMMARY dosyalarında.
- Total execution time: Faz 1’in altı ve Faz 2’nin on planı ile belgelenmiş düzeltmeler uygulandı; kesin toplam süre ölçülmedi.

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 6 | - | - |
| 02 | 10 | - | - |

**Recent Trend:**

- Last 5 plans: 02-06, 02-07, 02-08, 02-09, 02-10
- Trend: Faz 1 tamamlandı; Faz 2 yürütümü 10/10 ve teknik teslimi 13/13. Güncel yerel üretici15 raporu hazır; kullanıcı UAT 3/3 geçti, faz tamamlandı. Kamu raporu 261111-epm sürümünde kalır.

**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01 | unknown | 2 tasks | 7 files |
| Phase 01 P02 | 18 min | 2 tasks | 7 files |
| Phase 01 P03 | 22 min | 2 tasks | 20 files |
| Phase 01 P04 | 18 min | 2 tasks | 35 files |
| Phase 01 P05 | 53min | 2 tasks | 113 files |
| Phase 01 P06 | 16 min | 2 tasks | 27 files |
| Phase 02 P01 | 21min | 3 tasks | 14 files |
| Phase 02 P02 | 7min | 3 tasks | 12 files |
| Phase 02 P03 | 26min | 3 tasks | 372 files |
| Phase 02 P04 | 26min | 3 tasks | 75 files |
| Phase 02 P05 | 38min | 3 tasks | 387 files |
| Phase 02 P06 | 37min | 3 tasks | 128 files |
| Phase 02 P07 | 50min | 3 tasks | 262 files |
| Phase 02 P08 | 49min | 3 tasks | 225 files |
| Phase 02 P09 | 60min | 3 tasks | 117 files |
| Phase 02 P10 | 128min | 3 tasks | 163 files |
| Phase 03 P01 | 59min | 2 tasks | 12 files |
| Phase 03 P02 | 192min | 2 tasks | 17 files |
| Phase 03 P03 | 144min | 2 tasks | 11 files |
| Phase 03 P04 | 205min | 2 tasks | 20 files |
| Phase 03 P05 | ölçülmedi | 2 tasks | 12 files |
| Phase 03 P06 | 95min | 2 tasks | 12 files |
| Phase 03 P07 | 84min | 2 tasks | 12 files |
| Phase 03 P08 | 214min | 2 tasks | 19 files |
| Phase 03 P09 | 150min | 2 tasks | 12 files |
| Phase 03 P10 | unknown | 2 tasks | 55 files |
| Phase 03 P11 | unknown | 2 tasks | 12 files |

## Accumulated Context

### Decisions

Kararların tamamı PROJECT.md Key Decisions tablosundadır.

- [Güncel 2026-11-11]: Kaynak derleme politikasıyla dokuz dosya ac4b8fdec02f4a9ebb666036ed251683 yerel sürümünde; açık atıf, pasif arşiv, içerik önceliği ve tam teslimi bozmayan --refresh uygulanmıştır. Sol/xhigh nihai değerlendirmesi 13/13 teknik teslim doğrusu verdi; üç ortak ilke kullanıcı UAT 3/3 ile tamamlandı. Aşağıdaki ilerleme sayıları tarihsel karar anlarını gösterir.

- Başlangıç ön listesi TBMM kayıtlarına dayalı dokuz partidir; CHP ve Cumhur İttifakı'nın mevcut/geçmiş ortakları dışarıdadır.
- Doğrudan aktarım siyah ve tırnak içinde, kaynaklı yapay zekâ özeti koyu mavidir; görünür metin türü etiketi kullanılmaz, veri kökeni kayıtlarda korunur. Kaynakta olmayan olgu üretilmez.
- Teknik ekosistem ön araştırması kullanıcı seçimiyle atlandı; esas kaynak araştırması ve aşama doğrulama ayarları korunur.
- Bütün aşamalar mvp modundadır; önce bir pilot partiyle kaynak → veri → HTML akışı, sonra kapsam genişlemesi.
- Sol/Terra 6.1 rol eşlemeleri ve mevcut reasoning seviyeleri korunur; iki rutin Luna rolü değişmedi, otomatik Astra yoktur.
- [Phase 1]: Önceki görünür metin türü etiketi kararı kullanıcının açık düzeltmesiyle güncellendi: alıntı siyah ve tırnak içinde, kaynaklı özet koyu mavi; görünür metin türü etiketi kullanılmaz. Metin kökeni veri kayıtlarında ve dışa aktarımda korunur.
- [Phase 1]: Pilot Yeni Parti; inceleme partinin kaynakla doğrulanacak kuruluşundan başlar. Ortak konulardaki bütün uygun kanıtlı eşleşmeler kaydedilir; ilgili belge zinciri takip edilir. Ana sekmeler partiler ve Karşılaştırmalı Özet; kaynaklar sekme altında ve metin içinde kaynak kaydına bağlantıyla sunulur. Ayrıntılar 01-CONTEXT.md içinde.
- [Phase 01 — tarihsel]: Alan adı için Yargıtay/TBMM doğrulaması aranmıştı. Kullanıcının 2026-11-11 tarihli D-13 kararı bu kullanım engelini kaldırır; eski sürümler tarihsel kayıt olarak korunur.
- [Phase 01]: TİP tüzüğü yalnız ortak konu sözlüğü dayanağıdır; kesim anındaki sürümü doğrulanmadı ve diğer parti dosyası incelenmiş sayılmaz.
- [Phase 01]: Eşleşme adayları ve çözümlenen eksikler geçmişi korunarak kaydedilir.
- [Phase 01]: Eski 2009 hesabı ve dönemi doğrulanmamış tutarlar güncel partiye mali satır olarak bağlanmaz.
- [Phase 01]: Eski kapalı sürümler kendi rapor üreticileriyle denetlenir; ajan incelemesi insan incelemesi sayılmaz.
- [Phase 02]: Kullanıcı planlama ön araştırmasını atladı ve ayrı seçimiyle proje ayarı workflow.nyquist_validation=false yapıldı. Bağımsız plan incelemesi ve uygulamada gerçek kaynak doğrulaması korunur.
- [Phase 02]: 02-01: TİP tracer completed_prefix boş kalır; tam parti teslimi ve insan kaynak kabulü olarak sunulmaz.
- [Phase 02]: 02-02: Kaynak türü sürüm yetkisinden ayrılır; tek sürüm ve dönem belirsizliği açık gösterilir. Tracer tamamlanmış parti sayılmaz.
- [2026-11-11 D-13]: Amaç kaynak derlemesidir. Parti yayınları, haberler ve sosyal paylaşımlar açık atıfla kullanılır; alan adı için sicil kanıtı, tarihsel yürürlük kanıtı veya her kaynağa insan onayı ön koşulu yoktur. Yeni Parti resmî sitesi https://yenipartiyiz.biz; tüzük /parti-tuzugu ve program /parti-programi doğrudan kullanılır. İddia/beyan söyleyene atfedilir; bilinmeyen tarih veya hesap dönemi uydurulmaz.
- [2026-11-11 D-14–D-16]: İçerik önce, yöntem ve eski incelemeler kapalı ayrıntılarda. Özgün kaynaklar korunur, HTML belgeler yerel varlıklı sayfa görünümünde açılır. Düzeltme mevcut kamu raporuna yayımlandı; kalan 02-03–02-10 planları güncellendi, Faz 2 ilerleyişi 2/10 kaldı.
- [2026-11-11 model seçimi]: Kullanıcının daha güçlü ajan isteğiyle bu düzeltmenin planlama ve uygulaması GPT-6.1 Sol/xhigh ile yapıldı. Otomatik Astra eklenmedi; genel kayıtlı maliyet/rol varsayılanları değişmedi.
- [Phase 02]: 02-03: TİP 7d5f78dde79a4b0bb48f64a16fd263c1 sürümü ve 02-02’ye bağlı makbuzla tam teslim; prefix yalnız ['tip']. Parti yayınları açık atıfla derlendi; söylem/mali başlıklar sonraki fazlar için Henüz incelenmedi kaldı.
- [Phase 02]: 02-04: DEM 77074f17144b41399615da5ee4b37bcf yerel sürümü ve TİP’e bağlı makbuzla teslim; prefix yalnız tip,dem. Sicil 30 Kasım 2012 ile 25 Kasım toplantısı ve ayrı HDP sicili ayrıldı; güncel bağımsız program açık kaldı.
- [Phase 02]: 02-05: İYİ Parti 45fdfa3f6abe4a8882c52b2658fc6c6d yerel sürümü ve DEM’e bağlı makbuzla teslim; prefix tip,dem,iyi. Gerçek sicil yargitay-207; 2020/2026 değişiklikli tüzükler ve tam HTML programı derlendi, PDF/kabul tarihi ve kurumsal kaynak görünümü sınırları korundu.
- [Phase 02]: 02-06: Yeni Yol, 732fcd2bfc954200b4292c51ef29f526 yerel sürümü ve İYİ Parti’ye bağlı makbuzla teslim; prefix tip,dem,iyi,yeni-yol. Gerçek sicil yargitay-331, kuruluş 13.01.2025; ortak grup ve aynı adlı eski parti ayrıldı. Tam tüzük/program, bağımsız site ve ilk kongre açıkları gerçek aramalarla korunur.

- [Quick 261111-j4v]: Süreç içi PDF/kütüphane tekrar kullanımı eklendi; 34 test geçti. Gerçek Yeni Yol makbuz ölçümü 180 saniyede zaman aşımına uğradı; makbuz/veri değişmedi, toplam hızlanma veya yeni makbuz kabulü iddia edilmedi. Önceki başarılı teslim geçerlidir; Faz 2 6/10, sıradaki 02-07.
- [Phase 02]: 02-07: DBP, 4a4ce5448c894a9ebc3c12e97cacb6dd yerel sürümü ve Yeni Yol’a bağlı makbuzla teslim; prefix tip,dem,iyi,yeni-yol,dbp. Gerçek sicil yargitay-117, kuruluş 02.05.2008; BDP–DBP bağı açık metinlerle kaynaklıdır. Ayrı güncel program ve birincil kuruluş tutanakları açık kaldı. UTF-8 pasif görünüm hatası regresyonla düzeltildi; ilk aday ve eski baytlar korundu.
- [Phase 02]: 02-09: Saadet d42f5105a1a1431d86cdfb3db8669fe2 yerel sürümü ve EMEP’e bağlı makbuzla teslim; prefix tip,dem,iyi,yeni-yol,dbp,emep,saadet. Gerçek sicil yargitay-70, kuruluş 20.07.2001; Yeni Yol/grup/üyelik ayrımı korunur. Tam 25 sayfa tüzük ve 70 sayfa program ile 2002 ikinci baskı edinildi; asıl tutanaklar, eski program ve tam sürüm zinciri açık.

- [Phase 02]: 02-10: Demokrat bcc67d04d9d741e191589d0f5ac173ca yerel sürümü ve Saadet’e bağlı makbuzla teslim; tam prefix tip,dem,iyi,yeni-yol,dbp,emep,saadet,demokrat. Gerçek sicil yargitay-3, kuruluş 23.06.1983 ve ad değişikliği 27.05.2007 ayrı; 1946 DP ve ayrı güncel DYP kaynaklı notlarla ayrılır. Dokuz dosya audit’i, 32 test ve son makbuzdan sonra sekiz sıralı receipt-check geçti. Teslim anında dört ham probe/üç descriptor-less prohibition unresolved ve flagged-unverified idi. Kapanışta üç ortak ilke kullanıcı UAT ile onaylandı; dört ham tanı korunarak faz tamamlandı.
- [Phase 03]: Kaynak envanterinin tamamlanması, parti bazlı ayrıntılı incelemenin tamamlandığı anlamına gelmez; DEM kongresi ek belge, BDP nüshaları tarihsel kaynaktır.
- [Phase 03]: 03-02 yerel partial sürüm `d370042ecc23499b9abfd6c11af33120`; renderer 17, 301 kaynaklı konu ve 1.632 envanter kaydı. İçerik testleri 17/17, konu testleri 3/3 ve PHASE3_AUDIT_OK; sonraki parti incelemeleri 03-03 ile başlar.
- [Phase 03]: 03-05 DEM tüzük nüshaları eşit ve sırası bilinmeyen alternatifler olarak işlendi; kongre kararı ek belge, bağımsız tam program açığı ayrı kaldı. Yerel sürüm `6090bfda16a14ce99a1b6c9d3ff47d71` Faz 2 ve Faz 3 denetimlerini geçti; gelir kapsamı 03-14 geri taramasına devredildi.
- [Phase 03]: 03-06 İYİ'nin iki değişiklik notlu tüzüğü ve tam HTML programı ortak konulara işlendi; PDF biçimi erişim açığı ayrı korundu. Yerel sürüm `a828140c2fb649b5b8d0cef32b42769e` Faz 2 ve Faz 3 denetimlerini geçti; kayıt yenilemesi ve erken çocukluk yaş kapsamı 03-14'e aktarıldı.
- [Phase 03]: 03-07 Yeni Yol için ayrı tüzel kimlikle tüzük ve program aramaları yenilendi; tam metinler bulunamadığından 301 ortak konu gerçek belge açıklarına bağlandı. Yerel sürüm `b27a1387425c40889313e92dfc91739e` Faz 2 ve Faz 3 denetimlerini geçti; başka parti ve ortak grup metinleri yerine kullanılmadı.
- [Phase 03]: 03-08: DBP tüzüklerinde sırası bilinmeyen farklı hükümler eşit kaynaklı gösterildi; tarihsel BDP programı ve bağımsız güncel DBP programı açığı ayrı korundu. Üretici 17 dondurularak sürümün kendi yayıncı atfını gösteren üretici 18 kullanıldı.
- [Phase 03]: EMEP kongre önerisi ve Yargıtay gövdesi, kabul ve sıra bilinmeden ayrı kaynak türleriyle gösterilir.
- [Phase 03]: 1996 ayrı Emek Partisi belgesi ve koşullu destekler güncel EMEP kimliği veya evrensel gelir olarak genellenmez.
- [Phase 03]: 03-10: Aynı SHA taşıyan Saadet tüzük adresleri maddi değişiklik değildir; 2002 ve sonraki nüsha iki kaynakla, kesin yürürlük ve ara zincir varsayılmadan karşılaştırılır.
- [Phase 03]: 03-10: Dar soruya eşlik eden kaynak bağlamı olumlu cevap sayılmaz; 63 sınırlı yokluk kaydı kapsamıyla korunur.
- [Phase 03]: 03-11: Dar soruya eşlik eden bağlam olumlu politika yanıtı sayılmaz; koşullu Temel Vatandaşlık Geliri kaynak koşullarıyla korunur.

### Pending Todos

None yet.

### Blockers/Concerns

- [Faz 3 planlama]: Açık planlama engeli yok; 03-PLAN-CHECK.md bağımsız PASS kaydıdır. Sekiz unclassified/unresolved ham uç ve üç descriptor-less prohibition 03-16-PLAN.md içinde açık korunur; bunlar yürütüm/kabul sırasında ele alınır. Planlardaki kapsamlı kaynak incelemesi, uygulama ve faz sonu UAT henüz yapılmadı.
- [Faz 2 kapanış]: Açık uygulama açığı yok; 02-UAT.md içindeki üç ortak ilke kullanıcı tarafından ayrı ayrı pass ile onaylandı. Faz 2 tamamlandı; dört ham tanı unclassified/unresolved olarak korunur. Kaynaklar için tekil insan kabulü kullanım koşulu değildir.
- [Faz 2 destek sınırı]: UTF-8 dışı kodlama yalnız HTTP başlığında kalıyorsa yeni yakalama açık hata verir; meta/BOM desteklenir. Eski baytlar korunur.

- Faz 1 için açık uygulama engeli yok; 8/8 UAT toplu kullanıcı kabulüyle kapandı.
- [2026-11-11 düzeltmesi]: Yeni Parti site/tüzük/program kullanım engelleri çözüldü; önceki girişimler tarihçede korunur. Gerçek ulusal kesin hesap ve Kocaeli hesap başlangıcı belirsizliği sürer; tüzükteki mali kurallar gerçekleşmiş harcama olarak sunulmaz.
- [Phase 1 → Phase 2] COVERAGE.md içindeki 13 unclassified/unresolved ham uç satırı değiştirilmedi. Kullanıcı bu yöntem sınırlarıyla fazı kabul etti; bunlar yeni kaynak kanıtı veya otomatik sınıflandırma sonucu değildir.
- [Phase 2] Parti tüzel kimliği, bireysel milletvekili üyeliği ve ortak grup ayrımı kapsam genişlerken korunacak; model/maliyet tercihleri değişmedi.
- [Phase 2] Planlar bağımsız incelemeden bir sıra çelişkisi düzeltilerek geçti; 4/4 gereksinim ve 12/12 karar kapsandı. Plan zamanındaki dört sınıflandırılamayan ham uç varsayımı ve üç descriptor-less prohibition 02-10-PLAN.md içinde tarihsel olarak korunur. Kapanışta yalnız üç ortak ilke kullanıcı UAT ile onaylandı; dört ham tanı değişmedi.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 261110-pds | GitHub aktarımı ve pilot HTML raporunun yayımlanması | 2026-11-10 | 46f4882 | [261110-pds-repoyu-github-a-kopyala-ve-pilot-html-ra](./quick/261110-pds-repoyu-github-a-kopyala-ve-pilot-html-ra/) |
| 261111-epm | Kaynak derleme yaklaşımı, gerçek Yeni Parti içeriği, sade rapor ve özgün görünümlü belge arşivlerinin yayımlanması | 2026-11-11 | 7e18593 | [261111-epm-kaynak-derleme-y-ntemini-sadele-tir-yeni](./quick/261111-epm-kaynak-derleme-y-ntemini-sadele-tir-yeni/) |
| 261111-j4v | Süreç içi PDF yeniden kullanımı; 34 test geçti, tek makbuz ölçümü 180s sınırında tamamlanmadı | 2026-11-11 | a475f5a | [261111-j4v-ayn-pdf-sayfalar-n-n-s-re-i-indeki-yinel](./quick/261111-j4v-ayn-pdf-sayfalar-n-n-s-re-i-indeki-yinel/) |

### Roadmap Evolution

- Phase 1 edited: success_criteria: kullanıcının görünür metin türü etiketi yerine tırnaklı alıntı seçimi uygulandı; kapsam ve bağımlılıklar korunuyor
- Phase 6 edited: success_criteria: kullanıcının görünür metin türü etiketi yerine tırnaklı alıntı seçimi uygulandı; kapsam ve bağımlılıklar korunuyor

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-11-14T10:26:17.159Z
Stopped at: Completed 03-11-PLAN.md
Resume file: None
