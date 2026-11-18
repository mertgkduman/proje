"""Technical fixtures for per-target source reading metadata."""
import copy
import contextlib
import io
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import arsiv
import uygulamalar


class PracticeSourceReview(unittest.TestCase):
    def setUp(self):
        self.data = dict(
            document=[dict(id='d', party_id='p')],
            document_version=[dict(id='v', document_id='d')],
            passage=[dict(id='p1', version_id='v'), dict(id='p2', version_id='v')],
            practice_source_party=[],
            practice_event=[dict(id='e')],
            practice_event_evidence=[dict(event_id='e', passage_id='p1', stage='action')],
            practice_contribution=[], practice_statement=[], practice_relation=[],
            practice_dispute=[], practice_dispute_evidence=[], practice_position_change=[],
            finding_evidence=[],
        )
        self.review = dict(subject_kind='practice_event_evidence', subject_id='e|p1|action',
                           reviewer_kind='agent', reviewed_at='2026-11-18T12:00:00+00:00',
                           source_version_ids=json.dumps(['v']), passage_ids=json.dumps(['p1']),
                           inspected_sections=json.dumps(['Full article and dated context']),
                           supported_claim='The article attributes the action to its source.',
                           limitations='This does not establish a final outcome.', result='reviewed',
                           reason='Passage and surrounding conditions were read.')

    def check(self, rows):
        return uygulamalar.validate_practice_source_review(self.data, rows)

    def test_target_requires_specific_real_reading(self):
        self.assertTrue(callable(getattr(uygulamalar, 'validate_practice_source_review', None)))
        event = dict(self.review, subject_kind='practice_event', subject_id='e', supported_claim='The event is described in the article.')
        self.assertTrue(self.check([event, self.review]))
        for key, value in [('subject_id', 'e|p2|action'), ('reviewer_kind', 'human'),
                           ('result', 'accepted'), ('source_version_ids', '["other"]'),
                           ('passage_ids', '["p2"]'), ('inspected_sections', '[" "]'),
                           ('supported_claim', ' '), ('limitations', '')]:
            with self.subTest(key=key):
                row = dict(self.review, **{key: value})
                with self.assertRaises(ValueError):
                    self.check([event, row])
        with self.assertRaises(ValueError):
            self.check([event])
        with self.assertRaises(ValueError):
            self.check([event, self.review, copy.deepcopy(self.review)])
        with self.assertRaisesRegex(ValueError, 'genel açıklama'):
            self.check([dict(self.review, subject_kind='practice_event', subject_id='e'), self.review])

    def test_package_coverage_does_not_require_unrelated_base_subjects(self):
        self.data['practice_event'].append(dict(id='other'))
        self.data['practice_event_evidence'].append(dict(event_id='other', passage_id='p2', stage='result'))
        selected = dict(practice_event=[], practice_event_evidence=[self.data['practice_event_evidence'][0]])
        self.assertTrue(uygulamalar.validate_practice_source_review(self.data, [self.review], selected))
        with self.assertRaises(ValueError):
            self.check([self.review])

        self.data['practice_unmatched'] = [dict(event_id='e', party_id='p'), dict(event_id='other', party_id='other')]
        event = dict(self.review, subject_kind='practice_event', subject_id='e', supported_claim='Technical event claim')
        selection = dict(practice_event=self.data['practice_event'], practice_event_evidence=self.data['practice_event_evidence'])
        self.assertTrue(uygulamalar.validate_practice_source_review(self.data, [event, self.review], selection, party_id='p'))

    def test_party_ownership_and_shared_source_are_checked(self):
        self.data['practice_statement'] = [dict(id='s', party_id='other', summary_finding_id='f', quote_finding_id='f')]
        self.data['practice_relation'] = [dict(id='r', event_id='e', statement_id='s', party_id='other',
                                              target_finding_id='f', result_finding_id=None,
                                              explanation_finding_id='f')]
        self.data['finding_evidence'] = [dict(finding_id='f', passage_id='p1')]
        targets = uygulamalar.practice_review_targets(self.data)
        rows = [dict(self.review, subject_kind=kind, subject_id=identity, supported_claim='Technical claim for ' + kind)
                for kind, identity in targets]
        with self.assertRaisesRegex(ValueError, 'parti sahibi'):
            self.check(rows)
        self.data['practice_source_party'] = [dict(version_id='v', party_id='other', passage_id='p1', scope_reason='Shared source for test')]
        self.assertTrue(self.check(rows))
        self.data['practice_source_party'][0]['version_id'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'parti sahibi'):
            self.check(rows)

    def test_review_extension_cannot_be_lost_in_descent(self):
        base = dict(practice_source_review_contract=[dict(version=1)], practice_source_review=[self.review])
        candidate = copy.deepcopy(base)
        uygulamalar.validate_practice_descent(base, candidate)
        del candidate['practice_source_review_contract']
        with self.assertRaises(ValueError):
            uygulamalar.validate_practice_descent(base, candidate)

    def test_manifest_binds_optional_review_extension(self):
        data = {name: [] for name in uygulamalar.PRACTICE_TABLES}
        data['practice_contract'] = [dict(version=1, stage='partial', inventory_digest='0' * 64)]
        old = uygulamalar.practice_manifest_fields(data)
        self.assertNotIn('practice_source_review_sha256', old)
        data.update(practice_source_review_contract=[dict(version=1)], practice_source_review=[self.review])
        first = uygulamalar.practice_manifest_fields(data)['practice_source_review_sha256']
        data['practice_source_review'][0] = dict(self.review, reason='A different recorded reason.')
        self.assertNotEqual(first, uygulamalar.practice_manifest_fields(data)['practice_source_review_sha256'])
        self.assertNotIn('practice_source_review_revision_sha256', uygulamalar.practice_manifest_fields(data))
        data.update(practice_source_review_revision_contract=[dict(version=2)],
                    practice_source_review_revision=[dict(self.review, revision=2)])
        digest = uygulamalar.practice_manifest_fields(data)['practice_source_review_revision_sha256']
        data['practice_source_review_revision'][0]['reason'] = 'A different revised reason.'
        self.assertNotEqual(digest, uygulamalar.practice_manifest_fields(data)['practice_source_review_revision_sha256'])

    def test_unmatched_and_dispute_subjects_bind_real_passages(self):
        self.data['finding'] = [dict(id='f', party_id='p')]
        self.data['finding_evidence'] = [dict(finding_id='f', passage_id='p1')]
        self.data['practice_unmatched'] = [dict(id='u', event_id='e', party_id='p')]
        self.data['practice_dispute'] = [dict(id='d1', event_id='e', summary_finding_id='f')]
        self.data['practice_dispute_evidence'] = [dict(dispute_id='d1', passage_id='p1', point='point', role='support')]
        selected = {name: self.data[name] for name in ('practice_unmatched', 'practice_dispute', 'practice_dispute_evidence')}
        targets = uygulamalar.practice_review_targets(self.data, selected)
        self.assertIn(('practice_unmatched', 'u'), targets)
        self.assertIn(('practice_dispute_evidence', 'd1|p1|point|support'), targets)
        rows = [dict(self.review, subject_kind=kind, subject_id=identity, supported_claim='Technical claim for ' + kind)
                for kind, identity in targets]
        self.assertTrue(uygulamalar.validate_practice_source_review(self.data, rows, selected))
        self.data['finding'][0]['party_id'] = 'foreign'
        with self.assertRaisesRegex(ValueError, 'parti sahibi'):
            uygulamalar.validate_practice_source_review(self.data, rows, selected)

    def test_revision_preserves_prior_reading_and_requires_current_scope(self):
        selection = dict(practice_event=self.data['practice_event'])
        first = dict(self.review, subject_kind='practice_event', subject_id='e')
        self.assertTrue(uygulamalar.validate_practice_source_review(self.data, [first], selection))
        self.data['document_version'].append(dict(id='v2', document_id='d'))
        self.data['passage'].append(dict(id='p3', version_id='v2'))
        self.data['practice_event_evidence'].append(dict(event_id='e', passage_id='p3', stage='result'))
        with self.assertRaises(ValueError):
            uygulamalar.validate_practice_source_review(self.data, [first], selection)
        self.assertTrue(hasattr(uygulamalar, 'PRACTICE_SOURCE_REVIEW_REVISION_TABLES'),
                        'a versioned append-only review adapter is required')
        second = dict(first, revision=2, reviewed_at='2026-11-19T12:00:00+00:00',
                      source_version_ids='["v", "v2"]', passage_ids='["p1", "p3"]',
                      supported_claim='The expanded evidence describes both technical points.',
                      reason='Both technical source sections were inspected.')
        self.assertTrue(uygulamalar.validate_practice_source_review(self.data, [first], selection, revisions=[second]))
        new_evidence = self.data['practice_event_evidence'][-1]
        affected = uygulamalar.practice_review_package_targets(self.data, {'practice_event_evidence': [new_evidence]}, {'p3'}, 'p')
        self.assertIn(('practice_event', 'e'), affected)
        new_reading = dict(self.review, subject_id='e|p3|result', source_version_ids='["v2"]',
                           passage_ids='["p3"]', supported_claim='The newly added technical result is described.')
        with self.assertRaises(ValueError):
            uygulamalar.validate_practice_source_review(self.data, [first, new_reading], revisions=[], target_keys=affected)
        self.assertTrue(uygulamalar.validate_practice_source_review(self.data, [first, new_reading], revisions=[second], target_keys=affected))
        for invalid in (dict(second, revision=3), dict(second, reviewed_at=first['reviewed_at']),
                        dict(second, passage_ids='["p1"]'), dict(second, reviewer_kind='human'),
                        dict(second, source_version_ids='["v"]')):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    uygulamalar.validate_practice_source_review(self.data, [first], selection, revisions=[invalid])
        with self.assertRaises(ValueError):
            uygulamalar.validate_practice_source_review(self.data, [first], selection, revisions=[second, copy.deepcopy(second)])
        with self.assertRaises(ValueError):
            uygulamalar.validate_practice_source_review(self.data, [first], selection,
                revisions=[second, dict(second, supported_claim='Conflicting technical interpretation.')])
        self.data['document_version'][1]['document_id'] = 'foreign'
        self.data['document'].append(dict(id='foreign', party_id='other'))
        self.data['practice_unmatched'] = [dict(event_id='e', party_id='p')]
        with self.assertRaises(ValueError):
            uygulamalar.validate_practice_source_review(self.data, [first], selection, revisions=[second])

    def test_revision_marker_and_history_cannot_be_removed_or_rewritten(self):
        revision = dict(self.review, revision=2, reviewed_at='2026-11-19T12:00:00+00:00')
        base = dict(practice_source_review_contract=[dict(version=1)], practice_source_review=[self.review],
                    practice_source_review_revision_contract=[dict(version=2)], practice_source_review_revision=[revision])
        candidate = copy.deepcopy(base)
        self.assertIsNone(uygulamalar.validate_practice_descent(base, candidate))
        for key in ('practice_source_review_revision_contract', 'practice_source_review_revision'):
            changed = copy.deepcopy(candidate)
            del changed[key]
            with self.assertRaises(ValueError):
                uygulamalar.validate_practice_descent(base, changed)
        candidate['practice_source_review_revision'][0]['reason'] = 'A rewritten historical reason.'
        with self.assertRaises(ValueError):
            uygulamalar.validate_practice_descent(base, candidate)

    def test_private_sqlite_adapter_preserves_v1_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = sqlite3.connect(Path(tmp) / 'records.sqlite3')
            db.execute('PRAGMA foreign_keys=ON')
            for name, definition in uygulamalar.PRACTICE_SOURCE_REVIEW_TABLES.items():
                db.execute(f'CREATE TABLE {name} ({definition})')
            values = self.review
            db.execute('INSERT INTO practice_source_review_contract VALUES (1)')
            db.execute('INSERT INTO practice_source_review VALUES (' + ','.join('?' for _ in values) + ')', list(values.values()))
            before = db.execute('SELECT * FROM practice_source_review').fetchall()
            for name, definition in uygulamalar.PRACTICE_SOURCE_REVIEW_REVISION_TABLES.items():
                db.execute(f'CREATE TABLE {name} ({definition})')
            db.execute('INSERT INTO practice_source_review_revision_contract VALUES (2)')
            revision = dict(values, revision=2)
            db.execute('INSERT INTO practice_source_review_revision (' + ','.join(revision) + ') VALUES (' + ','.join('?' for _ in revision) + ')', list(revision.values()))
            self.assertEqual(db.execute('SELECT * FROM practice_source_review').fetchall(), before)
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
            db.close()

    def test_source_check_routes_review_to_shared_preview_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / 'package.json'
            review = root / 'review.json'
            package.write_text(json.dumps(dict(base_release='a' * 32, party_id='p', practice_records={})))
            refs = [dict(subject_kind=self.review['subject_kind'], subject_id=self.review['subject_id'])]
            review.write_text(json.dumps(dict(practice_source_review=[self.review], source_review_refs=refs)))
            output = io.StringIO()
            with patch('sys.argv', ['arsiv.py', 'practice-source-check', '--input', str(package), '--review', str(review)]), \
                 patch('uygulamalar.render_practice_preview') as preview, contextlib.redirect_stdout(output):
                arsiv.main()
            self.assertIn('PRACTICE_SOURCE_REVIEW_OK', output.getvalue())
            sent = preview.call_args.args[0]
            self.assertEqual(sent['practice_records']['practice_source_review'], [self.review])
            self.assertEqual(sent['source_review_refs'], refs)
            revision = dict(self.review, revision=2, reviewed_at='2026-11-19T12:00:00+00:00')
            review.write_text(json.dumps(dict(practice_source_review=[self.review], practice_source_review_revision=[revision], source_review_refs=refs)))
            with patch('sys.argv', ['arsiv.py', 'practice-source-check', '--input', str(package), '--review', str(review)]), \
                 patch('uygulamalar.render_practice_preview') as preview, contextlib.redirect_stdout(io.StringIO()):
                arsiv.main()
            sent = preview.call_args.args[0]['practice_records']
            self.assertEqual(sent['practice_source_review_revision_contract'], [dict(version=2)])
            self.assertEqual(sent['practice_source_review_revision'], [revision])

    def test_invalid_review_cannot_replace_existing_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'existing'
            out.mkdir()
            report = out / 'report'
            report.write_text('Existing output')
            before = hashlib.sha256(report.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):
                uygulamalar.render_practice_preview({'practice_records': {'practice_source_review': []}}, out)
            self.assertEqual(hashlib.sha256(report.read_bytes()).hexdigest(), before)
