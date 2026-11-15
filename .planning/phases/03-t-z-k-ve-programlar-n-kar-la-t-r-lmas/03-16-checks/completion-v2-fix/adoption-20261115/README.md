# Isolated completion-v2 adoption check

The input copy was created at `/tmp/proje-v2-adoption-20261115` before this run. The included input SHA-256 manifest was generated from its copied `src`, `tests` and `data` trees before launch; the copied data included the accepted release `85b1a453ce2346a8ad0df325a2b73ae9`, source packages, objects and archive views. The source copy and its manifest describe this run, not later code changes.

The detached session's host, PID, SID and unique token are in the unmodified handshake. The unmodified log records `test_real_source_adoption_import_export_and_rollback`: one test passed in 74.898 seconds, and the separate exit file records 0. This exercised real import and export in a temporary DATA copy, checked rejection/rollback for an invalid base, and checked that the historical v1 completion marker was retained. It did not publish or audit a release, and does not establish the later sourced-addition or supersession paths.
