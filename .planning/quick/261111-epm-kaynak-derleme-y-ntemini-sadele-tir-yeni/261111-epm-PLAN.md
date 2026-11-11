---
quick_id: 261111-epm
phase: quick-261111-epm
plan: "01"
title: Kaynak derleme yöntemini düzelt; Yeni Parti belgelerini ve okunabilir arşivi yayımla
type: execute
wave: 1
depends_on: []
autonomous: true
requirements: [DOS-01, DOS-02, KAY-01, KAY-02, KAY-03, KAY-04, MET-01, MET-02, MET-03, MET-04, EKS-01, EKS-02, VER-01, RAP-01, RAP-02, RAP-03]
files_modified:
  - .planning/PROJECT.md
  - .planning/REQUIREMENTS.md
  - .planning/STATE.md
  - AGENTS.md
  - README.md
  - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-CONTEXT.md
  - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-03-PLAN.md
  - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-04-PLAN.md
  - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-05-PLAN.md
  - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-06-PLAN.md
  - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-07-PLAN.md
  - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-08-PLAN.md
  - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-09-PLAN.md
  - .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-10-PLAN.md
  - src/arsiv.py
  - src/dosyalar.py
  - src/kaynaklar.py
  - src/arsiv_gorunum.py
  - src/rapor.py
  - src/rapor_v10.py
  - src/rapor_v11.css
  - tests/test_source_policy.py
  - tests/test_archive_views.py
  - tests/test_documents.py
  - tests/test_dossiers.py
  - tests/test_report.py
  - tests/test_publication.py
  - tests/test_acceptance.py
  - tests/browser_probe.py
  - data/dossiers/261111-epm-yeni-parti.json
  - data/current.json
  - data/objects/{new_sha256}/{new_source_files}
  - data/views/{view_id}/index.html
  - data/views/{view_id}/manifest.json
  - data/views/{view_id}/assets/{asset_sha256}.{extension}
  - data/releases/{new_release_id}/records.sqlite3
  - data/releases/{new_release_id}/records.json
  - data/releases/{new_release_id}/index.html
  - data/releases/{new_release_id}/manifest.json
estimate:
  tokens: 55000
  raw_tokens: 55000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - Parti yayınları, atıflı haberler ve kimliği/tarihi/adresi belirtilen sosyal paylaşımlar aynı kaynak derleme politikasından kayıt, JSON, HTML, publish ve audit yollarının tamamında geçer; sicil üzerinden alan adı kanıtı ve her kaynak için insan onayı zorunlu değildir.
    - Yeni Parti sekmesinde kuruluş gerekçesi, tüzük düzenlemeleri ve program vaatleri gerçek pasajlarla okunur; resmî site https://yenipartiyiz.biz olarak kaynaklı gösterilir; haber ve iddialar söyleyen kişiye/yayına atfedilir.
    - Tüzük ve program için ayrı doğru arşiv bağlantıları açılır; HTML kodu yerine özgün sayfaya benzeyen güvenli çevrimdışı belge görünür.
    - Okur önce parti içeriğini görür; kaynak arama, yetki, inceleme ve geçmiş eksik ayrıntıları kapalı ayrıntı bölümlerinden erişilir; gerçek güncel eksikler kısa ve görünür kalır.
    - Önceki release ve nesne baytları, renderer 10 ve eski makbuzlar korunur; yeni release TİP stage=tracer ve completed_prefix=[] taşır; Faz 2 halen 2/10 plan tamamlanmış durumdadır.
  artifacts:
    - path: src/kaynaklar.py
      provides: Sürümlü kaynak politikası ve atıf denetimi
    - path: src/arsiv_gorunum.py
      provides: Özgün baytları değiştirmeyen, varlıkları yerelleştirilmiş pasif arşiv görünümü
    - path: data/dossiers/261111-epm-yeni-parti.json
      provides: Gerçek Yeni Parti pasajları, özet/alıntılar, kaynak atıfları ve düzeltme ilişkileri
    - path: src/rapor_v10.py
      provides: Önceki renderer 10 yayınlarının aynı HTML ile yeniden üretimi
    - path: tests/test_source_policy.py
      provides: Atıflı kaynakların yazma, dışa aktarma ve yayın zincirindeki gerçek davranış testleri
    - path: tests/test_archive_views.py
      provides: İki belgenin doğru eşleşmesi, çevrimdışı görünüm ve pasif içerik testleri
  key_links:
    - from: source_attribution
      to: document_version, passage, finding_evidence
      via: Kaynağa neyin atfedildiği, yayıncı/yazar/hesap, tarih ve kalıcı URL
    - from: document_version
      to: data/views/{view_id}/index.html
      via: Özgün SHA-256 ve türetilmiş dosya/varlık manifesti
    - from: data/current.json
      to: Yeni SQLite/JSON/HTML release ve gh-pages statik kopyası
      via: Aynı denetlenmiş sürüm ve eksiksiz yerel arşiv dosyaları
---

<objective>
Kullanıcının 2026-11-11 tarihli açık yöntem düzeltmesini TİP'e devam etmeden uygula: siyasi partiler hakkında atıflı bilgi derleyen arşiv, gerçek Yeni Parti tüzük/program içeriği, sade Türkçe okuma akışı ve özgün görünümlü çevrimdışı kaynaklar teslim et. Bu karar eski alan adı/otorite ve evrensel insan kabulü koşullarını açıkça değiştirir; kaynak beyanını hukuken doğrulanmış olguya dönüştürmez.

Purpose: Okur partinin neden kurulduğunu, ne vaat ettiğini, ne yaptığını, para kaynakları ve harcamaları hakkında mevcut kaynakların ne söylediğini kolayca öğrenebilsin.
Output: Güncellenen yöntem ve kalan planlar, sürümlü kaynak politikası, gerçek içerikli yeni değişmez release, güvenli arşiv görünümleri ve mevcut GitHub Pages akışında aynı sürümün yayını.
</objective>

<execution_context>
@/hpc/home/mg551/.codex/gsd-core/workflows/execute-plan.md
@/hpc/home/mg551/.codex/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@AGENTS.md
@.planning/PROJECT.md
@.planning/REQUIREMENTS.md
@README.md
@.planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-CONTEXT.md
@.planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-03-PLAN.md
@.planning/quick/261110-pds-repoyu-github-a-kopyala-ve-pilot-html-ra/261110-pds-SUMMARY.md
@src/arsiv.py
@src/dosyalar.py
@src/rapor.py
@tests/test_publication.py
@tests/browser_probe.py

Planning-time observations: current=b14c96c54e4b420686c46e5cfb1071a3, schema=4, renderer=10, dossier_validation_version=1, phase2_delivery={party_id:tip,stage:tracer,completed_prefix:[]}. Re-observe current before writing; preserve intervening work. Existing charter HTML is b3709f52e07f6d65797d021f571c2b97eca5ac02771a633fe55aafec4130518e; program HTML is 58fa220ab814bd82a4c8d0d233bf55ab268eb9f856750cd88abc544e17ceba1b. The former has canonical /parti-tuzugu and is the charter even if a previous user-facing link called it the program. Live pages were opened during planning: https://yenipartiyiz.biz/parti-tuzugu labels its charter 22 July 2026; https://yenipartiyiz.biz/parti-programi labels its founding program 24 July 2026. Treat these as dates stated by the publisher. The existing site archive includes inline CSS, /yeniparti.png and Google font stylesheets, plus active scripts that must stay inactive locally. No new package is required.
</context>

<tasks>

<task type="tracer" tdd="true">
  <name>1. Kaynak derleme politikasını gerçek kayıt → yayın diliminde uygula ve kalan işi bu karara bağla</name>
  <files>.planning/PROJECT.md, .planning/REQUIREMENTS.md, AGENTS.md, README.md, .planning/STATE.md, .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-CONTEXT.md, .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-03-PLAN.md, .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-04-PLAN.md, .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-05-PLAN.md, .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-06-PLAN.md, .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-07-PLAN.md, .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-08-PLAN.md, .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-09-PLAN.md, .planning/phases/02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar/02-10-PLAN.md, src/kaynaklar.py, src/arsiv.py, src/dosyalar.py, src/rapor.py, src/rapor_v10.py, tests/test_source_policy.py, tests/test_dossiers.py, tests/test_publication.py</files>
  <behavior>
    - An archived party-published charter passage can be recorded, exported, rendered, published and audited without a document_authority row or external registry domain proof.
    - An attributed news allegation remains a report/claim, and a social item retains publisher/author or handle, explicit post date and public permalink; neither becomes an independently established fact.
    - Missing publication date stays null/unknown; a claimed registry identity still cannot contradict its actual registry source. Unrelated party evidence, unsupported site claims, unsafe URLs and missing provenance fail.
    - Old release validation and renderer output remain unchanged; the new policy is explicit, versioned and cannot be removed from a descendant release to bypass integrity checks.
  </behavior>
  <action>
First add focused failing end-to-end tests in tests/test_source_policy.py using an isolated copy of the current archive and one archived charter excerpt. Exercise record/load → export → render → publish --party tip --stage tracer → audit, without mutating live current. Keep the real FK, hash, quote/passage, immutable release and delivery-prefix checks.

Freeze the current src/rapor.py as src/rapor_v10.py before changing it; preserve its use of unchanged rapor_v8.css and historical source labels. Introduce renderer 11 and explicit backward dispatch. Add the source-policy contract in src/kaynaklar.py: a versioned policy record and source_attribution linked to document_version, with publisher, available author, social handle where applicable, publication date/precision, public URL and attribution basis. Distinguish party publication, journalism and social publication from a legal registry identity assertion. Add social as a source type without changing labels used by old renderers. Require attribution and archived supporting content for new material; allow unavailable article author and unknown article/document date without invented values; social-post presentation requires its identifiable author/handle, date and permalink. Derive human-readable attribution from these records, including the pattern “Sosyal medya kullanıcısı [hesap] bunu [tarih] paylaştı.”

Migrate workspace copies additively to schema 5, keeping migration rollback/backup and previous row values. Mark new manifests source_policy_version=2, data_schema_version=5 and dossier_validation_version=2; keep the cutoff method and its actual event-date meaning separate from this policy version. Dispatch historical schema 1–4 and dossier validation 1 by snapshot/manifest contract. Route record, dossier load, validate_evidence, validate_dossier, export_db, publish_release and audit_release through the same new policy. Remove the requirement that party-published Tüzük/Program content or a sourced official_site have a TBMM/Yargıtay domain-authority chain. The official_site value still needs a source-backed publisher/URL relationship; unsupported arbitrary domains fail. Preserve registry consistency checks for assertions actually presented as registry identities. Confirmed source text means the passage was checked against its source, not that its allegation was legally established. Attributed journalism/social statements must not require original actor authorization or independent confirmation merely to be compiled; keep formal action/match claims distinct where their stronger meaning requires it. Financial reporting can be quoted with publisher, stated amount, period and scope; unknown periods must not be invented to fit financial tables. Do not create human review rows on the user's behalf or require human approval for every source.

Record dated superseding decisions D-13–D-16 in active 02-CONTEXT.md: D-13 compilation and attribution policy; D-14 substantive reader view with method detail collapsed; D-15 faithful passive archive derivatives with immutable originals; D-16 this authorized correction before 02-03, preserving phase progress and updating the existing report publication. Carry the same method into PROJECT, REQUIREMENTS explanations, README and the generated project block of AGENTS while preserving model preferences and workflow rules. In STATE replace current blocking assumptions with the new decision and retain dated historical context. Revise actual actions, must_haves, acceptance and threat-model clauses in remaining plans 02-03 through 02-10 and their shared party_delivery_contract; an appended note alone must not leave contradictory execution instructions. Replace domain/effectivity/authority proof and universal acceptance gates with source-attributed use; retain chronology, identity separation, accurate dates, order and archived evidence. D-01/D-02 remain the later party sequence; D-03/D-04 and D-05–D-12 remain with D-09 site semantics amended by D-13. Preserve completed 02-01/02-02 artifacts and Phase 1 history. Keep the phase at 2/10 and 02-03 unstarted.
  </action>
  <verify><automated>python3 tests/run.py --pattern test_source_policy.py</automated></verify>
  <done>The isolated real charter path passes every writer/export/publish/audit stage under an explicit source policy; news/social attribution and rejected misuse are covered; old policy still audits historical releases. Governing docs and all eight pending plans agree with the new dated decisions.</done>
</task>

<task type="auto" tdd="true">
  <name>2. Yeni Parti'nin gerçek belgelerini derle ve özgün görünümlü pasif arşiv kopyalarını bağla</name>
  <files>src/arsiv_gorunum.py, src/arsiv.py, src/dosyalar.py, tests/test_archive_views.py, tests/test_documents.py, tests/test_acceptance.py, data/dossiers/261111-epm-yeni-parti.json, data/objects/{new_sha256}/{new_source_files}, data/views/{view_id}/index.html, data/views/{view_id}/manifest.json, data/views/{view_id}/assets/{asset_sha256}.{extension}</files>
  <behavior>
    - Charter and program each open a separately identified offline page with their actual title, substantive text, layout and available images/styles; source markup is not the displayed document.
    - Page scripts, event handlers, forms, frames and embedded active documents cannot execute or submit; the view works without remote resource requests and arbitrary filesystem paths are unavailable.
    - Existing original and readable bytes remain byte-identical; derivative corruption is detected using its own manifest rather than changing the legacy readable_bytes algorithm.
    - Newly sourced content resolves the obsolete site/charter/program gaps with traceable resolution records; unresolved financing or historical questions remain attributed/unknown rather than becoming invented facts.
  </behavior>
  <action>
Per D-13/D-15 directly use https://yenipartiyiz.biz, /parti-tuzugu and /parti-programi as the party's publications. Reuse suitable original captures or capture fresh bytes with true access times. Read both complete documents and their PDF links as useful; select concise Turkish source-backed findings covering why founded and political identity, member rights/expression, election and oversight of leadership, principal program promises, and the charter's stated financing/spending rules. Separate these rules from actual financial results. Use existing archived reporting to make the “what has it done” section useful with explicit publisher/date attribution; keep allegations and announced totals attributed, and preserve distinctions such as preliminary member voting versus final congress election. Actual accounts, unknown periods or inaccessible sources may remain concise genuine gaps. Do not impose new comprehensive comparison or financial research work from Phases 3–5.

Create the reproducible records input data/dossiers/261111-epm-yeni-parti.json with consistent source/document/passage/finding links, black quoted exact excerpts and dark-blue summaries, the site field, publisher dates as stated by the documents, and source-type/author metadata. Preserve known legal identity and founding observations unless new actual evidence corrects them; never infer registry identifiers or historical effectivity from a site label. Resolve outdated domain/charter/program missing rows through the existing missing_resolution mechanism, using the new real passages and dated reason; retain original attempts/missing history. New appropriately classified document/version records may reuse original object bytes; do not rewrite past release snapshots or mislabel the old independent-copy record as previously verified. Source chronology and unknown document periods stay distinct from publication/access dates. Use dossier-load or the record API into a workspace; if dossier-check is needed, add a stage option retaining complete as its default so this pilot correction can be checked without pretending to complete a new party.

Implement versioned archive views in src/arsiv_gorunum.py, referenced by version through an additive archive_view record and a manifest recording source SHA-256, derivative format/version and every output/asset digest. Write new data/views/{view_id} directories; keep legacy objects/{sha}/readable.html and original files unchanged. Render static source HTML as a document, retaining safe layout, headings, inline CSS and available images/fonts with resource URLs rewritten to local archived assets. Fetch only the visible page resources needed for these documents with existing bounded capture behavior, safe http(s) URLs and explicit size/time limits. Remove active content and handlers, disable forms, strip frames/objects and unsafe URL schemes, and prevent CSS/resource fetches outside the local asset bundle. If visual fidelity cannot be achieved for a resource, preserve substantive reading and record the specific limitation; use the existing local Chrome print/snapshot capability when it improves the original appearance. Never settle for a page consisting of escaped markup.

Keep readable_bytes unchanged for legacy verification; validate the new derivative using archive_view metadata and its manifest. Expand the loopback server's narrow route allowlist only for actual view index/manifest/assets with safe_path, appropriate MIME and nosniff, and restrictive archive CSP disabling scripts, navigation bases, forms, frames and network connections. Put equivalent restrictions into archive HTML for static hosting/file viewing. Raw original.html.bin remains download-only. Add fixture attacks and real charter/program checks, including exact canonical/title pairing: b3709f… is charter, 58fa220… is program. Preserve original-source and PDF download links alongside the rendered page.
  </action>
  <verify><automated>python3 tests/run.py --pattern test_archive_views.py</automated></verify>
  <done>Both actual documents have useful linked findings and correctly paired rendered offline views; unchanged originals remain available. Obsolete document/site gaps have sourced resolutions, real gaps remain, and the local server cannot activate archived source code.</done>
</task>

<task type="auto" tdd="true">
  <name>3. Sade okuyucu raporunu yeni değişmez sürüm ve mevcut statik yayın akışıyla teslim et</name>
  <files>src/rapor.py, src/rapor_v11.css, src/arsiv.py, src/dosyalar.py, tests/test_report.py, tests/test_dossiers.py, tests/test_publication.py, tests/test_acceptance.py, tests/browser_probe.py, README.md, .planning/STATE.md, data/current.json, data/releases/{new_release_id}/records.sqlite3, data/releases/{new_release_id}/records.json, data/releases/{new_release_id}/index.html, data/releases/{new_release_id}/manifest.json; isolated gh-pages worktree: index.html, .nojekyll, releases/{new_release_id}/index.html and linked objects/views/assets</files>
  <behavior>
    - The initial Yeni Parti panel shows useful five-heading content and an official-site link; citations reveal author/publisher/date, the actual passage and both correct archive documents.
    - Method, attempts, rejected candidates, authority checks, review labels and superseded gaps remain available inside closed detail sections, without repeated workflow warnings in the normal reading path.
    - Keyboard tabs, source deep links/back focus, mobile reading and offline archive clicks work; excerpts remain quoted black and summaries dark blue.
    - The new release keeps TİP tracer/prefix state; previous releases, original objects and the two prior receipts still audit using their recorded versions.
  </behavior>
  <action>
Per D-03/D-05–D-09/D-14 build renderer 11 around the five reader questions using the new findings. Put the source-backed story and charter/program summaries in the normal reading flow, with concise contextual attribution such as “[yayın] haberine göre” and party statements clearly expressed as their statements. Render the sourced official_site as a usable hyperlink. Keep finding IDs, provenance data and citation navigation; remove repetitive technical classification badges from the reading prose and move their details, attempts, authority reviews, rejected candidates and old resolved gaps into closed source/method details. Unknown publication date should appear unobtrusively in source detail. Deduplicate repeated current gap messages and keep their actual reason accessible. Preserve D-03 tab order, Turkish labels, keyboard navigation, responsive reading, print semantics and quote/summary colors. Add src/rapor_v11.css rather than modifying CSS used by historical renderers. Prefer new archive_view links when available and retain ordinary legacy links for other sources. Keep all required finding/match data reachable even when details are collapsed.

Adjust tests that encode the superseded authority rule or pin the live renderer/schema to 10/4: retain historical-version fixtures and replace obsolete expectations with the new observable attribution/reader behavior. Do not weaken quote equality, FK/ownership, URL safety or corruption detection. Extend browser_probe using the already cached headless Chrome to check the live-source appearance against local rendered charter/program screenshots, source-link clicks through both documents, local assets/network independence, and keyboard/mobile behavior. Assert visibility through DOM state and detail ancestry rather than global negative string searches that also match historical method records.

Publish a new immutable local release from the validated workspace with publish --party tip --stage tracer; verify stage=tracer and completed_prefix=[] explicitly. Do not use stage complete, create a TİP completion receipt or mark 02-03 executed. Keep prior receipts valid. Run the relevant suites and full existing suite once after final changes, audit Phase 1 compatibility and the current Phase 2 tracer, and compare pre-task checksums of old releases/objects. Repair failures within this source-policy correction before pointer/publication handoff.

Per D-16 prepare the same static report/archive bundle used by the authorized 261110-pds publication, including every linked view, original, stylesheet/font/image asset and the root redirect. Inspect the existing repository remote and gh-pages tip immediately before writing; use an isolated worktree and a normal push preserving concurrent work and prior versioned report URLs. Publish the corrected reader artifact through that existing GitHub Pages workflow, without unsolicited messages or PRs. Check deployment status and open https://mertgkduman.github.io/proje/ and both public archived documents; compare served artifact digests and correct charter/program identity with local outputs. If network/auth prevents this step, preserve the complete audited local bundle and state the concrete publication blocker; do not report the old public site as updated. Record the new release/public URL, visible changes and any limited fidelity gaps in the quick summary and README. Update STATE quick-task activity/dated decision only: current phase 02, two completed plans, next 02-03, TİP not complete. Retain model preferences.
  </action>
  <verify><automated>python3 tests/run.py --pattern test_report.py</automated><human-check>Inspect the generated local and published report plus live/local charter/program screenshots at desktop and 360px; this is an executor check and introduces no per-source approval gate.</human-check></verify>
  <done>The current and public reader report show actual source-backed Yeni Parti content, useful attribution and correct passive archives. All meaningful regressions pass, old release bytes/audits and prior receipts remain valid, and phase progress still points to unstarted 02-03.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|---|---|
| External page → attributed records | A publisher's assertion must stay attributed and linked to archived text. |
| Source HTML/CSS/assets → local/public archive viewer | Untrusted active content must not execute, submit data or obtain local files. |
| Workspace → immutable release → existing public site | Data, renderer and archive paths must refer to the same checked version. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|---|---|---|---|---|---|
| T-epm-S | Spoofing | Source attribution | medium | mitigate | Retain publisher/author/handle/date/permalink and party relationship; distinguish reports, party statements and registry assertions. |
| T-epm-T | Tampering | Original/view/release files | high | mitigate | New versioned policy/view manifests, all file/asset hashes, existing FK/quote checks, old-byte regression and version-specific audits. |
| T-epm-E | Elevation of privilege | Archive HTML and local server | high | mitigate | Passive HTML, local-only assets, disabled active elements/handlers, CSP, nosniff and explicit safe-path routes; original HTML remains a download. |
| T-epm-D | Denial of service | Asset capture | medium | mitigate | Bounded resource count/bytes/time and no unrestricted recursive crawl. |
| T-epm-R | Repudiation | Superseding policy/content | low | mitigate | Dated user decision, linked resolutions, previous immutable snapshots and precise quick summary. |
</threat_model>

<verification>
Use the repository's existing Python runner; new focused tests run offline from archived material. After the three task-specific commands, run python3 tests/run.py once, python3 src/arsiv.py audit --release current --phase 1, python3 src/arsiv.py audit --release current --phase 2 --party tip --stage tracer, and receipt-check on data/deliveries/02-01-tip-tracer.json and data/deliveries/02-02-tip-sources.json. Audit the captured pre-task release and historical renderer 10 plus a Phase 1 release. Check old file checksums, new manifest policy/schema/view versions and exact empty completed_prefix. Validate changed phase plans with GSD frontmatter/structure validators. Browser verification must actually open both document URLs and inspect rendered reading text, assets, closed method details, source navigation and viewport overflow. Record the public publication outcome truthfully.
</verification>

<source_audit>
| Source | Scoped item | Tasks | Status |
|---|---|---|---|
| GOAL | User's method, actual Yeni Parti content, reader and archive correction before TİP | 1–3 | COVERED |
| REQ | DOS-01/DOS-02/KAY-01/KAY-04 correction within current pilot and pending party contracts | 1–3 | COVERED |
| REQ | KAY-02/KAY-03/MET-01–04/EKS-01–02/VER-01 regression, attribution and archive integrity | 1–3 | COVERED |
| REQ | RAP-01–03 affected reader/source-navigation behavior | 2–3 | COVERED |
| RESEARCH | Existing stdlib/SQLite patterns, HTML escaped-source defect, renderer/version coupling, local cached Chrome, archived charter/program and live publisher pages | 1–3 | COVERED |
| CONTEXT | D-01/D-02 sequence retained after explicit pilot correction; D-03/D-04 reader/order and delivery | 1, 3 | COVERED |
| CONTEXT | D-05–D-08 version/source display; D-09 official site under new sourcing policy; D-10–D-12 existing chronology and identity distinctions | 1–3 | COVERED |
| CONTEXT | Authorized 2026-11-11 superseding D-13–D-16 source policy, reader, archive and correction/publication | 1–3 | COVERED |

Remaining nine-party phase completion and detailed comparisons/financial research are outside this quick correction and retain their existing phase assignments. No deferred phase feature is introduced. No RESEARCH.md is required for this quick existing-stack correction; source-page inspection and concrete discovery observations are recorded above. This single three-task quick plan intentionally groups the user's cross-cutting correction and synchronized pending-plan amendments; it does not replace Phase 2's remaining execution plans.
</source_audit>

<success_criteria>
Source-attributed compilation works end-to-end, actual Yeni Parti content and official site are available, both correct documents open as safe readable archived pages, the public reader flow is substantive and concise, historical releases still audit, and TİP/phase progress is unchanged.
</success_criteria>

<output>
Create .planning/quick/261111-epm-kaynak-derleme-y-ntemini-sadele-tir-yeni/261111-epm-SUMMARY.md with code/data/doc commits, source/release/public URLs, checks performed and any concrete remaining archive-fidelity or publication limitation.
</output>
