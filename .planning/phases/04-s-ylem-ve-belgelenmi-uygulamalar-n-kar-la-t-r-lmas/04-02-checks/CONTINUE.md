# 04-02 continuation handoff

Plan is incomplete. Do not create SUMMARY or advance the plan counter until both tasks and all gates pass.

Root continuation scope: the next fresh executor completes **Task 1 only**, including its real acceptance and automated tracer feedback gates, then leaves a committed handoff for Task 2. This is an automatic context handoff within the already authorized plan, not a request for human approval. The final Task 2 executor completes plan-wide verification, SUMMARY and tracking.

## State

- RED commit `f5ca16a` adds `tests/test_practice_content.py`; the initial ordering assertion failed intentionally before the WIP implementation.
- Uncommitted WIP: `src/arsiv.py`, `src/rapor.py`, `tests/test_practice_content.py`; new untracked `src/rapor_v26.py`, `src/rapor_v25.css`. Preserve and review these changes. Renderer 26 was copied before changing the active renderer; archive dispatch now includes 26 and active version is 27.
- Existing unrelated untracked `.gsd/`, `.planning/milestone.lock`, phase 03 `ROOT-ACTIVE-HANDOFF.md`, `.planning/ui-reviews/`, and `data/.staging/` predate this work; leave them alone.
- `python3 tests/run.py --pattern test_practice_content.py`: exit 0, 2 tests in 6.891s. These narrow tests exercise rendering order/statement repetition from cloned archived JSON and exact renderer 26 byte reproduction; they do **not** establish the full Task 1 gate.
- `python3 tests/run.py --pattern test_practice_tracer.py`: exit 0, 5 tests in 214.622s, `TESTS_OK count=5`. This includes the real tracer load/export/render replay and renderer 24/25 byte checks. The session finished and `data/.write.lock` was absent afterwards.
- Root independently confirmed no writer lock and that `src/rapor_v26.py` SHA-256 `ef011f57067d5b1f1ce42b849588ee6ee9b6dc2a5c14be507079db4eddfc73e8` equals the pre-edit renderer at commit `f5ca16a`.
- Preserve the existing plan commit ledger. Read large monoliths by the functions needed for this task rather than consuming context on unrelated historical code. Task 2 security/temporal expansion is for a later fresh executor; no unsupported acceptance path may be replaced by a permissive stub.

## Remaining Task 1

Complete and test actual DB→JSON→two-view multiple events and shared event relationships across parties and principles, with unique real DOM IDs, direct Faz3 and source-passage links, and sound links to other event relationships. Add the explicitly versioned backward-compatible variant table adapter with downgrade/marker rejection while preserving schema 6 and existing schema 7 exports/manifests. Implement unmatched events with genuine statement scope and distinguish not researched from attempted missing. Validate all task acceptance criteria; the current two tests are insufficient and current shared-event links require validation. Run the full `test_practice_content.py` tracer verification twice as required before expansion, then commit Task 1 using the root pin and safety checks.

## Remaining Task 2

Implement the canonical dispute/reply, position change, scoped shared source and evidence/stage contracts and their validation, including one sufficiently concrete independent news report, rejection of party repetition alone, temporal and actor authority/individual MP distinctions, source ownership and contribution limits. Show target/result, stage limitations, disputes and sourced replies in both views without inventing outcomes, motives or institutional positions. Add meaningful accepted/rejected load/export/render tests in temporary roots, run `test_practice_contract.py` and `test_comparison_content.py`, preserve real tracer and archived hashes, resolve applicable deferred items, then complete plan verification and normal tracking. See plan, execution contract and root dispatch for full details.
