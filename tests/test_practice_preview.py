"""Acceptance checks for isolated practice package operations."""
import subprocess
import sys
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import sqlite3
from html.parser import HTMLParser
from urllib.parse import unquote
from unittest.mock import patch

import arsiv
import kaynaklar
import uygulamalar


class PracticePreview(unittest.TestCase):
    def test_party_source_capture_root_api(self):
        import io
        from email.message import Message
        response = io.BytesIO(b'<html><body>Technical source</body></html>')
        response.headers = Message()
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.geturl = lambda: 'https://example.org/source'
        with tempfile.TemporaryDirectory() as tmp, patch('arsiv.urllib.request.urlopen', return_value=response):
            root = Path(tmp)
            try:
                capture = arsiv.capture_source('https://example.org/source', 'html',
                                               root / 'practices/sources/yeni-parti', storage_root=root)
            except TypeError as exc:
                self.fail('capture must support an explicit private storage root: ' + str(exc))
            self.assertEqual((root / capture['original_path']).read_bytes(), b'<html><body>Technical source</body></html>')
            self.assertTrue(capture['original_path'].startswith('practices/sources/yeni-parti/'))

    def test_shared_release_manifest_and_audit_contract(self):
        self.assertTrue(callable(getattr(arsiv, 'build_release_manifest', None)),
                        'preview and publishing must share the standard manifest builder')

    def test_preview_rejects_nonlocal_sqlite_before_creating_output(self):
        payload = json.loads((arsiv.DATA / 'practices' / '04-coverage-tracer.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'preview'
            with patch('arsiv.subprocess.check_output', return_value='nfs\n'), \
                    patch('tempfile.TemporaryDirectory', side_effect=AssertionError('unsafe SQLite staging started')):
                with self.assertRaisesRegex(ValueError, 'yerel dosya sistemi'):
                    uygulamalar.render_practice_preview(payload, out)
            self.assertFalse(out.exists())
            self.assertEqual(list(Path(tmp).iterdir()), [])

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
            db.execute("UPDATE document_version SET original_path='../outside.html'")
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
            self.assertTrue((out / 'releases').is_dir(), 'preview must use standard release layout')
            releases = list((out / 'releases').iterdir())
            self.assertEqual(len(releases), 1)
            release_dir = releases[0]
            for name in ('records.sqlite3', 'records.json', 'index.html', 'manifest.json'):
                self.assertTrue((release_dir / name).is_file(), name)
            manifest = json.loads((release_dir / 'manifest.json').read_text(encoding='utf-8'))
            for field in ('phase2_delivery', 'source_policy_version', 'comparison_stage', 'practice_stage'):
                self.assertIn(field, manifest)
            self.assertEqual(arsiv.audit_release(release_dir.name, storage_root=out), release_dir.name)
            asset = out / next(iter(manifest['asset_files']))
            original = asset.read_bytes()
            asset.write_bytes(original + b'corrupt')
            with self.assertRaises(ValueError):
                arsiv.audit_release(release_dir.name, storage_root=out)
            asset.write_bytes(original)
            report_file = release_dir / 'index.html'
            original_report = report_file.read_bytes()
            report_file.write_bytes(original_report + b'<!-- tampered -->')
            manifest['files']['index.html'] = hashlib.sha256(report_file.read_bytes()).hexdigest()
            (release_dir / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'HTML kapalı snapshot'):
                arsiv.audit_release(release_dir.name, storage_root=out)
            report_file.write_bytes(original_report)
            manifest['files']['index.html'] = hashlib.sha256(original_report).hexdigest()
            (release_dir / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            snapshot = json.loads((release_dir / 'records.json').read_text(encoding='utf-8'))
            self.assertEqual(arsiv.export_db(release_dir / 'records.sqlite3', snapshot['release_id'], storage_root=out), snapshot)
            report = (release_dir / 'index.html').read_text(encoding='utf-8')
            class Links(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.paths = []

                def handle_starttag(self, tag, attrs):
                    self.paths.extend(value for name, value in attrs if name == 'href' and value and value.startswith('../../'))
            links = Links()
            links.feed(report)
            self.assertTrue(links.paths)
            for path in links.paths:
                self.assertTrue((release_dir / unquote(path.split('#')[0])).is_file(), path)
            for view in ('party', 'comparison'):
                self.assertIn('id="' + view + '-practice-tracer-relation-id"', report)
            coverage_out = Path(tmp) / 'coverage-preview'
            coverage = subprocess.run([sys.executable, str(arsiv.ROOT / 'src' / 'arsiv.py'),
                                       'practice-preview', '--input', str(arsiv.DATA / 'practices' / '04-coverage-tracer.json'),
                                       '--inventory', str(arsiv.DATA / 'practices' / '04-inventory.json'),
                                       '--out', str(coverage_out)], capture_output=True, text=True)
            self.assertEqual(coverage.returncode, 0, coverage.stderr)
            self.assertIn('PRACTICE_PREVIEW_OK', coverage.stdout)
            coverage_dir = next((coverage_out / 'releases').iterdir())
            coverage_snapshot = json.loads((coverage_dir / 'records.json').read_text(encoding='utf-8'))
            self.assertEqual(arsiv.export_db(coverage_dir / 'records.sqlite3', coverage_snapshot['release_id'], storage_root=coverage_out), coverage_snapshot)
            self.assertEqual(arsiv.audit_release(coverage_dir.name, storage_root=coverage_out), coverage_dir.name)
            coverage_report = (coverage_dir / 'index.html').read_text(encoding='utf-8')
            for view in ('party', 'comparison'):
                self.assertIn('id="' + view + '-practice-tracer-relation-id"', coverage_report)
            coverage_links = Links()
            coverage_links.feed(coverage_report)
            self.assertTrue(coverage_links.paths)
            for path in coverage_links.paths:
                self.assertTrue((coverage_dir / unquote(path.split('#')[0])).is_file(), path)
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

    def test_merge_reports_undecided_shared_event_without_overwriting(self):
        package = json.loads((arsiv.DATA / 'practices' / '04-coverage-tracer.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / 'first.json'
            second = root / 'second.json'
            first.write_text(json.dumps(package), encoding='utf-8')
            def rename(value):
                if isinstance(value, dict):
                    return {key: rename(item) for key, item in value.items()}
                if isinstance(value, list):
                    return [rename(item) for item in value]
                return 'temporary-event' if value == 'tracer-cesme' else value
            second.write_text(json.dumps(rename(package)), encoding='utf-8')
            out = root / 'merged.json'
            out.write_bytes(b'unchanged')
            result = subprocess.run([sys.executable, str(arsiv.ROOT / 'src' / 'arsiv.py'),
                                     'practice-merge', '--inventory', str(arsiv.DATA / 'practices' / '04-inventory.json'),
                                     '--inputs', str(first), str(second), '--out', str(out)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(out.read_bytes(), b'unchanged')
            try:
                diagnostic = json.loads(result.stderr)
            except json.JSONDecodeError:
                self.fail('merge must report undecided candidates as JSON')
            self.assertTrue(diagnostic['candidates'])

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
