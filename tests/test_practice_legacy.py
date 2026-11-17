"""Regression checks for the local tracer and its inherited release."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import arsiv
from uygulamalar import PRACTICE_TABLES, migrate_practice_workspace, practice_manifest_fields, validate_practices


BASE = '9003e475ee5d49b29a1310c0bfe2007d'


class PracticeLegacy(unittest.TestCase):
    def test_schema6_export_and_renderer24_remain_byte_identical(self):
        folder = arsiv.DATA / 'releases' / BASE
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        self.assertEqual(arsiv.export_db(folder / 'records.sqlite3', BASE), data)
        self.assertEqual(arsiv.render_comparison_snapshot(data, arsiv.render_v24_report).encode(), (folder / 'index.html').read_bytes())

    def test_current_is_tracer_with_previous_contracts(self):
        folder = arsiv.DATA / 'releases' / arsiv.current()
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(data['schema_version'], 7, 'Gerçek yerel tracer henüz yayımlanmadı')
        self.assertIn(data['practice_contract'][0]['stage'], ('tracer', 'partial', 'complete'))
        self.assertGreaterEqual(manifest['renderer_version'], 25)
        for key, value in practice_manifest_fields(data).items():
            self.assertEqual(manifest.get(key), value)
        self.assertEqual(manifest['source_policy_version'], 2)
        self.assertEqual(manifest['phase2_delivery']['completed_prefix'], list(arsiv.DELIVERY_ORDER))
        base_folder = arsiv.DATA / 'releases' / BASE
        base_manifest = json.loads((base_folder / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['phase2_delivery'], base_manifest['phase2_delivery'])
        self.assertEqual(data['comparison_contract'][0]['stage'], 'complete')
        self.assertEqual(data['comparison_contract'][0]['taxonomy_version'], 4)
        self.assertTrue(data['comparison_completion_revision'])
        selected = max(data['comparison_completion_revision'], key=lambda row: row['epoch'])['selection']
        self.assertTrue(json.loads(selected)['rows'])
        self.assertEqual(manifest['comparison_completion_selection_sha256'], base_manifest['comparison_completion_selection_sha256'])
        arsiv.validate_phase_one_html(data, (folder / 'index.html').read_text(encoding='utf-8'))
        bad = dict(data)
        bad['practice_event_evidence'] = [dict(row, epistemic_type='fact') for row in data['practice_event_evidence']]
        with self.assertRaisesRegex(ValueError, 'doğrulanmış olguya'):
            validate_practices(bad)
        bad = dict(data)
        bad['review'] = [row for row in data['review'] if row['subject_id'] != 'tracer-event']
        with self.assertRaisesRegex(ValueError, 'kaynak incelemesi eksik'):
            validate_practices(bad)

    def test_missing_snapshot_marker_is_rejected(self):
        folder = arsiv.DATA / 'releases' / arsiv.current()
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['data_schema_version'], 7, 'Gerçek yerel tracer henüz yayımlanmadı')
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

    def test_removing_all_practice_tables_does_not_downgrade_schema(self):
        folder = arsiv.DATA / 'releases' / arsiv.current()
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['data_schema_version'], 7, 'Gerçek yerel tracer henüz yayımlanmadı')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'records.sqlite3'
            shutil.copyfile(folder / 'records.sqlite3', path)
            db = arsiv.connect(path)
            try:
                db.execute('PRAGMA foreign_keys = OFF')
                for name in reversed(PRACTICE_TABLES):
                    db.execute(f'DROP TABLE {name}')
                db.commit()
            finally:
                db.close()
            with self.assertRaisesRegex(ValueError, 'işaretçisi kaldırılamaz'):
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

    def test_manifest_marker_removal_is_rejected(self):
        release = arsiv.current()
        original_folder = arsiv.DATA / 'releases' / release
        data = json.loads((original_folder / 'records.json').read_text(encoding='utf-8'))
        self.assertEqual(data['schema_version'], 7, 'Gerçek yerel tracer henüz yayımlanmadı')
        with tempfile.TemporaryDirectory() as tmp:
            temp_data = Path(tmp)
            folder = temp_data / 'releases' / release
            shutil.copytree(original_folder, folder)
            manifest_path = folder / 'manifest.json'
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            parent = manifest['base_release']
            del manifest['practice_selection_sha256']
            manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
            audit = arsiv.audit_release
            def skip_parent(value='current', seen=None):
                if value == parent:
                    return parent
                return audit(value, seen)
            with patch.object(arsiv, 'DATA', temp_data), patch.object(arsiv, 'export_db', return_value=data), patch.object(arsiv, 'audit_release', side_effect=skip_parent):
                with self.assertRaisesRegex(ValueError, 'Uygulama manifesti'):
                    audit(release)


if __name__ == '__main__':
    unittest.main()
