"""Contract checks for sourced practice disputes and evidence stages."""
import copy
import json
import unittest

import arsiv
from uygulamalar import validate_practices


class PracticeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = arsiv.DATA / 'releases' / 'f67ca0a35e634035bf3aa83a46571f50'
        cls.data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))

    def test_initiative_evidence_does_not_support_a_result(self):
        data = copy.deepcopy(self.data)
        relation = data['practice_relation'][0]
        relation['result_finding_id'] = data['practice_contribution'][0]['finding_id']
        data['practice_event_evidence'][0]['stage'] = 'initiative'
        with self.assertRaisesRegex(ValueError, 'sonuç|Sonuç'):
            validate_practices(data)

    def test_dispute_is_visible_with_source_in_both_views(self):
        data = copy.deepcopy(self.data)
        data['practice_dispute'] = [dict(id='d1', event_id='tracer-cesme', supported_points='Desteklenen teknik nokta', disputed_points='Tartışılan teknik nokta', unresolved_points='Çözülemeyen teknik nokta', summary_finding_id='tracer-event')]
        data['practice_dispute_evidence'] = [dict(dispute_id='d1', passage_id='0105-cesme-p', point='Teknik nokta', source_position='Teknik kaynak anlatımı', role='conflict')]
        html = arsiv.render_comparison_snapshot(data, arsiv.render_report)
        self.assertEqual(html.count('Desteklenen teknik nokta'), 2)
        self.assertEqual(html.count('Tartışılan teknik nokta'), 2)
        self.assertEqual(html.count('Çözülemeyen teknik nokta'), 2)


if __name__ == '__main__':
    unittest.main()
