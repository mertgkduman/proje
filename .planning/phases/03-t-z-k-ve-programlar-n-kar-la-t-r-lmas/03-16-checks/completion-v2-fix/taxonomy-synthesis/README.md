# Cross-taxonomy synthesis correction regression

The RED run used `/tmp/proje-taxonomy-red-20261115`, with input hashes and
process handshake captured before execution. The source-backed taxonomy-4
A→B→C chain passed its shared validators, then the helper rejected a new
taxonomy-5 synthesis selection because the earlier correction remained in
the registry. The RED fixture was a bounded helper probe, not a complete
taxonomy migration.

The GREEN run uses a separately frozen input tree,
`/tmp/proje-taxonomy-green-20261115`. Its candidate taxonomy-5 synthesis and
review are independently recorded in a test-only source file, the successor
basis origin is checked, and the old correction registry is retained. It
exercises the historical chain, scoped retirement, and rejection of an
unauthorized cross-taxonomy correction. This does not establish that a full
new-taxonomy import, publish, or audit has passed; those remain future work.
