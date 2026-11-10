---
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
reviewed: 2026-11-10T17:22:47Z
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
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 1: Code Re-review Report

**Reviewed:** 2026-11-10T17:22:47Z  
**Depth:** standard  
**Files Reviewed:** 23  
**Status:** clean

## Summary

This is a targeted verification of the repairs through `5d159b8`, following the standard review of the original 23-file scope. Both later blockers now pass their exact isolated reproductions: an identical re-capture of `tip-charter-v1` leaves `organ-secimi` closed, and `1.000 TL` with `number_format=tr` accepts `1000` and rejects `1`. Eight relevant tests passed independently, including unchanged/changed captures, number formats, document ownership, staged publication and candidate resolution. The prior review separately ran 29 relevant tests. No remaining software findings were found in this focused repair verification. Human assessment of source meaning, the TİP identifier relationship, dates, neutrality and interface presentation remains outstanding and is not represented as approved.

## Narrative Findings (AI reviewer)

No remaining findings in the focused repair verification.

## Later blocker resolution

- **Unchanged capture:** `src/arsiv.py:329-342` now preserves each version while comparing the previous capture for the lead and party before reopening. The exact previous reproduction stayed closed; `tests/test_chain.py` also confirmed changed content reopens with the appropriate reason.
- **Turkish numerical format:** `src/arsiv.py:612-622` requires an explicit source format and parses Turkish grouping and decimal separators separately from canonical notation. The exact previous reproduction now rejects `1` and accepts `1000`; `tests/test_finance.py` also covers grouped decimals, missing formats and malformed grouping. The choice of format and the financial source's substantive meaning remain matters for source review.

## Status of previous findings

- **Original CR-01, identity:** Resolved for the reported wrong-party/key cases by registry host/path/key and document-party checks in `check_identity`, applied to new publication. The former TİP-specific exception was removed; its canonical key and historical parliamentary identifier are retained separately. Earlier immutable releases explicitly use legacy compatibility. These technical checks do not decide the substance of the cross-source identity assessment.
- **Original CR-02, ownership:** Separate version rows retain document/party ownership even with shared bytes; the CLI returns the ID. The subsequent unchanged-capture regression is resolved above.
- **Original CR-03, examined source:** Access attempts, closure, and phase validation bind the examined version to the lead's party and captured original/final URL, without treating legacy hash aliases as redirect evidence.
- **Original CR-04, unrelated numbers:** The originally reported date and unrelated-category reproductions are rejected, and a review plus adjacent amount/currency expression is required. The subsequently reported Turkish numeric-format reproduction is resolved above; semantic review is separate.
- **Original CR-05, publication gate:** Phase-capable bases and snapshots containing a method undergo staged acceptance and HTML checks before `current` changes; the missing-review and removed-method tests pass.
- **Original CR-06, candidate resolution:** The documented `resolve-candidate` CLI routes to the atomic transition, with a CLI-path regression for history and failure.
- **Original WR-01, provenance display:** Match rendering now applies each finding's quote or summary style. Version 5 was frozen byte-for-byte from the former renderer and new releases use version 6.
- **Original WR-02, PDF libraries:** README documents native dependencies and the loader reports missing libraries; a mocked missing-library test passes.

## Threat-control evidence and limits

These are implementation observations for the orchestrator's ASVS1 review, not a security certification or human-source approval.

| Plan threat IDs | Relevant evidence and remaining limits |
|---|---|
| T-01-01, T-01-04, T-06-01, T-06-03 | `safe_url`/`safe_path` at `src/arsiv.py:93-105`, escaped readable bytes at `:108-110`, report escaping and URL checks at `src/rapor.py:6-12`, and loopback allowlisted serving at `src/arsiv.py:978-996`; negative URL/path tests are in `tests/test_publication.py` and `tests/test_report.py`. |
| T-01-02, T-06-02 | Integrity, FK, object and derivative checks at `src/arsiv.py:714-750`; staged acceptance and pointer swap at `:880-920`; failure and acceptance tests in `tests/test_publication.py`. The HTML acceptance function at `:863-869` checks presence of IDs, not complete HTML/data semantic equivalence. |
| T-01-03 | Capture timeout and source-size cap at `src/arsiv.py:185-196`; review did not independently exercise all network failure modes. |
| T-02-01, T-02-02, T-02-03 | Identity checks at `src/arsiv.py:113-130`, frozen cutoff and source hash at `:687-707`, and scope/date regressions in `tests/test_scope.py` and `tests/test_dates.py`. Strict identity is applied to new publications; old manifests retain documented legacy identity behavior. Human validation of registry semantics remains open. |
| T-03-01, T-03-02, T-03-03 | Lead normalization, attempt and source binding at `src/arsiv.py:347-418`, closure at `:558-572`, and missing-attempt checks at `:643-651`. The latest-capture comparison at `:329-342` and the chain test distinguish unchanged bytes from changed content. |
| T-04-01, T-04-02, T-04-03 | Authority checks at `src/arsiv.py:423-434`, evidence checks at `:550-555`, exact-passage/hash checks and topic-basis validation at `:742-778`; wrong-party and topic tests cover selected negative cases. Manual source meaning is not established by these checks. |
| T-05-01, T-05-02, T-05-03 | Actor and distinct occurrence evidence checks at `src/arsiv.py:448-485`, candidate-set checks at `:779-786`, financial checks and explicit number formats at `:585-622`, and matching/finance tests. Source format and material financial meaning still require review. |

---

_Reviewed: 2026-11-10T17:22:47Z_  
_Reviewer: the agent (gsd-code-reviewer)_  
_Depth: standard_
