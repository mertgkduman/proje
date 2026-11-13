"""Acceptance checks for the sourced phase-three comparison release."""
import json
import copy
from pathlib import Path
import shutil
import tempfile
import unittest
import sqlite3
import rapor_v15
import rapor

import arsiv


class ComparisonReleaseTest(unittest.TestCase):
    @staticmethod
    def fixture_release():
        release = arsiv.current()
        while release:
            manifest = json.loads((arsiv.DATA / 'releases' / release / 'manifest.json').read_text())
            if manifest.get('renderer_version') == 15:
                return release
            release = manifest.get('base_release')
        raise AssertionError('Dokuz partili renderer 15 tabanı bulunamadı')

    @staticmethod
    def comparison_data():
        base = arsiv.DATA / 'releases' / ComparisonReleaseTest.fixture_release()
        data = json.loads((base / 'records.json').read_text(encoding='utf-8'))
        package = json.loads((Path(__file__).resolve().parents[1] / 'data/comparisons/03-tracer.json').read_text(encoding='utf-8'))
        data.update({name: [] for name in arsiv.COMPARISON_TABLES})
        data['comparison_contract'] = [dict(version=1,taxonomy_version=package['taxonomy_version'],stage=package['stage'])]
        for entry in package['records']:
            data[entry['kind']].append(entry['values'])
        return data

    def test_invalid_ownership_and_missing_evidence_rejected(self):
        data = self.comparison_data()
        arsiv.validate_comparisons(data)
        field = data['comparison_field'][0]
        field['quote_finding_id'] = next(f['id'] for f in data['finding'] if f['party_id'] == 'tip' and f['provenance'] == 'quote')
        with self.assertRaises(ValueError): arsiv.validate_comparisons(data)
        data = self.comparison_data()
        data['finding_evidence'] = [e for e in data['finding_evidence'] if e['finding_id'] != '03-iyi-quote']
        with self.assertRaises(ValueError): arsiv.validate_comparisons(data)
        data = self.comparison_data()
        next(r for r in data['comparison_row'] if r['party_id'] == 'iyi')['version_id'] = '0203-tip-charter-v1'
        with self.assertRaises(ValueError): arsiv.validate_comparisons(data)
        data = self.comparison_data()
        data['comparison_synthesis_evidence'][0]['passage_id'] = next(p['id'] for p in data['passage'] if p['version_id'] == '0205-iyi-charter-istanbul-v1')
        with self.assertRaises(ValueError): arsiv.validate_comparisons(data)

    def test_failed_migration_preserves_original_and_current(self):
        before = arsiv.current()
        with tempfile.TemporaryDirectory() as temp:
            source = arsiv.DATA / 'releases' / self.fixture_release() / 'records.sqlite3'
            target = Path(temp) / 'records.sqlite3'
            shutil.copyfile(source, target)
            db = arsiv.connect(target)
            try:
                with self.assertRaises(RuntimeError):
                    arsiv.migrate_comparisons(db, Path(temp) / 'backup.sqlite3', fail_at='migration')
                self.assertFalse(db.execute("SELECT 1 FROM sqlite_master WHERE name='comparison_contract'").fetchone())
                self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            finally: db.close()
            with sqlite3.connect(source) as original, sqlite3.connect(Path(temp) / 'backup.sqlite3') as backup:
                self.assertEqual(list(original.iterdump()), list(backup.iterdump()))
        self.assertEqual(arsiv.current(), before)

    def test_frozen_renderer_reproduces_previous_html(self):
        base = arsiv.DATA / 'releases' / self.fixture_release()
        data = json.loads((base / 'records.json').read_text(encoding='utf-8'))
        self.assertEqual(rapor_v15.render_report(data).encode(), (base / 'index.html').read_bytes())

    def test_comparison_text_is_escaped(self):
        data = self.comparison_data()
        data['comparison_synthesis'][0]['text'] = '<img src=x onerror=alert(1)>'
        report = rapor.render_report(data)
        self.assertNotIn('<img src=x onerror=alert(1)>', report)
        self.assertIn('&lt;img src=x', report)

    def test_new_stylesheet_preserves_historical_style(self):
        source = Path(__file__).resolve().parents[1] / 'src'
        historical = source / 'rapor_v14.css'
        current = source / 'rapor_v16.css'
        self.assertEqual(arsiv.sha(historical), '721a9fe91d18231d01941d8788bac0264862870957c1a85cc13090ec5603fef4')
        self.assertEqual(rapor.STYLE, current.read_text(encoding='utf-8'))
        self.assertIn('.comparison-row', rapor.STYLE)
        self.assertIn('.summary { color: #003366;', rapor.STYLE)
        self.assertIn('.quote { color: #000;', rapor.STYLE)

    def test_published_evidence_cannot_be_rewritten(self):
        base = self.comparison_data()
        candidate = copy.deepcopy(base)
        next(p for p in candidate['passage'] if p['id'] == '03-iyi-sonra-uye')['exact'] = 'değiştirilmiş'
        with self.assertRaises(ValueError): arsiv.validate_comparison_descent(base, candidate)
        candidate = copy.deepcopy(base)
        candidate['comparison_row'] = [r for r in candidate['comparison_row'] if r['party_id'] != 'iyi']
        with self.assertRaises(ValueError): arsiv.validate_comparison_descent(base, candidate)

    def test_real_sources_reach_closed_comparison_release(self):
        # Fail on the missing behaviour before paying for the archive copy and
        # immutable release audit; the remainder exercises the real pathway.
        self.assertTrue(callable(getattr(arsiv, 'load_comparison', None)),
                        'comparison package loading is required')
        original_data = arsiv.DATA
        fixture_release = self.fixture_release()
        package = Path(__file__).resolve().parents[1] / 'data/comparisons/03-tracer.json'
        payload = json.loads(package.read_text(encoding='utf-8'))
        # Legitimate Windows line endings must survive byte-exact publication.
        synthesis = next(r['values'] for r in payload['records'] if r['kind'] == 'comparison_synthesis')
        synthesis['text'] += '\r\n'
        with tempfile.TemporaryDirectory() as tmp:
            arsiv.DATA = Path(tmp) / 'data'
            try:
                shutil.copytree(original_data, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
                (arsiv.DATA / 'current.json').write_text(json.dumps({'release_id': fixture_release}) + '\n')
                before = arsiv.current()
                base = arsiv.DATA / 'releases' / before
                hashes = {p.name: arsiv.sha(p) for p in base.iterdir() if p.is_file()}
                tree_hashes = {p.relative_to(arsiv.DATA): arsiv.sha(p) for p in (arsiv.DATA / 'releases').rglob('*') if p.is_file()}
                receipts = {p.relative_to(arsiv.DATA): arsiv.sha(p) for p in (arsiv.DATA / 'deliveries').glob('02-*.json')}
                self.assertGreaterEqual(len(receipts), 8)
                previous_delivery = json.loads((base / 'manifest.json').read_text())['phase2_delivery']
                self.assertEqual(previous_delivery['completed_prefix'], ['tip','dem','iyi','yeni-yol','dbp','emep','saadet','demokrat'])
                work = arsiv.open_workspace(tmp)
                arsiv.load_comparison(work, payload)
                with self.assertRaises(RuntimeError):
                    arsiv.publish_release(work, fail_at='json', refresh=True)
                self.assertEqual(arsiv.current(), before)
                work = arsiv.open_workspace(tmp)
                arsiv.load_comparison(work, payload)
                release = arsiv.publish_release(work, refresh=True)
                self.assertNotEqual(before, release)
                folder = arsiv.DATA / 'releases' / release
                manifest = json.loads((folder / 'manifest.json').read_text())
                data = json.loads((folder / 'records.json').read_text())
                report = (folder / 'index.html').read_text(encoding='utf-8')
                self.assertEqual(manifest['data_schema_version'], 6)
                self.assertEqual(manifest['renderer_version'], arsiv.RENDERER_VERSION)
                self.assertEqual(manifest['phase2_delivery'], previous_delivery)
                self.assertEqual(len(data['comparison_row']), 9)
                self.assertEqual(sum(row['state'] == 'not_researched' for row in data['comparison_row']), 7)
                self.assertEqual([row['party_id'] for row in data['comparison_row']],
                                 ['yeni-parti','tip','dem','iyi','yeni-yol','dbp','emep','saadet','demokrat'])
                for row in data['comparison_row']:
                    rid = row['id']
                    for link in (f'id="comparison-{rid}"', f'id="dossier-comparison-{rid}"',
                                 f'href="#comparison-{rid}"', f'href="#dossier-comparison-{rid}"'):
                        self.assertIn(link, report)
                self.assertIn('35 (otuz beş) asıl ve 5 (beş) yedek', report)
                self.assertIn('0205-iyi-charter-download-v1', report)
                self.assertIn('0203-tip-charter-v1', report)
                for text in ('elli asıl', 'yirmi beş yedek', 'altmış asıl', 'otuz yedek',
                             'onda birinin', 'beşte birinin', 'Henüz incelenmedi'):
                    self.assertIn(text, report)
                self.assertEqual(hashes, {p.name: arsiv.sha(p) for p in base.iterdir() if p.is_file()})
                self.assertEqual(tree_hashes, {p: arsiv.sha(arsiv.DATA / p) for p in tree_hashes})
                self.assertEqual(receipts, {p: arsiv.sha(arsiv.DATA / p) for p in receipts})
                # publish_release audits the closed snapshot before changing current.
                self.assertEqual(arsiv.current(), release)
            finally:
                arsiv.DATA = original_data


if __name__ == '__main__':
    unittest.main()
