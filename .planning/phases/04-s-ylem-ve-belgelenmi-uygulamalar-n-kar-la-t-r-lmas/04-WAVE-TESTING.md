# Phase 4 wave test execution

Wave 1 verified all 221 discovered test IDs on the same source fingerprint and release: 108 recorded successes before interruption, then 113 successes in 20 isolated batches. The original single-process exit 137 remains interrupted with unknown cause. It is not a successful single-process result.

For subsequent wave gates, preserve the full discovered test set while using fresh sequential module processes; put the long `test_same_taxonomy_sourced_revision_round_trip` in its own process. The session has 2 CPUs and an 8 GiB allocation. This is an execution adaptation, not a change to the project test configuration or test assertions.

- Create a new per-wave contract from current unittest discovery. New source/test fingerprint or release invalidates prior-wave success credit: begin with zero credited IDs for new code.
- Bind source/test hashes, release and manifest before/after each batch; require matching checks and a zero exit code.
- Flush each per-test outcome and process exit code to durable evidence immediately. Resume only unfinished IDs after transport interruption.
- Retain every discovered test, real source/DB/browser check and negative assertion. Reject unknown/duplicate IDs and zero-test success.
- Apply the configured 10,800-second bound to each batch, record timeout/interruption as inconclusive, and do not invent successful single-process results.
- Aggregate completion only when every test ID for the same code/current has a passing outcome. Preserve all failed/interrupted attempts and execution-method differences.

The checked runner and Wave 1 identity/result contracts are under `04-01-checks/`. Use separate per-wave paths and fresh contracts for later code changes.
