"""Gerçek kapalı raporda karşılaştırma bağlantısının odağını denetle."""
import subprocess
import tempfile
import unittest
import os
import functools
import http.server
import threading
import re
import urllib.request
from pathlib import Path

from browser_probe import browser

ROOT = Path(__file__).resolve().parents[1]
import json
REPORT = Path(os.environ.get('NAV_REPORT', ROOT / 'data/releases' / json.loads((ROOT / 'data/current.json').read_text())['release_id'] / 'index.html'))


class ComparisonNavigation(unittest.TestCase):
    def test_direct_hash_reveals_and_focuses_same_row(self):
        executable = browser()
        self.assertIsNotNone(executable, 'Chromium bulunamadı')
        source = REPORT.read_text(encoding='utf-8')
        marker = '''<script>setTimeout(()=>{const e=document.getElementById('comparison-04-03-v3-03-v2-iyi-demokrasi');document.body.dataset.targetExists=String(!!e);document.body.dataset.focusCheck=String(!!e && e===document.activeElement && !e.closest('[role=tabpanel]').hidden)},200)</script>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'index.html'
            path.write_text(source.replace('</html>', marker + '</html>'), encoding='utf-8')
            result = subprocess.run([executable, '--headless', '--no-sandbox', '--disable-gpu', '--virtual-time-budget=1000', '--dump-dom', path.as_uri() + '#comparison-04-03-v3-03-v2-iyi-demokrasi'], capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr[-1000:])
        self.assertTrue('data-target-exists="true"' in result.stdout, 'Kanonik hedef yok')
        self.assertTrue('data-focus-check="true"' in result.stdout, 'Doğrudan hedef odaklanmadı')

    def test_four_browser_navigation_modes(self):
        executable = browser()
        self.assertIsNotNone(executable, 'Chromium bulunamadı')
        records_path = Path(os.environ.get('NAV_RECORDS', ROOT / 'data/releases' / json.loads((ROOT / 'data/current.json').read_text())['release_id'] / 'records.json'))
        records = json.loads(records_path.read_text())
        selected = next(r for r in records['comparison_row'] if r['id'] == '04-03-v3-03-v2-iyi-demokrasi')
        self.assertEqual((selected['party_id'], selected['version_id'], selected['taxonomy_version']), ('iyi', '0205-iyi-program-page-v1', 4))
        version = next(v for v in records['document_version'] if v['id'] == '0205-iyi-program-page-v1')
        view = next(v for v in records['archive_view'] if v['version_id'] == version['id'])
        self.assertEqual(view['source_sha256'], version['sha256'])
        self.assertTrue((ROOT / 'data' / view['index_path']).is_file())
        row = '04-03-v3-03-v2-iyi-demokrasi'
        marker = '''<script>
(async()=>{
 const checks=[]; const pause=()=>new Promise(r=>setTimeout(r,150));
 const a=document.getElementById('comparison-ROW');
 checks.push(!!a && document.activeElement===a && a.checkVisibility());
 checks.push(!!a.querySelector('.summary') && !!a.querySelector('.quote') && !!a.querySelector('.citation'));
 checks.push(getComputedStyle(a.querySelector('.quote')).color==='rgb(0, 0, 0)' && getComputedStyle(a.querySelector('.summary')).color==='rgb(0, 51, 102)');
 a.querySelector('a[href="#dossier-comparison-ROW"]').click(); await pause();
 const d=document.getElementById('dossier-comparison-ROW');
 checks.push(d.checkVisibility() && document.activeElement===d && d.closest('[role=tabpanel]').id==='party-iyi');
 d.querySelector('a[href="#comparison-ROW"]').click(); await pause();
 checks.push(a.checkVisibility() && document.activeElement===a && a.closest('[role=tabpanel]').id==='comparison-summary');
 history.back(); await pause(); checks.push(document.activeElement===d && d.checkVisibility());
 history.forward(); await pause(); checks.push(document.activeElement===a && a.checkVisibility());
 const cite=a.querySelector('.citation'); cite.click(); await pause();
 const s=document.getElementById(cite.hash.slice(1));
 checks.push(s.open && s.checkVisibility() && document.activeElement===s && s.innerText.includes('0205-iyi-program-page-v1') && !!s.querySelector('a[href^="../../"]'));
 checks.push(document.documentElement.scrollWidth<=innerWidth);
 const old=document.activeElement; location.hash='#%ZZ'; await pause(); checks.push(document.activeElement===old);
 const scope='04-03-v3-0306-iyi-scope-parti-yardim-kampanya-absence';
 const proof=document.querySelector('a[href="#comparison-'+scope+'"]');
 const scopeRow=document.getElementById('comparison-'+scope);
 checks.push(!!proof && !!scopeRow && scopeRow.innerText.includes('İncelenen kapsam:'));
 const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);checks.push(ids.length===new Set(ids).size);
 document.body.dataset.navigationChecks=checks.map(Number).join('');
})().catch(e=>document.body.dataset.navigationError=e.message);
</script>'''.replace('ROW', row)
        source = REPORT.read_text(encoding='utf-8').replace('</html>', marker + '</html>')
        with tempfile.TemporaryDirectory(dir=ROOT / 'data/releases') as tmp:
            path = Path(tmp) / 'index.html'
            path.write_text(source, encoding='utf-8')
            handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / 'data'))
            server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
            try:
                urls = [path.as_uri(), 'http://127.0.0.1:%d/%s' % (server.server_port, path.relative_to(ROOT / 'data').as_posix())]
                with urllib.request.urlopen('http://127.0.0.1:%d/%s' % (server.server_port, view['index_path']), timeout=10) as archive:
                    self.assertEqual(archive.status, 200)
                    self.assertGreater(len(archive.read()), 0)
                for url in urls:
                    for width in (360, 1365):
                        with self.subTest(url=url, width=width):
                            result = subprocess.run([executable, '--headless', '--no-sandbox', '--disable-gpu', '--window-size=%d,900' % width, '--virtual-time-budget=5000', '--dump-dom', url + '#comparison-' + row], capture_output=True, text=True, timeout=120)
                            self.assertEqual(result.returncode, 0, result.stderr[-500:])
                            checks = re.search(r'data-navigation-(?:checks|error)="[^"]*"', result.stdout)
                            self.assertIsNotNone(checks, 'Tarayıcı sonucu üretilmedi')
                            self.assertEqual(checks.group(), 'data-navigation-checks="111111111111"')
            finally:
                server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__':
    unittest.main()
