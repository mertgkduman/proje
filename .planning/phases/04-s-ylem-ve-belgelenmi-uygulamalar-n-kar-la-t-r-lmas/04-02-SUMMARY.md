---
phase: 04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas
plan: "02"
subsystem: practice-evidence-and-reporting
tags: [practice, evidence, comparison, source-provenance]
requires:
  - phase: 04-01
    provides: source-backed schema-7 practice tracer and frozen renderer 25
provides:
  - Chronological multi-event relationships and scoped unmatched-statement states in both views
  - Versioned evidence assessments, disputes, replies, actor periods and sourced position changes
affects: [04-03, practice-packages, report-rendering]
tech-stack:
  added: []
  patterns: [versioned optional snapshot extensions, scoped evidence, immutable historical renderer]
key-files:
  created: [src/rapor_v25.css, src/rapor_v26.py, tests/test_practice_content.py, tests/test_practice_contract.py]
  modified: [src/arsiv.py, src/uygulamalar.py, src/rapor.py, tests/test_comparisons.py]
key-decisions:
  - Preserve the version-1 variant table set; bind the additional evidence tables with a separate marker and manifest digest.
  - Represent occurrence basis and actor periods with structured metadata linked to the existing event, finding and passage records.
  - Keep unknown event dates visible and explicitly mark actor-period overlap as unverified.
patterns-established:
  - A supported result requires a result-stage passage; an initiative cannot supply it.
  - A source attributed to another party requires an explicit passage-scoped sharing record.
requirements-completed: []
actuals:
  tokens: 34843
  tasks: 2
  commits: 7
plan_head_before: 62c7bfcca71b4de7d059e76178dc898f1cc9f30d
completed: 2026-11-18
status: complete
---

# Phase 04 Plan 02: Practice evidence and comparison Summary

**Chronological practice cards now connect sourced stages, disputes, individual contributions and dated position changes in both report views.**

## Accomplishments

- Grouped all eligible events under their statements and retained shared-event, Faz 3 and original-passage links; genuine unmatched search states remain distinct.
- Added canonical dispute, dispute evidence and position-change records, with typed occurrence assessment and actor-period metadata. Separate source, stage, date and ownership checks run through load and snapshot export.
- Rendered target and documented result first, followed by evidence stages, contribution limits and open dispute points. Relevant replies and source details remain available without inferring an absent reply or motive.
- Preserved existing variant snapshot shape and immutable renderers; no synthetic test fixture was added to the research archive.

## Task Commits

- `f5ca16a`, `ed438a6`: Task 1 RED tests; `5f9bbc8`: Task 1 implementation.
- `3389541`, `85f1578`: Task 1 continuation records.
- `dde753c`: Task 2 RED tests; `7c7bc6a`: Task 2 implementation and related regression adjustments.

## Verification

- Task 1 acceptance: `test_practice_content.py`, 3/3, exit 0 (112.408s); postcommit tracer feedback 3/3, exit 0 (143.673s). Real-source `test_practice_tracer.py` 5/5, exit 0 (217.315s).
- Task 2: `test_practice_contract.py`, 4/4, exit 0 (184.760s), including temporary database load/export, both views, independent-news assessment and rejected repetition, stage, source, temporal and actor cases. RED evidence was checked as `RED_EVIDENCE_OK`.
- Shared regression: `test_practice_content.py`, 3/3, exit 0 (249.957s); `test_comparison_content.py`, 29/29, exit 0 (285.790s). The final styling-only change was checked by focused dispute-render and date regressions, 2/2, exit 0; the active CSS and frozen stylesheet test also passed.
- Original schema-6 and schema-7 stored JSON bytes were reproduced during Task 1. Current remains `f67ca0a35e634035bf3aa83a46571f50`.
- Frozen SHA-256: renderer 24 `adbc002bc4b2c39077ba9e908c01bc56e5133f896d66c9636a0d84682f6d053b`; renderer 25 `dedd4a8bfca3490affe655dc8834bb758813f150760ac4a704b127b5051fb7a6`; renderer 26 `ef011f57067d5b1f1ce42b849588ee6ee9b6dc2a5c14be507079db4eddfc73e8`; CSS 24 `a0fdab5efdad55631771818a70890287b42b13ffbb67782e7c04cb7a48a845de`.

## Deviations from Plan

- **[Rule 3 — compatibility]** Extended `src/arsiv.py` to include and audit the additional marked tables, retain extension-only findings in comparison projections, and reject missing markers. Changing the original version-1 table set would have changed existing snapshot serialization.
- **[Rule 1 — regression]** Updated the active CSS assertion in `tests/test_comparisons.py` to the new stylesheet while retaining frozen-asset checks. Generalized a legacy event note that otherwise mentioned a congress in unrelated events.
- Structured basis and actor-period records add machine-checkable provenance metadata without creating a second free-text store. They record the supplied assessment; semantic accuracy still depends on examining the linked sources.

## Scope and limitations

This plan supplies the implementation and synthetic acceptance fixtures. It does not complete phase-wide political research or constitute human acceptance. The wider phase regression remains with the orchestrator.

## Self-Check: PASSED

Created files and listed task commits were verified on disk; all cited command results have explicit exit codes. No new network endpoint or external publication was introduced.
