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
    def test_attribution_is_never_copied_from_same_hash_sibling(self):
        import copy
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'data/releases/bcc67d04d9d741e191589d0f5ac173ca/records.json').read_text())
        original=data['source_attribution'][0]
        version=next(v for v in data['document_version'] if v['id']==original['version_id'])
        passage=next(p for p in data['passage'] if p['version_id']==version['id'])
        sibling=copy.deepcopy(version);sibling['id']='test-sibling-version'
        data['document_version'].append(sibling)
        attribution=copy.deepcopy(original);attribution.update(version_id=sibling['id'],author='Farklı Yazar',publisher='Farklı Yayıncı',published_at='2000-01-01',basis='Farklı dayanak')
        data['source_attribution'].append(attribution)
        report=render_report(data)
        source=report.split('id="source-'+passage['id']+'"',1)[1].split('</details>',1)[0]
        self.assertIn(original['publisher'],source)
        for value in ('Farklı Yazar','Farklı Yayıncı','Farklı dayanak','01.01.2000'):
            self.assertNotIn(value,source)

    def test_renderer_13_reproduces_existing_release(self):
        from rapor_v13 import render_report as old_render
        root=Path(__file__).resolve().parents[1]
        release=root/'data/releases/bcc67d04d9d741e191589d0f5ac173ca'
        data=json.loads((release/'records.json').read_text())
        self.assertEqual(old_render(data),(release/'index.html').read_text())

    def test_real_browser_reads_both_passive_archives(self):
        import arsiv
        from browser_probe import probe_archives
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'data/releases'/arsiv.current()/'records.json').read_text())
        views={v['version_id']:v for v in data['archive_view']}
        self.assertEqual(len(views),len(data['archive_view']),'Arşiv sürüm kimlikleri tekil kalmalı')
        self.assertTrue({'epm-charter-v1','epm-program-v1'}.issubset(views),
                        'Sonraki parti dosyaları eklenirken iki pilot arşivi korunmalı')
        result=probe_archives((root/'data/releases'/arsiv.current()/'index.html').as_uri(),(root/'data'/views['epm-charter-v1']['index_path']).as_uri(),(root/'data'/views['epm-program-v1']['index_path']).as_uri())
        self.assertEqual(result['status'],'BROWSER_ARCHIVES_OK')
    def test_reader_shows_party_content_and_faithful_archive_links(self):
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'data/releases/b14c96c54e4b420686c46e5cfb1071a3/records.json').read_text())
        payload=json.loads((root/'data/dossiers/261111-epm-yeni-parti.json').read_text())
        data['source_policy']=[{'version':2,'legacy_findings':json.dumps([f['id'] for f in data['finding']])}]
        for row in payload['records']:
            target=data.setdefault(row['kind'],[])
            target.append(dict(dict.fromkeys(target[0],None) if target else {},**row['values']))
        report=render_report(data)
        self.assertIn('class="archive-view"',report,'Arşiv bağlantısı özgün görünümlü türeve gitmeli')
        self.assertIn('href="https://yenipartiyiz.biz"',report)
        self.assertIn('Neden kuruldu?',report)
        self.assertIn('Ne vaat ediyor?',report)
        self.assertIn('Ekonomim · Haber Merkezi',report)
        self.assertIn('Kocaeli TV · Bugün Kocaeli',report)
        self.assertIn('id="prior-yeni-parti-kurulus"',report)
        for row in (x['values'] for x in payload['records'] if x['kind']=='archive_view'):
            self.assertIn('href="../../'+row['index_path']+'"',report)

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
        self.assertIn('id="attempt-0104-tuzuk-verify"',report)
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
