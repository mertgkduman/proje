# Current-release verification: blocked

Local refresh `3a3021c8e81749c3834462d1a0d81231` was published successfully;
publisher exit 0, current pointer matches, and no production writer remains.
Its actual HTML SHA256 equals the historical report's
`60bafd3b384e020800a01b00a0c58beaf0392d1587d69e372c44667e4186cf3f`.
All 200 files in the 50-release historical chain, 10 delivery inputs including
eight receipts, 128 raw originals covering 141 version references, 1,452 views
and frozen renderer 22 matched prospective hashes (`preservation.json`).

The pre-production full regression passed 202 tests with 2,255 captured inputs
unchanged; it tested the old current and isolated v2 API, not this new current.
The post-publication focused job exited 1. Comparisons (10), content (29),
synthesis (9) and stage compatibility (2) passed. Navigation ran four tests:
the actual four file/http by 360/1365 cases each passed all 19 checks and found
the archive excerpt (`navigation-evidence.json`), but the suite failed three
direct-hash preview subtests for `%`, `%20`, and `%ZZ`: the test reported the
target missing, unfocused and invisible. `focused-navigation.log` is the raw
failure output; no underlying cause or correction is claimed here.

The job stopped on that failure. A separate post-failure corroboration found
all 163 captured focused inputs unchanged in both the workspace and the saved
copy (`focused-post-failure-integrity.json`); it is not the worker's own check.
Topics, documents, publication and dossiers
focused suites and actual current ordinary, phase-2 and phase-3 complete audits
were not run. The focused job did not reach its post-run input-integrity check.
The three human UAT groups and three value assessments remain pending. Root must
reconcile the test failure and any consequent code gate before resuming; do not
republish the already-current release blindly.
