---
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
fixed_at: 2026-11-10T17:21:06Z
review_path: .planning/phases/01-kapsam-y-ntem-ve-kaynakl-pilot-rapor/01-REVIEW.md
iteration: 2
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 1: Code Review Fix Report

Both findings from the second review are addressed. Logic changes and the material interpretation of sources still require human review.

## Iteration 2 fixes

### CR-01: Re-capturing unchanged bytes

**Commit:** `3df7994`. A capture remains distinct, but a closed lead is reopened only if its party's latest prior capture for that address has different bytes; a first capture has a distinct reopening reason. Tests verify the same-hash capture remains closed and a changed hash reopens with the recorded content-change reason. **Status:** fixed, requires human verification.

### CR-02: Turkish monetary separators

**Commit:** `5d159b8`. Known financial amounts now require a stored source `number_format` (`tr` or `canonical`); Turkish grouping and comma decimals and canonical decimals are parsed according to that explicit choice. Ambiguous notation without a format and malformed grouping are rejected. Tests cover `1.000`, `1.234,56`, `1.000,50`, decimal notation, and the alternate meaning of `1.000`. A new nullable column is added only to newly opened authoring workspaces; immutable snapshots are unchanged. The format and the material meaning still need review. **Status:** fixed, requires human verification.

## Iteration 1 fixes (historical)

### CR-02: Shared source bytes retain document ownership

**Commit:** `7d4a151`. Versions remain separate by document and party while source bytes can be shared; the CLI prints the created ID. Regression: identical bytes across parties.

### CR-03: Examined lead source binding

**Commits:** `215293d`, `59168cf`. Capture URLs and party must match at access, closure and phase validation. Historical hash-dedup aliases are not trusted as redirect evidence. Regression: unrelated source rejected. **Status:** fixed, requires human verification.

### CR-04: Financial expression validation

**Commits:** `0540869`, `8742e2e`. A reviewed financial record requires its category in the same clause as the amount and adjacent currency; tests reject dates, unrelated categories and preserve zero versus unknown. These checks do not establish material meaning. **Status:** fixed, requires human verification.

### CR-05: Staged phase acceptance

**Commits:** `3ac52c8`, `c4a2f7a`. Phase acceptance runs against staged database and HTML before the pointer moves; a phase-capable base cannot bypass it by removing its method. Older in-progress bases remain usable. **Status:** fixed, requires human verification.

### CR-06: Candidate transition CLI

**Commit:** `5e602bf`. The documented `resolve-candidate` command calls the atomic writer; CLI-path tests cover rollback and history. **Status:** fixed, requires human verification.

### WR-01: Match quote provenance

**Commits:** `5130ec4`, `a5ec500`. Both match findings retain quote/summary styling. Renderer 5 is frozen and renderer 6 handles new releases; tests cover mixed provenance. Local release `ce36c63ae9e44e50bb36b440aa4ada2b` contains renderer 6; the prior release is retained.

### WR-02: PDF dependencies

**Commit:** `d52ba20`. README documents Poppler-glib, GLib, GObject and Cairo runtime requirements; missing libraries produce an actionable diagnostic, tested with a mocked missing library.

### CR-01: Identity source and registry binding

**Commits:** `746793e`, `90e49b2`, `0fd27e1`. TİP's canonical legal key is now `yargitay-208`, matching its archived registry URL; the stable party ID and approved scope remain intact. The old parliamentary identifier is preserved in `tip-tbmm-identifier` and the agent review record `tip-identifier-migration`, referring to the archived TBMM passage and `tip-registry-name`. The party-specific exception was removed. The writer and strict phase export check ownership, registry host and exact identifier, name and dates; regressions reject another party's passage, a wrong registry URL and an altered date. The source relationship is an agent assessment, not human approval; identity and date semantics require independent human review. Old immutable manifests use documented legacy audit compatibility, while new publications always enforce strict identity checks. **Status:** fixed, requires human verification.

## Verification

Targeted regressions and the iteration 2 full Python suite ran in the main checkout: 44 tests passed. `audit --release current --phase 1` returned `PHASE1_AUDIT_OK 6fd06aa1a6c643ed99b2b1c95f32822d`; the current snapshot and older releases remain unchanged. Historical renderers remain available. Source accuracy, political neutrality, the TİP identifier relationship and financial semantics still require human review.

_Fixer: gsd-code-fixer; iteration 2_
