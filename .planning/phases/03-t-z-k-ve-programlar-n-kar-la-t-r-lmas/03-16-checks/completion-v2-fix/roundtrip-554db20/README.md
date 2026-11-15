# Historical isolated revision round trip

The detached test ran from the pre-launch copy `/tmp/proje-v2-roundtrip2-20261115`; the included prospective SHA-256 manifest covers its copied `src`, `tests` and `data` files. The included runtime and handshake record the interpreter, host, PID/SID and token. Its `src/arsiv.py` SHA-256 `7157d72bf796688a8f6e4cd5e7fb42195e496b3ff0258fd035b149a49c369e6b` and `tests/test_completion_coverage.py` SHA-256 `8dbd9257ed55211bdfe97814da5d439594bc05d147f39d48df5d3f145568665b` both match commit `554db20` exactly.

The unmodified log and separate exit file record one passing test, 3602.903 seconds, exit 0. It imported a real-source same-taxonomy addition, published/audited a partial release, and imported/published/audited a complete source-backed test-only replacement in isolated DATA. The logged temporary successor `ca51b36ff5aa4086b825fcdd29453320` was inside the test's temporary directory and is not a production release or a retained release artifact.

This predates the 2026-11-15 re-review and the subsequent correction/reading authentication changes; it does not prove the later source, new reviewer findings, latest importer cases or final acceptance.
