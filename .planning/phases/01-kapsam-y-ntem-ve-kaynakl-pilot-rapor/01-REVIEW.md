---
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
reviewed: 2026-11-10T17:01:40Z
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
  critical: 6
  warning: 2
  info: 0
  total: 8
status: issues_found
---

# Phase 1: Code Review Report

**Reviewed:** 2026-11-10T17:01:40Z  
**Depth:** standard  
**Files Reviewed:** 23  
**Status:** issues_found

## Summary

The scoped Python archive, frozen and current renderers, CLI, tests, and instructions were reviewed against the phase plans. Six correctness blockers affect identity attribution, source tracing, monetary evidence, publication and later corrections. Two further issues affect provenance display and operating the archive. Reproductions used temporary copies; the current release was not modified. The current dataset contains no financial rows, so the monetary finding describes an allowed future input rather than an assertion about a current figure. Source semantics and the outstanding human review remain human judgments.

## Narrative Findings (AI reviewer)

### CR-01: Identity validation accepts another legal entity's source

**Classification:** BLOCKER  
**File:** `src/arsiv.py:278-281`  
**Issue:** The identity check only compares the supplied registry key to the equally supplied party record; it does not verify that the passage belongs to that party, that its source identifies the registry key, or that the stated validity dates come from that entity. `tests/test_scope.py:27-28` demonstrates this directly by successfully associating the current Yeni Parti founding passage `kurulus` with a different, same-named `same-name-old` entity and an unrelated key. This can create an apparently sourced identity for the wrong legal entity, undermining T-02-01 and later identity-dependent financial checks.

**Fix:** Bind identity observations to an independently verified registry document and exact registry identifier, validate passage/document ownership and the applicable validity interval, and enforce the invariant again at export. Add a negative test where the old entity is presented with the new entity's passage.

### CR-02: Document deduplication merges sources from different parties

**Classification:** BLOCKER  
**File:** `src/arsiv.py:263-267`  
**Issue:** A SHA-256 match deduplicates the entire `document_version` globally, including its document and party identity, instead of just its underlying content object. In an isolated workspace, recording a TİP document version with the bytes of `registry-365-v1` returned that Yeni Parti version, created no requested version, and attached the TİP URL as an alias of the Yeni Parti record. Shared official pages and identical source bytes can legitimately concern multiple parties, and this silently loses the new document provenance and makes its passages either unrecordable or attributable to the wrong party. The CLI also discards the returned existing ID (`src/arsiv.py:871-873`).

**Fix:** Deduplicate immutable byte objects by hash but preserve a version/capture record for each relevant document and party (and its URL and timestamps); return the effective identifier to CLI callers. Test identical bytes across two party documents and verify both evidence chains survive.

### CR-03: A lead can be marked examined using an unrelated source

**Classification:** BLOCKER  
**File:** `src/arsiv.py:368-376`  
**Issue:** An `access/examined` attempt requires only that `source_version_id` be non-null; no check links its URL, redirects or aliases to the lead. `close_topic` then trusts that attempt (`src/arsiv.py:520-526`). In a temporary copy, a lead for `https://example.org/not-registry` was accepted as examined with the unrelated `registry-365-v1` and its topic closed successfully. The displayed research chain can therefore assert that a source was reviewed when the attached archive is a different source, defeating the T-03 closure/evidence guarantee.

**Fix:** Verify that the captured version's original/final URL or a validated alias corresponds to the accessed lead, including redirect handling, and enforce the same relationship when closing and auditing a topic. Add a negative mismatched-version closure test.

### CR-04: Financial validation treats dates and unrelated numbers as monetary evidence

**Classification:** BLOCKER  
**File:** `src/arsiv.py:559-567`  
**Issue:** The validator accepts an amount if the same number appears anywhere in the passage; it does not tie the number to a money expression or to the claimed financial category. The existing finance fixture contains `2026-08-01 ... 0 TL`. Changing its amount to `2026` and category to `bağış` passes `check_financial`, although 2026 is part of a date and no donation is stated. Such a record is rendered as a sourced monetary claim, including invented categories or zero values, contrary to T-05-03 and the documented distinction between unknown and documented zero.

**Fix:** Require a reviewed source locator tying the exact amount, currency and category together, reject numbers found only in dates or unrelated quantities, and retain human verification for semantic interpretation. Add negative tests for date components and category mismatches.

### CR-05: Publish advances current without the phase acceptance checks

**Classification:** BLOCKER  
**File:** `src/arsiv.py:826-842`  
**Issue:** `publish_release` calls `export_db` and `audit_release`, but never `validate_phase_one_workspace`; the documented phase audit is a separate command after the pointer moves. In a temporary copy, adding a supported, evidence-linked finding without a `review` record allowed `publish_release` to replace `current`; `validate_phase_one` then rejected that same release for its missing review. Other phase checks, such as heading completeness and valid provenance, are also outside the publication gate. Thus an invalid release can become the active reader output even though a phase validation function exists.

**Fix:** For phase-one publication, run the phase acceptance checks on the staged closed snapshot and corresponding generated HTML before renaming it and changing `current`. If incomplete intermediate snapshots are needed, expose them as explicitly non-current drafts. Add a test asserting that failed phase validation leaves `current` unchanged.

### CR-06: Existing unverified candidates cannot be resolved via the supported CLI

**Classification:** BLOCKER  
**File:** `src/arsiv.py:483-502`  
**Issue:** `check_unlinked_resolution` rejects a resolution for an unverified candidate and requires the atomic `resolve_candidate` transition, but the CLI in `src/arsiv.py:857-895` exposes no command or record kind that calls it. The existing release has seven unverified candidates. When new evidence arrives, the documented `record` workflow cannot resolve any of them; inserting another eligible candidate leaves the original missing unresolved, while a direct resolution is rejected. The Python-only test invokes `resolve_candidate` directly and misses the supported interface failure.

**Fix:** Add a documented CLI operation accepting candidate ID, match ID and resolution payload, route it to `resolve_candidate`, and test the full command path, preserved history, and failed-transition rollback.

### WR-01: Match rendering changes quote provenance

**Classification:** WARNING  
**File:** `src/rapor.py:112-118`  
**Issue:** Match text is always rendered with class `summary` and no quotation marks, regardless of the underlying finding's `provenance`. A valid match that uses a `quote` finding therefore repeats verbatim text in dark blue as if it were an edited summary, even though the same finding elsewhere is black and quoted. The 18 current matches happen to use summaries; the defect appears when an allowed quoted statement or action is added.

**Fix:** Render each match finding using its own provenance, applying black quoted text for quotes and dark blue for summaries, and test one match containing each type.

### WR-02: The stated standard-library runtime omits a required native dependency

**Classification:** WARNING  
**File:** `README.md:3`  
**Issue:** The documentation says Python and its standard library suffice, but auditing any release with PDF passages calls `pdf_page_text`, which requires Poppler GLib, GObject and GLib shared libraries (`src/arsiv.py:112-116`, `src/arsiv.py:696-701`). The current release has a PDF passage, including a manually reviewed page, so an otherwise compliant clean environment cannot audit it. The manual path is reached only after loading and extracting the page.

**Fix:** Document the native library requirements and platform installation/check procedure, provide an actionable diagnostic when any shared library is missing, and test the missing-dependency error path.

## Threat-control evidence and limits

The code includes HTML escaping and HTTP(S) URL checks (`src/rapor.py:7-12`), archive path checks (`src/arsiv.py:99-104`), parameterized value insertion and SQLite foreign keys (`src/arsiv.py:186-190`, `src/arsiv.py:302-303`), hash and derivative checks (`src/arsiv.py:688-695`), and staged pointer replacement (`src/arsiv.py:826-842`). These are relevant to T-01-01, T-01-02 and T-06-01; the findings above identify limits in the identity, research-chain and acceptance controls. These observations do not substitute for an ASVS assessment or a human review of evidence semantics.

---

_Reviewed: 2026-11-10T17:01:40Z_  
_Reviewer: the agent (gsd-code-reviewer)_  
_Depth: standard_
