"""Source and content invariants for phase-three comparisons."""
import unittest
import tempfile
import shutil
from pathlib import Path

import arsiv
import test_comparisons


class ComparisonContentTest(unittest.TestCase):
    def test_basis_role_migration_preserves_legacy_rows(self):
        release = arsiv.current()
        source = arsiv.DATA / 'releases' / release / 'records.sqlite3'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'records.sqlite3'
            shutil.copyfile(source, path)
            db = arsiv.connect(path)
            try:
                before = [tuple(r) for r in db.execute('SELECT topic_id,taxonomy_version,passage_id,rationale FROM topic_basis')]
                arsiv.migrate_comparisons(db, Path(temp) / 'backup.sqlite3')
                after = [tuple(r) for r in db.execute('SELECT topic_id,taxonomy_version,passage_id,rationale FROM topic_basis')]
                self.assertEqual(before, after)
                self.assertIn('source_role', {r['name'] for r in db.execute('PRAGMA table_info(topic_basis)')})
            finally:
                db.close()

    def test_attributed_program_can_support_a_verified_topic(self):
        release = arsiv.current()
        source = arsiv.DATA / 'releases' / release / 'records.sqlite3'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'records.sqlite3'
            shutil.copyfile(source, path)
            db = arsiv.connect(path)
            try:
                columns = {row['name'] for row in db.execute('PRAGMA table_info(topic_basis)')}
                if 'source_role' not in columns:
                    db.execute('ALTER TABLE topic_basis ADD COLUMN source_role TEXT')
                db.execute("INSERT INTO topic VALUES (?,?,?,?,?,?)", ('test-demokrasi', 'Demokrasi', 2, '2026-11-13', 'verified', 'Test'))
                db.execute("INSERT INTO topic_basis (topic_id,taxonomy_version,passage_id,rationale,source_role) VALUES (?,?,?,?,?)", ('test-demokrasi', 2, 'epm-parliamentary-p', 'Programdaki yönetim sistemi', 'program'))
                db.commit()
            finally:
                db.close()
            try:
                arsiv.export_db(path, 'test')
            except ValueError as exc:
                self.fail(f'Atıflı program dayanağı kabul edilmeli: {exc}')
            db = arsiv.connect(path)
            try:
                db.execute("UPDATE topic_basis SET source_role='charter' WHERE topic_id='test-demokrasi'")
                db.commit()
            finally:
                db.close()
            with self.assertRaises(ValueError):
                arsiv.export_db(path, 'test')

    def test_identical_source_bytes_cannot_be_a_material_change(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        change = data['comparison_change'][0]
        change.update(row_id='03-saadet-merkez', before_passage_id='0209-saadet-program-url-relation', after_passage_id='0209-saadet-program')
        passages = {p['id']: p for p in data['passage']}
        versions = {v['id']: v for v in data['document_version']}
        before = versions[passages[change['before_passage_id']]['version_id']]
        after = versions[passages[change['after_passage_id']]['version_id']]
        self.assertEqual(before['sha256'], after['sha256'])
        with self.assertRaisesRegex(ValueError, '[Aa]ynı içerik'):
            arsiv.validate_comparisons(data)

    def test_no_explicit_statement_requires_a_review_scope(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        row = next(r for r in data['comparison_row'] if r['party_id'] == 'yeni-parti')
        row.update(state='no_explicit_statement', version_id='epm-charter-v1')
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(data)


if __name__ == '__main__':
    unittest.main()
