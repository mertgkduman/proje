---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
reviewed: 2026-11-15T19:14:58Z
depth: standard
files_reviewed: 24
files_reviewed_list:
  - data/comparisons/03-acceptance.json
  - data/comparisons/03-completion-basis-v2-source.json
  - data/comparisons/03-completion-review-v2.json
  - data/comparisons/03-completion-risk-v2-source.json
  - data/comparisons/03-navigation-checks.json
  - data/comparisons/03-probe-record.json
  - data/comparisons/03-source-review-notes.md
  - data/comparisons/03-source-review.json
  - data/current.json
  - data/releases/85b1a453ce2346a8ad0df325a2b73ae9/index.html
  - data/releases/85b1a453ce2346a8ad0df325a2b73ae9/manifest.json
  - data/releases/85b1a453ce2346a8ad0df325a2b73ae9/records.json
  - data/releases/85b1a453ce2346a8ad0df325a2b73ae9/records.sqlite3
  - src/arsiv.py
  - src/rapor.py
  - src/rapor_v22.py
  - tests/fixtures/completion_revision_correction.json
  - tests/fixtures/completion_revision_source.json
  - tests/fixtures/completion_revision_supersession.json
  - tests/fixtures/completion_sr25_correction.json
  - tests/fixtures/completion_sr25_reading.json
  - tests/fixtures/completion_sr25_replacement.json
  - tests/test_comparisons.py
  - tests/test_completion_coverage.py
findings:
  critical: 2
  warning: 0
  info: 0
  total: 2
status: issues_found
---

# Phase 03: Completion v2 Second Re-review

**Depth:** standard  
**Scope:** the 24-file union at source checkpoint `2bb29b503d43af49b0195a50f8ce759dc0860831`, root metadata HEAD `8cc945e805988039cfa58fcc419d7425d2ecaae4`, compared with prior review commit `8ac0513`. The earlier reviews are preserved in Git at `959c692` and `8ac0513`. Large data, HTML and SQLite artifacts were inspected structurally and by actual identifiers and hashes; this is not a fresh review of every historical source page.

## Summary

The three prior probes were repeated against the regenerated committed adoption package: the forged 95-field review and unrelated positive/negative supersession were rejected by the shared revision validator, while the same authentic SR25 reading under a new local ID was accepted. The prior unmodified witness-ID case is therefore closed at that validator boundary; the actual new-taxonomy transition and latest-code isolated import/publish/audit remain unverified. The fix also authenticates the initial reading registry, preserves original source bodies, and requires source-registered old/new correction contexts. The two remaining blockers below affect dependent syntheses and a genuine future source-discovery transition.

All 24 supplied scope hashes matched. No broad tests, audits, publication or global suite were rerun in this review. The recorded earlier `554db20` isolated round trip is historical evidence for older copied inputs, not a latest-code result. Accepted current release `85b1a453ce2346a8ad0df325a2b73ae9` remains v1 and renderer 22. No production correction or new document discovery is asserted. Eight raw probes and three descriptorless prohibitions remain unresolved; all three UAT groups and three value assessments await human responses.

## Narrative Findings (AI reviewer)

### CR-01: BLOCKER — A retained synthesis can depend on a superseded row hidden from the active view

**File:** `src/arsiv.py:1963` (also `src/arsiv.py:952`, `src/arsiv.py:1282`, `src/arsiv.py:2687`, `tests/test_completion_coverage.py:303`)  
**Issue:** Synthesis validation uses all historical rows rather than the active revision's selection. The committed SR25 replacement fixture selects a new row and removes `04-03-v3-0304-tip-program-kapitalizm-row` from the visible selection, and its documented test passes `validate_comparisons`. The actual retained synthesis `04-0314-policy-more-kapitalizm-bunalim-1` still names the removed row as TİP's positive side. In a read-only probe on the accepted data, `validate_synthesis_v2(full_data, synthesis)` returned `True`; applying the fixture's corresponding old-row/field removal to the active projection made the same API reject it with `Sentez tarafı konu ve partiyle uyuşmalı`. The active renderer still includes the old synthesis while hiding its referenced row. For a correction that changes substance, a stale claim can therefore remain visible without its active support. Conversely, the same-taxonomy basis requires the original synthesis and review unchanged and has no explicit synthesis replacement path, so the author cannot retire or correct that dependent claim while preserving history.

**Fix:** Validate each active synthesis's typed sides and evidence against the active row/field projection, while separately validating historical syntheses against their own immutable revision selections. Add source-authenticated synthesis supersession or equivalent explicit re-review and selection binding so dependent claims can be updated when a row changes. Exercise the actual SR25 fixture with both shared validators and rendered active output, plus a substantive correction that requires a replacement synthesis; preserve old claim, old review and old release unchanged.

### CR-02: BLOCKER — A discovered document cannot close a gap with a bounded negative search

**File:** `src/arsiv.py:1474` (also `src/arsiv.py:1478`, `src/arsiv.py:1482`, `src/arsiv.py:1487`)  
**Issue:** When an existing `document_missing` cell is replaced by `no_explicit_statement` after the real document is found and reviewed, neither cell has a supported field. This branch chooses the old missing cell as `evidence_context`, so `supported` is empty, but requires a nonempty `scope_reassessment.passage_ids` list to be a subset of it. The condition is impossible regardless of the genuine document, complete dated search boundary or independently authored correction. A bounded read-only `completion_superseded_cells` probe used actual outstanding Yeni Yol program gap `cell-449637ae7f0609816815667d` and a clearly labelled hypothetical future document/scope/correction fixture; it rejected the transition with `Farklı kaynak durumu için aynı kapsamın kaynaklı yeniden değerlendirilmesi gerekli`. This does not claim that a new Yeni Yol document exists. It demonstrates that, when one is found, even a truthful bounded absence cannot be published as its successor.

**Fix:** Handle missing-to-reviewed-negative as its own transition. Require the previously genuine missing/attempt chain, the newly acquired document and its actual source attribution, an independently authored correction and complete dated negative scope tied to that document and query; validate any supporting scope evidence directly against that new source instead of requiring a positive field. Preserve the old gap and proof. Add a test with a clearly labelled real-source-based fixture for missing→negative and a negative case for a wrong party, document, or incomplete scope; run it through import, partial/complete revisions and audit.

---

_Reviewer: gsd-code-reviewer_  
_Depth: standard_
