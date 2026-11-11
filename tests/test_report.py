"""Raporun gerçek veride erişilebilir sekme sözleşmesi."""
import json
import re
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from rapor import render_report
from browser_probe import probe_tabs


class ReaderText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.depth:
            self.depth += 1
        elif tag == 'article' and 'data-match-id' in attrs or tag == 'p' and 'data-status' in attrs:
            self.depth = 1

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)


class ReportTest(unittest.TestCase):
    def test_scoped_parties_and_summary_are_navigable(self):
        root = Path(__file__).resolve().parents[1]
        release = json.loads((root / 'data/current.json').read_text())['release_id']
        data = json.loads((root / 'data/releases' / release / 'records.json').read_text())
        report = render_report(data)
        self.assertIn('role="tablist"', report)
        self.assertEqual(re.findall(r'role="tab" id="tab-([^"]+)"', report),
                         ['yeni-parti', 'tip', 'dem', 'iyi', 'yeni-yol', 'dbp',
                          'emep', 'saadet', 'demokrat', 'comparison'])
        self.assertIn('id="comparison-summary"', report)
        for party in data['scope_party']:
            self.assertIn('id="party-' + party['party_id'] + '"', report)
        self.assertIn('data-finding-id="kurulus-summary"', report)
        self.assertIn('id="scope-method"', report)
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', report)
        self.assertIn('<h1>Türkiye siyasi partileri: kaynaklı pilot rapor</h1>', report)
        for removed in ('Bu dokuz partilik ön liste', 'PROJECT.md kullanıcı kararı',
                        'Grup adından bireysel parti üyeliği çıkarılmaz.',
                        'Bu başlıklar beş parti dosyası başlığından ayrıdır.',
                        'TİP kaynağı yalnız sözlük dayanağıdır',
                        'Erişilen belgenin kesim günündeki sürümü ayrıca doğrulanmamıştır.',
                        'aday, dayanak doğrulanmadı', 'Doğrulanamadı:'):
            self.assertNotIn(removed, report)
        self.assertEqual(report.count('href="#attempt-0104-tuzuk-verify"'), 1)
        self.assertIn('class="status">Doğrulanamadı</span>', report)
        text = ReaderText()
        text.feed(report)
        visible = ' '.join(text.parts)
        self.assertIn('Aktör: kurumsal', visible)
        self.assertIn('uygun', visible)
        for raw in ('eligible', 'institution', 'unverified', 'excluded', 'candidate-0105'):
            self.assertNotIn(raw, visible)
        self.assertIn('data-status="eligible"', report)
        self.assertIn('aria-label="Kaynak:', report)
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
