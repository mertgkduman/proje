---
gsd_state_version: "1.0"
milestone: v1.0
current_phase: 02
current_phase_name: Bütün partiler için dosyalar ve sürümlü kaynaklar
current_plan: 8
status: executing
stopped_at: 02-07 tamamlandı; DBP teslimi bildirildikten sonra sıradaki 02-08 EMEP
last_updated: "2026-11-11T19:54:59.157Z"
last_activity: 2026-11-11
last_activity_desc: 02-07 tamamlandı; DBP tam yerel dosyası ve Yeni Yol’a bağlı makbuzu hazır, sıradaki 02-08 EMEP
state_head: 94d3b15acf66d859e23a37e54e9f310a2e6f13ab
progress:
  total_phases: 6
  completed_phases: 1
  total_plans: 16
  completed_plans: 13
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-11-10)

**Core value:** Kaynağına kadar izlenebilen, karşılaştırılabilir ve eksiklerini açıkça gösteren siyasi parti bilgisine eşit erişim.
**Current focus:** Phase 02 — Bütün partiler için dosyalar ve sürümlü kaynaklar

## Current Position

Current Plan: 8
Total Plans in Phase: 10
Phase: 02 (Bütün partiler için dosyalar ve sürümlü kaynaklar) — EXECUTING
Plan: 7/10 tamamlandı; sıradaki 02-08
Status: Ready to execute
Last activity: 2026-11-11 — 02-07 tamamlandı: DBP’nin 20 kaynaklı özet/alıntı çifti, yedi alanlı kartı, kuruluş/ilk kongre/ad değişikliği kronolojisi ve tüzük/program edinimi 4a4ce5448c894a9ebc3c12e97cacb6dd yerel sürümü ve Yeni Yol’a bağlı makbuzla hazırdır. Ayrı güncel program ve birincil kuruluş tutanakları açık kaldı. Pasif HTML UTF-8 hatası regresyonla düzeltildi; ilk aday ve eski baytlar korundu. DBP tesliminin bildirilmesinden sonra sıradaki plan 02-08 EMEP’tir.

Progress: [██░░░░░░░░] 17%

## Performance Metrics

**Velocity:**

- Total plans completed: 13
- Average duration: Kesin toplam ölçülmedi; plan bazlı yaklaşık süreler SUMMARY dosyalarında.
- Total execution time: Faz 1'in altı ve Faz 2'nin yedi planı ile belgelenmiş düzeltmeler uygulandı; kesin toplam süre ölçülmedi.

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 6 | - | - |
| 2 | 7/10 | - | - |

**Recent Trend:**

- Last 5 plans: 02-03, 02-04, 02-05, 02-06, 02-07
- Trend: Faz 1 tamamlandı; Faz 2 7/10 planda. DBP tam yerel dosyası ve makbuzu hazır; sonraki parti EMEP’tir. Kamu raporu 261111-epm sürümünde kalır.

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

## Accumulated Context

### Decisions

Kararların tamamı PROJECT.md Key Decisions tablosundadır.

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

### Pending Todos

None yet.

### Blockers/Concerns

- Faz 1 için açık uygulama engeli yok; 8/8 UAT toplu kullanıcı kabulüyle kapandı.
- [2026-11-11 düzeltmesi]: Yeni Parti site/tüzük/program kullanım engelleri çözüldü; önceki girişimler tarihçede korunur. Gerçek ulusal kesin hesap ve Kocaeli hesap başlangıcı belirsizliği sürer; tüzükteki mali kurallar gerçekleşmiş harcama olarak sunulmaz.
- [Phase 1 → Phase 2] COVERAGE.md içindeki 13 unclassified/unresolved ham uç satırı değiştirilmedi. Kullanıcı bu yöntem sınırlarıyla fazı kabul etti; bunlar yeni kaynak kanıtı veya otomatik sınıflandırma sonucu değildir.
- [Phase 2] Parti tüzel kimliği, bireysel milletvekili üyeliği ve ortak grup ayrımı kapsam genişlerken korunacak; model/maliyet tercihleri değişmedi.
- [Phase 2] Planlar bağımsız incelemeden bir sıra çelişkisi düzeltilerek geçti; 4/4 gereksinim ve 12/12 karar kapsandı. Dört sınıflandırılamayan ham uç varsayımı ve üç descriptor-less prohibition çözülmüş/doğrulanmış sayılmadan 02-10-PLAN.md içinde korundu; faz sonu doğrulamasına taşınır.

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

Last session: 2026-11-11T19:54:21.353Z
Stopped at: 02-07 tamamlandı; DBP teslimi bildirildikten sonra sıradaki 02-08 EMEP
Resume file: .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-08-PLAN.md
