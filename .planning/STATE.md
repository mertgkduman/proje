---
gsd_state_version: "1.0"
milestone: v1.0
current_phase: 01
current_phase_name: Kapsam, yöntem ve kaynaklı pilot rapor
status: Awaiting human verification — Phase 01 UAT
stopped_at: Phase 01 human_needed; all 6 plans executed, 8 UAT checks pending
last_updated: "2026-11-10T17:51:18.340Z"
last_activity: 2026-11-10
last_activity_desc: Faz 1 altı plan uygulandı; 44 test ve PHASE1_AUDIT_OK geçti. Kod bulguları giderildi; bağımsız doğrulama human_needed, 12/13 must-have ve 8 UAT kontrolü bekliyor.
state_head: 76b27bda7769eb6d152dd1456b86d403e42b558a
progress:
  total_phases: 6
  completed_phases: 0
  total_plans: 6
  completed_plans: 6
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-11-09)

**Core value:** Kaynağına kadar izlenebilen, karşılaştırılabilir ve eksiklerini açıkça gösteren siyasi parti bilgisine eşit erişim.
**Current focus:** Phase 01 — Kapsam, yöntem ve kaynaklı pilot rapor

## Current Position

Phase: 01 (Kapsam, yöntem ve kaynaklı pilot rapor) — VERIFYING
Plan: 6 of 6
Status: Awaiting human verification — Phase 01 UAT
Last activity: 2026-11-10 — 6/6 plan, 44 test ve bağımsız doğrulama tamamlandı; 8 insan UAT kontrolü bekliyor.

Progress: [██████████] 6/6 plans

## Performance Metrics

**Velocity:**

- Total plans completed: 6
- Average duration: Kesin toplam ölçülmedi; plan bazlı yaklaşık süreler SUMMARY dosyalarında.
- Total execution time: Altı plan ve son inceleme/düzeltmeler uygulandı; kesin toplam süre ölçülmedi.

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 6 | Kesin toplam ölçülmedi | - |

**Recent Trend:**

- Last 5 plans: 01-02, 01-03, 01-04, 01-05, 01-06
- Trend: 6/6 plan uygulandı; faz kapanışı 8 insan UAT kontrolünü bekliyor.

**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01 | unknown | 2 tasks | 7 files |
| Phase 01 P02 | 18 min | 2 tasks | 7 files |
| Phase 01 P03 | 22 min | 2 tasks | 20 files |
| Phase 01 P04 | 18 min | 2 tasks | 35 files |
| Phase 01 P05 | 53min | 2 tasks | 113 files |
| Phase 01 P06 | 16 min | 2 tasks | 27 files |

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
- [Phase 01]: Alan adı sahipliği incelenen Yargıtay ve TBMM kayıtlarıyla doğrulanamadığında doğrulanmamış bırakılır.
- [Phase 01]: TİP tüzüğü yalnız ortak konu sözlüğü dayanağıdır; kesim anındaki sürümü doğrulanmadı ve diğer parti dosyası incelenmiş sayılmaz.
- [Phase 01]: Eşleşme adayları ve çözümlenen eksikler geçmişi korunarak kaydedilir.
- [Phase 01]: Eski 2009 hesabı ve dönemi doğrulanmamış tutarlar güncel partiye mali satır olarak bağlanmaz.
- [Phase 01]: Eski kapalı sürümler kendi rapor üreticileriyle denetlenir; ajan incelemesi insan incelemesi sayılmaz.

### Pending Todos

None yet.

### Blockers/Concerns

- Başlatmayı engelleyen teknik sorun yok; gereksinimler ve yol haritası kullanıcı tarafından onaylandı.
- TBMM ön listesi arşivlenerek yeniden kontrol edilecek; ortak Meclis grubu ile bireysel parti üyeliği ayrımı korunacak.
- Plan kontrolü geçti; COVERAGE.md içindeki 13 sınıflandırılmamış uç varsayımı ve dört descriptor-less prohibition yürütmede insan incelemesine bağlıdır, otomatik çözülmüş sayılmaz. Yeni Parti tüzük/programının özgün dosyaları ve otoritesi yürütmede doğrulanacaktır.

### Roadmap Evolution

- Phase 1 edited: success_criteria: kullanıcının görünür metin türü etiketi yerine tırnaklı alıntı seçimi uygulandı; kapsam ve bağımlılıklar korunuyor
- Phase 6 edited: success_criteria: kullanıcının görünür metin türü etiketi yerine tırnaklı alıntı seçimi uygulandı; kapsam ve bağımlılıklar korunuyor

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-11-10T17:51:18.060Z
Stopped at: Phase 01 human_needed; all 6 plans executed, 8 UAT checks pending
Resume file: .planning/phases/01-kapsam-y-ntem-ve-kaynakl-pilot-rapor/01-UAT.md
