"""Gerçek sürüm ve yalıtılmış bozuk veriler için faz kabulü."""
import json
from pathlib import Path
import shutil
import sqlite3
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import arsiv


class PhaseOneAcceptance(unittest.TestCase):
    def test_server_exposes_only_published_paths(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        server = subprocess.Popen([sys.executable, str(Path(arsiv.__file__)), 'serve', '--port', str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        base = 'http://127.0.0.1:%s/' % port
        try:
            for _ in range(50):
                try:
                    with urllib.request.urlopen(base + 'releases/' + arsiv.current() + '/index.html', timeout=1) as response:
                        self.assertEqual(response.status, 200)
                        response.read()
                    break
                except urllib.error.URLError:
                    if server.poll() is not None: raise AssertionError('Sunucu başlamadı')
                    time.sleep(.05)
            else:
                self.fail('Sunucu başlamadı')
            for path in ('.write.lock', 'current.json', 'objects/%2e%2e/current.json'):
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(base + path, timeout=2)
                self.assertEqual(error.exception.code, 404)
        finally:
            server.terminate()
            server.wait(timeout=5)

    def test_current_snapshot_passes(self):
        audit = getattr(arsiv, 'validate_phase_one', None)
        self.assertTrue(callable(audit), 'Faz 1 kabul denetimi sağlanmalı')
        self.assertEqual(audit('current'), arsiv.current())

    def test_missing_pilot_heading_is_rejected(self):
        audit = getattr(arsiv, 'validate_phase_one_workspace', None)
        self.assertTrue(callable(audit), 'Çalışma alanı kabul denetimi sağlanmalı')
        with tempfile.TemporaryDirectory() as directory:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(directory) / 'data'
                shutil.copytree(old, arsiv.DATA)
                work = arsiv.open_workspace(directory)
                db = arsiv.connect(Path(work) / 'records.sqlite3')
                db.execute("UPDATE missing SET heading='Bozuk' WHERE heading='Tüzük'")
                db.commit(); db.close()
                with self.assertRaises(ValueError):
                    audit(work)
            finally:
                arsiv.DATA = old

    def test_comparison_needs_evidence_and_preserves_multiple_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(directory) / 'data'
                shutil.copytree(old, arsiv.DATA)
                work = arsiv.open_workspace(directory)
                path = Path(work) / 'records.sqlite3'
                db = arsiv.connect(path)
                ids = [r['id'] for r in db.execute('SELECT id FROM passage LIMIT 2')]
                db.execute("INSERT INTO comparison VALUES ('test-comparison','test-topic','candidate')")
                db.commit()
                with self.assertRaises(ValueError):
                    arsiv.export_db(path, 'test')
                db.executemany('INSERT INTO comparison_evidence VALUES (?,?)', [('test-comparison', i) for i in ids])
                db.commit(); db.close()
                result = arsiv.export_db(path, 'test')
                self.assertEqual({e['passage_id'] for e in result['comparison_evidence'] if e['comparison_id']=='test-comparison'}, set(ids))
                with arsiv.connect(path) as db, self.assertRaises(sqlite3.IntegrityError):
                    db.execute("INSERT INTO comparison_evidence VALUES ('test-comparison','yok')")
            finally:
                arsiv.DATA = old


if __name__ == '__main__':
    unittest.main()
