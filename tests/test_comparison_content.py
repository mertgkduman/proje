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
    def test_reconcile_rolls_back_after_complete_mapping_loader_failure(self):
        source = arsiv.DATA / 'releases' / arsiv.current() / 'records.sqlite3'
        original_data, original_load, original_export = arsiv.DATA, arsiv.load_comparison, arsiv.export_db
        before_pointer = arsiv.current()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root / 'work'
            work.mkdir()
            arsiv.DATA = root / 'data'
            arsiv.DATA.mkdir()
            try:
                shutil.copyfile(source, work / 'records.sqlite3')
                (work / 'workspace.json').write_text(json.dumps({'base': before_pointer, 'token': 'test-token'}))
                (arsiv.DATA / '.write.lock').write_text(json.dumps({'token': 'test-token'}))
                (arsiv.DATA / 'current.json').write_text(json.dumps({'release_id': before_pointer}))
                db = arsiv.connect_readonly(work / 'records.sqlite3')
                try:
                    topics = [dict(r) for r in db.execute('SELECT * FROM comparison_topic WHERE taxonomy_version=2')]
                    dictionary = [dict(r) for r in db.execute('SELECT * FROM topic WHERE taxonomy_version=2')]
                    bases = [dict(r) for r in db.execute('SELECT * FROM topic_basis WHERE taxonomy_version=2')]
                    rows = [dict(r) for r in db.execute('SELECT * FROM comparison_row WHERE taxonomy_version=2')]
                    mappings = []
                    for row in rows:
                        fields = [{'old_id': r['id'], 'new_id': 'v3-' + r['id']} for r in db.execute('SELECT id FROM comparison_field WHERE row_id=?', (row['id'],))]
                        changes = [{'old_id': r['id'], 'new_id': 'v3-' + r['id']} for r in db.execute('SELECT id FROM comparison_change WHERE row_id=?', (row['id'],))]
                        mappings.append(dict(old_row_id=row['id'], new_row_id='v3-' + row['id'], topic_id=row['topic_id'], reason='Test eşlemesi', fields=fields, changes=changes))
                finally:
                    db.close()
                for topic in topics:
                    topic['taxonomy_version'] = 3
                topics[0]['definition'] += ' Test kapsamı.'
                taxonomy = dict(taxonomy_version=3, records=[dict(kind='comparison_topic', values=t) for t in topics], row_mappings=mappings)
                section = json.loads((Path(__file__).resolve().parents[1] / 'data/comparisons/03-source-inventory.json').read_text())['sections'][0]
                inventory = dict(taxonomy_version=3, status='complete', sections=[section])
                backfill = dict(contract_version=1, taxonomy_version=3, stage='partial', records=[])
                before = arsiv.sha(work / 'records.sqlite3')
                captured = []
                def fail_after_mapping(candidate, payload):
                    captured.extend(r for r in payload['records'] if r['kind'] == 'comparison_row')
                    raise RuntimeError('injected loader failure')
                arsiv.load_comparison = fail_after_mapping
                with self.assertRaisesRegex(RuntimeError, 'injected loader failure'):
                    arsiv.comparison_reconcile(work, taxonomy, inventory, backfill)
                self.assertEqual(len(captured), len(rows))
                self.assertEqual(arsiv.sha(work / 'records.sqlite3'), before)
                self.assertEqual(arsiv.current(), before_pointer)
                # Exercise the actual transactional loader; source-byte export is
                # independently checked by the integration publication audit.
                for item in dictionary + bases:
                    item['taxonomy_version'] = 3
                taxonomy['records'] = ([dict(kind='topic', values=t) for t in dictionary] +
                                       [dict(kind='topic_basis', values=b) for b in bases] + taxonomy['records'])
                arsiv.load_comparison = original_load
                arsiv.export_db = lambda *args, **kwargs: {}
                arsiv.comparison_reconcile(work, taxonomy, inventory, backfill)
                db = arsiv.connect_readonly(work / 'records.sqlite3')
                try:
                    self.assertEqual(db.execute('SELECT taxonomy_version FROM comparison_contract').fetchone()[0], 3)
                    self.assertEqual(db.execute('SELECT count(*) FROM comparison_row WHERE taxonomy_version=2').fetchone()[0], len(rows))
                    self.assertEqual(db.execute('SELECT count(*) FROM comparison_row WHERE taxonomy_version=3').fetchone()[0], len(rows))
                    for state in ('evidence', 'no_explicit_statement', 'document_missing'):
                        old = next(row for row in rows if row['state'] == state)
                        new = dict(db.execute('SELECT * FROM comparison_row WHERE id=?', ('v3-' + old['id'],)).fetchone())
                        for key in ('state', 'party_id', 'version_id', 'scope_id', 'missing_id', 'source_role'):
                            self.assertEqual(new[key], old[key], (state, key))
                    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
                finally:
                    db.close()
                self.assertEqual(arsiv.current(), before_pointer)
            finally:
                arsiv.DATA, arsiv.load_comparison, arsiv.export_db = original_data, original_load, original_export

    def test_reconcile_rejects_one_party_new_topic_without_changing_workspace(self):
        reconcile = getattr(arsiv, 'comparison_reconcile', None)
        self.assertTrue(callable(reconcile), 'Atomic comparison reconciliation is required')
        source = arsiv.DATA / 'releases' / arsiv.current() / 'records.sqlite3'
        previous_data = arsiv.DATA
        before_pointer = arsiv.current()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root / 'work'
            work.mkdir()
            arsiv.DATA = root / 'data'
            arsiv.DATA.mkdir()
            try:
                shutil.copyfile(source, work / 'records.sqlite3')
                (work / 'workspace.json').write_text(json.dumps({'base': before_pointer, 'token': 'test-token'}))
                (arsiv.DATA / '.write.lock').write_text(json.dumps({'token': 'test-token'}))
                (arsiv.DATA / 'current.json').write_text(json.dumps({'release_id': before_pointer}))
                before = arsiv.sha(work / 'records.sqlite3')
                taxonomy = {'taxonomy_version': 3, 'records': [{'kind': 'comparison_topic', 'values': {'topic_id': 'new-topic', 'taxonomy_version': 3}}], 'row_mappings': []}
                inventory = {'taxonomy_version': 3, 'status': 'complete', 'sections': []}
                backfill = {'contract_version': 1, 'taxonomy_version': 3, 'stage': 'partial', 'records': [{'kind': 'comparison_row', 'values': {'id': 'one-party', 'topic_id': 'new-topic', 'taxonomy_version': 3, 'party_id': 'iyi', 'state': 'evidence'}}]}
                with self.assertRaisesRegex(ValueError, '(?i)dokuz|parti'):
                    reconcile(work, taxonomy, inventory, backfill)
                self.assertEqual(arsiv.sha(work / 'records.sqlite3'), before)
                self.assertEqual(arsiv.current(), before_pointer)
            finally:
                arsiv.DATA = previous_data

    def test_selected_taxonomy_rendering_keeps_legacy_byte_compatibility(self):
        render = getattr(arsiv, 'render_comparison_snapshot', None)
        self.assertTrue(callable(render), 'Selected-taxonomy snapshot rendering is required')
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        self.assertEqual(render(data, rapor.render_report), rapor.render_report(data))
        historical = data['comparison_topic'][0]
        current = copy.deepcopy(historical)
        current['taxonomy_version'] = 3
        current['definition'] = 'Yeni sözlükteki tanım'
        data['comparison_topic'].append(current)
        data['comparison_contract'][0]['taxonomy_version'] = 3
        old_row = next(r for r in data['comparison_row'] if r['party_id'] == 'tip')
        old_field = next(f for f in data['comparison_field'] if f['row_id'] == old_row['id'])
        old_finding = next(f for f in data['finding'] if f['id'] == old_field['summary_finding_id'])
        active_row = copy.deepcopy(next(r for r in data['comparison_row'] if r['party_id'] == 'iyi'))
        active_row.update(id='selected-row', taxonomy_version=3)
        data['comparison_row'].append(active_row)
        active_field = copy.deepcopy(next(f for f in data['comparison_field'] if f['row_id'] != old_row['id']))
        active_field.update(id='selected-field', row_id='selected-row')
        data['comparison_field'].append(active_field)
        passage = next(e['passage_id'] for e in data['finding_evidence'] if e['finding_id'] == active_field['quote_finding_id'])
        report = render(data, rapor.render_report)
        self.assertIn('Yeni sözlükteki tanım', report)
        self.assertNotIn(historical['definition'], report)
        self.assertNotIn('id="finding-' + old_finding['id'] + '"', report)
        for target in ('id="comparison-selected-row"', 'id="dossier-comparison-selected-row"', 'href="#source-' + passage + '"'):
            self.assertIn(target, report)
        arsiv.validate_phase_one_html(data, report)
        active_id = active_field['summary_finding_id']
        comparison_ids = {f[k] for f in data['comparison_field'] for k in ('summary_finding_id', 'quote_finding_id')}
        ordinary_id = next(f['id'] for f in data['finding'] if f['id'] not in comparison_ids and 'data-finding-id="' + f['id'] + '"' in report)
        for fid in (active_id, ordinary_id):
            with self.assertRaisesRegex(ValueError, 'Bulgu HTML'):
                arsiv.validate_phase_one_html(data, report.replace('data-finding-id="' + fid + '"', 'data-removed-finding="' + fid + '"'))
        shared = copy.deepcopy(data)
        shared['dossier_field'][0]['finding_id'] = old_finding['id']
        self.assertIn(old_finding['id'], {f['id'] for f in arsiv.comparison_render_data(shared)['finding']})
        self.assertEqual(historical['taxonomy_version'], 1)

    def test_selected_projection_reproduces_renderer_17_snapshot(self):
        path = Path(__file__).resolve().parents[1] / 'src' / 'rapor_v17.py'
        spec = importlib.util.spec_from_file_location('frozen_rapor_v17', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        release = arsiv.current()
        while release:
            folder = arsiv.DATA / 'releases' / release
            manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
            if manifest['renderer_version'] == 17:
                break
            release = manifest.get('base_release')
        self.assertTrue(release)
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        self.assertEqual(arsiv.render_comparison_snapshot(data, module.render_report).encode(), (folder / 'index.html').read_bytes())

    def test_program_topic_basis_points_to_the_actual_heading(self):
        root = Path(__file__).resolve().parents[1]
        package = json.loads((root / 'data/comparisons/03-taxonomy.json').read_text(encoding='utf-8'))
        passages = {r['values']['id']: r['values']['exact'] for r in package['records'] if r['kind'] == 'passage'}
        expected = {
            'sosyalist-demokrasi': 'SOSYALİST DEMOKRASİ',
            'kapitalizm-bunalim': 'KAPİTALİZM BÜTÜNSEL BİR BUNALIM İÇİNDE',
            'turkiye-cumhuriyet-tarih': 'TÜRKİYE’DE BURJUVA DEVRİMİ',
            'siyasal-ittifaklar': '3. YOL VE İTTİFAKLAR',
            'cezaevleri': 'CEZAEVLERİ',
            'uyusturucu-mucadele': 'UYUŞTURUCUYA KARŞI',
            'tuketici-haklari': 'Tüketiciler Korunmalı',
            'yaribaskanlik-sistemi': 'Yarı Başkanlık',
            'senato': 'Senato',
            'yabanci-sermaye': 'Yabancı Sermaye',
            'finansal-hizmetler': 'Finansal Hizmetler',
            'abd-iliskileri': 'ABD İlişkileri',
            'istihbarat': 'İSTİHBARAT',
        }
        for identifier, heading in expected.items():
            self.assertEqual(passages['03-program-' + identifier], heading, identifier)

    def test_repeated_fields_merge_only_when_conditions_match_and_keep_sources(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        row = next(r for r in data['comparison_row'] if r['party_id'] == 'iyi')
        field = next(f for f in data['comparison_field'] if f['row_id'] == row['id'])
        original_passage = next(e['passage_id'] for e in data['finding_evidence'] if e['finding_id'] == field['quote_finding_id'])
        passage = copy.deepcopy(next(p for p in data['passage'] if p['id'] == original_passage))
        passage['id'] = 'repeat-source'
        data['passage'].append(passage)
        repeated = copy.deepcopy(field)
        repeated['id'] = 'repeated-field'
        for key in ('summary_finding_id', 'quote_finding_id'):
            finding = copy.deepcopy(next(f for f in data['finding'] if f['id'] == field[key]))
            finding['id'] = 'repeated-' + key
            data['finding'].append(finding)
            data['finding_evidence'].append(dict(finding_id=finding['id'], passage_id='repeat-source', role='support'))
            repeated[key] = finding['id']
        data['comparison_field'].append(repeated)
        report = rapor.render_report(data)
        quote = next(f['text'] for f in data['finding'] if f['id'] == field['quote_finding_id'])
        views = [report.split('id="' + prefix + row['id'] + '"', 1)[1].split('<details>', 1)[0] for prefix in ('comparison-', 'dossier-comparison-')]
        for view in views:
            self.assertEqual(view.count('“' + quote + '”'), 1)
            self.assertIn('#source-' + original_passage, view)
            self.assertIn('#source-repeat-source', view)
        repeated['condition_key'] = 'Farklı koşul'
        report = rapor.render_report(data)
        views = [report.split('id="' + prefix + row['id'] + '"', 1)[1].split('<details>', 1)[0] for prefix in ('comparison-', 'dossier-comparison-')]
        for view in views:
            self.assertEqual(view.count('“' + quote + '”'), 2)
            self.assertIn('Farklı koşul', view)

    def test_taxonomy_basis_passages_precede_their_references(self):
        root = Path(__file__).resolve().parents[1]
        baseline = json.loads((root / 'data/releases/9119e174a8d94f2d9c77efa155347242/records.json').read_text(encoding='utf-8'))
        for name in ('03-taxonomy.json', '03-exception-cases.json'):
            package = json.loads((root / 'data/comparisons' / name).read_text(encoding='utf-8'))
            passages = {item['id'] for item in baseline['passage']}
            topics = set()
            for entry in package['records']:
                if entry['kind'] == 'passage':
                    passages.add(entry['values']['id'])
                elif entry['kind'] == 'topic_basis':
                    self.assertIn(entry['values']['passage_id'], passages, name)
                elif entry['kind'] in ('topic', 'comparison_topic'):
                    value = entry['values']
                    key = (entry['kind'], value.get('id', value.get('topic_id')), value['taxonomy_version'])
                    self.assertNotIn(key, topics, name)
                    topics.add(key)

    def test_source_inventory_is_converted_for_complete_snapshot(self):
        convert = getattr(arsiv, 'comparison_inventory_records', None)
        self.assertTrue(callable(convert), 'Kaynak envanteri snapshot kayıtlarına aktarılmalı')
        section = dict(party_id='iyi', version_id='0205-iyi-charter-download-v1', source_role='charter', section='Madde 48', page_range='PDF 31', full_text_available=True, scanned_at='2026-11-13', topic_ids=['merkez-yonetimi-secimi'], unmatched_headings=[], search_boundary='Madde 48', missing_id=None)
        inventory = dict(taxonomy_version=1, status='complete', sections=[section])
        records = convert(inventory, 1)
        self.assertEqual(records[0]['kind'], 'comparison_source_inventory')
        self.assertEqual(records[0]['values']['topic_ids'], ['merkez-yonetimi-secimi'])
        self.assertEqual(records, convert(inventory, 1))
        inventory['taxonomy_version'] = 2
        next_version = convert(inventory, 2)
        self.assertNotEqual(records[0]['values']['id'], next_version[0]['values']['id'])
        inventory['taxonomy_version'] = 1
        section['unmatched_headings'] = ['Eşleşmeyen başlık']
        with self.assertRaises(ValueError):
            convert(inventory, 1)
        section['unmatched_headings'] = []
        inventory['status'] = 'in_progress'
        with self.assertRaises(ValueError):
            convert(inventory, 1)

    def test_program_fields_are_distinguishable_in_both_views(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        package = json.loads((Path(__file__).resolve().parents[1] / 'data/comparisons/03-program-opening.json').read_text(encoding='utf-8'))
        data['comparison_contract'][0].update(taxonomy_version=2, stage='partial')
        for entry in package['records']:
            data[entry['kind']].append(entry['values'])
        report = rapor.render_report(data)
        for label in ('İlke', 'Hedef', 'Önerilen araç'):
            self.assertGreaterEqual(report.count('>' + label + '</h5>'), 2)

    def test_child_topic_follows_its_parent_in_comparison_view(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        common = dict(taxonomy_version=2, domain='program', applicable_levels='ulusal', basis_kind='program')
        data['comparison_topic'].extend([
            dict(common, topic_id='parent', parent_topic_id=None, order_index=50, definition='ÜST KONU ÖRNEĞİ'),
            dict(common, topic_id='child', parent_topic_id='parent', order_index=1, definition='ALT KONU ÖRNEĞİ'),
        ])
        report = rapor.render_report(data)
        self.assertLess(report.index('ÜST KONU ÖRNEĞİ'), report.index('ALT KONU ÖRNEĞİ'))

    def test_new_comparison_topic_requires_a_sourced_dictionary_topic(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        data['comparison_contract'][0].update(taxonomy_version=2, stage='partial')
        data['comparison_topic'].append(dict(topic_id='unsupported', taxonomy_version=2, domain='program', parent_topic_id=None, order_index=1, definition='Kaynaklanmamış konu', applicable_levels='ulusal', basis_kind='program'))
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(data)

    def test_complete_stage_requires_a_closed_source_inventory(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        data['scope_party'] = [p for p in data['scope_party'] if p['party_id'] in ('iyi', 'tip')]
        data['comparison_row'] = [r for r in data['comparison_row'] if r['party_id'] in ('iyi', 'tip')]
        data['comparison_contract'][0]['stage'] = 'complete'
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(data)
        data['comparison_source_inventory'] = []
        sources = [('iyi', 'charter', '0205-iyi-charter-download-v1'), ('iyi', 'program', '0205-iyi-program-page-v1'), ('tip', 'charter', '0203-tip-charter-v1'), ('tip', 'program', '0203-tip-program-v1')]
        for party, role, version in sources:
            data['comparison_source_inventory'].append(dict(id=party + role, taxonomy_version=1, party_id=party, version_id=version, source_role=role, section='İlgili bölüm', page_range=None, full_text_available=1, scanned_at='2026-11-13', topic_ids='["merkez-yonetimi-secimi"]', unmatched_headings='[]', search_boundary='İlgili bölüm incelendi', missing_id=None))
        self.assertTrue(arsiv.validate_comparisons(data))
        data['comparison_source_inventory'][0]['unmatched_headings'] = '["Eşleşmeyen başlık"]'
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(data)
        data['comparison_source_inventory'][0]['unmatched_headings'] = '[]'
        data['comparison_source_inventory'][0]['version_id'] = '0203-tip-charter-v1'
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(data)

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

    def test_alternatives_remain_independent_across_taxonomy_versions(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        row = next(r for r in data['comparison_row'] if r['party_id'] == 'iyi')
        row['alternative_group'] = 'same-alternatives'
        other = copy.deepcopy(row)
        other.update(id='alt-old', version_id='0205-iyi-charter-istanbul-v1')
        data['comparison_row'].append(other)
        old_passage = next(p for p in data['passage'] if p['id'] == '03-iyi-once-uye')
        for typ in ('summary', 'quote'):
            fid = 'alt-old-' + typ
            data['finding'].append(dict(id=fid, party_id='iyi', heading='Tüzük', pair_id='alt-old-pair', text=old_passage['exact'], provenance=typ, epistemic_type='claim'))
            data['finding_evidence'].append(dict(finding_id=fid, passage_id=old_passage['id'], role='support'))
        data['comparison_field'].append(dict(id='alt-old-field', row_id=other['id'], field='charter_answer', summary_finding_id='alt-old-summary', quote_finding_id='alt-old-quote', condition_key=None))
        topic = copy.deepcopy(data['comparison_topic'][0])
        topic['taxonomy_version'] = 3
        data['comparison_topic'].append(topic)
        data['topic'].append(dict(id=topic['topic_id'], label='Merkez seçimi', taxonomy_version=3, valid_from='2026-11-13', status='verified', change_reason='Test sözlüğü'))
        data['topic_basis'].append(dict(topic_id=topic['topic_id'], taxonomy_version=3, passage_id='03-iyi-sonra-uye', rationale='Tüzük hükmü', source_role='charter'))
        for old in (row, other):
            new = copy.deepcopy(old)
            new.update(id='v3-' + old['id'], taxonomy_version=3)
            data['comparison_row'].append(new)
            for field in [f for f in data['comparison_field'] if f['row_id'] == old['id']]:
                new_field = copy.deepcopy(field)
                new_field.update(id='v3-' + field['id'], row_id=new['id'])
                data['comparison_field'].append(new_field)
        data['comparison_contract'][0].update(taxonomy_version=3, stage='partial')
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
        self.assertGreaterEqual(arsiv.RENDERER_VERSION, 17)

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
                self.assertTrue(db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='comparison_source_inventory'").fetchone())
            finally:
                db.close()

    def test_migrated_inventory_is_included_in_snapshot_export(self):
        release = arsiv.current()
        source = arsiv.DATA / 'releases' / release / 'records.sqlite3'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'records.sqlite3'
            shutil.copyfile(source, path)
            db = arsiv.connect(path)
            try:
                arsiv.migrate_comparisons(db, Path(temp) / 'backup.sqlite3')
                db.execute("INSERT INTO comparison_source_inventory VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", ('inventory-test', 1, 'iyi', '0205-iyi-charter-download-v1', 'charter', 'Madde 48', None, 1, '2026-11-13', '["merkez-yonetimi-secimi"]', '[]', 'Madde 48', None))
                db.commit()
            finally:
                db.close()
            exported = arsiv.export_db(path, 'test')
            self.assertEqual(exported['comparison_source_inventory'][0]['id'], 'inventory-test')

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
                db.execute("INSERT INTO topic VALUES (?,?,?,?,?,?)", ('test-tarihsel', 'Tarihsel kaynak', 2, '2026-11-13', 'verified', 'Test'))
                db.execute("INSERT INTO topic_basis (topic_id,taxonomy_version,passage_id,rationale,source_role) VALUES (?,?,?,?,?)", ('test-tarihsel', 2, '0207-dbp-bdp-program-copy', 'Tarihsel BDP programı', 'historical'))
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
