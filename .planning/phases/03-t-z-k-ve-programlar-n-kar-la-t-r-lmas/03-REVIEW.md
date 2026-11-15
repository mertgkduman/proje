---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
reviewed: 2026-11-15T16:32:47Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - data/comparisons/03-acceptance.json
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
  - tests/test_comparisons.py
  - tests/test_completion_coverage.py
findings:
  critical: 3
  warning: 0
  info: 0
  total: 3
status: issues_found
---

# Phase 03: Code Review Report

**Depth:** standard  
**Scope:** incremental changes from `13dea851333e00328669549492284e9a97bd225c` to `2b4c50471c05528119139019c4bdd9050d3e0aca`; 13 files listed above. Large release data and HTML were inspected structurally and by IDs and hashes, rather than treated as new source prose. The predecessor review is preserved in `03-16-checks/pre16-review.md`; its previously closed findings are historical and were not reopened or all historical source re-reviewed here.

## Summary

The new completion proof is persisted in SQLite and exported JSON, and the actual manifest file hashes match. The selected snapshot contains 305 topics, 4,935 rows, 3,941 fields, 854 syntheses and 1,729 inventory entries; SQLite integrity and foreign-key checks passed. Source-review evidence actually records an authored 24-group agent reading and distinguishes direct, inherited and finding-only provenance. That reading is not human political acceptance. Three blocker defects remain in enforcement and forward updates. Two are demonstrated using read-only in-memory mutations of the actual selected release through existing validators. Tests and full project regression were not rerun in this review; previously recorded focused tests, audits and browser evidence are not a new global regression result. Eight raw probes and three descriptorless prohibitions remain unresolved; human UAT remains pending.

## Narrative Findings (AI reviewer)

### CR-01: BLOCKER — Completion compares coverage against an author-supplied copy, not required coverage

**File:** `src/arsiv.py:678` (also `src/arsiv.py:741`, `tests/test_completion_coverage.py:35`)  
**Issue:** The expected topic, row, field, synthesis and inventory lists are taken from the same submitted completion evidence and compared to the supplied records. Per-party counts are likewise checked only against those records. Neither establishes the required topic × party × applicable level/organ/field matrix independently. In a read-only probe against the actual selected release, removing the unsampled `04-03-v3-0304-tip-charter-scope-aday-tanitim-html-row` (TIP, `aday-tanitimi`, `ulusal ve yerel`, `Kamu adayı tanıtımı`), removing that row from the proof and decrementing TIP's proof row count makes `validate_comparisons(data)` return `True`. Thus the gate can certify a snapshot with a missing substantive level/organ while both lists agree. Descent separately protects records already in a base; it cannot establish a record that was omitted before a first completion proof or from newly authored coverage. Existing negative tests modify data while leaving the copied proof untouched, so they do not detect this failure.

**Fix:** Derive required coverage from independent, versioned topic applicability, source inventory and documented level/organ/field dispositions, including explicit sourced inapplicability and genuine document gaps. Candidate inputs include `comparison_topic.applicable_levels` (`src/arsiv.py:113`), the independent source inventory and scope records (`src/arsiv.py:116`, `src/arsiv.py:122`), and the authored audit basis in `03-16-precheck/coverage-map.json`; these inputs need a defined, sourced matrix, not invented coverage. Check actual records against that matrix. Add negative tests that modify both the data and submitted proof, including omitted levels, organs, fields and inventory sections, through `validate_comparisons`, `load_comparison`, `publish_release` and audit. Introduce the stronger contract additively; retain accepted v1 historical interpretation rather than retroactively requiring future proof from it.

### CR-02: BLOCKER — A source-meaning review can omit all reviewed fields and syntheses

**File:** `src/arsiv.py:715` (also `src/arsiv.py:722` and `src/arsiv.py:729`)  
**Issue:** `selected_rows`, each row's `fields`, and `inspected_synthesis` default to empty lists. The only enforced sampling coverage is that some selected row names each party. A read-only probe retained one actual row per party in eight of the existing checks, removed all inspected fields and syntheses, and `validate_completion(data)` returned `True`. Nonempty free-text rationale and unchanged source hashes then stand in for the specific source→summary and multi-party synthesis judgments the plan requires. Previous field/finding review records do not establish that this second-reading sample covered the planned source types, levels, conditions or synthesis evidence. This does not assert that the actual current 24-group reading was fabricated; its documented substantive evidence exists, but the gate accepts a materially incomplete replacement proof before adoption.

**Fix:** Require explicit, cross-linked substantive decisions and actual inspected field/finding/passage and synthesis IDs appropriate to the recorded risk coverage, with verifiable links to the claimed versions and source roles. Record structured coverage of the applicable level/organ, source-type, condition and synthesis categories and a rationale for the selection; do not enforce an arbitrary fixed sample quota. Add a regression that removes all sampled fields and syntheses while retaining one row per party and valid prior reviews; exercise `validate_completion`, `validate_comparisons` and the real `load_comparison`/comparison-check path. Preserve the actual v1 proof and its historical interpretation.

### CR-03: BLOCKER — The adopted marker freezes all future selected records without a revision path

**File:** `src/arsiv.py:685` (also `src/arsiv.py:123`, `src/arsiv.py:662`, `src/arsiv.py:957`)  
**Issue:** The selected proof must equal *all* current rows, fields, syntheses and inventory for its taxonomy, but descent requires the old marker and its evidence to remain byte-for-byte unchanged. SQLite permits only one version-1 marker per taxonomy and rejects other marker versions. After the current release adopts its marker, adding a legitimate new sourced row, field, synthesis or inventory entry to taxonomy 4 makes the original proof mismatch; replacing the proof violates descent and a second same-version marker violates the primary key. Consequently ordinary corrections or newly discovered source evidence cannot be published under that taxonomy without creating an unrelated taxonomy revision. In addition, any retained marker is rejected for a partial stage, and the existing descent stage rule also prevents a complete base from progressing to a partial candidate. This conflates historical proof preservation with the current completion state and obstructs incremental forward work.

**Fix:** Preserve historical proofs as immutable, revisioned snapshots, bind the active completion decision to a new revision or release, and validate preserved records separately from newly added records. Permit a legitimately sourced same-taxonomy addition and new completion revision without inventing a taxonomy change. Define supported partial/new-taxonomy/supersession transitions so the old marker remains immutable without asserting that an unfinished new selection is complete. Exercise the actual APIs `load_comparison`, `export_db`, `publish_release`, `audit_release` and `validate_comparison_descent` for a sourced addition and a partial-to-complete forward transition from the marked release; verify that modifying or removing old proof still fails.

---

_Reviewer: gsd-code-reviewer_  
_Depth: standard_
