# Chained synthesis replacement regression

The RED run used `/tmp/proje-chain-red-20261115`, with hashes captured before
execution. Its real SR25 source-backed A→B→C chain failed at the shared
revision validator because B was no longer selected in C's revision.

The first post-fix run used `/tmp/proje-chain-green-20261115`, with its own
pre-execution input hashes and handshake. It passed the gap, canonical package,
and chained shared-validator checks but its missing-terminal negative expected
an uppercase error string instead of the actual lowercase text, so the test
failed. The final chain run uses `/tmp/proje-chain-final-20261115` and corrects
that assertion; its own hashes, handshake, raw log and exit are recorded here.
The latest isolated import/publish/audit scenario is not part of either run.
