# Retained candidate audit and memory fix

The exact previously killed candidate `a87bc0aadf3546f0b46ff376c6b6a622`
passed its read-only `audit_release` on the changed local implementation.
The process exited 0 after 891.893 seconds, peaked at 1,297,632 KiB RSS,
and had a 4 GiB address-space limit. The four candidate files and isolated
current pointer were byte-identical before and after; all 2,251 prospective
inputs in the original captured workspace matched their expected hashes at
both checks. `audit.log` contains the hashes, timings, and memory samples.
The candidate remains unaccepted and the production pointer was not changed.

The strengthened actual-release regression passes in 16.047 seconds. The same
test against the pristine HEAD source loaded in an isolated in-memory module
fails, observing six retained descendant snapshots. This checks the regression
without changing the working tree; see `revert-red.log` and
`fixture-regression.md`. Five adjacent CLI and descent tests passed; see
`adjacent-tests.log`.

One bounded profile of the actual immediate-base/candidate comparison succeeded
in 17.543 seconds at 1,044,532 KiB peak RSS. In the profiled call,
`validate_completion_revisions` accounted for 11.640 seconds cumulative;
the two largest list-membership generators accounted for about 5.61 seconds
combined. List membership did not dominate this measurement, so no CPU
optimization was applied. The full API flow repeatedly audits ancestors and
may still be lengthy; the full regression and publication gate remain pending.
See `profile.log` and `profile_descent.py`.

Implementation SHA-256: `d9c00f5a83974d607b63d24c02f7d69bc1cb748675a4868345b0ab402aff9396`.
Regression test SHA-256: `279f6a0baf2d997f1e1195d4e5d00593fd2aa685081d8e2699c27118aa8995a4`.
