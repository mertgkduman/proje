---
status: resolved
trigger: "Phase 03 actual completion-v2 API gate killed by Slurm memory cgroup before final successor pre-pointer audit completed"
created: 2026-11-15T21:35:38Z
updated: 2026-11-15T22:04:10Z
---

## Symptoms

expected: The real source addition, partial publication, complete replacement and structural missing-to-bounded-negative successor must import/publish/audit successfully with all immutable history retained.
actual: The latest-source isolated API child exited -9 at 2026-11-15T21:32:36Z after approximately 88 minutes, with no unittest completion. Kernel evidence identifies memory-cgroup OOM for exact child PID 1388555 (anon-rss 5358084 kB).
errors: See phase 03-16-checks/completion-v2-fix/latest-api-final/STATUS.md, raw exit/log and kernel evidence; this is not a pass.
timeline: Historical 554db20 smaller round trip passed in 3602.903 seconds; the new 6ef0b5d source includes the authenticating revision contract and five-epoch structural gap scenario. Current test-only ef2511d readiness change did not touch source or package.
reproduction: Preserve /tmp/tmphj4lx7ev/data; candidate a87bc0aadf3546f0b46ff376c6b6a622 has four closed files, 202581338-byte JSON and 218509312-byte SQLite. Its own current still points to 6a673af7506d4b4a8310665b502c984f. Reproduce the actual readonly audit of this unaccepted candidate without rerunning the first 88 minutes. Never adopt it as production or mutate its immutable files.

## Current Focus

hypothesis: audit_release retains every descendant's exported snapshot while recursively validating its base, multiplying memory by chain depth; source payload volume and cgroup limit combine to trigger OOM.
bug_class: deterministic volume-dependent resource failure
next_action: independent code review and final full API regression are owned by the parent phase workflow; publication and existing human UAT remain pending.
reasoning_checkpoint:
  hypothesis: audit_release retains each descendant export across recursive ancestor audit; with large snapshots and a deep release chain, aggregate live payloads exceed the Slurm memory limit.
  confirming_evidence:
    - Real seven-release audit reached export calls with retained descendant exported locals [0, 1, 2, 3, 4, 5, 6], causing the new regression to fail.
    - The exact API child was killed by the kernel memory cgroup at 5358084 kB anonymous RSS with a 194 MiB JSON candidate.
  falsification_test: ancestor-first audit retains descendant exports or the preserved failed candidate still exceeds the same memory budget.
  fix_rationale: traverse and validate ancestors before creating the current snapshot, and reuse the already parsed immediate-base JSON; keep every validation enabled.
  blind_spots: the full regression and independent review remain pending; other workloads may exhibit different allocation peaks.
  candidate_causes:
    - code: recursive frames retain exported snapshots and duplicate a base JSON load.
    - environment and data: a fixed Slurm cgroup cap combines with a deep chain and large records.
  and_gate: yes; the live allocations, depth, data size, and memory limit all contribute to the failure.

## Evidence

- timestamp: 2026-11-15T21:35:38Z
  observation: Exact PID-specific kernel OOM proof and all 2251 prospective API inputs preserved; production remains immutable v1 release 85b1a453ce2346a8ad0df325a2b73ae9, no production writer.
- timestamp: 2026-11-15T21:44:53Z
  observation: audit_release calls export_db before recursing in both phase-two and non-delivery schema-5/6 paths; the exported local is used after recursion, and the phase-two path reads base records.json twice. This establishes object lifetime by code inspection, pending runtime observation. Coverage-based fault localization skipped: no suitably failing bounded test with per-test coverage yet.
- timestamp: 2026-11-15T21:44:53Z
  observation: test_audit_memory.AuditMemoryTest.test_closed_release_descent_does_not_hold_descendant_exports FAILED pre-fix after 12.592 seconds, observing exported locals in 0, 1, 2, 3, 4, 5 and 6 outer audit frames while auditing a real seven-release chain.
- timestamp: 2026-11-15T21:44:53Z
  observation: After ancestor-first recursion and duplicate base-read removal, two real-fixture regression tests passed in 14.571 seconds, including ancestor file tamper and base-chain cycle rejection. Read-only replay of the exact candidate started under 4 GiB RLIMIT_AS; retained input and candidate hashes are recorded in audit.log.
- timestamp: 2026-11-15T21:59:32Z
  observation: The exact failed candidate passed its actual read-only audit, exit 0, in 891.893 seconds with peak RSS 1297632 KiB under 4 GiB RLIMIT_AS. All 2251 prospective input hashes, the four candidate file hashes and isolated current pointer hash matched before and after; see completion-v2-memory/audit.log.
- timestamp: 2026-11-15T22:03:00Z
  observation: The strengthened regression failed against pristine HEAD loaded in an isolated in-memory module, preserving the working tree; it passes against the fix. Five adjacent tests passed. A real immediate-base/candidate descent profile passed in 17.543s; revision validation took 11.640s cumulative and the two largest list membership generators took about 5.61s combined, so no CPU optimization was applied.

## Eliminated

## Resolution

root_cause: Recursive audit retains each descendant's full exported snapshot until its ancestors finish; large data and a deep chain exceed the Slurm memory cgroup limit.
fix: Audit required ancestors before exporting the current snapshot, reuse the parsed immediate base, and release base data after descent validation.
verification:
  target_test: pass (strengthened real-fixture tests, 16.047s)
  mutation_check: skipped (Stryker is not configured for this Python project; no installation authorized)
  no_op_deletion: pass (historical audits and validators retained; duplicate immediate-base read eliminated)
  adjacent_tests: pass (five CLI and comparison-descent tests; see adjacent-tests.log)
  revert_and_reconfirm: pass (strengthened regression fails on pristine HEAD in isolated in-memory module, passes with fix; no working-tree revert)
  guardrail_verdict: accepted
  original_boundary: exact retained candidate passes under 4 GiB RLIMIT_AS, exit 0, 891.893s, peak RSS 1297632 KiB; candidate/current and 2251 input hashes unchanged
  pending: full regression, independent review, production gate and existing human UAT groups
oracle_type: derived (no descendant snapshot held during ancestor export)
files_changed: src/arsiv.py; tests/test_audit_memory.py; completion-v2-memory/audit_candidate.py
prevention: why not caught: existing small fixtures did not assert live snapshot lifetime across deep ancestry; guard: tests/test_audit_memory.py::AuditMemoryTest.test_closed_release_descent_does_not_hold_descendant_exports
