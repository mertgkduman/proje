"""Gerçek, değiştirilmemiş rapor ve arşivde Chromium gezinti kabulü."""
import datetime
import functools
import hashlib
from html.parser import HTMLParser
import http.server
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from urllib.parse import quote, urldefrag

from browser_probe import browser

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
RELEASE = json.loads((DATA / 'current.json').read_text())['release_id']
REPORT = Path(os.environ.get('NAV_REPORT', DATA / 'releases' / RELEASE / 'index.html')).resolve()
RECORDS = Path(os.environ.get('NAV_RECORDS', DATA / 'releases' / RELEASE / 'records.json')).resolve()
PROBE = ROOT / 'tests/comparison_navigation.cjs'


def selected_records(records_path=RECORDS):
    records = json.loads(records_path.read_text())
    taxonomy = records['comparison_contract'][0]['taxonomy_version']
    rows = records['comparison_row']
    def one(**criteria):
        found = [r for r in rows if r['taxonomy_version'] == taxonomy and all(r[k] == v for k, v in criteria.items())]
        if len(found) != 1:
            raise AssertionError('Seçili konu/parti/kaynak kaydı tek değil: ' + str(criteria))
        return found[0]
    row = one(party_id='iyi', topic_id='demokrasi-katilim', state='evidence', version_id='0205-iyi-program-page-v1')
    scope = one(party_id='iyi', topic_id='parti-yardim-kampanya', state='no_explicit_statement', version_id='0205-iyi-charter-download-v1')
    review = next(s for s in records['comparison_review_scope'] if s['id'] == scope['scope_id'])
    if not all(word in (review['sections'] + ' ' + review['reason']).lower() for word in ('kampanya',)):
        raise AssertionError('Kapsam kaydı beklenen somut soruyu karşılamıyor')
    field = next(f for f in records['comparison_field'] if f['row_id'] == row['id'] and f['field'] == 'principle')
    refs = [e['passage_id'] for e in records['finding_evidence'] if e['finding_id'] == field['summary_finding_id']]
    passage = next(p for p in records['passage'] if p['id'] in refs and p['version_id'] == row['version_id'] and 'Sağlıklı işleyen bir demokrasi' in p['exact'])
    version = next(v for v in records['document_version'] if v['id'] == row['version_id'])
    view = next(v for v in records['archive_view'] if v['version_id'] == version['id'])
    if view['source_sha256'] != version['sha256'] or not (DATA / view['index_path']).is_file():
        raise AssertionError('Arşiv özgün sürümle uyuşmuyor')
    names = [next(p['legal_name'] for p in records['party'] if p['id'] == x) for x in ('yeni-parti','tip','dem','iyi','yeni-yol','dbp','emep','saadet','demokrat')]
    return {'row': row['id'], 'scope': scope['id'], 'passage': passage['id'], 'version': version['id'],
            'locator': passage['section'], 'archive': view['index_path'], 'excerpt': 'Sağlıklı işleyen bir demokrasi', 'names': names}


class ComparisonNavigation(unittest.TestCase):
    def test_preview_places_rows_by_topic_domain_and_frozen_20_is_exact(self):
        import sys
        sys.path.insert(0, str(ROOT / 'src'))
        from rapor import render_report
        from rapor_v20 import render_report as render_20
        from rapor_v21 import render_report as render_21
        from arsiv import comparison_render_data
        folder = DATA / 'releases' / 'ef353c40c60b400eb1c52b3245e9a65b'
        records = json.loads((folder / 'records.json').read_text())
        snapshot = comparison_render_data(records)
        self.assertEqual(render_20(snapshot).encode(), (folder / 'index.html').read_bytes())
        old21 = DATA / 'releases' / 'd8d06dbe3a794d2fb92459391af5a549'
        old21_data = json.loads((old21 / 'records.json').read_text())
        self.assertEqual(render_21(comparison_render_data(old21_data)).encode(), (old21 / 'index.html').read_bytes())
        class Sections(HTMLParser):
            def __init__(self):
                super().__init__(); self.sections = []; self.rows = {}
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == 'section': self.sections.append(attrs.get('id'))
                if tag == 'article' and attrs.get('id', '').startswith('dossier-comparison-'):
                    self.rows[attrs['id'][len('dossier-comparison-'):]] = self.sections[-1]
            def handle_endtag(self, tag):
                if tag == 'section': self.sections.pop()
        parser = Sections(); parser.feed(render_report(snapshot))
        topics = {(t['topic_id'], t['taxonomy_version']): t['domain'] for t in snapshot['comparison_topic']}
        for row in snapshot['comparison_row']:
            section = {'charter': 'tuzuk', 'program': 'program'}[topics[row['topic_id'], row['taxonomy_version']]]
            self.assertEqual(parser.rows[row['id']], 'party-' + row['party_id'] + '-' + section)

    def invoke(self, url, width, config):
        executable = browser()
        self.assertIsNotNone(executable, 'Chromium bulunamadı')
        target = url + '#comparison-' + quote(config['row'], safe='')
        result = subprocess.run(['node', str(PROBE), executable, target, str(width), json.dumps(config, ensure_ascii=False)], capture_output=True, text=True, timeout=160)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        observed = json.loads(result.stdout)
        self.assertEqual(urldefrag(observed['requested'])[0], url)
        self.assertEqual(urldefrag(observed['actual'])[0], url)
        self.assertEqual(observed['width'], width)
        return observed

    def test_direct_hash_reveals_and_focuses_same_row(self):
        config = selected_records()
        observed = self.invoke(REPORT.as_uri(), 1365, dict(config, direct=True))
        self.assertTrue(observed['exists'] and observed['focused'] and observed['visible'])

    def test_unicode_and_space_ids_in_real_source_preview(self):
        import sys
        sys.path.insert(0, str(ROOT / 'src'))
        from arsiv import comparison_render_data
        from rapor import render_report
        # Resolve the published selection before assigning hostile preview IDs.
        # Serialized v2 revision selections deliberately retain original IDs;
        # they are provenance, not input to this URL/DOM rendering fixture.
        records = comparison_render_data(json.loads(RECORDS.read_text()))
        original = selected_records()
        def rename(value):
            if isinstance(value, str): return aliases.get(value, value)
            if isinstance(value, list): return [rename(x) for x in value]
            if isinstance(value, dict): return {k: rename(v) for k, v in value.items()}
            return value
        with tempfile.TemporaryDirectory(prefix='nav-preview-', dir=DATA / 'releases') as tmp:
            report = Path(tmp) / 'index.html'
            for token in ('%', '%20', '%ZZ'):
                with self.subTest(token=token):
                    aliases = {original['row']: 'gezinti ' + token + ' #?/&"\' ş', original['passage']: 'kaynak ' + token + ' #?/&"\' ğ'}
                    preview = rename(records)
                    config = dict(original, row=aliases[original['row']], passage=aliases[original['passage']])
                    report.write_text(render_report(preview), encoding='utf-8')
                    direct = self.invoke(report.as_uri(), 1365, dict(config, direct=True))
                    self.assertTrue(direct['exists'] and direct['focused'] and direct['visible'])
                    observed = self.invoke(report.as_uri(), 360, config)
                    self.assertEqual(observed['checks'], '1' * 19)
                    self.assertTrue(observed['archiveExcerptFound'])

    def test_four_browser_navigation_modes(self):
        config = selected_records()
        self.assertEqual(REPORT, (DATA / 'releases' / RELEASE / 'index.html').resolve())
        self.assertEqual(RECORDS, (DATA / 'releases' / RELEASE / 'records.json').resolve())
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DATA))
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        outcomes = []
        try:
            urls = [REPORT.as_uri(), 'http://127.0.0.1:%d/%s' % (server.server_port, REPORT.relative_to(DATA).as_posix())]
            for url in urls:
                for width in (360, 1365):
                    with self.subTest(url=url, width=width):
                        observed = self.invoke(url, width, config)
                        self.assertEqual(observed['checks'], '1' * 19)
                        self.assertTrue(observed['archiveExcerptFound'])
                        outcomes.append(dict(scheme='file' if url.startswith('file:') else 'http', **observed))
        finally:
            server.shutdown(); server.server_close(); thread.join()
        self.assertEqual(len(outcomes), 4)
        if output := os.environ.get('NAV_EVIDENCE'):
            payload = {'release_id': RELEASE, 'report_sha256': hashlib.sha256(REPORT.read_bytes()).hexdigest(),
                       'records_sha256': hashlib.sha256(RECORDS.read_bytes()).hexdigest(),
                       'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       'command': 'python3 tests/run.py --pattern test_comparison_navigation.py',
                       'row_id': config['row'], 'source_version': config['version'], 'archive': config['archive'], 'results': outcomes}
            Path(output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    unittest.main()
