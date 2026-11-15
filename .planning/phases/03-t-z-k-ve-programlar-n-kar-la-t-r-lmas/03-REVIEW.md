---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
reviewed: 2026-11-15T18:25:01Z
depth: standard
files_reviewed: 20
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
  - tests/fixtures/completion_revision_source.json
  - tests/fixtures/completion_revision_supersession.json
  - tests/test_comparisons.py
  - tests/test_completion_coverage.py
findings:
  critical: 3
  warning: 0
  info: 0
  total: 3
status: issues_found
---

# Phase 03: Completion v2 Re-review

**Depth:** standard  
**Scope:** union of the prior 13 files and the v2 fix delta, at source checkpoint `192f43f2e82d88e22b8dcff38bfc23fa02ebe68c`; root metadata HEAD `d9d0bf3a368cbaa799812582b8947bb624aa4db2`. Large data, SQLite and HTML artifacts were checked structurally, by IDs and hashes; this is not a fresh review of all historic source pages. The prior three-blocker review is preserved at Git commit `959c692`; `03-REVIEW-FIX.md` accurately leaves its findings pending. The defects below concern the new v2 implementation and do not alter that history.

## Summary

The actual committed adoption package contains the independently authored basis and risk universe: 2,745 topic/party dispositions, 4,935 cells, 4,838 assertions, 854 synthesis obligations, 49 risks and 158 decisions. All 66 referenced source-package digests matched. The committed decisions and risk universe match their authored input. The accepted `85b1a453ce2346a8ad0df325a2b73ae9` release remains v1; the documented real second reading is agent work, not human approval. Nevertheless, v2 still allows unauthenticated decisions and unjustified supersessions, and its fixed witness IDs block valid forward reviews.

Probes below used in-memory copies of the actual committed package and accepted release data through existing validator APIs; they changed no source or data files. No tests, audit, publication or global suite were rerun. The latest-code isolated import/publish/audit path and actual new-taxonomy transition remain unverified. The earlier isolated run uses older copied inputs and was not disturbed. Eight raw probes and three descriptorless prohibitions remain unresolved; the three UAT groups and three value assessments remain pending.

## Narrative Findings (AI reviewer)

### CR-01: BLOCKER — Existing unrelated source cells can be presented as a correction and hide an obligation

**File:** `src/arsiv.py:1240` (also `src/arsiv.py:1253`, `src/arsiv.py:1364`, `src/arsiv.py:2417`)  
**Issue:** Supersession verifies only that the old and new cells share topic, party and role, that the old row was selected, and that the cited IDs belong to the new cell. It never verifies a separately authored correction linking those particular old and new contexts, nor that the new context actually supersedes the old one. I built an epoch 2 in memory from the committed canonical package, preserved its basis and prior revision, and claimed that existing positive row `04-03-v3-0304-tip-charter-context-aday-tanitim-html-row` replaced distinct negative-scope row `04-03-v3-0304-tip-charter-scope-aday-tanitim-html-row`. The link cited the positive cell's existing `basis-8a236988dbbb141d12717df4`; the new selection omitted the negative row. `validate_completion_revisions(data)` returned `True`. The selected view removes the old row, although its separate dated finding that the introduction procedure was not explicit is not corrected by the positive candidate-selection context. This defeats the independent coverage remedy by authorizing a material omission using an unrelated existing source.

**Fix:** Require an independently authored, immutable, source-resolved correction decision tying both exact old and new cells/rows to their source scopes, meaning, evidence and reason. Reject a pre-existing unrelated cell as a replacement solely because its own evidence is valid. Keep documentary absence separate from positive context and preserve D-13–D-16 uncertainty. Preserve the old record and revision, and allow active omission only after validating the explicit correction relation. Add this exact positive-versus-negative actual-ID case through `validate_completion_revisions`, `load_comparison` and the real publish/audit path; also verify the old obligation remains visible when no valid correction exists.

### CR-02: BLOCKER — Risk witnesses accept forged source-reading provenance and unsupported decisions

**File:** `src/arsiv.py:966` (also `src/arsiv.py:991`, `src/arsiv.py:1367`)  
**Issue:** A field witness only requires nonempty `judgment`, `recorded_at` and `source_reading`, and accepts any truthy `original_field_review`; it never checks the `decision` value, timestamp validity, or whether the alleged original review is the authored review for that field. In a read-only probe with the committed actual package and accepted data, I replaced all 95 field decisions' `original_field_review` with `{'forged':'yes'}`, set their judgment, reading and recorded time to `x`, and set their decision to `unsupported`. Existing IDs, basis IDs and source links stayed intact. Both `validate_source_risk_review` and the complete `validate_completion_revisions` returned `True`. Actual source decisions in the committed package are substantive; the problem is that altered or fabricated decisions can be adopted and frozen while the validator reports risk coverage.

**Fix:** Bind inherited decisions, result, time, reading and original-review lineage to independently registered authored source-research evidence; for genuinely new readings allow new immutable authored review records and revisions with valid source links, appropriate supported/limited result, timezone-aware date and a specific rationale. Verify field/finding/passage links and applicable risk constraints without assuming that nonempty text or a source hash proves meaning. Persist enough source and review content for later closed audits without mutable external JSON. Add actual-package negative cases for forged review bodies, invalid dates/results and stripped context, including the shared revision gate and importer.

### CR-03: BLOCKER — Fixed witness identities prevent new reviewed corrections

**File:** `src/arsiv.py:1025` (also `src/arsiv.py:970`, `src/arsiv.py:985`, `src/arsiv.py:1354`)  
**Issue:** Each immutable risk searches only its predeclared `witness_decision_ids`, cell IDs and assertion IDs; successors cannot change those risk entries. The actual `field:principle` risk lists only `SR25:field:tip-kapitalizm-principle`, one cell and one assertion, even though its `additional_eligible_witness_policy` explicitly permits a newly authored source-linked witness. As a bounded probe on the committed package, I retained the exact same substantive decision but gave it a new immutable ID and removed the old ID from the proposed current decisions. `validate_source_risk_review` rejected it with `Kaynak anlamı riski için maddi inceleme eksik: field:principle`. A real supersession of that sampled row or a changed-taxonomy migration needs a new active row/field/decision, yet the old ID and old cell remain the only eligible proof. Historical complete revisions can retain the old decision, but the active revision cannot satisfy the risk with its new source-linked witness.

**Fix:** Keep the original risk class and historic decisions immutable, while treating listed witness IDs as examples and allowing each later revision to supply new independently authenticated witnesses evaluated against typed applicability and source/lineage constraints instead of a frozen list of decision and cell IDs. Verify a real replacement of the SR25-sampled context and a source-backed new-taxonomy transition, preserving and revalidating the old revision. Include a negative case showing an unrelated witness is rejected; do not solve this by accepting arbitrary IDs or dropping the risk.

---

_Reviewer: gsd-code-reviewer_  
_Depth: standard_
