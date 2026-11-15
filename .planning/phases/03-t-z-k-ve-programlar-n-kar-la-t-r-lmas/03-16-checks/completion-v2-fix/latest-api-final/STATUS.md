# Latest-source isolated API run: failed gate

The real API test did not finish. The supervisor recorded exit `-9` at
`2026-11-15T21:32:36.638270+00:00`; its raw output and exit record are retained
as `run.log` and `exit.json`. There is no unittest success result. The kernel
log in `kernel-oom.log` explicitly identifies child PID 1388555 as killed by
the Slurm job memory cgroup, with anonymous RSS 5,358,084 kB. Kernel wall time
and supervisor wall time differ; the PID identifies the same process.

The partial path and the source-backed complete successor reached publication
inside the isolated temporary DATA tree. The following structural-gap successor
had a closed bundle but its pre-pointer audit had not completed: the isolated
pointer remained at complete epoch 3 release `6a673af7506d4b4a8310665b502c984f`.
No later checks, manifest-tamper assertion, or overall pass are claimed.

`input-comparison.json` compares all 2,251 inputs to their prospective hashes:
the isolated input copy has zero changes. Two current test files differ from
the captured epoch (`tests/test_comparisons.py` and
`tests/test_completion_coverage.py`); the copied test predates the test-only
`ef2511d` historical-fixture readiness change. The source matches stable
implementation `6ef0b5d`, and the canonical package remains the recorded
prospective package. No claim is made that this run tested later test changes.

Original runtime directory `/tmp/proje-v2-api-final-20261115T200402Z` and
isolated temporary tree `/tmp/tmphj4lx7ev` are preserved. Supervisor PID/SID
1388553 and child PID/SID 1388555 have exited. Production current remains
`85b1a453ce2346a8ad0df325a2b73ae9` with no production writer lock. A successful
actual API run is required before the authorized local v2 refresh can resume.
