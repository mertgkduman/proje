"""Regression checks for the local tracer and its inherited release."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import arsiv
from uygulamalar import migrate_practice_workspace, practice_manifest_fields


BASE = '9003e475ee5d49b29a1310c0bfe2007d'


class PracticeLegacy(unittest.TestCase):
    def test_current_is_tracer_with_previous_contracts(self):
        folder = arsiv.DATA / 'releases' / arsiv.current()
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(data['schema_version'], 7, 'Gerçek yerel tracer henüz yayımlanmadı')
        self.assertEqual(data['practice_contract'][0]['stage'], 'tracer')
        self.assertEqual(manifest['renderer_version'], 25)
        for key, value in practice_manifest_fields(data).items():
            self.assertEqual(manifest.get(key), value)
        self.assertEqual(manifest['source_policy_version'], 2)
        self.assertEqual(manifest['phase2_delivery']['completed_prefix'], list(arsiv.DELIVERY_ORDER))
        self.assertEqual(data['comparison_contract'][0]['stage'], 'complete')
        self.assertEqual(data['comparison_contract'][0]['taxonomy_version'], 4)
        self.assertTrue(data['comparison_completion_revision'])
        self.assertTrue(json.loads(max(data['comparison_completion_revision'], key=lambda row: row['epoch'])['selection'])['rows'])

    def test_missing_snapshot_marker_is_rejected(self):
        folder = arsiv.DATA / 'releases' / arsiv.current()
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        self.assertEqual(data['schema_version'], 7, 'Gerçek yerel tracer henüz yayımlanmadı')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'records.sqlite3'
            shutil.copyfile(folder / 'records.sqlite3', path)
            db = arsiv.connect(path)
            try:
                db.execute('DELETE FROM practice_contract')
                db.commit()
            finally:
                db.close()
            with self.assertRaisesRegex(ValueError, 'sözleşmesi eksik'):
                arsiv.export_db(path, 'downgrade-test')

    def test_failed_migration_preserves_existing_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'records.sqlite3'
            shutil.copyfile(arsiv.DATA / 'releases' / BASE / 'records.sqlite3', path)
            before = arsiv.sha(path)
            db = arsiv.connect(path)
            try:
                with self.assertRaises(RuntimeError):
                    migrate_practice_workspace(db, Path(tmp) / 'backup.sqlite3', fail_at='migration')
            finally:
                db.close()
            self.assertEqual(before, arsiv.sha(path))


if __name__ == '__main__':
    unittest.main()
