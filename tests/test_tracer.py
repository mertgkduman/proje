import pathlib
import subprocess
import sys
import unittest
import json
import hashlib
import sqlite3

from browser_probe import probe

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TracerTest(unittest.TestCase):
    def test_real_evidence_chain(self):
        result = subprocess.run([sys.executable, str(ROOT / 'src/arsiv.py'), 'audit', '--release', 'current'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('AUDIT_OK', result.stdout)
        report = (ROOT / 'data/current.json').read_text(encoding='utf-8')
        self.assertIn('release_id', report)
        release = json.loads(report)['release_id']
        folder = ROOT / 'data/releases' / release
        payload = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        version = payload['document_version'][0]
        raw = (ROOT / 'data' / version['original_path']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), version['sha256'])
        self.assertIn('Kuruluş Tarihi', raw.decode('utf-8'))
        with sqlite3.connect(folder / 'records.sqlite3') as db:
            self.assertEqual(db.execute('select exact from passage').fetchone()[0], '24.07.2026')
            self.assertEqual(db.execute("select count(*) from finding_evidence where finding_id in ('kurulus-summary', 'kurulus-quote') and passage_id='kurulus'").fetchone()[0], 2)
        page = (folder / 'index.html').read_text(encoding='utf-8')
        self.assertIn('#003366', page)
        self.assertIn('“24.07.2026”', page)
        self.assertEqual(probe(folder / 'index.html'), 'BROWSER_CLICK_OK')
