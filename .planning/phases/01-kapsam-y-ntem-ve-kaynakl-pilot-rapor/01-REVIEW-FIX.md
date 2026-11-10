---
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
fixed_at: 2026-11-10T17:10:50Z
review_path: .planning/phases/01-kapsam-y-ntem-ve-kaynakl-pilot-rapor/01-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 7
skipped: 1
status: partial
---

# Phase 1: Code Review Fix Report

Seven findings are fixed; CR-01 has a narrower mitigation but remains open for independent source review. All logic changes require human verification of the evidence semantics.

## Fixed issues

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

## Partially addressed issue

### CR-01: Identity source and registry binding

**Commits:** `746793e`, `90e49b2`. The writer and strict phase export check source ownership, official registry host and identifier, source name and dates; tests reject a different party's passage and altered date. For compatibility, exactly one existing crosswalk maps TİP's TBMM key to Yargıtay 208. This is an agent-assessed assumption, not a human-approved or independently source-linked crosswalk. General identity and date semantics cannot be established merely from text occurrence. The crosswalk and validity interpretation require independent human source review; therefore this finding is not claimed fully resolved.

## Verification

Targeted regressions and the full Python suite ran in the main checkout: 42 tests passed. `audit --release current --phase 1` returned `PHASE1_AUDIT_OK ce36c63ae9e44e50bb36b440aa4ada2b`. Historical renderers remain available. Source accuracy, political neutrality, the TİP crosswalk and the financial semantics still require human review.

_Fixer: gsd-code-fixer; iteration 1_
