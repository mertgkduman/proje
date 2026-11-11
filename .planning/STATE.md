---
gsd_state_version: "1.0"
milestone: v1.0
current_phase: 02
current_phase_name: Bütün partiler için dosyalar ve sürümlü kaynaklar
status: executing
stopped_at: Quick 261111-epm yayımlandı; sıradaki 02-03
last_updated: "2026-11-11T16:26:20.753Z"
last_activity: 2026-11-11
last_activity_desc: Yeni Parti kaynak derlemesi, sade rapor ve özgün görünümlü arşivler yayımlandı; 02-03 sırada
state_head: 7e18593792f6c54ab3c7207d27e8c89888fb0d62
progress:
  total_phases: 6
  completed_phases: 1
  total_plans: 16
  completed_plans: 8
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-11-10)

**Core value:** Kaynağına kadar izlenebilen, karşılaştırılabilir ve eksiklerini açıkça gösteren siyasi parti bilgisine eşit erişim.
**Current focus:** Phase 02 — Bütün partiler için dosyalar ve sürümlü kaynaklar

## Current Position

Phase: 02 (Bütün partiler için dosyalar ve sürümlü kaynaklar) — EXECUTING
Plan: 2/10 tamamlandı; sıradaki 02-03
Status: Ready to execute
Last activity: 2026-11-11 — Quick 261111-epm tamamlandı: Yeni Parti kaynakları, sade okuyucu raporu ve belge görünümleri mevcut GitHub Pages adresinde yayımlandı; 02-03 başlamadı.

Progress: [██░░░░░░░░] 17%

## Performance Metrics

**Velocity:**

- Total plans completed: 8
- Average duration: Kesin toplam ölçülmedi; plan bazlı yaklaşık süreler SUMMARY dosyalarında.
- Total execution time: Altı plan ve son inceleme/düzeltmeler uygulandı; kesin toplam süre ölçülmedi.

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 6 | - | - |
| 2 | 2/10 | - | - |

**Recent Trend:**

- Last 5 plans: 01-04, 01-05, 01-06, 02-01, 02-02
- Trend: Faz 1 tamamlandı; Faz 2 2/10 planda. Kullanıcının kaynak derleme düzeltmesi 261111-epm ile yayımlandı; sıradaki 02-03.

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

### Roadmap Evolution

- Phase 1 edited: success_criteria: kullanıcının görünür metin türü etiketi yerine tırnaklı alıntı seçimi uygulandı; kapsam ve bağımlılıklar korunuyor
- Phase 6 edited: success_criteria: kullanıcının görünür metin türü etiketi yerine tırnaklı alıntı seçimi uygulandı; kapsam ve bağımlılıklar korunuyor

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-11-11T16:26:20.424Z
Stopped at: Quick 261111-epm yayımlandı; sıradaki 02-03
Resume file: .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-03-PLAN.md
