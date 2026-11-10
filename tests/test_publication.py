import json
from pathlib import Path
import shutil
import tempfile
import unittest
import sqlite3
import rapor

import arsiv


class PublicationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_data = arsiv.DATA
        arsiv.DATA = Path(self.tmp.name) / 'data'
        shutil.copytree(self.old_data, arsiv.DATA)

    def tearDown(self):
        arsiv.DATA = self.old_data
        self.tmp.cleanup()

    def test_detects_corrupt_readable_archive(self):
        release = arsiv.current()
        records = json.loads((arsiv.DATA / 'releases' / release / 'records.json').read_text())
        (arsiv.DATA / records['document_version'][0]['readable_path']).write_text('hasarlı')
        with self.assertRaises(ValueError):
            arsiv.audit_release(release)

    def test_failures_leave_a_complete_release(self):
        for point in ('close', 'json', 'html', 'validate', 'after_current'):
            with self.subTest(point=point):
                before = arsiv.current()
                work = arsiv.open_workspace(self.tmp.name)
                with self.assertRaises(RuntimeError):
                    arsiv.publish_release(work, fail_at=point)
                after = arsiv.current()
                if point == 'after_current':
                    self.assertNotEqual(before, after)
                else:
                    self.assertEqual(before, after)
                self.assertEqual(arsiv.audit_release(), after)

    def test_lock_excludes_second_writer_and_old_workspace(self):
        work = arsiv.open_workspace(self.tmp.name)
        with self.assertRaises(FileExistsError):
            arsiv.open_workspace(self.tmp.name)
        arsiv.publish_release(work)
        next_work = arsiv.open_workspace(self.tmp.name)
        with self.assertRaises(ValueError):
            arsiv.publish_release(work)
        self.assertTrue((arsiv.DATA / '.write.lock').exists())
        arsiv.publish_release(next_work)

    def test_stale_base_rejected(self):
        work = arsiv.open_workspace(self.tmp.name)
        before = arsiv.current()
        metadata_path = work / 'workspace.json'
        metadata = json.loads(metadata_path.read_text())
        metadata['base'] = 'deadbeef'
        metadata_path.write_text(json.dumps(metadata))
        with self.assertRaises(ValueError):
            arsiv.publish_release(work)
        self.assertEqual(arsiv.current(), before)
        self.assertEqual(arsiv.audit_release(), before)

    def test_phase_acceptance_precedes_pointer_change(self):
        before = arsiv.current()
        work = arsiv.open_workspace(self.tmp.name)
        db = arsiv.connect(work / 'records.sqlite3')
        db.execute("DELETE FROM review WHERE kind='finding' AND subject_id=(SELECT id FROM finding LIMIT 1)")
        db.commit(); db.close()
        with self.assertRaisesRegex(ValueError, 'incelemesi eksik'):
            arsiv.publish_release(work)
        self.assertEqual(arsiv.current(), before)

    def test_foreign_key_corruption_rejected(self):
        work = arsiv.open_workspace(self.tmp.name)
        before = arsiv.current()
        with sqlite3.connect(work / 'records.sqlite3') as db:
            db.execute("INSERT INTO finding_evidence VALUES ('missing','kurulus','support')")
        with self.assertRaises(ValueError):
            arsiv.publish_release(work)
        self.assertEqual(arsiv.current(), before)

    def test_original_and_manifest_corruption_rejected(self):
        release = arsiv.current()
        folder = arsiv.DATA / 'releases' / release
        records = json.loads((folder / 'records.json').read_text())
        original = arsiv.DATA / records['document_version'][0]['original_path']
        original.write_bytes(b'corrupt')
        with self.assertRaises(ValueError): arsiv.audit_release()
        (folder / 'index.html').write_text('corrupt')
        with self.assertRaises(ValueError): arsiv.audit_release()

    def test_paths_cannot_escape_root_through_traversal_or_symlink(self):
        with self.assertRaises(ValueError): arsiv.safe_path(arsiv.DATA, '../other')
        (arsiv.DATA / 'outside').symlink_to(Path(self.tmp.name), target_is_directory=True)
        with self.assertRaises(ValueError): arsiv.safe_path(arsiv.DATA, 'outside/secret')

    def test_rejects_dangerous_urls(self):
        for url in ('javascript:alert(1)', 'file:///etc/passwd', 'https://user:pass@example.org/'):
            with self.subTest(url=url), self.assertRaises(ValueError): arsiv.safe_url(url)

    def test_report_escapes_untrusted_text_and_rejects_script_url(self):
        release = arsiv.current()
        payload = json.loads((arsiv.DATA / 'releases' / release / 'records.json').read_text())
        payload['finding'][0]['text'] = '<img src=x onerror=alert(1)>'
        rendered = rapor.render_report(payload)
        self.assertNotIn('<img src=x', rendered)
        self.assertIn('&lt;img', rendered)
        payload['document_version'][0]['original_url'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError): rapor.render_report(payload)
