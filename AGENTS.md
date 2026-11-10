<!-- GSD:project-start source:PROJECT.md -->

## Project

**Türkiye Siyasi Partileri: Tüzük, Program, İlke ve Uygulama Araştırması**

Türkiye'deki siyasi partilerin kuruluş bilgilerini, tüzüklerini, programlarını, kamuoyuna verdikleri sözleri, finansmanlarını, harcamalarını ve belgelenmiş uygulamalarını inceleyen bağımsız, tarafsız ve kaynak temelli bir araştırma arşividir. Dağınık bilgileri doğrulanabilir kaynaklarla bir araya getirerek herkesin aynı bilgiye erişmesini ve kendi değerlendirmesini yapmasını amaçlar. Standart parti dosyaları ve karşılaştırmalar, sekmelere ayrılmış Türkçe bir HTML raporu ve yeni belgelerle güncellenebilir ortak veri tabanı üzerinden sunulacaktır.

**Core Value:** Herkesin siyasi partiler hakkında kendi değerlendirmesini yapabilmesi için kaynağına kadar izlenebilen, karşılaştırılabilir ve eksiklerini açıkça gösteren bilgiye eşit erişim sağlamak.

### Constraints

- **Tarafsızlık:** Bütün partiler aynı başlıklar ve doğrulama ölçütleriyle incelenir; kapsam kararı araştırma sonucu gibi sunulmaz.
- **Kaynak zorunluluğu:** Her önemli bulgu izlenebilir kanıta dayanır; yapay zekâ modelinin bilgisi kaynak olarak kabul edilmez.
- **Metin sunumu:** Doğrudan aktarım siyah ve tırnak içinde, yapay zekâ özeti/düzenlemesi koyu mavidir; görünür metin türü etiketi kullanılmaz, metin kökeni kayıtlarda korunur.
- **Eksikleri görünür kılma:** “Bulunamadı”, “Erişilemedi” ve “Doğrulanamadı” durumları açıkça gösterilir.
- **İlk kapsam:** TBMM kayıtlarında temsil edilen partiler arasından CHP ve Cumhur İttifakı'nın mevcut/geçmiş ortakları çıkarılır; onaylanan dokuz partilik ön liste esas alınır ve değişiklikler belgelenir.
- **Dil ve teslim biçimi:** Araştırma Türkçe ve herkesin okuyabileceği şekilde sunulur; ana okuyucu çıktısı sekmeli HTML raporudur.
- **Geliştirilebilirlik:** Kaynaklar, belge sürümleri ve bulgu değişiklikleri izlenebilir olmalı; veri tabanı yeni bilgilerle güncellenebilmelidir.
- **Model ve maliyet tercihi:** Kullanıcının 2026-11-09 tarihli seçimiyle kayıtlı Sol ve Terra modelleri 6.1 sürümlerine geçirilmiştir. Belirtilmeyen orkestrasyon ve alt görevlerde GPT-6.1 Terra/high; ağır araştırma, planlama, sentez ve yöntem doğrulamasında yapılandırılmış GPT-6.1 Sol/xhigh rolleri esas alınır. Rol bazında önceden seçilmiş reasoning seviyeleri ve iki rutin Luna rolü korunur. Astra açık kullanıcı seçimi olmadan otomatik model veya yedek model olarak eklenmez.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->

## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `$gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `$gsd-debug` for investigation and bug fixing
- `$gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `$gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
