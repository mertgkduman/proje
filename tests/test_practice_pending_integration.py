"""Two isolated, temporary releases; all review metadata is synthetic."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import arsiv
import uygulamalar
from uygulama_birlestirme import merge_packages
from test_practice_merge_engine import raw, digest


class PracticePendingIntegration(unittest.TestCase):
    def test_inherited_reading_is_pending_after_partial_merge(self):
        original_data = arsiv.DATA
        inventory = json.loads((original_data / 'practices/04-inventory.json').read_text())
        initial_package = json.loads((original_data / 'practices/04-coverage-tracer.json').read_text())
        base = initial_package['base_release']
        base_data = json.loads((original_data / 'releases' / base / 'records.json').read_text())
        passages = {row['id']: row for row in base_data['passage']}
        rows = []
        for (kind, identity), (refs, _) in uygulamalar.practice_review_targets(base_data, initial_package['practice_records']).items():
            rows.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent',
                reviewed_at='2026-11-18T12:00:00+00:00',
                source_version_ids=json.dumps(sorted({passages[p]['version_id'] for p in refs})),
                passage_ids=json.dumps(sorted(refs)), inspected_sections=json.dumps(['Technical section for ' + kind]),
                supported_claim='Technical fixture subject ' + identity, limitations='Synthetic fixture only.',
                result='reviewed', reason='Temporary fixture validation.'))
        initial_package['practice_records']['practice_source_review_contract'] = [dict(version=1)]
        initial_package['practice_records']['practice_source_review'] = rows
        initial_package['source_review_refs'] = [dict(subject_kind=r['subject_kind'], subject_id=r['subject_id']) for r in rows]
        event_id = initial_package['practice_records']['practice_event'][0]['id']
        old_review = next(row for row in rows if (row['subject_kind'], row['subject_id']) == ('practice_event', event_id))
        old_evidence = initial_package['practice_records']['practice_event_evidence'][0]
        original_passage = passages[old_evidence['passage_id']]
        with tempfile.TemporaryDirectory(prefix='gsd-pending-integration-') as temp:
            root = Path(temp)
            accepted = root / 'accepted'
            uygulamalar.render_practice_preview(initial_package, accepted)
            accepted_folder, = (accepted / 'releases').iterdir()
            accepted_id = accepted_folder.name
            accepted_snapshot = json.loads((accepted_folder / 'records.json').read_text())
            self.assertEqual(next(r for r in accepted_snapshot['practice_source_review'] if r == old_review), old_review)
            (accepted / 'current.json').write_text(json.dumps(dict(release_id=accepted_id)))
            schemas = (uygulamalar.PRACTICE_TABLES | uygulamalar.PRACTICE_VARIANT_TABLES |
                       uygulamalar.PRACTICE_EVIDENCE_TABLES | uygulamalar.PRACTICE_COVERAGE_TABLES |
                       uygulamalar.PRACTICE_SOURCE_REVIEW_TABLES | uygulamalar.PRACTICE_SOURCE_REVIEW_REVISION_TABLES)
            accepted_records = {name: accepted_snapshot[name] for name in schemas if name in accepted_snapshot}
            incoming = copy.deepcopy(initial_package)
            incoming.update(base_release=accepted_id, stage='partial', source_review_refs=[])
            incoming['practice_records']['practice_contract'][0]['stage'] = 'partial'
            incoming['practice_records'].pop('practice_source_review_contract')
            incoming['practice_records'].pop('practice_source_review')
            new_passage = dict(original_passage, id='technical-pending-passage')
            incoming['entries'] = [dict(kind='passage', values=new_passage)]
            incoming['practice_records']['practice_event_evidence'].append(dict(old_evidence, passage_id=new_passage['id']))
            inputs = [dict(identity='technical-pending', raw=raw(incoming))]
            decisions = raw(dict(version=1, inventory_digest=uygulamalar._digest(inventory),
                                 input_digests={'technical-pending': digest(inputs[0]['raw'])}, decisions=[]))
            outcome = merge_packages(inventory, inputs, decisions, decisions_sha256=digest(decisions), base_records=accepted_records)
            merged = outcome['payload']
            merged['practice_records'].update(uygulamalar.materialize_practice_merge(inventory, inputs, decisions, accepted_records, outcome))
            merged = uygulamalar.prepare_practice_merge_pending_reviews(merged, accepted_records)
            with patch.object(arsiv, 'DATA', accepted):
                result = root / 'result'
                uygulamalar.render_practice_preview(merged, result, base_release=accepted_id,
                                                   storage_root=accepted, allow_inherited_review_pending=True)
                output_folder, = (result / 'releases').iterdir()
                snapshot = json.loads((output_folder / 'records.json').read_text())
                self.assertEqual(arsiv.export_db(output_folder / 'records.sqlite3', output_folder.name, storage_root=result), snapshot)
                self.assertEqual(next(r for r in snapshot['practice_source_review'] if r == old_review), old_review)
                self.assertEqual(snapshot['practice_source_review_revision'], [])
                event_only = dict(practice_event=[next(r for r in snapshot['practice_event'] if r['id'] == event_id)])
                self.assertEqual(uygulamalar.practice_source_review_pending(snapshot, [old_review], [], event_only),
                                 [dict(subject_kind='practice_event', subject_id=event_id, state='pending')])
                with self.assertRaises(ValueError):
                    uygulamalar.validate_practice_source_review(snapshot, [old_review], event_only, revisions=[])
                complete = dict(snapshot, practice_contract=[dict(snapshot['practice_contract'][0], stage='complete')])
                with patch('uygulamalar.practice_coverage_states', return_value=[]), self.assertRaisesRegex(ValueError, 'Kaynak inceleme pasajı hedefle uyuşmuyor'):
                    uygulamalar.validate_practices(complete)
                updated = dict(old_review, revision=2, reviewed_at='2026-11-19T12:00:00+00:00',
                    passage_ids=json.dumps(sorted([old_evidence['passage_id'], new_passage['id']])),
                    supported_claim='Technical fixture after added evidence.', reason='Both temporary fixture passages were inspected.')
                self.assertTrue(uygulamalar.validate_practice_source_review(snapshot, [old_review], event_only, revisions=[updated]))
                self.assertEqual(uygulamalar.practice_source_review_pending(snapshot, [old_review], [updated], event_only), [])
                # Synthetic R2 readings for every affected subject, plus an
                # initial reading for the newly added evidence target.
                all_initial = copy.deepcopy(snapshot['practice_source_review'])
                initial_by_key = {(r['subject_kind'], r['subject_id']): r for r in all_initial}
                all_revisions = []
                versions = {p['id']: p['version_id'] for p in snapshot['passage']}
                for (kind, identity), (required, _) in uygulamalar.practice_review_targets(snapshot).items():
                    key = (kind, identity)
                    version_ids = json.dumps(sorted({versions[p] for p in required}))
                    passage_ids = json.dumps(sorted(required))
                    if key not in initial_by_key:
                        all_initial.append(dict(old_review, subject_kind=kind, subject_id=identity,
                            source_version_ids=version_ids, passage_ids=passage_ids,
                            inspected_sections=json.dumps(['Technical new evidence section ' + identity]),
                            supported_claim='Technical new evidence subject ' + identity,
                            reason='The new technical source was inspected.'))
                    elif set(json.loads(initial_by_key[key]['passage_ids'])) != required:
                        all_revisions.append(dict(initial_by_key[key], revision=2,
                            reviewed_at='2026-11-19T12:00:00+00:00', source_version_ids=version_ids,
                            passage_ids=passage_ids, supported_claim='Updated technical target ' + kind + identity,
                            reason='The changed technical evidence was inspected.'))
                self.assertTrue(uygulamalar.validate_practice_source_review(snapshot, all_initial, revisions=all_revisions))
                self.assertEqual(uygulamalar.practice_source_review_pending(snapshot, all_initial, all_revisions), [])


if __name__ == '__main__':
    unittest.main()
