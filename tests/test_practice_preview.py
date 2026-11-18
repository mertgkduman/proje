"""Acceptance checks for isolated practice package operations."""
import subprocess
import sys
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import sqlite3

import arsiv
import kaynaklar


class PracticePreview(unittest.TestCase):
    def test_attribution_reads_explicit_storage_root(self):
        db = sqlite3.connect(':memory:')
        db.row_factory = sqlite3.Row
        self.addCleanup(db.close)
        db.executescript('''CREATE TABLE party(id TEXT, legal_name TEXT);
            CREATE TABLE document(id TEXT, party_id TEXT, source_kind TEXT);
            CREATE TABLE document_version(id TEXT, document_id TEXT, original_url TEXT, final_url TEXT, original_path TEXT, mime TEXT);
            CREATE TABLE source_attribution(version_id TEXT, kind TEXT, publisher TEXT);
            INSERT INTO party VALUES ('p','Example Party');
            INSERT INTO document VALUES ('d','p','party');
            INSERT INTO document_version VALUES ('v','d','https://example.org/', 'https://example.org/', 'source.html', 'text/html');''')
        attr = dict(version_id='v', kind='party_publication', publisher='Example Party',
                    basis='technical fixture', public_url='https://example.org/',
                    published_at='2026-01-01', date_precision='day')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'source.html').write_text('Example Party', encoding='utf-8')
            self.assertTrue(kaynaklar.check_attribution(db, attr, storage_root=root))
            (root / 'source.html').write_text('Different publisher', encoding='utf-8')
            with self.assertRaises(ValueError):
                kaynaklar.check_attribution(db, attr, storage_root=root)

    def test_legacy_tracer_preview_keeps_global_state(self):
        current = arsiv.DATA / 'current.json'
        before = hashlib.sha256(current.read_bytes()).hexdigest()
        db = arsiv.DATA / 'releases' / arsiv.current() / 'records.sqlite3'
        database_before = hashlib.sha256(db.read_bytes()).hexdigest()
        lock = arsiv.DATA / '.write.lock'
        lock_before = lock.read_bytes() if lock.exists() else None
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'preview'
            result = subprocess.run([sys.executable, str(arsiv.ROOT / 'src' / 'arsiv.py'),
                                     'practice-preview', '--input', str(arsiv.DATA / 'practices' / '04-tracer.json'),
                                     '--inventory', str(arsiv.DATA / 'practices' / '04-inventory.json'),
                                     '--out', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('PRACTICE_PREVIEW_OK', result.stdout)
            for name in ('records.sqlite3', 'records.json', 'index.html', 'manifest.json'):
                self.assertTrue((out / name).is_file(), name)
            snapshot = json.loads((out / 'records.json').read_text(encoding='utf-8'))
            self.assertEqual(arsiv.export_db(out / 'records.sqlite3', snapshot['release_id']), snapshot)
            report = (out / 'index.html').read_text(encoding='utf-8')
            for view in ('party', 'comparison'):
                self.assertIn('id="' + view + '-practice-tracer-relation-id"', report)
            coverage_out = Path(tmp) / 'coverage-preview'
            coverage = subprocess.run([sys.executable, str(arsiv.ROOT / 'src' / 'arsiv.py'),
                                       'practice-preview', '--input', str(arsiv.DATA / 'practices' / '04-coverage-tracer.json'),
                                       '--inventory', str(arsiv.DATA / 'practices' / '04-inventory.json'),
                                       '--out', str(coverage_out)], capture_output=True, text=True)
            self.assertEqual(coverage.returncode, 0, coverage.stderr)
            self.assertIn('PRACTICE_PREVIEW_OK', coverage.stdout)
            coverage_snapshot = json.loads((coverage_out / 'records.json').read_text(encoding='utf-8'))
            self.assertEqual(arsiv.export_db(coverage_out / 'records.sqlite3', coverage_snapshot['release_id']), coverage_snapshot)
            self.assertTrue(coverage_snapshot['practice_coverage_contract'])
        self.assertEqual(before, hashlib.sha256(current.read_bytes()).hexdigest())
        self.assertEqual(database_before, hashlib.sha256(db.read_bytes()).hexdigest())
        self.assertEqual(lock_before, lock.read_bytes() if lock.exists() else None)

    def test_invalid_inventory_preserves_existing_output(self):
        inventory_path = arsiv.DATA / 'practices' / '04-inventory.json'
        inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
        inventory['cells'].pop()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invalid = root / 'invalid.json'
            invalid.write_text(json.dumps(inventory), encoding='utf-8')
            out = root / 'existing'
            out.mkdir()
            sentinel = out / 'sentinel'
            sentinel.write_bytes(b'unchanged')
            result = subprocess.run([sys.executable, str(arsiv.ROOT / 'src' / 'arsiv.py'),
                                     'practice-preview', '--input', str(arsiv.DATA / 'practices' / '04-tracer.json'),
                                     '--inventory', str(invalid), '--out', str(out)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(out.iterdir()), [sentinel])
            self.assertEqual(sentinel.read_bytes(), b'unchanged')

    def test_preview_command_is_available(self):
        result = subprocess.run([sys.executable, str(arsiv.ROOT / 'src' / 'arsiv.py'),
                                 'practice-preview', '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, 'isolated preview CLI must be available')
        for option in ('--input', '--out', '--inventory', '--base-release'):
            self.assertIn(option, result.stdout)

    def test_merge_and_source_review_commands_are_available(self):
        for name in ('practice-merge', 'practice-source-check'):
            with self.subTest(command=name):
                result = subprocess.run([sys.executable, str(arsiv.ROOT / 'src' / 'arsiv.py'),
                                         name, '--help'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, name + ' CLI must be available')
