"""Human acceptance stays distinct from research evidence and opens real examples."""
import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest

from arsiv import comparison_render_data
from rapor import render_report
from rapor_v23 import render_report as render_23


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/releases/3a3021c8e81749c3834462d1a0d81231'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a' and attrs.get('href', '').startswith('#'):
            self.anchors.append(attrs['href'][1:])


class PhaseThreeReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = comparison_render_data(json.loads((BASE / 'records.json').read_text()))
        cls.acceptance = json.loads((ROOT / 'data/comparisons/03-human-acceptance.json').read_text())
        cls.accepted = copy.deepcopy(cls.data)
        cls.accepted['review'].append(cls.acceptance)
        cls.report = render_report(cls.accepted)

    def test_previous_published_renderer_is_exact(self):
        self.assertEqual(render_23(self.data).encode(), (BASE / 'index.html').read_bytes())

    def test_six_accepted_checks_link_to_existing_unique_targets(self):
        from urllib.parse import unquote
        parser = Links()
        parser.feed(self.report)
        ids = set(parser.ids)
        self.assertEqual(len(parser.ids), len(ids))
        self.assertTrue(all(unquote(a) in ids for a in parser.anchors))
        for number in range(1, 7):
            self.assertIn('phase-03-check-' + str(number), parser.ids)
        self.assertIn('6/6 kontrol kabul edildi', self.report)
        self.assertIn('id="tab-phase-03-verification"', self.report)
        self.assertIn('id="phase-03-verification"', self.report)

    def test_approval_transcript_and_development_preferences_are_private(self):
        review = json.loads(self.acceptance['reason'])
        self.assertNotIn(review['user_message'], self.report)
        self.assertNotIn(review['presentation_preference'], self.report)
        self.assertNotIn('hepsi gecti olsun', self.report)
        self.assertNotIn('acceptance_mode', self.report)

    def test_agent_review_does_not_become_user_acceptance(self):
        data = copy.deepcopy(self.data)
        acceptance = dict(self.acceptance, reviewer_kind='agent')
        data['review'].append(acceptance)
        self.assertNotIn('id="tab-phase-03-verification"', render_report(data))

    def test_acceptance_titles_and_labels_are_escaped(self):
        data = copy.deepcopy(self.accepted)
        acceptance = data['review'][-1]
        review = json.loads(acceptance['reason'])
        review['tests'][0]['title'] = '<img src=x onerror=alert(1)>'
        review['tests'][0]['examples'][0]['label'] = '<script>alert(1)</script>'
        acceptance['reason'] = json.dumps(review)
        report = render_report(data)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', report)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', report)
        self.assertNotIn('<img src=x onerror=alert(1)>', report)


if __name__ == '__main__':
    unittest.main()
