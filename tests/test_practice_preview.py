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
    def test_archive_view_uses_default_or_explicit_storage_root(self):
        import arsiv_gorunum
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            view = arsiv_gorunum.build_view(b'<p>test</p>', 'https://example.org/', root, fetch_assets=False)
            view['version_id'] = 'source-v'
            db = sqlite3.connect(root / 'records.sqlite3')
            db.executescript("CREATE TABLE document(id TEXT PRIMARY KEY,party_id TEXT);"
                             "CREATE TABLE document_version(id TEXT PRIMARY KEY,document_id TEXT,sha256 TEXT);"
                             "INSERT INTO document VALUES('source','yeni-parti');")
            db.execute('INSERT INTO document_version VALUES(?,?,?)', ('source-v', 'source', view['source_sha256']))
            db.commit()
            db.close()
            scope = []
            package = dict(base_release='base', contract_version=1, stage='tracer', taxonomy_version=4,
                           party_id='yeni-parti', scope_inventory=scope,
                           entries=[dict(kind='archive_view', values=view)],
                           practice_records=dict(practice_contract=[dict(stage='tracer', inventory_digest=uygulamalar._digest(scope))]))

            def validate_then_stop(data_root, row):
                arsiv_gorunum.validate_view(data_root, row)
                raise RuntimeError('view verified')

            for explicit in (False, True):
                with self.subTest(explicit=explicit), patch('arsiv.DATA', root), \
                        patch('arsiv.validate_view', side_effect=validate_then_stop), \
                        patch('uygulamalar.migrate_practice_workspace'):
                    with self.assertRaisesRegex(RuntimeError, 'view verified'):
                        kwargs = {'storage_root': root} if explicit else {}
                        uygulamalar._load_practice_copy(root, package, 'base', **kwargs)

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
            # Model an earlier reading before the technical passage was added;
            # the new revision must cover both old and newly added evidence.
            revision_rows = []
            for index, row in enumerate(review_rows):
                current_passages = json.loads(row['passage_ids'])
                earlier = [p for p in current_passages if p != 'technical-p']
                if 'technical-p' in current_passages and earlier:
                    revision_rows.append(dict(row, revision=2, reviewed_at='2026-11-19T12:00:00+00:00',
                                              reason='Updated technical fixture after the added passage.'))
                    review_rows[index] = dict(row, passage_ids=json.dumps(earlier),
                                              source_version_ids=json.dumps(sorted({passages[p]['version_id'] for p in earlier})))
            event = records['practice_event'][0]
            initial_event_review = next(r for r in review_rows if (r['subject_kind'], r['subject_id']) == ('practice_event', event['id']))
            event_revision = next(r for r in revision_rows if (r['subject_kind'], r['subject_id']) == ('practice_event', event['id']))
            earlier_data = dict(review_data, practice_event_evidence=[r for r in review_data['practice_event_evidence'] if r['passage_id'] != 'technical-p'])
            event_only = dict(practice_event=[event])
            self.assertTrue(uygulamalar.validate_practice_source_review(earlier_data, [initial_event_review], event_only))
            with self.assertRaises(ValueError):
                uygulamalar.validate_practice_source_review(review_data, [initial_event_review], event_only)
            self.assertTrue(uygulamalar.validate_practice_source_review(review_data, [initial_event_review], event_only, revisions=[event_revision]))
            records['practice_source_review_contract'] = [dict(version=1)]
            records['practice_source_review'] = review_rows
            records['practice_source_review_revision_contract'] = [dict(version=2)]
            records['practice_source_review_revision'] = revision_rows
            package['source_review_refs'] = [dict(subject_kind=r['subject_kind'], subject_id=r['subject_id']) for r in review_rows]
            out = root / 'preview'
            uygulamalar.render_practice_preview(package, out, inventory, source_root=source_root)
            release = next((out / 'releases').iterdir())
            data = json.loads((release / 'records.json').read_text())
            self.assertEqual(data['practice_source_review'], review_rows)
            self.assertEqual(data['practice_source_review_revision'], revision_rows)
            self.assertIn('practice_source_review_sha256', json.loads((release / 'manifest.json').read_text()))
            self.assertIn('practice_source_review_revision_sha256', json.loads((release / 'manifest.json').read_text()))
            self.assertEqual(data, arsiv.export_db(release / 'records.sqlite3', release.name, storage_root=out))
            self.assertEqual(arsiv.audit_release(release.name, storage_root=out), release.name)
            self.assertTrue((out / version['original_path']).is_file())
            self.assertTrue((out / view['index_path']).is_file())
            report = (release / 'index.html').read_text()
            self.assertGreaterEqual(report.count('technical-p'), 2)
            self.assertIn('../../' + version['original_path'], report)
            self.assertIn('../../' + view['index_path'], report)
            report_before = arsiv.sha(release / 'index.html')
            # Exercise the public merge boundary using the same physical capture.
            # Its review rows remain original provenance, not a broader review.
            input_path = root / 'physical.json'
            input_path.write_text(json.dumps(package, ensure_ascii=False), encoding='utf-8')
            decision_path = root / 'physical-decisions.json'
            decision_path.write_text(json.dumps(dict(version=1, inventory_digest=uygulamalar._digest(inventory),
                input_digests={input_path.name: hashlib.sha256(input_path.read_bytes()).hexdigest()}, decisions=[])), encoding='utf-8')
            inventory_path = arsiv.DATA / 'practices/04-inventory.json'
            merged_path = root / 'physical-merged.json'
            command = [sys.executable, str(arsiv.ROOT / 'src/arsiv.py'), 'practice-merge',
                '--inventory', str(inventory_path), '--inputs', str(input_path),
                '--event-decisions', str(decision_path), '--out', str(merged_path),
                '--source-root', input_path.name + '=' + str(source_root)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            merged = json.loads(merged_path.read_text(encoding='utf-8'))
            merged_out = root / 'merged-preview'
            uygulamalar.render_practice_preview(merged, merged_out, inventory,
                merge_source_roots={input_path.name: source_root})
            merged_release, = (merged_out / 'releases').iterdir()
            merged_data = json.loads((merged_release / 'records.json').read_text())
            self.assertEqual(merged_data, arsiv.export_db(merged_release / 'records.sqlite3', merged_release.name, storage_root=merged_out))
            self.assertEqual(arsiv.audit_release(merged_release.name, storage_root=merged_out), merged_release.name)
            self.assertNotIn('practice_source_review', merged_data)
            self.assertTrue(any(row['origin_kind'] == 'review_origins' for row in merged_data['practice_merge_origin']))
            merged_report = (merged_release / 'index.html').read_text()
            self.assertGreaterEqual(merged_report.count('technical-p'), 2)
            self.assertTrue((merged_out / version['original_path']).is_file())
            self.assertTrue((merged_out / view['index_path']).is_file())
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

    def test_merge_same_event_preserves_base_event_and_is_order_independent(self):
        package = json.loads((arsiv.DATA / 'practices/04-coverage-tracer.json').read_text(encoding='utf-8'))
        inventory_path = arsiv.DATA / 'practices/04-inventory.json'
        inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def renamed(value):
                if isinstance(value, dict):
                    return {key: renamed(item) for key, item in value.items()}
                if isinstance(value, list):
                    return [renamed(item) for item in value]
                return 'technical-alias-event' if value == 'tracer-cesme' else value
            paths = [root / 'first.json', root / 'second.json']
            alias_package = renamed(package)
            # The scope inventory is signed and describes the accepted base;
            # the alias does not rewrite its historical references.
            alias_package['scope_inventory'] = package['scope_inventory']
            # The accepted base already owns the contribution, relation and
            # legacy IDs.  An independent alias may cite the event evidence,
            # but cannot rewrite those immutable rows to point to itself.
            for table in ('practice_contribution', 'practice_relation', 'practice_legacy_link'):
                alias_package['practice_records'][table] = []
            for path, value in zip(paths, [package, alias_package]):
                path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
            digests = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
            decision = dict(version=1, inventory_digest=uygulamalar._digest(inventory), input_digests=digests,
                decisions=[dict(id='technical-same', candidate_keys=['cesme-2026-09-27'],
                    event_refs=[dict(input_package_sha256=digests[paths[0].name], event_id='tracer-cesme'),
                                dict(input_package_sha256=digests[paths[1].name], event_id='technical-alias-event')],
                    decision='same', canonical_event_id='tracer-cesme', overlap_reason='Technical duplicate fixture.',
                    source_passage_ids=['0105-cesme-p'], reviewed_at='2026-11-18T12:00:00+00:00', reviewer_kind='agent')])
            decisions = root / 'decisions.json'
            decisions.write_text(json.dumps(decision, ensure_ascii=False), encoding='utf-8')
            outputs = []
            for index, inputs in enumerate((paths, list(reversed(paths)))):
                out = root / ('merged-' + str(index) + '.json')
                result = subprocess.run([sys.executable, str(arsiv.ROOT / 'src/arsiv.py'), 'practice-merge',
                    '--inventory', str(inventory_path), '--inputs', *map(str, inputs),
                    '--event-decisions', str(decisions), '--out', str(out)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, 'same-event merge must succeed: ' + result.stderr)
                outputs.append(json.loads(out.read_text(encoding='utf-8')))
            self.assertEqual(outputs[0], outputs[1])
            records = outputs[0]['practice_records']
            self.assertEqual([row for row in records['practice_event'] if row['id'] == 'tracer-cesme'],
                             package['practice_records']['practice_event'])
            self.assertEqual({row['canonical_event_id'] for row in records['practice_event_alias']}, {'tracer-cesme'})
            self.assertIn(package['practice_records']['practice_event_evidence'][0], records['practice_event_evidence'])

    def test_public_merge_distinct_and_unresolved_preserve_references(self):
        """Both uncertain outcomes pass through the real public adapter."""
        package = json.loads((arsiv.DATA / 'practices/04-coverage-tracer.json').read_text())
        inventory = json.loads((arsiv.DATA / 'practices/04-inventory.json').read_text())
        def rename(value):
            if isinstance(value, dict):
                return {key: rename(item) for key, item in value.items()}
            if isinstance(value, list):
                return [rename(item) for item in value]
            return 'technical-separate-event' if value == 'tracer-cesme' else value
        other = rename(package)
        other['scope_inventory'] = package['scope_inventory']
        for table in ('practice_contribution', 'practice_relation', 'practice_legacy_link'):
            other['practice_records'][table] = []
        inputs = [dict(identity='first.json', raw=json.dumps(package, ensure_ascii=False).encode()),
                  dict(identity='second.json', raw=json.dumps(other, ensure_ascii=False).encode())]
        digests = {item['identity']: hashlib.sha256(item['raw']).hexdigest() for item in inputs}
        for kind in ('distinct', 'unresolved'):
            decision = dict(version=1, inventory_digest=uygulamalar._digest(inventory), input_digests=digests,
                decisions=[dict(id='technical-' + kind, candidate_keys=['cesme-2026-09-27'],
                    event_refs=[dict(input_package_sha256=digests['first.json'], event_id='tracer-cesme'),
                                dict(input_package_sha256=digests['second.json'], event_id='technical-separate-event')],
                    decision=kind, canonical_event_id=None, overlap_reason='Technical fixture preserves uncertainty.',
                    source_passage_ids=['0105-cesme-p'], reviewed_at='2026-11-18T12:00:00+00:00', reviewer_kind='agent')])
            with self.subTest(decision=kind):
                merged = uygulamalar.merge_practice_packages(inventory, inputs, json.dumps(decision).encode())
                records = merged['practice_records']
                self.assertEqual({r['canonical_event_id'] for r in records['practice_event_alias']},
                                 {'tracer-cesme', 'technical-separate-event'})
                self.assertEqual(records['practice_event_decision'][0]['decision'], kind)
                self.assertTrue({'tracer-cesme', 'technical-separate-event'} <=
                                {r['event_id'] for r in records['practice_event_evidence']})
                self.assertIn(package['practice_records']['practice_contribution'][0], records['practice_contribution'])
                self.assertIn(package['practice_records']['practice_relation'][0], records['practice_relation'])

    def test_public_merge_separate_party_physical_roots(self):
        import copy
        import io
        from email.message import Message
        import arsiv_gorunum
        original = json.loads((arsiv.DATA / 'practices/04-coverage-tracer.json').read_text())
        inventory = json.loads((arsiv.DATA / 'practices/04-inventory.json').read_text())
        pointer_before = arsiv.sha(arsiv.DATA / 'current.json')
        base_db = arsiv.DATA / 'releases' / arsiv.current() / 'records.sqlite3'
        db_before = arsiv.sha(base_db)
        self.assertFalse((arsiv.DATA / '.write.lock').exists())
        with tempfile.TemporaryDirectory(prefix='gsd-public-roots-') as tmp:
            root = Path(tmp)
            roots, inputs = {}, []
            for party in ('yeni-parti', 'tip'):
                source_root = root / party
                source_root.mkdir()
                raw = ('<html><body>Technical source for ' + party + '</body></html>').encode()
                response = io.BytesIO(raw)
                response.headers = Message()
                response.headers['Content-Type'] = 'text/html; charset=utf-8'
                response.geturl = lambda party=party: 'https://example.org/' + party
                with patch('arsiv.urllib.request.urlopen', return_value=response):
                    capture = arsiv.capture_source('https://example.org/' + party, 'html', storage_root=source_root)
                view = arsiv_gorunum.build_view(raw, capture['final_url'], source_root, fetch_assets=False)
                capture.pop('http_charset', None)
                document, version, passage = ('technical-' + party + suffix for suffix in ('-doc', '-version', '-passage'))
                source_version = dict(capture, id=version, document_id=document, document_date=None,
                                      version_label=None, date_precision='unknown', date_unknown_reason='Technical fixture')
                view['version_id'] = version
                package = copy.deepcopy(original)
                package['party_id'] = party
                if party == 'tip':
                    # The pilot's scope and legacy bridge are new rows owned by
                    # Yeni Parti; TİP must not submit them as its own scope.
                    package['practice_records']['practice_scope_v2'] = []
                    package['practice_records']['practice_legacy_scope'] = []
                package['entries'] = [
                    dict(kind='document', values=dict(id=document, party_id=party, title='Technical fixture', source_kind='news')),
                    dict(kind='document_version', values=source_version), dict(kind='archive_view', values=view),
                    dict(kind='passage', values=dict(id=passage, version_id=version,
                        exact='Technical source for ' + party, section='Technical fixture')),
                    dict(kind='source_attribution', values=dict(version_id=version, kind='journalism',
                        publisher='Technical publisher', public_url=capture['final_url'], basis='Technical fixture', date_precision='unknown'))]
                records = package['practice_records']
                new_event = 'technical-' + party + '-event'
                records['practice_event'].append(dict(records['practice_event'][0], id=new_event,
                                                      common_event_key='technical-' + party))
                records['practice_event_evidence'].append(dict(records['practice_event_evidence'][0],
                    event_id=new_event, passage_id=passage, concrete_basis='Technical source for ' + party))
                records['practice_source_party'].append(dict(version_id=version, party_id=party,
                                                              passage_id=passage, scope_reason='Technical fixture ownership.'))
                identity = party + '.json'
                roots[identity] = source_root
                inputs.append(dict(identity=identity, raw=json.dumps(package, ensure_ascii=False).encode()))
            digests = {item['identity']: hashlib.sha256(item['raw']).hexdigest() for item in inputs}
            decision = dict(version=1, inventory_digest=uygulamalar._digest(inventory), input_digests=digests,
                decisions=[dict(id='technical-same-base', candidate_keys=['cesme-2026-09-27'],
                    event_refs=[dict(input_package_sha256=digests[item['identity']], event_id='tracer-cesme') for item in inputs],
                    decision='same', canonical_event_id='tracer-cesme', overlap_reason='Shared immutable base event.',
                    source_passage_ids=['0105-cesme-p'], reviewed_at='2026-11-18T12:00:00+00:00', reviewer_kind='agent')])
            merged = uygulamalar.merge_practice_packages(inventory, inputs, json.dumps(decision).encode(), source_roots=roots)
            self.assertIsNone(merged['party_id'])
            out = root / 'preview'
            uygulamalar.render_practice_preview(merged, out, inventory, merge_source_roots=roots)
            folder, = (out / 'releases').iterdir()
            snapshot = json.loads((folder / 'records.json').read_text())
            self.assertEqual(snapshot, arsiv.export_db(folder / 'records.sqlite3', folder.name, storage_root=out))
            self.assertEqual(arsiv.audit_release(folder.name, storage_root=out), folder.name)
            self.assertGreaterEqual((folder / 'index.html').read_text().count('0105-cesme-p'), 2)
            for party in ('yeni-parti', 'tip'):
                self.assertTrue(any(r['party_id'] == party and r['passage_id'] == 'technical-' + party + '-passage'
                                    for r in snapshot['practice_source_party']))
                version = next(v for v in snapshot['document_version'] if v['id'] == 'technical-' + party + '-version')
                self.assertTrue((out / version['original_path']).is_file())
                self.assertTrue(any(r['event_id'] == 'technical-' + party + '-event' and
                                    r['passage_id'] == 'technical-' + party + '-passage'
                                    for r in snapshot['practice_event_evidence']))
            swapped = {'yeni-parti.json': roots['tip.json'], 'tip.json': roots['yeni-parti.json']}
            rejected = root / 'rejected'
            with self.assertRaises((ValueError, FileNotFoundError)):
                uygulamalar.render_practice_preview(merged, rejected, inventory, merge_source_roots=swapped)
            self.assertFalse(rejected.exists())
            # A party cannot submit a physical document owned by another party.
            forged = json.loads(inputs[1]['raw'])
            forged['entries'][0]['values']['party_id'] = 'yeni-parti'
            forged_input = dict(identity=inputs[1]['identity'], raw=json.dumps(forged).encode())
            forged_decision = dict(version=1, inventory_digest=uygulamalar._digest(inventory),
                input_digests={forged_input['identity']: hashlib.sha256(forged_input['raw']).hexdigest()}, decisions=[])
            before = arsiv.sha(folder / 'manifest.json')
            with self.assertRaisesRegex(ValueError, 'başka partinin'):
                uygulamalar.merge_practice_packages(inventory, [forged_input], json.dumps(forged_decision).encode(), source_roots=roots)
            self.assertEqual(arsiv.sha(folder / 'manifest.json'), before)
        self.assertEqual(arsiv.sha(arsiv.DATA / 'current.json'), pointer_before)
        self.assertEqual(arsiv.sha(base_db), db_before)
        self.assertFalse((arsiv.DATA / '.write.lock').exists())

    def test_public_merge_rejects_bad_digest_and_conflicting_decisions(self):
        package = json.loads((arsiv.DATA / 'practices/04-coverage-tracer.json').read_text())
        inventory_path = arsiv.DATA / 'practices/04-inventory.json'
        inventory = json.loads(inventory_path.read_text())
        pointer = arsiv.sha(arsiv.DATA / 'current.json')
        db = arsiv.DATA / 'releases' / arsiv.current() / 'records.sqlite3'
        db_hash = arsiv.sha(db)
        with tempfile.TemporaryDirectory(prefix='gsd-public-negative-') as tmp:
            root = Path(tmp)
            first, second = root / 'first.json', root / 'second.json'
            first.write_text(json.dumps(package), encoding='utf-8')
            second.write_text(json.dumps(package, indent=2), encoding='utf-8')
            digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (first, second)}
            row = dict(id='decision-one', candidate_keys=['cesme-2026-09-27'],
                event_refs=[dict(input_package_sha256=digests[p.name], event_id='tracer-cesme') for p in (first, second)],
                decision='same', canonical_event_id='tracer-cesme', overlap_reason='Technical fixture duplicate.',
                source_passage_ids=['0105-cesme-p'], reviewed_at='2026-11-18T12:00:00+00:00', reviewer_kind='agent')
            cases = [([first], dict(version=1, inventory_digest=uygulamalar._digest(inventory),
                                    input_digests={first.name: '0' * 64}, decisions=[]), 'digest'),
                     ([first, second], dict(version=1, inventory_digest=uygulamalar._digest(inventory),
                                            input_digests=digests, decisions=[row, dict(row, id='decision-two')]), 'conflicting')]
            for inputs, decisions, expected in cases:
                with self.subTest(expected=expected):
                    decision_path, out = root / (expected + '.json'), root / (expected + '-out.json')
                    decision_path.write_text(json.dumps(decisions), encoding='utf-8')
                    out.write_bytes(b'existing output')
                    result = subprocess.run([sys.executable, str(arsiv.ROOT / 'src/arsiv.py'), 'practice-merge',
                        '--inventory', str(inventory_path), '--inputs', *map(str, inputs),
                        '--event-decisions', str(decision_path), '--out', str(out)], capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, json.loads(result.stderr)['error'].lower())
                    self.assertEqual(out.read_bytes(), b'existing output')
        self.assertEqual(arsiv.sha(arsiv.DATA / 'current.json'), pointer)
        self.assertEqual(arsiv.sha(db), db_hash)
        self.assertFalse((arsiv.DATA / '.write.lock').exists())

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

    def test_merge_cli_publishes_complete_output_exclusively(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inventory = root / 'inventory.json'
            inventory.write_text('{}', encoding='utf-8')
            source = root / 'input.json'
            source.write_text('{}', encoding='utf-8')
            decisions = root / 'decisions.json'
            decisions.write_text('{}', encoding='utf-8')
            out = root / 'merged.json'
            args = ['arsiv.py', 'practice-merge', '--inventory', str(inventory), '--inputs', str(source),
                    '--event-decisions', str(decisions), '--out', str(out)]
            with patch.object(sys, 'argv', args), patch('uygulamalar.merge_practice_packages', return_value={'technical': True}):
                arsiv.main()
                self.assertEqual(json.loads(out.read_text(encoding='utf-8')), {'technical': True})
                with self.assertRaises(FileExistsError):
                    arsiv.main()
                self.assertEqual(json.loads(out.read_text(encoding='utf-8')), {'technical': True})
                self.assertFalse(list(root.glob('.practice-merge-*')))
