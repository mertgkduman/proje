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
    def test_shared_source_rejects_wrong_version_passage(self):
        snapshot = arsiv.DATA / 'releases' / arsiv.current() / 'records.json'
        data = json.loads(snapshot.read_text())
        passage = data['passage'][0]
        other = next(row for row in data['document_version'] if row['id'] != passage['version_id'])
        data['practice_source_party'].append(dict(version_id=other['id'], passage_id=passage['id'],
                                                  party_id=data['party'][0]['id'], scope_reason='technical mismatch'))
        with self.assertRaisesRegex(ValueError, 'Kaynak parti kapsamı geçersiz'):
            uygulamalar.validate_practices(data)

    def test_source_owner_cannot_be_forged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = sqlite3.connect(root / 'records.sqlite3')
            db.executescript("CREATE TABLE document(id TEXT PRIMARY KEY,party_id TEXT); INSERT INTO document VALUES('foreign','tip');")
            db.close()
            scope = []
            package = dict(base_release='base', contract_version=1, stage='tracer', taxonomy_version=4,
                           party_id='yeni-parti', scope_inventory=scope,
                           entries=[dict(kind='document_version', values=dict(id='foreign-version', document_id='foreign'))],
                           practice_records=dict(practice_contract=[dict(stage='tracer', inventory_digest=uygulamalar._digest(scope))]))
            with patch('uygulamalar.migrate_practice_workspace'):
                with self.assertRaisesRegex(ValueError, 'parti sahibine'):
                    uygulamalar._load_practice_copy(root, package, 'base', storage_root=root)

    def test_private_capture_rejects_root_escape_and_passive_script(self):
        import arsiv_gorunum
        import io
        from email.message import Message
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'root'
            root.mkdir()
            (root / 'escape').symlink_to(Path(tmp), target_is_directory=True)
            with self.assertRaises(ValueError):
                arsiv.capture_source('https://example.org/', 'html', root / 'escape/out', storage_root=root)
            values = dict(sha256='a' * 64, mime='text/html', original_path='objects/' + 'a' * 64 + '/../../escape')
            with self.assertRaises(ValueError):
                uygulamalar._validate_new_source_path(values, 'original_path')
            raw = b'<p>technical</p>'
            view = arsiv_gorunum.build_view(raw, 'https://example.org/', root, fetch_assets=False)
            manifest_path = root / view['manifest_path']
            manifest = json.loads(manifest_path.read_text())
            index = root / view['index_path']
            index.write_text(index.read_text() + '<script>bad()</script>')
            manifest['files']['index.html'] = arsiv.sha(root / view['index_path'])
            identity = {key: value for key, value in manifest.items() if key != 'view_id'}
            new_id = hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()[:32]
            new_folder = root / 'views' / new_id
            manifest_path.parent.rename(new_folder)
            manifest['view_id'] = new_id
            view.update(view_id=new_id, index_path='views/' + new_id + '/index.html', manifest_path='views/' + new_id + '/manifest.json')
            manifest_path = root / view['manifest_path']
            manifest_path.write_text(json.dumps(manifest))
            view['manifest_sha256'] = arsiv.sha(manifest_path)
            with self.assertRaisesRegex(ValueError, 'etkin öğe'):
                arsiv_gorunum.validate_view(root, view)

    def test_new_source_end_to_end(self):
        import io
        from email.message import Message
        import arsiv_gorunum
        raw = b'<html><body>Technical fixture passage<script>bad()</script></body></html>'
        response = io.BytesIO(raw)
        response.headers = Message()
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.geturl = lambda: 'https://example.org/source'
        package = json.loads((arsiv.DATA / 'practices/04-coverage-tracer.json').read_text())
        inventory = json.loads((arsiv.DATA / 'practices/04-inventory.json').read_text())
        current_before = arsiv.sha(arsiv.DATA / 'current.json')
        db_path = arsiv.DATA / 'releases' / arsiv.current() / 'records.sqlite3'
        db_before = arsiv.sha(db_path)
        self.assertFalse((arsiv.DATA / '.write.lock').exists())
        with tempfile.TemporaryDirectory() as tmp, patch('arsiv.urllib.request.urlopen', return_value=response):
            root = Path(tmp)
            source_root = root / 'practices/sources/yeni-parti'
            source_root.mkdir(parents=True)
            try:
                capture = arsiv.capture_source('https://example.org/source', 'html', storage_root=source_root)
            except TypeError as exc:
                self.fail('new-source fixture requires private capture: ' + str(exc))
            view = arsiv_gorunum.build_view(raw, capture['final_url'], source_root, fetch_assets=False)
            self.assertNotIn('<script', (source_root / view['index_path']).read_text())
            capture.pop('http_charset', None)
            version = dict(capture, id='technical-v', document_id='technical-d', document_date=None,
                           version_label=None, date_precision='unknown', date_unknown_reason='technical fixture')
            view['version_id'] = 'technical-v'
            package['entries'] = [
                dict(kind='document', values=dict(id='technical-d', party_id='yeni-parti', title='Technical fixture', source_kind='news')),
                dict(kind='document_version', values=version),
                dict(kind='archive_view', values=view),
                dict(kind='passage', values=dict(id='technical-p', version_id='technical-v', exact='Technical fixture passage', section='Technical fixture')),
                dict(kind='source_attribution', values=dict(version_id='technical-v', kind='journalism', publisher='Technical publisher', public_url=capture['final_url'], basis='Technical fixture', date_precision='unknown')),
            ]
            records = package['practice_records']
            evidence = dict(records['practice_event_evidence'][0], passage_id='technical-p', concrete_basis='Technical fixture passage')
            records['practice_event_evidence'].append(evidence)
            if 'practice_evidence_assessment' in records:
                original = records['practice_evidence_assessment'][0]
                records['practice_evidence_assessment'].append(dict(original, passage_id='technical-p'))
            # Ephemeral structural test metadata, not a political research record.
            # The fixture exercises serialization only; no review artifact is saved.
            review_data = json.loads((arsiv.DATA / 'releases' / arsiv.current() / 'records.json').read_text())
            for entry in package['entries']:
                review_data.setdefault(entry['kind'], []).append(entry['values'])
            for kind, rows in records.items():
                existing = review_data.setdefault(kind, [])
                for row in rows:
                    if row not in existing:
                        existing.append(row)
            passages = {row['id']: row for row in review_data['passage']}
            review_rows = []
            for (kind, identity), (refs, _) in uygulamalar.practice_review_targets(review_data, records).items():
                review_rows.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent',
                    reviewed_at='2026-11-18T12:00:00+00:00',
                    source_version_ids=json.dumps(sorted({passages[p]['version_id'] for p in refs})),
                    passage_ids=json.dumps(sorted(refs)), inspected_sections=json.dumps(['Technical test context for ' + kind]),
                    supported_claim='Technical test subject ' + identity, limitations='Synthetic test only.',
                    result='reviewed', reason='Temporary validation fixture.'))
            records['practice_source_review_contract'] = [dict(version=1)]
            records['practice_source_review'] = review_rows
            package['source_review_refs'] = [dict(subject_kind=r['subject_kind'], subject_id=r['subject_id']) for r in review_rows]
            out = root / 'preview'
            uygulamalar.render_practice_preview(package, out, inventory, source_root=source_root)
            release = next((out / 'releases').iterdir())
            data = json.loads((release / 'records.json').read_text())
            self.assertEqual(data['practice_source_review'], review_rows)
            self.assertIn('practice_source_review_sha256', json.loads((release / 'manifest.json').read_text()))
            self.assertEqual(data, arsiv.export_db(release / 'records.sqlite3', release.name, storage_root=out))
            self.assertEqual(arsiv.audit_release(release.name, storage_root=out), release.name)
            self.assertTrue((out / version['original_path']).is_file())
            self.assertTrue((out / view['index_path']).is_file())
            report = (release / 'index.html').read_text()
            self.assertGreaterEqual(report.count('technical-p'), 2)
            self.assertIn('../../' + version['original_path'], report)
            self.assertIn('../../' + view['index_path'], report)
            report_before = arsiv.sha(release / 'index.html')
            (source_root / version['original_path']).write_bytes(raw + b'changed')
            rejected = root / 'rejected'
            with self.assertRaises(ValueError):
                uygulamalar.render_practice_preview(package, rejected, inventory, source_root=source_root)
            self.assertFalse(rejected.exists())
            self.assertEqual(arsiv.sha(release / 'index.html'), report_before)
        self.assertEqual(arsiv.sha(arsiv.DATA / 'current.json'), current_before)
        self.assertEqual(arsiv.sha(db_path), db_before)
        self.assertFalse((arsiv.DATA / '.write.lock').exists())

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
