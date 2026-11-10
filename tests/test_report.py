"""Raporun gerçek veride erişilebilir sekme sözleşmesi."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from rapor import render_report


class ReportTest(unittest.TestCase):
    def test_scoped_parties_and_summary_are_navigable(self):
        root = Path(__file__).resolve().parents[1]
        release = json.loads((root / 'data/current.json').read_text())['release_id']
        data = json.loads((root / 'data/releases' / release / 'records.json').read_text())
        report = render_report(data)
        self.assertIn('role="tablist"', report)
        self.assertIn('id="comparison-summary"', report)
        for party in data['scope_party']:
            self.assertIn('id="party-' + party['party_id'] + '"', report)
        self.assertIn('data-finding-id="kurulus-summary"', report)
        self.assertIn('id="scope-method"', report)


if __name__ == '__main__':
    unittest.main()
