# Wave 1 regression repair

Status: pending

This is execute-phase step 5.8 repair after completed plan 04-01, not another phase plan. Keep phase progress at 1/15 and do not advance the plan counter.

## Observed failures

- The full 219-test run logs `test_dossiers.DossierTracer.test_each_finding_keeps_its_own_version_in_history` as failing. Its old regex counts `data-finding-id` as `id`; the uncommitted HTMLParser correction preserves the real uniqueness check. The corrected check still fails: 44,263 actual id attributes versus 44,261 distinct ids.
- Diagnostic HTML: `/tmp/gsd-phase04-dossier-history-diagnostic.html`; diagnostic log: `/tmp/gsd-phase04-wave1-dom-diagnostic.log`. `comparison-practice-tracer-relation-id` appears three times. Renderer 25 iterates historical comparison topics with the same topic_id at different taxonomy_version values, but add_practice_records filters only topic_id. Bind practice statements to the topic's taxonomy_version.
- `test_report.ReportTest.test_scoped_parties_and_summary_are_navigable` expects ten tabs. Both immutable releases 9003e475ee5d49b29a1310c0bfe2007d and 53b24e6740104cb5be5d3419491bd735 already have the eleventh phase-03-verification tab. Preserve the accepted Phase 3 tab and correct this outdated expectation.

## Task 1: preserve history and fix the renderer

Freeze the current producer as rapor_v25.py before edits. Advance the active renderer to 26; explicitly dispatch archived renderer 25 and admit both 25/26 for the relevant schema 6/7 manifests. Preserve the exact original renderer 24/25 HTML and CSS bytes. Make the comparison practice path filter taxonomy_version as well as topic_id. Keep genuine DOM uniqueness assertions and source/version navigation assertions. Correct the outdated tab expectation. Strengthen the real tracer regression so the three historical topic dictionaries cannot duplicate the card.

## Task 2: validate and deliver a corrected local release

Reconcile `/tmp/gsd-phase04-wave1-tests.log` and process 173310 before changing data/current.json: the original full suite is still running its last current-release audit as of dispatch. Do not mutate its input release/pointer while it runs. Then publish only through the normal locked workspace + publish --refresh path, preserving all historical releases and source bytes. Run the affected targeted regressions, historical renderer 25 byte reproduction, and required phase 2/3/4 audits. Run the full configured test gate once on the final code/current, bounded at 10,800 seconds; log and report the actual result without treating timeout as success.

Write actual commands, results, hashes, corrected release, and any remaining issues here. Update 04-WAVE-1-GATE.json and the session continuation record accurately. Do not advance phase/plan counters or mark phase requirements complete. Do not publicly deploy or push.
