"""Substantive closure must survive omissions in the selected source inventory."""
import json
import hashlib
from pathlib import Path
import shutil
import tempfile
import unittest

import arsiv
import test_comparisons


class SourceBasisCellTest(unittest.TestCase):
    def test_supersession_requires_previous_row_and_new_source_basis(self):
        old_key = dict(topic_id='aday-tanitimi', party_id='tip', source_role='charter', context_judgment='old-row')
        new_key = dict(old_key, context_judgment='new-row')
        basis = dict(cells=[dict(id='old-cell', logical_key=old_key, mapping_records=[], basis_ids=['old-basis']),
                            dict(id='new-cell', logical_key=new_key, mapping_records=[], basis_ids=['new-basis'])])
        first = dict(id='revision-1', epoch=1, selection=arsiv.canonical_json({'rows': [dict(id='old-row')]}))
        second = dict(id='revision-2', epoch=2)
        link = dict(revision_id='revision-2', old_cell_id='old-cell', new_cell_id='new-cell',
                    old_row_id='old-row', new_row_id='new-row', source_basis_refs='["new-basis"]',
                    reason='test-only source-backed replacement')
        data = dict(comparison_row=[dict(id='old-row'), dict(id='new-row')], comparison_completion_supersession=[link])
        selection = {'rows': [dict(id='new-row')]}
        self.assertEqual(arsiv.completion_superseded_cells(data, second, [first, second], basis, selection), {'old-cell'})
        for bad in (dict(link, source_basis_refs='["wrong"]'), dict(link, reason=''), dict(link, old_row_id='missing')):
            with self.assertRaisesRegex(ValueError, 'Kaynak ardıllığı'):
                arsiv.completion_superseded_cells(dict(data, comparison_completion_supersession=[bad]), second,
                                                   [first, second], basis, selection)

    def test_source_scope_requires_its_mapped_topic_and_organ(self):
        scope = dict(id='0304-tip-charter-scope-aday-tanitim-html-scope', party_id='tip',
                     version_id='0203-tip-charter-v1', sections='HTML tüzük Bölüm 1–7, Madde 1.1–7.2',
                     query_terms='Kamu adayı tanıtımı', reviewed_at='2026-11-13T13:55:32.558426+00:00',
                     result='no_explicit_statement',
                     reason='HTML tüzüğün tüm bölümleri ve ilgili hükümleri incelendi. Aday belirleme yetkisi PMye verilir; incelenen sürümde kamu seçimi aday adaylarının tanıtımına ilişkin ayrı usul açıklanmaz.')
        old = '0304-tip-charter-scope-aday-tanitim-html-row'
        new = '04-03-v3-0304-tip-charter-scope-aday-tanitim-html-row'
        key = dict(topic_id='aday-tanitimi', party_id='tip', source_role='charter',
                   version_id='0203-tip-charter-v1', level='ulusal ve yerel',
                   organ='Kamu adayı tanıtımı', context_judgment=old)
        cell = dict(id='cell-test', logical_key=key, disposition='no_explicit_statement',
                    source_judgment_record=dict(id=old, scope_id=scope['id'], state=scope['result'],
                                                **{k: v for k, v in key.items() if k != 'context_judgment'}),
                    mapping_records=[dict(old_row_id=old, new_row_id='intermediate', reason='authored mapping'),
                                     dict(old_row_id='intermediate', new_row_id=new, reason='authored mapping')],
                    basis_ids=['scope-basis'], field_dispositions=[])
        assertion = {'scope-basis': dict(kind='dated_source_scope', scope=scope)}
        row = dict(id=new, taxonomy_version=4, state='no_explicit_statement', scope_id=scope['id'],
                   **{k: v for k, v in key.items() if k != 'context_judgment'})
        data = dict(comparison_row=[row], comparison_review_scope=[scope], comparison_field=[],
                    finding_evidence=[], missing=[], attempt=[])
        self.assertTrue(arsiv.validate_source_basis_cells(data, 4, [cell], assertion))
        for candidate in (dict(data, comparison_row=[]),
                          dict(data, comparison_row=[dict(row, organ='başka organ')]),
                          dict(data, comparison_review_scope=[dict(scope, reason='değiştirilmiş')])):
            with self.subTest(candidate=candidate), self.assertRaisesRegex(ValueError, 'Kaynak yükümlülüğü'):
                arsiv.validate_source_basis_cells(candidate, 4, [cell], assertion)


class CompletionCoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reviewed = test_comparisons.ComparisonReleaseTest.reviewed_current()
        cls.taxonomy = cls.reviewed['comparison_contract'][0]['taxonomy_version']

    def altered(self, table, index, **changes):
        data = dict(self.reviewed)
        data[table] = list(data[table])
        data[table][index] = dict(data[table][index], **changes)
        return data

    def modern(self):
        payload = json.loads((Path(__file__).resolve().parents[1] /
                              'data/comparisons/03-completion-review-v2.json').read_text())
        data = dict(self.reviewed)
        for table in arsiv.COMPLETION_V2_TABLES:
            data[table] = [r['values'] for r in payload['records'] if r['kind'] == table]
        return data

    def test_real_review_and_legacy_snapshot_remain_valid(self):
        self.assertTrue(arsiv.validate_completion(self.reviewed))
        legacy = dict(self.reviewed)
        del legacy['comparison_completion']
        self.assertTrue(arsiv.validate_completion(legacy))

    def test_legacy_proof_projection_survives_additions_but_not_mutation(self):
        old = next(r for r in self.reviewed['comparison_row'] if r['taxonomy_version'] == self.taxonomy)
        added = dict(old, id='test-only-new-same-taxonomy-row')
        candidate = dict(self.reviewed, comparison_row=self.reviewed['comparison_row'] + [added],
                         comparison_contract=[dict(self.reviewed['comparison_contract'][0], stage='partial')])
        self.assertTrue(arsiv.validate_legacy_completion_projection(candidate))
        candidate['comparison_row'] = [dict(r, organ='changed') if r['id'] == old['id'] else r
                                       for r in candidate['comparison_row']]
        with self.assertRaisesRegex(ValueError, 'Önceki kaynak kapanışı kayıtları'):
            arsiv.validate_legacy_completion_projection(candidate)

    def test_independent_basis_detects_coordinated_source_omissions(self):
        basis = json.loads((Path(__file__).resolve().parents[1] /
                            'data/comparisons/03-completion-basis-v2-source.json').read_text())
        self.assertTrue(arsiv.validate_source_basis_universe(self.reviewed, basis))
        target = '04-03-v3-0304-tip-charter-scope-aday-tanitim-html-row'
        row = next(r for r in self.reviewed['comparison_row'] if r['id'] == target)
        inventory = next(i for i in self.reviewed['comparison_source_inventory']
                         if i['taxonomy_version'] == self.taxonomy)
        field = next(f for f in self.reviewed['comparison_field']
                     if any(r['id'] == f['row_id'] and r['taxonomy_version'] == self.taxonomy
                            for r in self.reviewed['comparison_row']))
        synthesis = next(s for s in self.reviewed['comparison_synthesis'] if s['taxonomy_version'] == self.taxonomy)
        candidates = [
            dict(self.reviewed, comparison_row=[r for r in self.reviewed['comparison_row'] if r['id'] != target]),
            dict(self.reviewed, comparison_row=[dict(r, organ='başka organ') if r['id'] == row['id'] else r
                                                for r in self.reviewed['comparison_row']]),
            dict(self.reviewed, comparison_source_inventory=[i for i in self.reviewed['comparison_source_inventory']
                                                             if i['id'] != inventory['id']]),
            dict(self.reviewed, comparison_field=[f for f in self.reviewed['comparison_field'] if f['id'] != field['id']]),
            dict(self.reviewed, comparison_synthesis=[s for s in self.reviewed['comparison_synthesis']
                                                       if s['id'] != synthesis['id']]),
        ]
        for candidate in candidates:
            with self.subTest(removed=set(self.reviewed) - set(candidate)), self.assertRaisesRegex(ValueError, 'Kaynak (yükümlülüğü|evreni)'):
                arsiv.validate_source_basis_universe(candidate, basis)

    def test_risk_coverage_requires_linked_field_and_synthesis_decisions(self):
        root = Path(__file__).resolve().parents[1] / 'data/comparisons'
        basis = json.loads((root / '03-completion-basis-v2-source.json').read_text())
        risk = json.loads((root / '03-completion-risk-v2-source.json').read_text())
        universe, decisions = risk['expected_risk_universe'], risk['decisions']
        self.assertTrue(arsiv.validate_source_risk_review(self.reviewed, basis, universe, decisions))
        stripped = [d for d in decisions if d['kind'] not in ('field_support', 'synthesis_support')]
        with self.assertRaisesRegex(ValueError, 'Kaynak anlamı riski'):
            arsiv.validate_source_risk_review(self.reviewed, basis, universe, stripped)
        principle = next(d for d in decisions if d['id'] == 'SR25:field:tip-kapitalizm-principle')
        tampered = [dict(d, summary_passage_ids=['not-a-real-passage']) if d is principle else d for d in decisions]
        with self.assertRaisesRegex(ValueError, 'field:principle'):
            arsiv.validate_source_risk_review(self.reviewed, basis, universe, tampered)

    def test_source_basis_round_trips_in_closed_storage_format(self):
        root = Path(__file__).resolve().parents[1] / 'data/comparisons'
        basis = json.loads((root / '03-completion-basis-v2-source.json').read_text())
        risk = json.loads((root / '03-completion-risk-v2-source.json').read_text())
        head, cells = arsiv.completion_basis_records(basis, risk['expected_risk_universe'],
                                                     'test-basis', '2026-11-15T16:52:28Z')
        restored, restored_risk = arsiv.decode_completion_basis(head, cells)
        self.assertEqual(restored, basis)
        self.assertEqual(restored_risk, risk['expected_risk_universe'])
        self.assertTrue(arsiv.validate_completion_basis_successor(basis, restored))
        altered_cells = list(restored['cells'])
        altered_cells[0] = dict(altered_cells[0], disposition='document_missing')
        with self.assertRaisesRegex(ValueError, 'Önceki kaynak yükümlülüğü'):
            arsiv.validate_completion_basis_successor(basis, dict(restored, cells=altered_cells))
        self.assertTrue(arsiv.validate_source_basis_universe(self.reviewed, restored))
        self.assertTrue(arsiv.validate_source_risk_review(self.reviewed, restored, restored_risk, risk['decisions']))

    def test_initial_basis_reconciles_authored_origins_before_adoption(self):
        root = Path(__file__).resolve().parents[1] / 'data/comparisons'
        basis = json.loads((root / '03-completion-basis-v2-source.json').read_text())
        risk = json.loads((root / '03-completion-risk-v2-source.json').read_text())
        self.assertTrue(arsiv.verify_initial_completion_basis(basis, risk['expected_risk_universe']))
        with self.assertRaisesRegex(ValueError, 'bağımsız hazırlanmış bütüne'):
            arsiv.verify_initial_completion_basis(dict(basis, cells=basis['cells'][1:]), risk['expected_risk_universe'])
        with self.assertRaisesRegex(ValueError, 'bağımsız hazırlanmış bütüne'):
            arsiv.verify_initial_completion_basis(basis, risk['expected_risk_universe'][1:])
        self.assertTrue(arsiv.verify_successor_completion_basis(basis, basis))
        documents = list(basis['source_documents'])
        documents[0] = dict(documents[0], sha256='0' * 64)
        with self.assertRaisesRegex(ValueError, 'Önceki kaynak paketinin kökeni'):
            arsiv.verify_successor_completion_basis(basis, dict(basis, source_documents=documents))

    def test_adoption_payload_retains_real_source_decisions(self):
        root = Path(__file__).resolve().parents[1] / 'data/comparisons'
        basis = json.loads((root / '03-completion-basis-v2-source.json').read_text())
        risk = json.loads((root / '03-completion-risk-v2-source.json').read_text())
        payload = arsiv.completion_adoption_payload(self.reviewed, basis, risk, '2026-11-15T16:52:28Z')
        head = next(r['values'] for r in payload['records'] if r['kind'] == 'comparison_completion_basis')
        cells = [r['values'] for r in payload['records'] if r['kind'] == 'comparison_coverage_disposition']
        revision = next(r['values'] for r in payload['records'] if r['kind'] == 'comparison_completion_revision')
        source, universe = arsiv.decode_completion_basis(head, cells)
        self.assertEqual(source, basis)
        self.assertEqual(universe, risk['expected_risk_universe'])
        self.assertEqual(json.loads(revision['review'])['decisions'], risk['decisions'])
        self.assertEqual(json.loads(revision['legacy_anchor'])['release_id'], self.reviewed['release_id'])

    def test_import_of_v2_is_atomic_while_export_guard_is_active(self):
        original = arsiv.DATA
        root = Path(__file__).resolve().parents[1] / 'data/comparisons'
        basis = json.loads((root / '03-completion-basis-v2-source.json').read_text())
        payload = json.loads((root / '03-completion-review-v2.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            arsiv.DATA = temp / 'data'
            try:
                arsiv.DATA.mkdir()
                for source in basis['source_documents']:
                    relative = Path(source['path']).relative_to('data')
                    target = arsiv.DATA / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(original / relative, target)
                work = temp / 'work'
                work.mkdir()
                shutil.copyfile(original / 'releases' / self.reviewed['release_id'] / 'records.sqlite3',
                                work / 'records.sqlite3')
                (arsiv.DATA / '.write.lock').write_text(json.dumps({'token': 'isolated-test-token'}))
                (work / 'workspace.json').write_text(json.dumps({'token': 'isolated-test-token', 'base': self.reviewed['release_id']}))
                before = arsiv.sha(work / 'records.sqlite3')
                with self.assertRaisesRegex(ValueError, 'sürüm 2'):
                    arsiv.load_comparison(work, payload)
                self.assertEqual(arsiv.sha(work / 'records.sqlite3'), before)
                (work / 'workspace.json').write_text(json.dumps({'token': 'isolated-test-token', 'base': 'wrong-base'}))
                with self.assertRaisesRegex(ValueError, 'gerçek taban'):
                    arsiv.load_comparison(work, payload)
                self.assertEqual(arsiv.sha(work / 'records.sqlite3'), before)
            finally:
                arsiv.DATA = original

    def test_manifest_binds_revision_basis_selection_and_review(self):
        data = self.modern()
        manifest = arsiv.completion_manifest_fields(data)
        revision = data['comparison_completion_revision'][0]
        self.assertEqual(manifest['comparison_completion_revision_id'], revision['id'])
        self.assertEqual(manifest['comparison_completion_stage'], 'complete')
        changed = dict(data, comparison_completion_revision=[dict(revision, review=revision['review'] + ' ')])
        self.assertNotEqual(manifest['comparison_completion_review_sha256'],
                            arsiv.completion_manifest_fields(changed)['comparison_completion_review_sha256'])
        changed = dict(data, comparison_completion_revision=[dict(revision, selection=revision['selection'] + ' ')])
        self.assertNotEqual(manifest['comparison_completion_selection_sha256'],
                            arsiv.completion_manifest_fields(changed)['comparison_completion_selection_sha256'])
        cells = list(data['comparison_coverage_disposition'])
        cells[0] = dict(cells[0], disposition='changed')
        changed = dict(data, comparison_coverage_disposition=cells)
        self.assertNotEqual(manifest['comparison_completion_basis_sha256'],
                            arsiv.completion_manifest_fields(changed)['comparison_completion_basis_sha256'])

    def test_selected_reader_projection_retains_old_snapshot_records(self):
        data = self.modern()
        revision = dict(data['comparison_completion_revision'][0])
        selection = json.loads(revision['selection'])
        retired = selection['rows'][0]['id']
        selection['rows'] = [r for r in selection['rows'] if r['id'] != retired]
        selection['fields'] = [f for f in selection['fields'] if f['row_id'] != retired]
        revision['selection'] = arsiv.canonical_json(selection)
        data['comparison_completion_revision'] = [revision]
        visible = arsiv.comparison_render_data(data)
        self.assertIn(retired, {r['id'] for r in data['comparison_row']})
        self.assertNotIn(retired, {r['id'] for r in visible['comparison_row']})

    def test_frozen_renderer_22_reproduces_historical_release(self):
        folder = arsiv.DATA / 'releases' / self.reviewed['release_id']
        self.assertEqual(arsiv.render_comparison_snapshot(self.reviewed, arsiv.render_v22_report).encode(),
                         (folder / 'index.html').read_bytes())

    def test_revision_validation_preserves_history_and_binds_active_stage(self):
        root = Path(__file__).resolve().parents[1] / 'data/comparisons'
        basis = json.loads((root / '03-completion-basis-v2-source.json').read_text())
        risk = json.loads((root / '03-completion-risk-v2-source.json').read_text())
        head, cells = arsiv.completion_basis_records(basis, risk['expected_risk_universe'],
                                                     'test-basis', '2026-11-15T16:52:28Z')
        anchor = arsiv.canonical_json(dict(release_id=self.reviewed['release_id'], marker_sha256=hashlib.sha256(
            arsiv.canonical_json(self.reviewed['comparison_completion'][0]).encode()).hexdigest()))
        revision = dict(id='test-revision-1', version=2, epoch=1, parent_revision_id=None,
                        taxonomy_version=self.taxonomy, basis_id=head['id'], stage='complete',
                        created_at='2026-11-15T16:52:28Z', legacy_anchor=anchor,
                        selection=arsiv.canonical_json(arsiv.completion_selection(self.reviewed, self.taxonomy)),
                        review=arsiv.canonical_json({'decisions': risk['decisions']}), reason='test fixture')
        data = dict(self.reviewed, comparison_completion_basis=[head], comparison_coverage_disposition=cells,
                    comparison_completion_revision=[revision], comparison_completion_supersession=[])
        self.assertTrue(arsiv.validate_completion_revisions(data))
        self.assertTrue(arsiv.validate_completion(data))
        successor = dict(revision, id='test-revision-2', epoch=2, parent_revision_id=revision['id'],
                         stage='partial', reason='source work in progress')
        partial = dict(data, comparison_contract=[dict(data['comparison_contract'][0], stage='partial')],
                       comparison_completion_revision=[revision, successor])
        self.assertTrue(arsiv.validate_completion_revisions(partial))
        self.assertTrue(arsiv.validate_comparison_descent(data, partial))
        altered = dict(partial, comparison_completion_basis=[dict(head, source_catalog='{}')])
        with self.assertRaisesRegex(ValueError, 'Önceki kaynak kapanışı kaydı'):
            arsiv.validate_comparison_descent(data, altered)
        altered = dict(partial, comparison_completion_revision=[successor])
        with self.assertRaisesRegex(ValueError, 'Önceki kaynak kapanışı kaydı'):
            arsiv.validate_comparison_descent(data, altered)
        with self.assertRaisesRegex(ValueError, 'revizyon zinciri'):
            arsiv.validate_completion_revisions(dict(partial, comparison_completion_revision=[revision, dict(successor, parent_revision_id='wrong')]))
        changed = dict(data, comparison_contract=[dict(data['comparison_contract'][0], stage='partial')])
        with self.assertRaisesRegex(ValueError, 'aktif aşamayla'):
            arsiv.validate_completion_revisions(changed)

    def test_reviewed_finding_provenance_is_required(self):
        data = dict(self.reviewed)
        data['comparison_semantic_review'] = [r for r in data['comparison_semantic_review']
                                              if r['subject_kind'] != 'comparison_field']
        data['review'] = [r for r in data['review'] if r['kind'] != 'finding']
        with self.assertRaises(ValueError):
            arsiv.validate_completion(data)

    def test_rejects_changed_applicable_level_and_organ(self):
        index = next(i for i, r in enumerate(self.reviewed['comparison_row'])
                     if r['taxonomy_version'] == self.taxonomy and r['state'] == 'evidence')
        row = self.reviewed['comparison_row'][index]
        for key in ('level', 'organ'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                arsiv.validate_comparisons(self.altered('comparison_row', index, **{key: row[key] + ' değiştirilmiş'}))

    def test_rejects_missing_source_review(self):
        data = dict(self.reviewed)
        marker = dict(data['comparison_completion'][0])
        evidence = json.loads(marker['evidence'])
        evidence['source_review']['checks'] = []
        marker['evidence'] = json.dumps(evidence, ensure_ascii=False)
        data['comparison_completion'] = [marker]
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(data)

    def test_rejects_dropped_field_and_synthesis(self):
        for table, select in (
            ('comparison_field', lambda x: any(r['id'] == x['row_id'] and r['taxonomy_version'] == self.taxonomy for r in self.reviewed['comparison_row'])),
            ('comparison_synthesis', lambda x: x['taxonomy_version'] == self.taxonomy),
        ):
            data = dict(self.reviewed)
            target = next(x for x in data[table] if select(x))
            data[table] = [x for x in data[table] if x is not target]
            with self.subTest(table=table), self.assertRaises(ValueError):
                arsiv.validate_comparisons(data)

    def test_rejects_open_selected_states(self):
        index = next(i for i, r in enumerate(self.reviewed['comparison_row'])
                     if r['taxonomy_version'] == self.taxonomy and r['state'] == 'evidence')
        for state in ('not_researched', 'in_progress'):
            with self.subTest(state=state), self.assertRaises(ValueError):
                arsiv.validate_comparisons(self.altered('comparison_row', index, state=state))

    def test_rejects_missing_topic_party_and_unmatched_inventory(self):
        data = dict(self.reviewed)
        row = next(r for r in data['comparison_row'] if r['taxonomy_version'] == self.taxonomy)
        data['comparison_row'] = [r for r in data['comparison_row'] if not
                                  (r['taxonomy_version'] == self.taxonomy and r['topic_id'] == row['topic_id'] and r['party_id'] == row['party_id'])]
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(data)
        index = next(i for i, r in enumerate(self.reviewed['comparison_source_inventory'])
                     if r['taxonomy_version'] == self.taxonomy and r['full_text_available'])
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(self.altered('comparison_source_inventory', index, unmatched_headings='["eşleşmeyen bölüm"]'))

    def test_rejects_available_document_as_missing(self):
        index = next(i for i, r in enumerate(self.reviewed['comparison_source_inventory'])
                     if r['taxonomy_version'] == self.taxonomy and r['full_text_available'])
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(self.altered('comparison_source_inventory', index, full_text_available=0))

    def test_coordinated_omission_is_not_a_coverage_decision(self):
        """The independent authored disposition still requires the omitted organ."""
        data = self.modern()
        target = '04-03-v3-0304-tip-charter-scope-aday-tanitim-html-row'
        row = next(r for r in data['comparison_row'] if r['id'] == target)
        marker = dict(data['comparison_completion'][0])
        proof = json.loads(marker['evidence'])
        proof['rows'] = [r for r in proof['rows'] if r['id'] != target]
        next(p for p in proof['coverage_review']['parties'] if p['party_id'] == row['party_id'])['row_count'] -= 1
        marker['evidence'] = json.dumps(proof, ensure_ascii=False)
        data['comparison_completion'] = [marker]
        data['comparison_row'] = [r for r in data['comparison_row'] if r['id'] != target]
        revision = dict(data['comparison_completion_revision'][0])
        selection = json.loads(revision['selection'])
        selection['rows'] = [r for r in selection['rows'] if r['id'] != target]
        revision['selection'] = arsiv.canonical_json(selection)
        revision['legacy_anchor'] = arsiv.canonical_json(dict(release_id=self.reviewed['release_id'],
            marker_sha256=hashlib.sha256(arsiv.canonical_json(marker).encode()).hexdigest()))
        data['comparison_completion_revision'] = [revision]
        with self.assertRaisesRegex(ValueError, 'Kaynak yükümlülüğü satır'):
            arsiv.validate_comparisons(data)

    def test_review_requires_substantive_inspections(self):
        data = self.modern()
        self.assertTrue(arsiv.validate_completion(data))
        revision = dict(data['comparison_completion_revision'][0])
        review = json.loads(revision['review'])
        review['decisions'] = [d for d in review['decisions'] if d['kind'] not in ('field_support', 'synthesis_support')]
        revision['review'] = arsiv.canonical_json(review)
        data['comparison_completion_revision'] = [revision]
        with self.assertRaisesRegex(ValueError, 'Kaynak anlamı riski'):
            arsiv.validate_comparisons(data)

    def test_complete_base_can_descend_to_partial_revision(self):
        base = self.modern()
        first = base['comparison_completion_revision'][0]
        successor = dict(first, id='test-partial-revision', epoch=2, parent_revision_id=first['id'],
                         stage='partial', reason='source work in progress')
        candidate = dict(base, comparison_contract=[dict(base['comparison_contract'][0], stage='partial')],
                         comparison_completion_revision=[first, successor])
        self.assertTrue(arsiv.validate_comparison_descent(base, candidate))

