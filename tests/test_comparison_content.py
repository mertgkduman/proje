"""Source and content invariants for phase-three comparisons."""
import unittest
import tempfile
import shutil
import importlib.util
import json
import copy
from pathlib import Path

import arsiv
import rapor
import test_comparisons


class ComparisonContentTest(unittest.TestCase):
    def test_an_alternative_group_cannot_have_only_one_version(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        row = next(r for r in data['comparison_row'] if r['party_id'] == 'iyi')
        row['alternative_group'] = 'incomplete-alternatives'
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(data)

    def test_two_sourced_versions_can_form_an_alternative_group(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        row = next(r for r in data['comparison_row'] if r['party_id'] == 'iyi')
        row['alternative_group'] = 'two-versions'
        other = copy.deepcopy(row)
        other.update(id='alternative-old', version_id='0205-iyi-charter-istanbul-v1')
        data['comparison_row'].append(other)
        old_passage = next(p for p in data['passage'] if p['id'] == '03-iyi-once-uye')
        for typ in ('summary', 'quote'):
            fid = 'alternative-old-' + typ
            data['finding'].append(dict(id=fid, party_id='iyi', heading='Tüzük', pair_id='alternative-old-pair', text=old_passage['exact'], provenance=typ, epistemic_type='claim'))
            data['finding_evidence'].append(dict(finding_id=fid, passage_id=old_passage['id'], role='support'))
        data['comparison_field'].append(dict(id='alternative-old-field', row_id=other['id'], field='charter_answer', summary_finding_id='alternative-old-summary', quote_finding_id='alternative-old-quote', condition_key=None))
        self.assertTrue(arsiv.validate_comparisons(data))

    def test_alternative_and_supplement_are_named_in_both_views(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        row = next(r for r in data['comparison_row'] if r['party_id'] == 'tip')
        row['alternative_group'] = 'alternatives'
        row['source_role'] = 'supplement'
        report = rapor.render_report(data)
        self.assertGreaterEqual(report.count('Alternatif belge nüshası:'), 2)
        self.assertGreaterEqual(report.count('Ek belge:'), 2)

    def test_renderer_16_is_frozen_before_renderer_17(self):
        source = Path(__file__).resolve().parents[1] / 'src' / 'rapor_v16.py'
        self.assertTrue(source.is_file(), 'Renderer 16 arşivlenmeli')
        spec = importlib.util.spec_from_file_location('frozen_rapor_v16', source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        release_id = arsiv.current()
        while release_id:
            release = arsiv.DATA / 'releases' / release_id
            manifest = json.loads((release / 'manifest.json').read_text(encoding='utf-8'))
            if manifest['renderer_version'] == 16:
                break
            release_id = manifest.get('base_release')
        self.assertTrue(release_id, 'Renderer 16 yayını bulunmalı')
        data = json.loads((release / 'records.json').read_text(encoding='utf-8'))
        self.assertEqual(module.render_report(data).encode(), (release / 'index.html').read_bytes())
        self.assertEqual(arsiv.RENDERER_VERSION, 17)

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
                db.execute("INSERT INTO topic VALUES (?,?,?,?,?,?)", ('test-dem-tuzuk', 'Tüzük', 2, '2026-11-13', 'verified', 'Test'))
                db.execute("INSERT INTO topic_basis (topic_id,taxonomy_version,passage_id,rationale,source_role) VALUES (?,?,?,?,?)", ('test-dem-tuzuk', 2, '0204-dem-charter-hedep', 'DEM tüzüğündeki ifade', 'charter'))
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
