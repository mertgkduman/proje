---
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
reviewed: 2026-11-10T17:18:09Z
depth: standard
files_reviewed: 23
files_reviewed_list:
  - README.md
  - src/arsiv.py
  - src/rapor.py
  - src/rapor_legacy.py
  - src/rapor_v2.py
  - src/rapor_v3.py
  - src/rapor_v4.py
  - tests/browser_probe.py
  - tests/chain_red_gate.cjs
  - tests/missing_red_gate.cjs
  - tests/run.py
  - tests/test_acceptance.py
  - tests/test_chain.py
  - tests/test_dates.py
  - tests/test_documents.py
  - tests/test_finance.py
  - tests/test_matches.py
  - tests/test_missing.py
  - tests/test_publication.py
  - tests/test_report.py
  - tests/test_scope.py
  - tests/test_topics.py
  - tests/test_tracer.py
findings:
  critical: 2
  warning: 0
  info: 0
  total: 2
status: issues_found
---

# Phase 1: Code Re-review Report

**Reviewed:** 2026-11-10T17:18:09Z  
**Depth:** standard  
**Files Reviewed:** 23  
**Status:** issues_found

## Summary

Re-reviewed the original scope and the fixes through `0fd27e1`, including the new frozen renderer and release compatibility. The eight original reproductions are addressed in the changed code. Two affected-path correctness defects remain: an unchanged source capture wrongly reopens research, and Turkish-formatted amounts can be converted by a factor of 1,000. Both were reproduced using isolated copies. The current release has no financial rows; the monetary example concerns future input. Twenty-nine relevant tests passed independently. Human assessment of source meaning, the TİP identifier relationship, neutrality, and interface presentation remains outstanding and is not represented as approved.

## Narrative Findings (AI reviewer)

### CR-01: Re-capturing unchanged bytes falsely reopens closed research

**Classification:** BLOCKER  
**File:** `src/arsiv.py:325-331`  
**Issue:** The CR-02 fix correctly preserves a separate version for each capture, but every version insertion matching a closed lead now unconditionally records a reopening reason of “new content version” and changes the topic to `in_progress`, without comparing hashes. In an isolated copy of the current release, inserting a second version of `tip-charter-v1` with the same URL and SHA-256 changed the `organ-secimi` topic from `closed` to `in_progress`. Routine re-capture of unchanged documents thus fabricates a content change and makes a completed research chain appear incomplete.

**Fix:** Retain the separate capture and document ownership, but compare the captured hash with the previous version associated with that lead before recording a content-change reopening. Reopen when the content actually changes, and keep a distinct rule for a genuinely new lead. Test identical and changed bytes at the same closed lead, including the stored reopening reason.

### CR-02: Turkish thousands separators are read as decimal points

**Classification:** BLOCKER  
**File:** `src/arsiv.py:601-607`  
**Issue:** `numeric()` removes dots only if a comma is also present. Therefore the conventional Turkish amount `1.000 TL` is parsed as `Decimal('1.000')` rather than 1,000 lira. Using the isolated finance fixture with a passage containing `gelir 1.000 TL`, `check_financial` accepted amount `1` and rejected `1000`. This can publish a sourced financial amount at one thousandth of its value. The existing date/category regressions do not exercise this numeric format.

**Fix:** Parse the source's declared number format explicitly, treating Turkish grouping and decimal separators consistently, or require an unambiguous reviewed structured transcription when the notation is ambiguous. Verify both `1.000 TL` → `1000` and `1.000,50 TL` → `1000.50`, as well as decimal and grouping edge cases; retain human review for what the amount means.

## Status of previous findings

- **Original CR-01, identity:** Resolved for the reported wrong-party/key cases by registry host/path/key and document-party checks in `check_identity`, applied to new publication. The former TİP-specific exception was removed; its canonical key and historical parliamentary identifier are retained separately. Earlier immutable releases explicitly use legacy compatibility. These technical checks do not decide the substance of the cross-source identity assessment.
- **Original CR-02, ownership:** Separate version rows retain document/party ownership even with shared bytes; the CLI returns the ID. The resulting changed-content regression is CR-01 above.
- **Original CR-03, examined source:** Access attempts, closure, and phase validation bind the examined version to the lead's party and captured original/final URL, without treating legacy hash aliases as redirect evidence.
- **Original CR-04, unrelated numbers:** The originally reported date and unrelated-category reproductions are rejected, and a review plus adjacent amount/currency expression is required. Numeric-format correctness remains open as CR-02 above; semantic review is separate.
- **Original CR-05, publication gate:** Phase-capable bases and snapshots containing a method undergo staged acceptance and HTML checks before `current` changes; the missing-review and removed-method tests pass.
- **Original CR-06, candidate resolution:** The documented `resolve-candidate` CLI routes to the atomic transition, with a CLI-path regression for history and failure.
- **Original WR-01, provenance display:** Match rendering now applies each finding's quote or summary style. Version 5 was frozen byte-for-byte from the former renderer and new releases use version 6.
- **Original WR-02, PDF libraries:** README documents native dependencies and the loader reports missing libraries; a mocked missing-library test passes.

## Threat-control evidence and limits

These are implementation observations for the orchestrator's ASVS1 review, not a security certification or human-source approval.

| Plan threat IDs | Relevant evidence and remaining limits |
|---|---|
| T-01-01, T-01-04, T-06-01, T-06-03 | `safe_url`/`safe_path` at `src/arsiv.py:93-105`, escaped readable bytes at `:108-110`, report escaping and URL checks at `src/rapor.py:6-12`, and loopback allowlisted serving at `src/arsiv.py:965-983`; negative URL/path tests are in `tests/test_publication.py` and `tests/test_report.py`. |
| T-01-02, T-06-02 | Integrity, FK, object and derivative checks at `src/arsiv.py:701-737`; staged acceptance and pointer swap at `:867-907`; failure and acceptance tests in `tests/test_publication.py`. The HTML acceptance function at `:850-856` checks presence of IDs, not complete HTML/data semantic equivalence. |
| T-01-03 | Capture timeout and source-size cap at `src/arsiv.py:185-196`; review did not independently exercise all network failure modes. |
| T-02-01, T-02-02, T-02-03 | Identity checks at `src/arsiv.py:113-130`, frozen cutoff and source hash at `:674-694`, and scope/date regressions in `tests/test_scope.py` and `tests/test_dates.py`. Strict identity is applied to new publications; old manifests retain documented legacy identity behavior. Human validation of registry semantics remains open. |
| T-03-01, T-03-02, T-03-03 | Lead normalization, attempt and source binding at `src/arsiv.py:339-410`, closure at `:550-564`, missing-attempt checks at `:630-638`, and version/object checks at `:701-737`. CR-01 demonstrates an incorrect reopening claim after an unchanged capture. |
| T-04-01, T-04-02, T-04-03 | Authority checks at `src/arsiv.py:415-426`, evidence checks at `:542-547`, exact-passage/hash checks and topic-basis validation at `:729-765`; wrong-party and topic tests cover selected negative cases. Manual source meaning is not established by these checks. |
| T-05-01, T-05-02, T-05-03 | Actor and distinct occurrence evidence checks at `src/arsiv.py:440-477`, candidate-set checks at `:766-773`, financial checks at `:577-607`, and matching/finance tests. CR-02 leaves financial numerical attribution unsafe for Turkish grouping. |

---

_Reviewed: 2026-11-10T17:18:09Z_  
_Reviewer: the agent (gsd-code-reviewer)_  
_Depth: standard_
