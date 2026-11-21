"""Two isolated, temporary releases; all review metadata is synthetic."""
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import arsiv
import uygulamalar
from uygulama_birlestirme import merge_packages
from test_practice_merge_engine import raw, digest


class PracticePendingIntegration(unittest.TestCase):
    def test_public_merge_preserves_accepted_r1_as_pending(self):
        """Create the real public merge and bind its output to its inputs."""
        self._exercise_public_pending('merge')

    def test_public_replay_preserves_accepted_r1_as_pending(self):
        """Replay the real merge and check inherited reading and completeness."""
        self._exercise_public_pending('replay')

    def _exercise_public_pending(self, phase):
        original = arsiv.DATA
        inventory = json.loads((original / 'practices/04-inventory.json').read_text())
        initial = json.loads((original / 'practices/04-coverage-tracer.json').read_text())
        base_data = json.loads((original / 'releases' / initial['base_release'] / 'records.json').read_text())
        passages = {r['id']: r for r in base_data['passage']}
        rows = []
        for (kind, identity), (refs, _) in uygulamalar.practice_review_targets(base_data, initial['practice_records']).items():
            rows.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent',
                reviewed_at='2026-11-18T12:00:00+00:00',
                source_version_ids=json.dumps(sorted({passages[p]['version_id'] for p in refs})),
                passage_ids=json.dumps(sorted(refs)), inspected_sections=json.dumps(['Technical section ' + kind]),
                supported_claim='Technical fixture subject ' + identity, limitations='Synthetic fixture only.',
                result='reviewed', reason='Temporary fixture validation.'))
        initial['practice_records'].update(practice_source_review_contract=[dict(version=1)], practice_source_review=rows)
        initial['source_review_refs'] = [dict(subject_kind=r['subject_kind'], subject_id=r['subject_id']) for r in rows]
        event = initial['practice_records']['practice_event'][0]['id']
        old_review = next(r for r in rows if (r['subject_kind'], r['subject_id']) == ('practice_event', event))
        old_evidence = initial['practice_records']['practice_event_evidence'][0]
        new_passage = dict(passages[old_evidence['passage_id']], id='technical-public-pending-passage')
        with tempfile.TemporaryDirectory(prefix='gsd-public-pending-') as tmp:
            root = Path(tmp)
            archive = root / 'archive'
            # Copy the complete private ancestry without touching canonical bytes.
            shutil.copytree(original, archive, ignore=shutil.ignore_patterns('.staging', '.write.lock'))
            with patch.object(arsiv, 'DATA', archive):
                accepted = root / 'accepted'
                fixture = os.environ.get('GSD_PENDING_ACCEPTED_FIXTURE')
                if fixture:
                    fixture_root = Path(fixture)
                    fixture_folder, = (fixture_root / 'releases').iterdir()
                    manifest_bytes = (fixture_folder / 'manifest.json').read_bytes()
                    self.assertEqual(hashlib.sha256(manifest_bytes).hexdigest(),
                                     os.environ['GSD_PENDING_ACCEPTED_MANIFEST_SHA256'])
                    self.assertEqual(json.loads(manifest_bytes)['base_release'], initial['base_release'])
                    shutil.copytree(fixture_root, accepted)
                else:
                    uygulamalar.render_practice_preview(initial, accepted)
                folder, = (accepted / 'releases').iterdir()
                accepted_id = folder.name
                shutil.copytree(folder, archive / 'releases' / accepted_id)
                # Establish the accepted release through its complete ordinary
                # audit before making it the private archive's trust anchor.
                self.assertEqual(arsiv.audit_release(accepted_id), accepted_id)
                (archive / 'current.json').write_text(json.dumps(dict(release_id=accepted_id)))
                accepted_data = json.loads((folder / 'records.json').read_text())
                if phase == 'replay':
                    self.assertEqual(arsiv.export_db(folder / 'records.sqlite3', accepted_id, storage_root=accepted), accepted_data)
                if fixture:
                    for table, expected in initial['practice_records'].items():
                        for row in expected:
                            self.assertIn(row, accepted_data[table])
                incoming = copy.deepcopy(initial)
                incoming.update(base_release=accepted_id, stage='partial')
                records = incoming['practice_records']
                records['practice_contract'][0]['stage'] = 'partial'
                incoming['entries'] = [dict(kind='passage', values=new_passage)]
                records['practice_event_evidence'].append(dict(old_evidence, passage_id=new_passage['id']))
                # Raw inputs must themselves have real, scoped technical reviews;
                # those revisions are provenance and must not become base approval.
                expanded = copy.deepcopy(accepted_data)
                expanded['passage'].append(new_passage)
                expanded['practice_event_evidence'].append(records['practice_event_evidence'][-1])
                by_key = {(r['subject_kind'], r['subject_id']): r for r in rows}
                new_rows, revisions = [], []
                versions = {p['id']: p['version_id'] for p in expanded['passage']}
                targets = uygulamalar.practice_review_package_targets(expanded, records, {new_passage['id']}, incoming['party_id'])
                for (kind, identity), (refs, _) in targets.items():
                    key = (kind, identity)
                    updates = dict(subject_kind=kind, subject_id=identity,
                        source_version_ids=json.dumps(sorted({versions[p] for p in refs})),
                        passage_ids=json.dumps(sorted(refs)), inspected_sections=json.dumps(['Technical section ' + kind + identity]),
                        supported_claim='Technical expanded subject ' + identity,
                        reason='Technical fixture inspected current evidence.')
                    if key in by_key:
                        if set(json.loads(by_key[key]['passage_ids'])) != refs:
                            revisions.append(dict(by_key[key], **updates, revision=2, reviewed_at='2026-11-19T12:00:00+00:00'))
                    else:
                        new_rows.append(dict(old_review, **updates))
                records['practice_source_review'] = rows + new_rows
                records['practice_source_review_revision_contract'] = [dict(version=2)]
                records['practice_source_review_revision'] = revisions
                incoming['source_review_refs'] = [dict(subject_kind=k, subject_id=i) for k, i in sorted(
                    {(r['subject_kind'], r['subject_id']) for r in rows + new_rows + revisions})]
                inputs = [dict(identity='incoming.json', raw=raw(incoming))]
                decision = raw(dict(version=1, inventory_digest=uygulamalar._digest(inventory),
                                    input_digests={'incoming.json': digest(inputs[0]['raw'])}, decisions=[]))
                cache = os.environ.get('GSD_PENDING_MERGE_FIXTURE')
                if cache and not fixture:
                    self.fail('Merge fixture requires the bound accepted fixture')
                binding = dict(base_release=accepted_id, accepted_manifest_sha256=hashlib.sha256(
                    (folder / 'manifest.json').read_bytes()).hexdigest(), inventory_digest=uygulamalar._digest(inventory),
                    input_sha256=digest(inputs[0]['raw']), decisions_sha256=digest(decision))
                if phase == 'merge' or not cache:
                    merged = uygulamalar.merge_practice_packages(inventory, inputs, decision)
                    if phase == 'merge' and cache:
                        merged_raw = json.dumps(merged, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
                        record = dict(binding=binding, merged_sha256=hashlib.sha256(merged_raw).hexdigest(),
                                      merged=merged)
                        with Path(cache).open('x', encoding='utf-8') as stream:
                            json.dump(record, stream, ensure_ascii=False, sort_keys=True)
                            stream.flush()
                            os.fsync(stream.fileno())
                else:
                    record = json.loads(Path(cache).read_text())
                    self.assertEqual(record['binding'], binding)
                    merged = record['merged']
                    merged_raw = json.dumps(merged, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
                    self.assertEqual(hashlib.sha256(merged_raw).hexdigest(), record['merged_sha256'])
                if phase == 'merge':
                    return
                result = root / 'result'
                uygulamalar.render_practice_preview(merged, result, inventory, base_release=accepted_id)
                output, = (result / 'releases').iterdir()
                snapshot = json.loads((output / 'records.json').read_text())
                self.assertEqual(snapshot, arsiv.export_db(output / 'records.sqlite3', output.name, storage_root=result))
                self.assertEqual(arsiv.audit_release(output.name, storage_root=result), output.name)
                self.assertIn(old_review, snapshot['practice_source_review'])
                self.assertEqual(snapshot['practice_source_review_revision'], [])
                self.assertIn(dict(old_evidence, passage_id=new_passage['id']), snapshot['practice_event_evidence'])
                event_only = dict(practice_event=[next(r for r in snapshot['practice_event'] if r['id'] == event)])
                self.assertEqual(uygulamalar.practice_source_review_pending(snapshot, [old_review], [], event_only),
                                 [dict(subject_kind='practice_event', subject_id=event, state='pending')])
                with self.assertRaises(ValueError):
                    uygulamalar.validate_practice_source_review(snapshot, [old_review], event_only, revisions=[])
                unchecked = copy.deepcopy(incoming)
                for table in ('practice_source_review_contract', 'practice_source_review',
                              'practice_source_review_revision_contract', 'practice_source_review_revision'):
                    unchecked['practice_records'].pop(table)
                unchecked['source_review_refs'] = []
                unchecked_path, review_path = root / 'unchecked.json', root / 'old-review.json'
                unchecked_path.write_text(json.dumps(unchecked))
                review_path.write_text(json.dumps(dict(practice_source_review=rows,
                    source_review_refs=[dict(subject_kind=r['subject_kind'], subject_id=r['subject_id']) for r in rows])))
                with patch.object(sys, 'argv', ['arsiv.py', 'practice-source-check', '--input', str(unchecked_path),
                                                '--review', str(review_path)]), self.assertRaisesRegex(ValueError, 'Kaynak inceleme'):
                    arsiv.main()
                complete = dict(snapshot, practice_contract=[dict(snapshot['practice_contract'][0], stage='complete')])
                with self.assertRaises(ValueError):
                    uygulamalar.validate_practices(complete)

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
            incoming.update(base_release=accepted_id, stage='partial')
            incoming['practice_records']['practice_contract'][0]['stage'] = 'partial'
            new_passage = dict(original_passage, id='technical-pending-passage')
            incoming['entries'] = [dict(kind='passage', values=new_passage)]
            incoming['practice_records']['practice_event_evidence'].append(dict(old_evidence, passage_id=new_passage['id']))
            # Raw package reviews remain provenance; they do not approve the
            # inherited accepted reading in the merged output.
            records = incoming['practice_records']
            expanded = copy.deepcopy(accepted_snapshot)
            expanded['passage'].append(new_passage)
            expanded['practice_event_evidence'].append(records['practice_event_evidence'][-1])
            by_key = {(r['subject_kind'], r['subject_id']): r for r in rows}
            new_rows, revisions = [], []
            versions = {p['id']: p['version_id'] for p in expanded['passage']}
            targets = uygulamalar.practice_review_package_targets(expanded, records, {new_passage['id']}, incoming['party_id'])
            for (kind, identity), (refs, _) in targets.items():
                key = (kind, identity)
                updates = dict(subject_kind=kind, subject_id=identity,
                    source_version_ids=json.dumps(sorted({versions[p] for p in refs})),
                    passage_ids=json.dumps(sorted(refs)), inspected_sections=json.dumps(['Technical section ' + kind + identity]),
                    supported_claim='Technical expanded subject ' + identity,
                    reason='Technical fixture inspected current evidence.')
                if key in by_key:
                    if set(json.loads(by_key[key]['passage_ids'])) != refs:
                        revisions.append(dict(by_key[key], **updates, revision=2, reviewed_at='2026-11-19T12:00:00+00:00'))
                else:
                    new_rows.append(dict(old_review, **updates))
            records['practice_source_review'] = rows + new_rows
            records['practice_source_review_revision_contract'] = [dict(version=2)]
            records['practice_source_review_revision'] = revisions
            incoming['source_review_refs'] = [dict(subject_kind=k, subject_id=i) for k, i in sorted(
                {(r['subject_kind'], r['subject_id']) for r in rows + new_rows + revisions})]
            inputs = [dict(identity='technical-pending', raw=raw(incoming))]
            decisions = raw(dict(version=1, inventory_digest=uygulamalar._digest(inventory),
                                 input_digests={'technical-pending': digest(inputs[0]['raw'])}, decisions=[]))
            outcome = merge_packages(inventory, inputs, decisions, decisions_sha256=digest(decisions), base_records=accepted_records)
            merged = outcome['payload']
            merged['practice_records'].update(uygulamalar.materialize_practice_merge(inventory, inputs, decisions, accepted_records, outcome))
            merged = uygulamalar.prepare_practice_merge_pending_reviews(merged, accepted_records)
            # Public replay audits the accepted base through its complete real
            # ancestry before using it as the private archive's trust anchor.
            archive = root / 'archive'
            shutil.copytree(original_data, archive, ignore=shutil.ignore_patterns('.staging', '.write.lock'))
            shutil.copytree(accepted_folder, archive / 'releases' / accepted_id)
            with patch.object(arsiv, 'DATA', archive):
                self.assertEqual(arsiv.audit_release(accepted_id), accepted_id)
                (archive / 'current.json').write_text(json.dumps(dict(release_id=accepted_id)))
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
