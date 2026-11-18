"""Technical fixtures for per-target source reading metadata."""
import copy
import json
import unittest

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
        self.assertTrue(self.check([self.review]))
        for key, value in [('subject_id', 'e|p2|action'), ('reviewer_kind', 'human'),
                           ('result', 'accepted'), ('source_version_ids', '["other"]'),
                           ('passage_ids', '["p2"]'), ('inspected_sections', '[" "]'),
                           ('supported_claim', ' '), ('limitations', '')]:
            with self.subTest(key=key):
                row = dict(self.review, **{key: value})
                with self.assertRaises(ValueError):
                    self.check([row])
        with self.assertRaises(ValueError):
            self.check([])
        with self.assertRaises(ValueError):
            self.check([self.review, copy.deepcopy(self.review)])
