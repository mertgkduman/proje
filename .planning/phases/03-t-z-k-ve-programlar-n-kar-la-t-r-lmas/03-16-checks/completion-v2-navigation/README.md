# V2 navigation preview fixture correction

The actual uninstrumented published report passed all four file/HTTP × 360/1365 cases before this change, including 19 checks and its real archive excerpt in each case. The three percent/Unicode preview subtests failed because they recursively renamed row and passage IDs in the full records, then asked `comparison_render_data` to apply the immutable v2 selection whose serialized IDs remained original. The invented preview row was correctly absent from that selection.

The test now projects the real published view first and then assigns hostile IDs only to that rendering fixture. It calls the renderer directly on that already projected view. No source validator, application code, selection contract, published record or assertion changed; all three tokens (`%`, `%20`, `%ZZ`) and Unicode/space/quote/fragment cases remain exercised. The actual unmodified-report test and frozen renderer 20/21 byte checks remain.

Actual targeted rerun: four tests passed in 138.082 seconds, exit 0. All 141 prospective inputs, including source, test, comparison authoring files and the actual current closed bundle, were unchanged afterward. `navigation-evidence.json` is the actual current-release four-mode browser proof. The copied supervisor is retained as runtime corroboration; the imported inputs were hashed before launch.

The prior 202-test full regression passed against its documented earlier test epoch and pre-production current. This is a subsequent test-fixture-only correction with full targeted coverage on the new current; it is not described as a second 202-test run. The source/package and published bundle are unchanged. Remaining current-data topics/documents/publication/dossiers checks and ordinary/P2/P3 audits are pending.
