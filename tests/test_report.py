"""Raporun gerçek veride erişilebilir sekme sözleşmesi."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from rapor import render_report
from browser_probe import probe_tabs


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
        passage = next(p for p in data['passage'] if p['id'] == 'kurulus')
        version = next(v for v in data['document_version'] if v['id'] == passage['version_id'])
        self.assertEqual(probe_tabs(report, 'kurulus', root / 'data', version['readable_path']), 'BROWSER_TABS_OK')

    def test_rejects_unsafe_archive_path_and_escapes_finding(self):
        root = Path(__file__).resolve().parents[1]
        release = json.loads((root / 'data/current.json').read_text())['release_id']
        data = json.loads((root / 'data/releases' / release / 'records.json').read_text())
        data['finding'][0]['text'] = '<script>alert(1)</script>'
        self.assertNotIn('<script>alert(1)</script>', render_report(data))
        data['lead'][0]['url'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError):
            render_report(data)
        data['lead'][0]['url'] = 'https://example.org/'
        data['document_version'][0]['readable_path'] = '../outside'
        with self.assertRaises(ValueError):
            render_report(data)


if __name__ == '__main__':
    unittest.main()
