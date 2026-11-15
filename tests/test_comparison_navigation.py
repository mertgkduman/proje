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
import hashlib
import datetime
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
 checks.push(s.id==='source-0306-iyi-program-demokrasi-katilim-principle-passage' && s.open && s.checkVisibility() && document.activeElement===s && s.innerText.includes('0205-iyi-program-page-v1') && s.innerText.includes('Demokrasi ve hukuk') && !!s.querySelector('a.archive-view[href="../../views/ecc51c44806790d9980a80aebb940c57/index.html"]'));
 history.back(); await pause(); checks.push(document.activeElement===cite && cite.checkVisibility());
 history.forward(); await pause(); checks.push(document.activeElement===s && s.open && s.checkVisibility());
 history.back(); await pause(); cite.click(); await pause();
 checks.push(document.documentElement.scrollWidth<=innerWidth);
 const old=document.activeElement; location.hash='#%ZZ'; await pause(); checks.push(document.activeElement===old);
 const scope='04-03-v3-0306-iyi-scope-parti-yardim-kampanya-absence';
 const proof=document.querySelector('a[href="#comparison-'+scope+'"]');
 const scopeRow=document.getElementById('comparison-'+scope);
 checks.push(!!proof && !!scopeRow && scopeRow.innerText.includes('İncelenen kapsam:'));
 document.getElementById('tab-comparison').click();proof.click();await pause();
 checks.push(document.activeElement===scopeRow && scopeRow.checkVisibility() && !!scopeRow.querySelector('a[href^="../../"]'));
 const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);checks.push(ids.length===new Set(ids).size);
 const tab=document.getElementById('tab-comparison');const event=new KeyboardEvent('keydown',{key:'ArrowUp',bubbles:true,cancelable:true});tab.dispatchEvent(event);checks.push(!event.defaultPrevented);
 const names=[...new Set([...a.closest('.comparison-topic').querySelectorAll(':scope > article.comparison-row > h4')].map(x=>x.textContent))];
 checks.push(JSON.stringify(names)===JSON.stringify(['YENİ PARTİ','TÜRKİYE İŞÇİ PARTİSİ','HALKLARIN EŞİTLİK VE DEMOKRASİ PARTİSİ','İYİ PARTİ','YENİ YOL','DEMOKRATİK BÖLGELER PARTİSİ','EMEK PARTİSİ','SAADET PARTİSİ','DEMOKRAT PARTİ']));
 checks.push(!document.getElementById('scope-method').open && !!a.closest('.comparison-topic').querySelector(':scope > p.summary'));
 tab.focus();tab.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true,cancelable:true}));
 checks.push(document.activeElement.id==='tab-demokrat' && document.activeElement.getAttribute('aria-selected')==='true' && document.activeElement.tabIndex===0 && document.getElementById('party-demokrat').hidden===false);
 document.body.dataset.navigationChecks=checks.map(Number).join('');
})().catch(e=>document.body.dataset.navigationError=e.message);
</script>'''.replace('ROW', row)
        source = REPORT.read_text(encoding='utf-8').replace('</html>', marker + '</html>')
        outcomes = []
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
                            probe = ROOT / '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks/probe-navigation.cjs'
                            result = subprocess.run(['node', str(probe), executable, url + '#comparison-' + row, str(width)], capture_output=True, text=True, timeout=130)
                            self.assertEqual(result.returncode, 0, result.stderr[-500:])
                            observed = json.loads(result.stdout)
                            self.assertEqual(observed['width'], width)
                            self.assertEqual(observed['checks'], '1111111111111111111')
                            outcomes.append({'scheme': 'file' if url.startswith('file:') else 'http', 'width': observed['width'], 'checks': observed['checks'], 'url': url + '#comparison-' + row})
            finally:
                server.shutdown(); server.server_close(); thread.join()
        self.assertEqual(len(outcomes), 4, 'Dört tarayıcı koşulu tamamlanmadı')
        if output := os.environ.get('NAV_EVIDENCE'):
            release = json.loads((ROOT / 'data/current.json').read_text())['release_id']
            if REPORT.resolve() != (ROOT / 'data/releases' / release / 'index.html').resolve():
                self.fail('Kanıt tam olarak geçerli yayına bağlanmalı')
            if records_path.resolve() != (ROOT / 'data/releases' / release / 'records.json').resolve():
                self.fail('Kanıtın kayıtları raporla aynı yayından gelmeli')
            payload = {'release_id': release, 'report_sha256': hashlib.sha256(REPORT.read_bytes()).hexdigest(),
                       'records_sha256': hashlib.sha256(records_path.read_bytes()).hexdigest(),
                       'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       'command': 'python3 tests/run.py --pattern test_comparison_navigation.py',
                       'row_id': row, 'source_version': version['id'], 'archive': view['index_path'], 'results': outcomes}
            Path(output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    unittest.main()
