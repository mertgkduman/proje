# Phase 4 wave test execution

Wave 1 verified all 221 discovered test IDs on the same source fingerprint and release: 108 recorded successes before interruption, then 113 successes in 20 isolated batches. The original single-process exit 137 remains interrupted with unknown cause. It is not a successful single-process result.

Whenever a later gate requires the full suite, preserve the full discovered test set while using fresh sequential module processes; put the long `test_same_taxonomy_sourced_revision_round_trip` in its own process. The session has 2 CPUs and an 8 GiB allocation. This is an execution adaptation, not a change to the project test configuration or test assertions.

Gate scope follows execute-phase and its `steps/post-merge-gate.md`: build and full-suite checks run after all worktrees are merged **or after the last plan completes in serial mode**. Sequential execution without worktrees does not exempt a wave. The earlier interpretation recorded here was incorrect. Wave 2 has plan acceptance and capability-hook evidence, but its general regression gate remains incomplete. Once the active 04-03 implementation and combined acceptance finish, run a fresh complete regression on the stable source tree to close the Wave 2/3 regression gap before advancing to Wave 4; do not claim a historical Wave 2 test run that never occurred. Later waves retain the normal build, full-suite, spot-check and capability-hook gates. The required phase-end regression also remains pending and must test the final source tree with zero credit from earlier fingerprints. Wave 1's broad regression repaired and checked genuine baseline regressions; it is not coverage credit for later implementation.

- Create a new per-wave contract from current unittest discovery. New source/test fingerprint or release invalidates prior-wave success credit: begin with zero credited IDs for new code.
- Bind source/test hashes, release and manifest before/after each batch; require matching checks and a zero exit code.
- Flush each per-test outcome and process exit code to durable evidence immediately. Resume only unfinished IDs after transport interruption.
- Retain every discovered test, real source/DB/browser check and negative assertion. Reject unknown/duplicate IDs and zero-test success.
- Apply the configured 10,800-second bound to each batch, record timeout/interruption as inconclusive, and do not invent successful single-process results.
- Aggregate completion only when every test ID for the same code/current has a passing outcome. Preserve all failed/interrupted attempts and execution-method differences.

The checked runner and Wave 1 identity/result contracts are under `04-01-checks/`. Use separate per-wave paths and fresh contracts for later code changes.
