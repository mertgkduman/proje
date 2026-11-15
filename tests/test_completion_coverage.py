"""Substantive closure must survive omissions in the selected source inventory."""
import json
import hashlib
import datetime as dt
from pathlib import Path
import shutil
import tempfile
import unittest

import arsiv
import test_comparisons


class SourceBasisCellTest(unittest.TestCase):
    def test_new_taxonomy_basis_retains_source_assertions(self):
        old = dict(taxonomy_version=4, source_assertions={'a': {'kind': 'dated_source_scope'}},
                   source_documents=[dict(path='data/example.json', sha256='old')])
        new = dict(taxonomy_version=5, source_assertions=dict(old['source_assertions'], b={'kind': 'supported_field'}),
                   source_documents=list(old['source_documents']))
        self.assertTrue(arsiv.validate_completion_basis_successor(old, new))
        with self.assertRaisesRegex(ValueError, 'kaynak dayanağı'):
            arsiv.validate_completion_basis_successor(old, dict(new, source_assertions={}))
        with self.assertRaisesRegex(ValueError, 'hemen ardılı'):
            arsiv.validate_completion_basis_successor(old, dict(new, taxonomy_version=6))

    def test_supersession_requires_previous_row_and_new_source_basis(self):
        old_key = dict(topic_id='aday-tanitimi', party_id='tip', source_role='charter', context_judgment='old-row')
        new_key = dict(old_key, context_judgment='new-row')
        basis = dict(cells=[dict(id='old-cell', logical_key=old_key, mapping_records=[], basis_ids=['old-basis']),
                            dict(id='new-cell', logical_key=new_key, mapping_records=[], basis_ids=['new-basis'])],
                     source_assertions={}, _correction_registry=[])
        first = dict(id='revision-1', epoch=1, taxonomy_version=4, selection=arsiv.canonical_json({'rows': [dict(id='old-row')]}))
        second = dict(id='revision-2', epoch=2, taxonomy_version=4)
        link = dict(revision_id='revision-2', old_cell_id='old-cell', new_cell_id='new-cell',
                    old_row_id='old-row', new_row_id='new-row', source_basis_refs='["new-basis"]',
                    reason='test-only source-backed replacement')
        data = dict(comparison_row=[dict(id='old-row'), dict(id='new-row')], finding=[], comparison_completion_supersession=[link])
        selection = {'rows': [dict(id='new-row')]}
        with self.assertRaisesRegex(ValueError, 'bağımsız düzeltme'):
            arsiv.completion_superseded_cells(data, second, [first, second], basis, selection)
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
        cls.reviewed = test_comparisons.ComparisonReleaseTest.reviewed_v1_history()
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

    def test_historical_contract_fixture_survives_v2_current(self):
        """A live v2 release cannot turn the historical v1 fixture into v2."""
        original = arsiv.DATA
        v2 = self.modern()
        self.assertTrue(arsiv.validate_completion(v2))
        historical_id = '85b1a453ce2346a8ad0df325a2b73ae9'
        with tempfile.TemporaryDirectory() as temp:
            arsiv.DATA = Path(temp) / 'data'
            try:
                historical = arsiv.DATA / 'releases' / historical_id
                historical.mkdir(parents=True)
                shutil.copyfile(original / 'releases' / historical_id / 'records.json', historical / 'records.json')
                current = arsiv.DATA / 'releases' / 'fixture-v2-current'
                current.mkdir()
                v2 = dict(v2, release_id='fixture-v2-current')
                (current / 'records.json').write_text(json.dumps(v2, ensure_ascii=False), encoding='utf-8')
                (arsiv.DATA / 'current.json').write_text(json.dumps({'release_id': 'fixture-v2-current'}), encoding='utf-8')
                live = test_comparisons.ComparisonReleaseTest.reviewed_current()
                self.assertEqual(live['release_id'], 'fixture-v2-current')
                self.assertEqual(live, v2)
                self.assertTrue(arsiv.validate_completion(live))
                class HistoricalContract(CompletionCoverageTest):
                    pass
                HistoricalContract.setUpClass()
                fixture = HistoricalContract('test_real_review_and_legacy_snapshot_remain_valid')
                fixture.test_real_review_and_legacy_snapshot_remain_valid()
                self.assertEqual(fixture.reviewed['release_id'], historical_id)
                self.assertFalse(fixture.reviewed.get('comparison_completion_revision'))
            finally:
                arsiv.DATA = original

    def structural_gap_fixture(self):
        """STRUCTURAL FUTURE fixture; no missing TİP program is claimed."""
        data = self.modern()
        head = data['comparison_completion_basis'][0]
        basis, _ = arsiv.decode_completion_basis(head, data['comparison_coverage_disposition'])
        new = next(c for c in basis['cells'] if c['id'] == 'cell-5337d008fcac7dfe93c8431d')
        new_row = new['fulfilment_locator_only']
        scope = basis['source_assertions'][new['basis_ids'][0]]['scope']
        missing = dict(id='test-structural-program-gap', party_id='tip', heading='Program', topic_id='abd-iliskileri',
                       status='Bulunamadı', attempt_id='test-structural-search', reason='STRUCTURAL FIXTURE only')
        attempt = dict(id='test-structural-search', party_id='tip', heading='Program', topic_id='abd-iliskileri',
                       type='search', result='no_result', attempted_at='2026-11-12T00:00:00Z', reason='STRUCTURAL FIXTURE only',
                       lead_id=None, query='STRUCTURAL FIXTURE: prior program search', source_version_id=None)
        old_key = dict(new['logical_key'], version_id=None, context_judgment='test-structural-gap-row')
        old_id = 'cell-' + hashlib.sha256(arsiv.canonical_json(old_key).encode()).hexdigest()[:24]
        assertion = dict(kind='documentary_gap', missing_id=missing['id'], missing=missing, attempt=attempt)
        gap_basis_id = 'basis-' + hashlib.sha256(arsiv.canonical_json(assertion).encode()).hexdigest()[:24]
        old = dict(id=old_id, logical_key=old_key, disposition='document_missing',
                   source_judgment_record=dict(id='test-structural-gap-row', state='document_missing',
                     selection_reason='STRUCTURAL FIXTURE only', scope_id=None, missing_id=missing['id'],
                     taxonomy_version=self.taxonomy, alternative_group=None,
                     **{k: v for k, v in old_key.items() if k != 'context_judgment'}),
                   mapping_records=[], basis_ids=[gap_basis_id], field_dispositions=[])
        old_context = dict(logical_key=old_key, disposition='document_missing', source_reason='STRUCTURAL FIXTURE only',
                           fields=[], scope=None, missing=missing, attempt=attempt)
        new_context = dict(logical_key=new['logical_key'], disposition='no_explicit_statement',
                           source_reason=new['source_judgment_record']['selection_reason'], fields=[],
                           scope=scope, missing=None, attempt=None)
        decision = dict(id='test-structural-correction', old_cell_id=old['id'], new_cell_id=new['id'],
                        old_row_id='test-structural-gap-row', new_row_id=new_row, result='supersedes', reviewer_kind='agent',
                        reviewed_at='2026-11-15T19:00:00Z', reason='STRUCTURAL FIXTURE: preserve real TİP scope and synthetic prior gap.',
                        old_context=old_context, new_context=new_context,
                        gap_reassessment=dict(missing_id=missing['id'], attempt_id=attempt['id'], version_id=scope['version_id'],
                          scope_id=scope['id'], query_terms=scope['query_terms'], sections=scope['sections'],
                          reviewed_at=scope['reviewed_at'], coverage='complete_relevant_scope',
                          reason='STRUCTURAL FIXTURE: the real bounded scope is reused.'))
        content = arsiv.canonical_json({'decisions': [decision]})
        registration = dict(decision=decision, origin=dict(path='data/comparisons/test-structural-correction.json',
                            pointer='/decisions/0', content=content, sha256=hashlib.sha256(content.encode()).hexdigest()))
        basis = dict(basis, cells=basis['cells'] + [old], source_assertions=dict(basis['source_assertions'], **{gap_basis_id: assertion}),
                     _correction_registry=[registration])
        first = dict(id='test-gap-first', epoch=1, taxonomy_version=self.taxonomy, created_at='2026-11-15T19:00:00Z',
                     selection=arsiv.canonical_json({'rows': [dict(id='test-structural-gap-row')]}))
        second = dict(id='test-gap-second', epoch=2, taxonomy_version=self.taxonomy, created_at='2026-11-15T19:01:00Z')
        link = dict(revision_id=second['id'], old_cell_id=old['id'], new_cell_id=new['id'], old_row_id='test-structural-gap-row',
                    new_row_id=new_row, reason='STRUCTURAL FIXTURE only',
                    source_basis_refs=arsiv.canonical_json(dict(correction_id=decision['id'], basis_ids=new['basis_ids'])))
        data = dict(data, comparison_row=data['comparison_row'] + [dict(old['source_judgment_record'], taxonomy_version=self.taxonomy)],
                    missing=data['missing'] + [missing], attempt=data['attempt'] + [attempt], comparison_completion_supersession=[link])
        return data, basis, first, second, link, decision, registration, new, old, assertion

    def test_structural_missing_to_reviewed_negative_with_real_tip_source(self):
        data, basis, first, second, link, decision, registration, new, old, assertion = self.structural_gap_fixture()
        new_row = new['fulfilment_locator_only']
        scope = basis['source_assertions'][new['basis_ids'][0]]['scope']
        self.assertEqual(arsiv.completion_superseded_cells(data, second, [first, second], basis, {'rows': [dict(id=new_row)]}), {old['id']})
        version = next(v for v in data['document_version'] if v['id'] == scope['version_id'])
        document_id = version['document_id']
        for changes in (
            dict(document=[dict(d, party_id='dem') if d['id'] == document_id else d for d in data['document']]),
            dict(document=[dict(d, title='Unrelated document') if d['id'] == document_id else d for d in data['document']]),
            dict(comparison_review_scope=[dict(s, sections='') if s['id'] == scope['id'] else s for s in data['comparison_review_scope']]),
        ):
            with self.subTest(changes=list(changes)), self.assertRaises(ValueError):
                arsiv.completion_superseded_cells(dict(data, **changes), second, [first, second], basis, {'rows': [dict(id=new_row)]})

    def test_re_review_rejects_unrelated_positive_as_negative_scope_correction(self):
        data = self.modern()
        first = data['comparison_completion_revision'][0]
        head = data['comparison_completion_basis'][0]
        basis, _ = arsiv.decode_completion_basis(head, data['comparison_coverage_disposition'])
        old_id = '04-03-v3-0304-tip-charter-scope-aday-tanitim-html-row'
        new_id = '04-03-v3-0304-tip-charter-context-aday-tanitim-html-row'
        self.assertIn(old_id, {r['id'] for r in arsiv.comparison_render_data(data)['comparison_row']})
        old = next(c for c in basis['cells'] if c['fulfilment_locator_only'] == old_id)
        new = next(c for c in basis['cells'] if c['fulfilment_locator_only'] == new_id)
        selection = json.loads(first['selection'])
        selection['rows'] = [r for r in selection['rows'] if r['id'] != old_id]
        second = dict(first, id='test-forged-correction', epoch=2, parent_revision_id=first['id'],
                      selection=arsiv.canonical_json(selection), reason='ordinary source is not a correction')
        link = dict(revision_id=second['id'], old_cell_id=old['id'], new_cell_id=new['id'],
                    old_row_id=old_id, new_row_id=new_id,
                    source_basis_refs=arsiv.canonical_json(['basis-8a236988dbbb141d12717df4']),
                    reason='ordinary source is not a correction')
        data['comparison_completion_revision'] = [first, second]
        data['comparison_completion_supersession'] = [link]
        with self.assertRaises(ValueError):
            arsiv.validate_completion_revisions(data)

    def test_re_review_rejects_forged_source_reading_decisions(self):
        data = self.modern()
        first = dict(data['comparison_completion_revision'][0])
        review = json.loads(first['review'])
        for decision in review['decisions']:
            if decision['kind'] == 'field_support':
                decision.update(original_field_review={'forged': 'yes'}, judgment='x', source_reading='x',
                                recorded_at='x', decision='unsupported')
        first['review'] = arsiv.canonical_json(review)
        data['comparison_completion_revision'] = [first]
        head = data['comparison_completion_basis'][0]
        basis, risks = arsiv.decode_completion_basis(head, data['comparison_coverage_disposition'])
        for label, call in (('risk', lambda: arsiv.validate_source_risk_review(data, basis, risks, review['decisions'])),
                            ('revision', lambda: arsiv.validate_completion_revisions(data))):
            with self.subTest(gate=label), self.assertRaises(ValueError):
                call()

    def test_re_review_accepts_authenticated_witness_with_new_identity(self):
        data = self.modern()
        first = data['comparison_completion_revision'][0]
        review = json.loads(first['review'])
        old = next(d for d in review['decisions'] if d['id'] == 'SR25:field:tip-kapitalizm-principle')
        old['id'] = 'test-identical-authored-reading-new-identity'
        head = data['comparison_completion_basis'][0]
        basis, risks = arsiv.decode_completion_basis(head, data['comparison_coverage_disposition'])
        self.assertTrue(arsiv.validate_source_risk_review(data, basis, risks, review['decisions']))

    def test_committed_adoption_package_passes_shared_validation(self):
        data = self.modern()
        self.assertTrue(arsiv.validate_completion(data))
        self.assertTrue(arsiv.validate_comparisons(data))

    def test_importer_rejects_forged_review_and_unrelated_correction_atomically(self):
        original = arsiv.DATA
        data = self.modern()
        self.assertTrue(arsiv.validate_completion(data))
        first = data['comparison_completion_revision'][0]
        basis, _ = arsiv.decode_completion_basis(data['comparison_completion_basis'][0], data['comparison_coverage_disposition'])
        with tempfile.TemporaryDirectory() as temp:
            arsiv.DATA = Path(temp) / 'data'
            try:
                arsiv.DATA.mkdir()
                work = Path(temp) / 'work'
                work.mkdir()
                shutil.copyfile(original / 'releases' / self.reviewed['release_id'] / 'records.sqlite3', work / 'records.sqlite3')
                (arsiv.DATA / '.write.lock').write_text(json.dumps({'token': 'test-isolated'}))
                (work / 'workspace.json').write_text(json.dumps({'token': 'test-isolated', 'base': self.reviewed['release_id']}))
                db = arsiv.connect(work / 'records.sqlite3')
                try:
                    arsiv.migrate_comparisons(db, work / 'seed-backup.sqlite3')
                    for table in ('comparison_completion_basis', 'comparison_coverage_disposition', 'comparison_completion_revision'):
                        for values in data[table]:
                            keys = list(values)
                            db.execute(f"INSERT INTO {table} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", [values[k] for k in keys])
                    db.commit()
                finally:
                    db.close()
                before = arsiv.sha(work / 'records.sqlite3')
                review = json.loads(first['review'])
                for decision in review['decisions']:
                    if decision['kind'] == 'field_support':
                        decision.update(original_field_review={'forged': 'yes'}, judgment='x', source_reading='x',
                                        recorded_at='x', decision='unsupported')
                revision = dict(first, id='test-import-forged', epoch=2, parent_revision_id=first['id'],
                                review=arsiv.canonical_json(review), reason='test forged review')
                payload = dict(contract_version=2, taxonomy_version=self.taxonomy, stage='complete',
                               records=[dict(kind='comparison_completion_revision', values=revision)])
                with self.assertRaisesRegex(ValueError, 'kayıtlı özgün'):
                    arsiv.load_comparison(work, payload)
                self.assertEqual(arsiv.sha(work / 'records.sqlite3'), before)
                old_id = '04-03-v3-0304-tip-charter-scope-aday-tanitim-html-row'
                new_id = '04-03-v3-0304-tip-charter-context-aday-tanitim-html-row'
                old = next(c for c in basis['cells'] if c['fulfilment_locator_only'] == old_id)
                new = next(c for c in basis['cells'] if c['fulfilment_locator_only'] == new_id)
                selected = json.loads(first['selection'])
                selected['rows'] = [r for r in selected['rows'] if r['id'] != old_id]
                revision = dict(first, id='test-import-unrelated', epoch=2, parent_revision_id=first['id'],
                                selection=arsiv.canonical_json(selected), reason='test unrelated source')
                link = dict(revision_id=revision['id'], old_cell_id=old['id'], new_cell_id=new['id'],
                            old_row_id=old_id, new_row_id=new_id,
                            source_basis_refs=arsiv.canonical_json(['basis-8a236988dbbb141d12717df4']), reason='not a correction')
                payload['records'] = [dict(kind='comparison_completion_revision', values=revision),
                                      dict(kind='comparison_completion_supersession', values=link)]
                with self.assertRaisesRegex(ValueError, 'bağımsız düzeltme'):
                    arsiv.load_comparison(work, payload)
                self.assertEqual(arsiv.sha(work / 'records.sqlite3'), before)
            finally:
                arsiv.DATA = original

    def test_new_registered_principle_reading_is_typed_and_dated(self):
        data = self.modern()
        head = data['comparison_completion_basis'][0]
        basis, risks = arsiv.decode_completion_basis(head, data['comparison_coverage_disposition'])
        decisions = json.loads(data['comparison_completion_revision'][0]['review'])['decisions']
        original = next(d for d in decisions if d['id'] == 'SR25:field:tip-kapitalizm-principle')

        def registered(candidate):
            body = arsiv.canonical_json({'decisions': [candidate]})
            origin = dict(path='data/comparisons/test-authored-reading.json', pointer='/decisions/0', content=body,
                          sha256=hashlib.sha256(body.encode()).hexdigest())
            return dict(initial=basis['_reading_registry']['initial'], additional=[dict(decision=candidate, origin=origin)])

        fresh = dict(original, id='new-test-principle', judgment='Test-only new bounded reading: source rejects automatic collapse.',
                     recorded_at='2026-11-15T17:30:00+00:00')
        amended = [fresh if d is original else d for d in decisions]
        self.assertTrue(arsiv.validate_source_risk_review(data, basis, risks, amended, reading_registry=registered(fresh)))
        for changes in (dict(recorded_at='x'), dict(decision='unsupported'), dict(source_reading='')):
            bad = dict(fresh, **changes)
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, 'kararı kaynak bağları veya kökeni'):
                arsiv.validate_source_risk_review(data, basis, risks,
                                                  [bad if d is original else d for d in decisions],
                                                  reading_registry=registered(bad))
        unrelated = [d for d in decisions if d is not original]
        with self.assertRaisesRegex(ValueError, 'field:principle'):
            arsiv.validate_source_risk_review(data, basis, risks, unrelated)

    def test_registered_non_field_decision_bodies_cannot_be_replaced(self):
        data = self.modern()
        basis, risks = arsiv.decode_completion_basis(data['comparison_completion_basis'][0],
                                                     data['comparison_coverage_disposition'])
        decisions = json.loads(data['comparison_completion_revision'][0]['review'])['decisions']
        for kind in ('scope_or_document_gap', 'synthesis_support', 'change_support', 'physical_page_gap', 'same_hash_copy'):
            target = next(d for d in decisions if d['kind'] == kind)
            changed = [dict(d, judgment='forged') if d is target else d for d in decisions]
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'kayıtlı özgün'):
                arsiv.validate_source_risk_review(data, basis, risks, changed)

    def test_sampled_sr25_context_accepts_authenticated_replacement(self):
        data = self.modern()
        old_head = data['comparison_completion_basis'][0]
        old_basis, risks = arsiv.decode_completion_basis(old_head, data['comparison_coverage_disposition'])
        previous = data['comparison_completion_revision'][0]
        root = Path(__file__).resolve().parents[1]
        fixture = json.loads((root / 'tests/fixtures/completion_sr25_replacement.json').read_text())
        row, field, semantic = [entry['values'] for entry in fixture['records']]
        source_path = 'data/comparisons/test-sr25-replacement.json'
        key = {k: row[k] for k in ('topic_id', 'party_id', 'source_role', 'version_id', 'level', 'organ')}
        key['context_judgment'] = row['id']
        assertion = dict(kind='supported_field', field='principle', condition_key=None,
                         summary_finding_id=field['summary_finding_id'], quote_finding_id=field['quote_finding_id'],
                         passage_ids=['0304-tip-program-kapitalizm-p1', '0304-tip-program-kapitalizm-p2', '0304-tip-program-kapitalizm-q'],
                         original_field=dict(path=source_path, pointer='/records/1/values'),
                         semantic_reviews=[dict(record=semantic, source=dict(path=source_path, pointer='/records/2/values'))], finding_reviews=[])
        aid = 'basis-' + hashlib.sha256(arsiv.canonical_json(assertion).encode()).hexdigest()[:24]
        cid = 'cell-' + hashlib.sha256(arsiv.canonical_json(key).encode()).hexdigest()[:24]
        cell = dict(id=cid, logical_key=key, disposition='evidence', source_judgment=dict(path=source_path, pointer='/records/0/values'),
                    source_judgment_record=row, mapping_refs=[], mapping_records=[], basis_ids=[aid],
                    field_dispositions=[dict(field='principle', disposition='source_supported', basis_id=aid)],
                    inventory_section_indexes=[], fulfilment_locator_only=row['id'])
        original_data = arsiv.DATA
        with tempfile.TemporaryDirectory() as temp:
            arsiv.DATA = Path(temp) / 'data'
            try:
                arsiv.DATA.mkdir()
                for source in old_basis['source_documents']:
                    relative = Path(source['path']).relative_to('data')
                    target = arsiv.DATA / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(original_data / relative, target)
                registrations, documents = {}, list(old_basis['source_documents'])
                for name in ('replacement', 'reading', 'correction'):
                    source = root / ('tests/fixtures/completion_sr25_' + name + '.json')
                    target = arsiv.DATA / ('comparisons/test-sr25-' + name + '.json')
                    shutil.copyfile(source, target)
                    content = target.read_text(encoding='utf-8')
                    path = 'data/comparisons/' + target.name
                    digest = hashlib.sha256(content.encode()).hexdigest()
                    documents.append(dict(path=path, sha256=digest, role='source_research_or_mapping', original_status=None))
                    if name != 'replacement':
                        registrations[name] = dict(decision=json.loads(content)['decisions'][0],
                                                   origin=dict(path=path, pointer='/decisions/0', content=content, sha256=digest))
                universe = [dict(item, cell_ids=item['cell_ids'] + [cid])
                            if (item['topic_id'], item['party_id']) == (row['topic_id'], row['party_id']) else item
                            for item in old_basis['universe']]
                reading_registry = dict(initial=old_basis['_reading_registry']['initial'], additional=[registrations['reading']])
                correction_registry = [registrations['correction']]
                new_basis = dict(old_basis, cells=old_basis['cells'] + [cell], universe=universe,
                                 source_documents=documents,
                                 source_assertions=dict(old_basis['source_assertions'], **{aid: assertion}),
                                 _reading_registry=reading_registry, _correction_registry=correction_registry)
                self.assertTrue(arsiv.verify_successor_completion_basis(old_basis, new_basis))
                created_at = dt.datetime.now(dt.timezone.utc).isoformat()
                head, cells = arsiv.completion_basis_records(new_basis, risks, 'test-sr25-basis',
                    created_at, old_head['id'])
                selection = json.loads(previous['selection'])
                old_row = '04-03-v3-0304-tip-program-kapitalizm-row'
                selection['rows'] = [r for r in selection['rows'] if r['id'] != old_row] + [row]
                selection['fields'] = [f for f in selection['fields'] if f['row_id'] != old_row] + [field]
                review = json.loads(previous['review'])
                review['decisions'] = [d for d in review['decisions'] if d['id'] != 'SR25:field:tip-kapitalizm-principle'] + [registrations['reading']['decision']]
                revision = dict(previous, id='test-sr25-revision', epoch=2, parent_revision_id=previous['id'],
                                basis_id=head['id'], created_at=created_at,
                                selection=arsiv.canonical_json(selection), review=arsiv.canonical_json(review),
                                reason='Test-only source-authenticated SR25 context replacement.')
                link = dict(revision_id=revision['id'], old_cell_id='cell-f791bd14f9b5dbaef66975e7', new_cell_id=cid,
                            old_row_id=old_row, new_row_id=row['id'],
                            source_basis_refs=arsiv.canonical_json(dict(correction_id=registrations['correction']['decision']['id'], basis_ids=[aid])),
                            reason='Test-only registered source-context decision.')
                candidate = dict(data, comparison_row=data['comparison_row'] + [row],
                                 comparison_field=data['comparison_field'] + [field],
                                 comparison_semantic_review=data['comparison_semantic_review'] + [semantic],
                                 comparison_completion_basis=data['comparison_completion_basis'] + [head],
                                 comparison_coverage_disposition=data['comparison_coverage_disposition'] + cells,
                                 comparison_completion_revision=[previous, revision],
                                 comparison_completion_supersession=[link])
                with self.assertRaisesRegex(ValueError, 'Sentez'):
                    arsiv.validate_completion_revisions(candidate)
                with self.assertRaisesRegex(ValueError, 'Sentez'):
                    arsiv.validate_comparisons(candidate)
                before_rebind_basis = new_basis
                before_rebind_candidate = candidate
                before_rebind_selection = json.loads(arsiv.canonical_json(selection))
                # The independently specified mechanical fixture rebinds the
                # exact original claim and review to the equivalent new row.
                template = json.loads((root / 'tests/fixtures/completion_synthesis_rebind.json').read_text())
                obligation = next(o for o in old_basis['synthesis_obligations'] if o['id'] == template['old_id'])
                new_claim = dict(obligation['source_authored_claim'], id=template['new_id'])
                meaning = json.loads(obligation['original_review']['reason'])
                for side in meaning['sides']:
                    if side['row_id'] == template['old_row_id']:
                        side['row_id'] = template['new_row_id']
                new_review = dict(obligation['original_review'], subject_id=template['new_id'], reason=arsiv.canonical_json(meaning))
                created_at = dt.datetime.now(dt.timezone.utc).isoformat()
                relation = dict(id='test-sr25-synthesis-lineage', kind='synthesis_supersession', revision_id=revision['id'],
                    old_id=template['old_id'], new_id=template['new_id'], result='supersedes', reviewer_kind='agent',
                    reviewed_at=created_at, reason=template['reason'], mode=template['mode'],
                    old_claim=obligation['source_authored_claim'], new_claim=new_claim,
                    old_review=obligation['original_review'], new_review=new_review)
                authored = dict(purpose=template['purpose'], records=[dict(kind='comparison_synthesis', values=new_claim),
                    dict(kind='comparison_semantic_review', values=new_review)], decisions=[relation])
                authored_path = arsiv.DATA / 'comparisons/test-sr25-synthesis-rebind.json'
                authored_content = arsiv.canonical_json(authored)
                authored_path.write_text(authored_content, encoding='utf-8')
                authored_ref = 'data/comparisons/test-sr25-synthesis-rebind.json'
                authored_sha = hashlib.sha256(authored_content.encode()).hexdigest()
                registration = dict(decision=relation, origin=dict(path=authored_ref, pointer='/decisions/0', content=authored_content, sha256=authored_sha))
                new_obligation = dict(id=new_claim['id'], topic_id=new_claim['topic_id'], source_authored_claim=new_claim,
                    source=dict(path=authored_ref, pointer='/records/0/values'), typed_source_judgment=meaning,
                    original_review=new_review, review_source=dict(path=authored_ref, pointer='/records/1/values'))
                new_basis = dict(new_basis, synthesis_obligations=new_basis['synthesis_obligations'] + [new_obligation],
                    source_documents=new_basis['source_documents'] + [dict(path=authored_ref, sha256=authored_sha, role='source_research_or_mapping', original_status=None)],
                    _correction_registry=new_basis['_correction_registry'] + [registration])
                self.assertTrue(arsiv.verify_successor_completion_basis(old_basis, new_basis))
                head, cells = arsiv.completion_basis_records(new_basis, risks, head['id'], created_at, old_head['id'])
                selection['syntheses'] = [s for s in selection['syntheses'] if s['id'] != template['old_id']] + [new_claim]
                revision = dict(revision, created_at=created_at, selection=arsiv.canonical_json(selection))
                evidence = [dict(e, synthesis_id=new_claim['id']) for e in data['comparison_synthesis_evidence'] if e['synthesis_id'] == template['old_id']]
                candidate = dict(candidate, comparison_synthesis=data['comparison_synthesis'] + [new_claim],
                    comparison_synthesis_evidence=data['comparison_synthesis_evidence'] + evidence,
                    comparison_semantic_review=candidate['comparison_semantic_review'] + [new_review],
                    comparison_completion_basis=data['comparison_completion_basis'] + [head],
                    comparison_coverage_disposition=data['comparison_coverage_disposition'] + cells,
                    comparison_completion_revision=[previous, revision])
                self.assertTrue(arsiv.validate_completion_revisions(candidate))
                self.assertTrue(arsiv.validate_comparisons(candidate))
                visible = arsiv.comparison_render_data(candidate)
                self.assertNotIn(old_row, {r['id'] for r in visible['comparison_row']})
                self.assertIn(row['id'], {r['id'] for r in visible['comparison_row']})
                self.assertNotIn(template['old_id'], {s['id'] for s in visible['comparison_synthesis']})
                self.assertIn(template['new_id'], {s['id'] for s in visible['comparison_synthesis']})
                report = arsiv.render_comparison_snapshot(candidate, arsiv.render_report)
                self.assertNotIn('id="comparison-' + old_row + '"', report)
                self.assertIn('id="comparison-' + row['id'] + '"', report)
                self.assertIn(arsiv.html.escape(new_claim['text']), report)
                # A second independently authored mechanical successor must
                # preserve A and B at their historical revision selections.
                final_claim = dict(new_claim, id='test-sr25-synthesis-rebound-again')
                final_review = dict(new_review, subject_id=final_claim['id'])
                chain_time = dt.datetime.now(dt.timezone.utc).isoformat()
                chain_relation = dict(relation, id='test-sr25-synthesis-second-lineage', revision_id='test-sr25-revision-3',
                    old_id=new_claim['id'], new_id=final_claim['id'], reviewed_at=chain_time,
                    old_claim=new_claim, new_claim=final_claim, old_review=new_review, new_review=final_review)
                chain_content = arsiv.canonical_json(dict(purpose='Test-only second mechanical lineage', records=[
                    dict(kind='comparison_synthesis', values=final_claim),
                    dict(kind='comparison_semantic_review', values=final_review)], decisions=[chain_relation]))
                chain_path = 'data/comparisons/test-sr25-synthesis-chain.json'
                (arsiv.DATA / 'comparisons/test-sr25-synthesis-chain.json').write_text(chain_content, encoding='utf-8')
                chain_sha = hashlib.sha256(chain_content.encode()).hexdigest()
                chain_registration = dict(decision=chain_relation, origin=dict(path=chain_path, pointer='/decisions/0',
                    content=chain_content, sha256=chain_sha))
                chain_obligation = dict(id=final_claim['id'], topic_id=final_claim['topic_id'], source_authored_claim=final_claim,
                    source=dict(path=chain_path, pointer='/records/0/values'), typed_source_judgment=meaning,
                    original_review=final_review, review_source=dict(path=chain_path, pointer='/records/1/values'))
                chain_basis = dict(new_basis, synthesis_obligations=new_basis['synthesis_obligations'] + [chain_obligation],
                    source_documents=new_basis['source_documents'] + [dict(path=chain_path, sha256=chain_sha,
                        role='source_research_or_mapping', original_status=None)],
                    _correction_registry=new_basis['_correction_registry'] + [chain_registration])
                self.assertTrue(arsiv.verify_successor_completion_basis(new_basis, chain_basis))
                chain_head, chain_cells = arsiv.completion_basis_records(chain_basis, risks, 'test-sr25-chain-basis', chain_time, head['id'])
                chain_selection = json.loads(revision['selection'])
                chain_selection['syntheses'] = [s for s in chain_selection['syntheses'] if s['id'] != new_claim['id']] + [final_claim]
                chain_revision = dict(revision, id=chain_relation['revision_id'], epoch=3, parent_revision_id=revision['id'],
                    basis_id=chain_head['id'], created_at=chain_time, selection=arsiv.canonical_json(chain_selection))
                chain_evidence = [dict(e, synthesis_id=final_claim['id']) for e in evidence]
                chain_candidate = dict(candidate, comparison_synthesis=candidate['comparison_synthesis'] + [final_claim],
                    comparison_synthesis_evidence=candidate['comparison_synthesis_evidence'] + chain_evidence,
                    comparison_semantic_review=candidate['comparison_semantic_review'] + [final_review],
                    comparison_completion_basis=candidate['comparison_completion_basis'] + [chain_head],
                    comparison_coverage_disposition=candidate['comparison_coverage_disposition'] + chain_cells,
                    comparison_completion_revision=[previous, revision, chain_revision])
                self.assertTrue(arsiv.validate_completion_revisions(chain_candidate))
                self.assertTrue(arsiv.validate_comparisons(chain_candidate))
                self.assertIn(template['old_id'], {s['id'] for s in json.loads(previous['selection'])['syntheses']})
                self.assertIn(new_claim['id'], {s['id'] for s in json.loads(revision['selection'])['syntheses']})
                self.assertIn(final_claim['id'], {s['id'] for s in arsiv.comparison_render_data(chain_candidate)['comparison_synthesis']})
                missing_terminal = dict(chain_selection, syntheses=[s for s in chain_selection['syntheses'] if s['id'] != final_claim['id']])
                with self.assertRaisesRegex(ValueError, 'sentez ardıllığı'):
                    arsiv.completion_superseded_syntheses(chain_candidate, chain_revision,
                        chain_candidate['comparison_completion_revision'], chain_basis, missing_terminal)
                # A later taxonomy carries the immutable earlier decisions but
                # has its own synthesis obligations and active selection.
                next_taxonomy = self.taxonomy + 1
                next_claim = dict(final_claim, id='test-sr25-next-taxonomy-synthesis', taxonomy_version=next_taxonomy)
                next_review = dict(final_review, subject_id=next_claim['id'])
                next_path = 'data/comparisons/test-sr25-next-taxonomy.json'
                next_content = arsiv.canonical_json(dict(purpose='Test-only taxonomy selection', records=[
                    dict(kind='comparison_synthesis', values=next_claim),
                    dict(kind='comparison_semantic_review', values=next_review)]))
                (arsiv.DATA / 'comparisons/test-sr25-next-taxonomy.json').write_text(next_content, encoding='utf-8')
                next_obligation = dict(chain_obligation, id=next_claim['id'], source_authored_claim=next_claim,
                    source=dict(path=next_path, pointer='/records/0/values'), original_review=next_review,
                    review_source=dict(path=next_path, pointer='/records/1/values'))
                next_basis = dict(chain_basis, taxonomy_version=next_taxonomy, synthesis_obligations=[next_obligation],
                    source_documents=chain_basis['source_documents'] + [dict(path=next_path,
                        sha256=hashlib.sha256(next_content.encode()).hexdigest(), role='source_research_or_mapping', original_status=None)])
                self.assertTrue(arsiv.verify_successor_completion_basis(chain_basis, next_basis))
                next_selection = dict(chain_selection, syntheses=[next_claim])
                next_revision = dict(chain_revision, id='test-sr25-next-taxonomy', epoch=4,
                    parent_revision_id=chain_revision['id'], taxonomy_version=next_taxonomy,
                    selection=arsiv.canonical_json(next_selection))
                next_revisions = chain_candidate['comparison_completion_revision'] + [next_revision]
                self.assertEqual(arsiv.completion_superseded_syntheses(chain_candidate, next_revision,
                    next_revisions, next_basis, next_selection), set())
                # A correction authored as part of the new taxonomy cannot
                # silently retire an old-taxonomy claim; lineage is separate.
                cross = dict(chain_relation, id='test-unauthorized-cross-taxonomy', revision_id=next_revision['id'],
                    old_id=final_claim['id'], new_id=next_claim['id'], old_claim=final_claim, new_claim=next_claim,
                    old_review=final_review, new_review=next_review)
                cross_content = arsiv.canonical_json({'decisions': [cross]})
                cross_registration = dict(decision=cross, origin=dict(path='data/comparisons/test-cross-taxonomy.json',
                    pointer='/decisions/0', content=cross_content, sha256=hashlib.sha256(cross_content.encode()).hexdigest()))
                cross_basis = dict(next_basis, synthesis_obligations=[chain_obligation, next_obligation],
                                   _correction_registry=next_basis['_correction_registry'] + [cross_registration])
                with self.assertRaisesRegex(ValueError, 'sentez ardıllığı'):
                    arsiv.completion_superseded_syntheses(chain_candidate, next_revision, next_revisions, cross_basis, next_selection)
                # A substantive addition gets a new dated source review, not
                # a mechanically inherited approval or a production change.
                substantive_claim = dict(new_claim, id='test-sr25-synthesis-substantive',
                    text=new_claim['text'] + ' TİP, aynı bağlamda sermaye sahiplerinin bunalımı işçi haklarını azaltmaya gerekçe yapmaya çalıştığını da belirtir.')
                substantive_meaning = json.loads(arsiv.canonical_json(meaning))
                substantive_meaning['explanation'] += ' Test-only new review: TİP p1 explicitly describes this attempted use of crisis.'
                reviewed_at = dt.datetime.now(dt.timezone.utc).isoformat()
                substantive_review = dict(new_review, subject_id=substantive_claim['id'], reviewed_at=reviewed_at,
                                          reason=arsiv.canonical_json(substantive_meaning))
                substantive_relation = dict(relation, id='test-sr25-substantive-lineage', new_id=substantive_claim['id'],
                    mode='substantive', reviewed_at=reviewed_at, new_claim=substantive_claim, new_review=substantive_review,
                    reason='Test-only substantive addition reviewed against the original TİP p1 passage.')
                substantive_doc = dict(purpose='Test-only substantive source review', records=[
                    dict(kind='comparison_synthesis', values=substantive_claim),
                    dict(kind='comparison_semantic_review', values=substantive_review)], decisions=[substantive_relation])
                content = arsiv.canonical_json(substantive_doc)
                path = 'data/comparisons/test-sr25-synthesis-substantive.json'
                (arsiv.DATA / 'comparisons/test-sr25-synthesis-substantive.json').write_text(content, encoding='utf-8')
                digest = hashlib.sha256(content.encode()).hexdigest()
                registered = dict(decision=substantive_relation, origin=dict(path=path, pointer='/decisions/0', content=content, sha256=digest))
                new_obligation = dict(id=substantive_claim['id'], topic_id=substantive_claim['topic_id'], source_authored_claim=substantive_claim,
                    source=dict(path=path, pointer='/records/0/values'), typed_source_judgment=substantive_meaning,
                    original_review=substantive_review, review_source=dict(path=path, pointer='/records/1/values'))
                substantive_basis = dict(before_rebind_basis, synthesis_obligations=before_rebind_basis['synthesis_obligations'] + [new_obligation],
                    source_documents=before_rebind_basis['source_documents'] + [dict(path=path, sha256=digest, role='source_research_or_mapping', original_status=None)],
                    _correction_registry=before_rebind_basis['_correction_registry'] + [registered])
                self.assertTrue(arsiv.verify_successor_completion_basis(old_basis, substantive_basis))
                head, cells = arsiv.completion_basis_records(substantive_basis, risks, 'test-sr25-substantive-basis', reviewed_at, old_head['id'])
                before_rebind_selection['syntheses'] = [s for s in before_rebind_selection['syntheses'] if s['id'] != template['old_id']] + [substantive_claim]
                substantive_revision = dict(revision, basis_id=head['id'], created_at=reviewed_at,
                                            selection=arsiv.canonical_json(before_rebind_selection))
                evidence = [dict(e, synthesis_id=substantive_claim['id']) for e in data['comparison_synthesis_evidence'] if e['synthesis_id'] == template['old_id']]
                substantive_candidate = dict(before_rebind_candidate, comparison_synthesis=data['comparison_synthesis'] + [substantive_claim],
                    comparison_synthesis_evidence=data['comparison_synthesis_evidence'] + evidence,
                    comparison_semantic_review=before_rebind_candidate['comparison_semantic_review'] + [substantive_review],
                    comparison_completion_basis=data['comparison_completion_basis'] + [head],
                    comparison_coverage_disposition=data['comparison_coverage_disposition'] + cells,
                    comparison_completion_revision=[previous, substantive_revision])
                self.assertTrue(arsiv.validate_completion_revisions(substantive_candidate))
                self.assertTrue(arsiv.validate_comparisons(substantive_candidate))
            finally:
                arsiv.DATA = original_data

    def sourced_successor(self, base, source_basis, risk, fixture, fixture_digest, *,
                          source_name='source', basis_id='test-successor-basis',
                          revision_id='test-successor-partial', stage='partial', correction=None):
        """Build a test-only new context from the real, already read TİP source."""
        source_path = 'data/comparisons/test-completion-revision-' + source_name + '.json'
        entries = fixture['records']
        row, field, review = entries[0]['values'], entries[1]['values'], entries[7]['values']
        key = {k: row[k] for k in ('topic_id', 'party_id', 'source_role', 'version_id', 'level', 'organ')}
        key['context_judgment'] = row['id']
        cell_id = 'cell-' + hashlib.sha256(arsiv.canonical_json(key).encode()).hexdigest()[:24]
        assertion = dict(kind='supported_field', field=field['field'], condition_key=field['condition_key'],
                         summary_finding_id=field['summary_finding_id'], quote_finding_id=field['quote_finding_id'],
                         passage_ids=['0304-tip-program-kapitalizm-p1', '0304-tip-program-kapitalizm-q'],
                         original_field=dict(path=source_path, pointer='/records/1/values'),
                         semantic_reviews=[dict(record=review, source=dict(path=source_path, pointer='/records/7/values'))],
                         finding_reviews=[])
        assertion_id = 'basis-' + hashlib.sha256(arsiv.canonical_json(assertion).encode()).hexdigest()[:24]
        cell = dict(id=cell_id, logical_key=key, disposition='evidence',
                    source_judgment=dict(path=source_path, pointer='/records/0/values'),
                    source_judgment_record=row, mapping_refs=[], mapping_records=[], basis_ids=[assertion_id],
                    field_dispositions=[dict(field='principle', disposition='source_supported', basis_id=assertion_id)],
                    inventory_section_indexes=[], fulfilment_locator_only=row['id'])
        universe = [dict(item, cell_ids=item['cell_ids'] + [cell_id])
                    if (item['topic_id'], item['party_id']) == (row['topic_id'], row['party_id']) else item
                    for item in source_basis['universe']]
        documents = source_basis['source_documents'] + [dict(path=source_path, sha256=fixture_digest,
                                                              role='source_research_or_mapping', original_status=None)]
        if correction:
            documents.append(dict(path=correction['origin']['path'], sha256=correction['origin']['sha256'],
                                  role='source_research_or_mapping', original_status=None))
        new_basis = dict(source_basis, cells=source_basis['cells'] + [cell], universe=universe,
                         source_assertions=dict(source_basis['source_assertions'], **{assertion_id: assertion}),
                         source_documents=documents)
        previous = base['comparison_completion_revision'][-1]
        prior_head = next(item for item in base['comparison_completion_basis'] if item['id'] == previous['basis_id'])
        prior_catalog = json.loads(prior_head['source_catalog'])
        reading_registry = prior_catalog['reading_registry']
        correction_registry = prior_catalog['correction_registry'] + ([correction] if correction else [])
        created_at = dt.datetime.now(dt.timezone.utc).isoformat()
        head, cells = arsiv.completion_basis_records(new_basis, risk['expected_risk_universe'],
                                                     basis_id, created_at,
                                                     previous['basis_id'], reading_registry=reading_registry,
                                                     correction_registry=correction_registry)
        selection = json.loads(previous['selection'])
        selection['rows'].append(row)
        selection['fields'].append(field)
        revision = dict(previous, id=revision_id, epoch=previous['epoch'] + 1,
                        parent_revision_id=previous['id'], basis_id=head['id'], stage=stage,
                        created_at=created_at, selection=arsiv.canonical_json(selection), reason='Test fixture: sourced context under review.')
        records = ([entries[i] for i in (2, 3, 4, 5, 6, 8, 9, 0, 1, 7)] +
                   [dict(kind='comparison_completion_basis', values=head)] +
                   [dict(kind='comparison_coverage_disposition', values=c) for c in cells] +
                   [dict(kind='comparison_completion_revision', values=revision)])
        return dict(contract_version=2, taxonomy_version=self.taxonomy, stage=stage, records=records), revision

    def fixture_correction_registration(self, root):
        source = root / 'tests/fixtures/completion_revision_correction.json'
        target = arsiv.DATA / 'comparisons/test-completion-correction.json'
        shutil.copyfile(source, target)
        content = target.read_text(encoding='utf-8')
        decision = json.loads(content)['decisions'][0]
        return dict(decision=decision, origin=dict(path='data/comparisons/test-completion-correction.json',
                    pointer='/decisions/0', content=content, sha256=hashlib.sha256(content.encode()).hexdigest()))

    def test_real_review_and_legacy_snapshot_remain_valid(self):
        self.assertTrue(arsiv.validate_completion(self.reviewed))
        legacy = dict(self.reviewed)
        del legacy['comparison_completion']
        self.assertTrue(arsiv.validate_completion(legacy))

    def test_mutable_input_cannot_claim_a_modified_historical_marker(self):
        data = dict(self.reviewed)
        marker = dict(data['comparison_completion'][0])
        proof = json.loads(marker['evidence'])
        target = '04-03-v3-0304-tip-charter-scope-aday-tanitim-html-row'
        proof['rows'] = [r for r in proof['rows'] if r['id'] != target]
        next(p for p in proof['coverage_review']['parties'] if p['party_id'] == 'tip')['row_count'] -= 1
        marker['evidence'] = json.dumps(proof, ensure_ascii=False)
        data['comparison_completion'] = [marker]
        data['comparison_row'] = [r for r in data['comparison_row'] if r['id'] != target]
        with self.assertRaisesRegex(ValueError, 'tarihsel işaretçisi'):
            arsiv.validate_comparisons(data)

    def test_initial_v2_without_a_legacy_marker_has_no_false_anchor(self):
        data = self.modern()
        revision = dict(data['comparison_completion_revision'][0], legacy_anchor=None)
        data['comparison_completion'] = []
        data['comparison_completion_revision'] = [revision]
        self.assertTrue(arsiv.validate_completion(data))
        data['comparison_completion_revision'] = [dict(revision, legacy_anchor='{"release_id":"fabricated"}')]
        with self.assertRaisesRegex(ValueError, 'Var olmayan önceki'):
            arsiv.validate_completion(data)

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
        with self.assertRaisesRegex(ValueError, 'çözümlenmemiş'):
            arsiv.validate_source_basis_universe(self.reviewed, dict(basis, unresolved=[{'kind': 'unresolved'}]))
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
            dict(self.reviewed, comparison_field=self.reviewed['comparison_field'] + [dict(field, id='unbound-test-field')]),
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
        registry = {'initial': risk['decisions'], 'additional': []}
        self.assertTrue(arsiv.validate_source_risk_review(self.reviewed, basis, universe, decisions, reading_registry=registry))
        stripped = [d for d in decisions if d['kind'] not in ('field_support', 'synthesis_support')]
        with self.assertRaisesRegex(ValueError, 'Kaynak anlamı riski'):
            arsiv.validate_source_risk_review(self.reviewed, basis, universe, stripped, reading_registry=registry)
        principle = next(d for d in decisions if d['id'] == 'SR25:field:tip-kapitalizm-principle')
        tampered = [dict(d, summary_passage_ids=['not-a-real-passage']) if d is principle else d for d in decisions]
        with self.assertRaisesRegex(ValueError, 'kayıtlı özgün'):
            arsiv.validate_source_risk_review(self.reviewed, basis, universe, tampered, reading_registry=registry)
        gap = next(d for d in decisions if d['kind'] == 'physical_page_gap')
        other_version = next(v['id'] for v in self.reviewed['document_version'] if v['id'] != gap['version_id'])
        tampered = [dict(d, version_id=other_version) if d is gap else d for d in decisions]
        with self.assertRaisesRegex(ValueError, 'kayıtlı özgün'):
            arsiv.validate_source_risk_review(self.reviewed, basis, universe, tampered, reading_registry=registry)

    def test_source_basis_round_trips_in_closed_storage_format(self):
        root = Path(__file__).resolve().parents[1] / 'data/comparisons'
        basis = json.loads((root / '03-completion-basis-v2-source.json').read_text())
        risk = json.loads((root / '03-completion-risk-v2-source.json').read_text())
        head, cells = arsiv.completion_basis_records(basis, risk['expected_risk_universe'],
                                                     'test-basis', '2026-11-15T16:52:28Z',
                                                     reading_registry={'initial': risk['decisions'], 'additional': []})
        restored, restored_risk = arsiv.decode_completion_basis(head, cells)
        self.assertEqual({k: v for k, v in restored.items() if not k.startswith('_')}, basis)
        self.assertEqual(restored_risk, risk['expected_risk_universe'])
        self.assertTrue(arsiv.validate_completion_basis_successor(basis, restored))
        altered_cells = list(restored['cells'])
        altered_cells[0] = dict(altered_cells[0], disposition='document_missing')
        with self.assertRaisesRegex(ValueError, 'Önceki kaynak yükümlülüğü'):
            arsiv.validate_completion_basis_successor(basis, dict(restored, cells=altered_cells))
        self.assertTrue(arsiv.validate_source_basis_universe(self.reviewed, restored))
        self.assertTrue(arsiv.validate_source_risk_review(self.reviewed, restored, restored_risk, risk['decisions']))
        cell = next(c for c in restored['cells'] if c['disposition'] == 'evidence')
        bid = next(i for i in cell['basis_ids'] if restored['source_assertions'][i]['kind'] == 'supported_field')
        assertion = dict(restored['source_assertions'][bid], semantic_reviews=[], finding_reviews=[])
        assertions = dict(restored['source_assertions'], **{bid: assertion})
        with self.assertRaisesRegex(ValueError, 'anlam incelemesi eksik'):
            arsiv.validate_source_basis_cells(self.reviewed, self.taxonomy, [cell], assertions)

    def test_initial_basis_reconciles_authored_origins_before_adoption(self):
        root = Path(__file__).resolve().parents[1] / 'data/comparisons'
        basis = json.loads((root / '03-completion-basis-v2-source.json').read_text())
        risk = json.loads((root / '03-completion-risk-v2-source.json').read_text())
        registry = {'initial': risk['decisions'], 'additional': []}
        self.assertTrue(arsiv.verify_initial_completion_basis(basis, risk['expected_risk_universe'], reading_registry=registry))
        with self.assertRaisesRegex(ValueError, 'bağımsız hazırlanmış bütüne'):
            arsiv.verify_initial_completion_basis(dict(basis, cells=basis['cells'][1:]), risk['expected_risk_universe'], reading_registry=registry)
        with self.assertRaisesRegex(ValueError, 'bağımsız hazırlanmış bütüne'):
            arsiv.verify_initial_completion_basis(basis, risk['expected_risk_universe'][1:], reading_registry=registry)
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
        self.assertEqual({k: v for k, v in source.items() if not k.startswith('_')}, basis)
        self.assertEqual(universe, risk['expected_risk_universe'])
        self.assertEqual(json.loads(revision['review'])['decisions'], risk['decisions'])
        self.assertEqual(json.loads(revision['legacy_anchor'])['release_id'], self.reviewed['release_id'])

    def test_real_source_adoption_import_export_and_rollback(self):
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
                shutil.copytree(original / 'objects', arsiv.DATA / 'objects')
                shutil.copytree(original / 'views', arsiv.DATA / 'views')
                work = temp / 'work'
                work.mkdir()
                shutil.copyfile(original / 'releases' / self.reviewed['release_id'] / 'records.sqlite3',
                                work / 'records.sqlite3')
                (arsiv.DATA / '.write.lock').write_text(json.dumps({'token': 'isolated-test-token'}))
                before = arsiv.sha(work / 'records.sqlite3')
                (work / 'workspace.json').write_text(json.dumps({'token': 'isolated-test-token', 'base': 'wrong-base'}))
                with self.assertRaisesRegex(ValueError, 'gerçek taban'):
                    arsiv.load_comparison(work, payload)
                self.assertEqual(arsiv.sha(work / 'records.sqlite3'), before)
                (work / 'workspace.json').write_text(json.dumps({'token': 'isolated-test-token', 'base': self.reviewed['release_id']}))
                arsiv.load_comparison(work, payload)
                exported = arsiv.export_db(work / 'records.sqlite3', 'isolated')
                self.assertEqual(exported['comparison_completion'], self.reviewed['comparison_completion'])
                self.assertEqual(len(exported['comparison_coverage_disposition']), len(basis['cells']))
                self.assertEqual(exported['comparison_completion_revision'][0]['epoch'], 1)
            finally:
                arsiv.DATA = original

    def test_same_taxonomy_sourced_addition_partial_then_complete(self):
        original = arsiv.DATA
        root = Path(__file__).resolve().parents[1]
        basis = json.loads((root / 'data/comparisons/03-completion-basis-v2-source.json').read_text())
        risk = json.loads((root / 'data/comparisons/03-completion-risk-v2-source.json').read_text())
        fixture_path = root / 'tests/fixtures/completion_revision_source.json'
        fixture = json.loads(fixture_path.read_text())
        base = self.modern()
        with tempfile.TemporaryDirectory() as temp:
            arsiv.DATA = Path(temp) / 'data'
            try:
                arsiv.DATA.mkdir()
                for source in basis['source_documents']:
                    relative = Path(source['path']).relative_to('data')
                    target = arsiv.DATA / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(original / relative, target)
                target = arsiv.DATA / 'comparisons/test-completion-revision-source.json'
                shutil.copyfile(fixture_path, target)
                payload, partial_revision = self.sourced_successor(base, basis, risk, fixture, arsiv.sha(target))
                candidate = dict(base, comparison_contract=[dict(base['comparison_contract'][0], stage='partial')])
                for table in {entry['kind'] for entry in payload['records']}:
                    candidate[table] = list(base.get(table, [])) + [entry['values'] for entry in payload['records'] if entry['kind'] == table]
                head = next(entry['values'] for entry in payload['records'] if entry['kind'] == 'comparison_completion_basis')
                cells = [entry['values'] for entry in payload['records'] if entry['kind'] == 'comparison_coverage_disposition']
                successor_basis, _ = arsiv.decode_completion_basis(head, cells)
                self.assertTrue(arsiv.verify_successor_completion_basis(basis, successor_basis))
                self.assertTrue(arsiv.validate_comparison_descent(base, candidate))
                complete_revision = dict(partial_revision, id='test-successor-complete', epoch=partial_revision['epoch'] + 1,
                                         parent_revision_id=partial_revision['id'], stage='complete',
                                         reason='Test fixture: source context and review complete.')
                complete = dict(candidate, comparison_contract=[dict(candidate['comparison_contract'][0], stage='complete')],
                                comparison_completion_revision=candidate['comparison_completion_revision'] + [complete_revision])
                self.assertTrue(arsiv.validate_completion(complete))
                self.assertTrue(arsiv.validate_comparison_descent(candidate, complete))
                replacement_path = root / 'tests/fixtures/completion_revision_supersession.json'
                replacement = json.loads(replacement_path.read_text())
                replacement_target = arsiv.DATA / 'comparisons/test-completion-revision-supersession.json'
                shutil.copyfile(replacement_path, replacement_target)
                correction = self.fixture_correction_registration(root)
                replacement_payload, replacement_revision = self.sourced_successor(
                    candidate, successor_basis, risk, replacement, arsiv.sha(replacement_target),
                    source_name='supersession', basis_id='test-replacement-basis',
                    revision_id='test-replacement-complete', stage='complete', correction=correction)
                replacement_selection = json.loads(replacement_revision['selection'])
                replacement_selection['rows'] = [r for r in replacement_selection['rows'] if r['id'] != 'test-tip-kapitalizm-context-row']
                replacement_selection['fields'] = [f for f in replacement_selection['fields'] if f['row_id'] != 'test-tip-kapitalizm-context-row']
                replacement_revision['selection'] = arsiv.canonical_json(replacement_selection)
                new_cells = [entry['values'] for entry in replacement_payload['records'] if entry['kind'] == 'comparison_coverage_disposition']
                new_head = next(entry['values'] for entry in replacement_payload['records'] if entry['kind'] == 'comparison_completion_basis')
                replacement_basis, _ = arsiv.decode_completion_basis(new_head, new_cells)
                old_cell = next(c for c in replacement_basis['cells'] if c['logical_key']['context_judgment'] == 'test-tip-kapitalizm-context-row')
                new_cell = next(c for c in replacement_basis['cells'] if c['logical_key']['context_judgment'] == 'test-tip-kapitalizm-replacement-row')
                link = dict(revision_id=replacement_revision['id'], old_cell_id=old_cell['id'], new_cell_id=new_cell['id'],
                            old_row_id='test-tip-kapitalizm-context-row', new_row_id='test-tip-kapitalizm-replacement-row',
                            source_basis_refs=arsiv.canonical_json(dict(correction_id=correction['decision']['id'], basis_ids=new_cell['basis_ids'])),
                            reason='Test-only replacement preserving the SR25 source boundary.')
                replacement_payload['records'].append(dict(kind='comparison_completion_supersession', values=link))
                result = dict(candidate, comparison_contract=[dict(candidate['comparison_contract'][0], stage='complete')])
                for table in {entry['kind'] for entry in replacement_payload['records']}:
                    result[table] = list(candidate.get(table, [])) + [entry['values'] for entry in replacement_payload['records'] if entry['kind'] == table]
                self.assertTrue(arsiv.verify_successor_completion_basis(successor_basis, replacement_basis))
                self.assertTrue(arsiv.validate_completion(result))
                visible = arsiv.comparison_render_data(result)
                self.assertNotIn(link['old_row_id'], {r['id'] for r in visible['comparison_row']})
                self.assertIn(link['new_row_id'], {r['id'] for r in visible['comparison_row']})
                self.assertIn(link['old_row_id'], {r['id'] for r in result['comparison_row']})
            finally:
                arsiv.DATA = original

    def test_same_taxonomy_sourced_revision_round_trip(self):
        """Publish and audit the real-source fixture in one isolated DATA tree."""
        original = arsiv.DATA
        root = Path(__file__).resolve().parents[1]
        basis = json.loads((root / 'data/comparisons/03-completion-basis-v2-source.json').read_text())
        risk = json.loads((root / 'data/comparisons/03-completion-risk-v2-source.json').read_text())
        adoption = json.loads((root / 'data/comparisons/03-completion-review-v2.json').read_text())
        fixture_path = root / 'tests/fixtures/completion_revision_source.json'
        fixture = json.loads(fixture_path.read_text())
        base = self.modern()
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            arsiv.DATA = temp / 'data'
            try:
                arsiv.DATA.mkdir()
                for directory in ('releases', 'objects', 'views'):
                    shutil.copytree(original / directory, arsiv.DATA / directory)
                # This isolated workflow starts from the immutable v1 fixture,
                # regardless of which release is live outside the test tree.
                (arsiv.DATA / 'current.json').write_text(json.dumps({'release_id': self.reviewed['release_id']}), encoding='utf-8')
                for source in basis['source_documents']:
                    relative = Path(source['path']).relative_to('data')
                    target = arsiv.DATA / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(original / relative, target)
                target = arsiv.DATA / 'comparisons/test-completion-revision-source.json'
                shutil.copyfile(fixture_path, target)
                partial, partial_revision = self.sourced_successor(base, basis, risk, fixture, arsiv.sha(target))
                partial['records'] = adoption['records'] + partial['records']
                original_release = self.reviewed['release_id']
                folder = arsiv.DATA / 'releases' / original_release
                preserved = {p.name: arsiv.sha(p) for p in folder.iterdir() if p.is_file()}

                def workspace(base_release, name):
                    work = temp / name
                    work.mkdir()
                    shutil.copyfile(arsiv.DATA / 'releases' / base_release / 'records.sqlite3', work / 'records.sqlite3')
                    token = 'isolated-' + name
                    (arsiv.DATA / '.write.lock').write_text(json.dumps({'token': token}))
                    (work / 'workspace.json').write_text(json.dumps({'token': token, 'base': base_release}))
                    return work

                work = workspace(original_release, 'partial-work')
                print('isolated: adopting v2 and rejecting forged reviews/corrections', flush=True)
                arsiv.load_comparison(work, adoption)
                before_rejected = arsiv.sha(work / 'records.sqlite3')
                initial = base['comparison_completion_revision'][0]
                forged_review = json.loads(initial['review'])
                for decision in forged_review['decisions']:
                    if decision['kind'] == 'field_support':
                        decision.update(original_field_review={'forged': 'yes'}, judgment='x', source_reading='x',
                                        recorded_at='x', decision='unsupported')
                forged_revision = dict(initial, id='test-forged-review', epoch=2, parent_revision_id=initial['id'],
                                       review=arsiv.canonical_json(forged_review), reason='test forged provenance')
                forged_payload = dict(contract_version=2, taxonomy_version=self.taxonomy, stage='complete',
                                      records=[dict(kind='comparison_completion_revision', values=forged_revision)])
                with self.assertRaisesRegex(ValueError, 'kayıtlı özgün'):
                    arsiv.load_comparison(work, forged_payload)
                self.assertEqual(arsiv.sha(work / 'records.sqlite3'), before_rejected)
                old_id = '04-03-v3-0304-tip-charter-scope-aday-tanitim-html-row'
                new_id = '04-03-v3-0304-tip-charter-context-aday-tanitim-html-row'
                old = next(c for c in basis['cells'] if c['fulfilment_locator_only'] == old_id)
                new = next(c for c in basis['cells'] if c['fulfilment_locator_only'] == new_id)
                selected = json.loads(initial['selection'])
                selected['rows'] = [r for r in selected['rows'] if r['id'] != old_id]
                forged_revision = dict(initial, id='test-unrelated-correction', epoch=2, parent_revision_id=initial['id'],
                                       selection=arsiv.canonical_json(selected), reason='test unrelated contexts')
                link = dict(revision_id=forged_revision['id'], old_cell_id=old['id'], new_cell_id=new['id'],
                            old_row_id=old_id, new_row_id=new_id,
                            source_basis_refs=arsiv.canonical_json(['basis-8a236988dbbb141d12717df4']),
                            reason='test unrelated contexts')
                forged_payload = dict(contract_version=2, taxonomy_version=self.taxonomy, stage='complete', records=[
                    dict(kind='comparison_completion_revision', values=forged_revision),
                    dict(kind='comparison_completion_supersession', values=link)])
                with self.assertRaisesRegex(ValueError, 'bağımsız düzeltme'):
                    arsiv.load_comparison(work, forged_payload)
                self.assertEqual(arsiv.sha(work / 'records.sqlite3'), before_rejected)
                print('isolated: importing source addition and partial revision', flush=True)
                arsiv.load_comparison(work, partial)
                partial_data = arsiv.export_db(work / 'records.sqlite3', 'partial-work')
                self.assertEqual(partial_data['comparison_contract'][0]['stage'], 'partial')
                self.assertEqual(partial_data['comparison_completion'], self.reviewed['comparison_completion'])
                self.assertIn('test-tip-kapitalizm-context-row', {r['id'] for r in partial_data['comparison_row']})
                arsiv.load_comparison(work, partial)
                self.assertEqual(arsiv.export_db(work / 'records.sqlite3', 'partial-work'), partial_data)
                print('isolated: publishing and auditing partial revision', flush=True)
                partial_release = arsiv.publish_release(work, refresh=True)
                self.assertEqual(arsiv.validate_phase_three(partial_release, 'partial'), True)
                with self.assertRaisesRegex(ValueError, 'aşaması uyuşmuyor'):
                    arsiv.validate_phase_three(partial_release, 'complete')
                head = next(b for b in partial_data['comparison_completion_basis'] if b['id'] == partial_revision['basis_id'])
                cells = [c for c in partial_data['comparison_coverage_disposition'] if c['basis_id'] == head['id']]
                partial_basis, _ = arsiv.decode_completion_basis(head, cells)
                replacement_path = root / 'tests/fixtures/completion_revision_supersession.json'
                replacement = json.loads(replacement_path.read_text())
                replacement_target = arsiv.DATA / 'comparisons/test-completion-revision-supersession.json'
                shutil.copyfile(replacement_path, replacement_target)
                correction = self.fixture_correction_registration(root)
                complete_payload, complete_revision = self.sourced_successor(
                    partial_data, partial_basis, risk, replacement, arsiv.sha(replacement_target),
                    source_name='supersession', basis_id='test-replacement-basis',
                    revision_id='test-replacement-complete', stage='complete', correction=correction)
                selection = json.loads(complete_revision['selection'])
                selection['rows'] = [r for r in selection['rows'] if r['id'] != 'test-tip-kapitalizm-context-row']
                selection['fields'] = [f for f in selection['fields'] if f['row_id'] != 'test-tip-kapitalizm-context-row']
                complete_revision['selection'] = arsiv.canonical_json(selection)
                new_head = next(entry['values'] for entry in complete_payload['records'] if entry['kind'] == 'comparison_completion_basis')
                new_cells = [entry['values'] for entry in complete_payload['records'] if entry['kind'] == 'comparison_coverage_disposition']
                replacement_basis, _ = arsiv.decode_completion_basis(new_head, new_cells)
                old_cell = next(c for c in replacement_basis['cells'] if c['logical_key']['context_judgment'] == 'test-tip-kapitalizm-context-row')
                new_cell = next(c for c in replacement_basis['cells'] if c['logical_key']['context_judgment'] == 'test-tip-kapitalizm-replacement-row')
                link = dict(revision_id=complete_revision['id'], old_cell_id=old_cell['id'], new_cell_id=new_cell['id'],
                            old_row_id='test-tip-kapitalizm-context-row', new_row_id='test-tip-kapitalizm-replacement-row',
                            source_basis_refs=arsiv.canonical_json(dict(correction_id=correction['decision']['id'], basis_ids=new_cell['basis_ids'])),
                            reason='Test-only replacement preserving the SR25 source boundary.')
                complete_payload['records'].append(dict(kind='comparison_completion_supersession', values=link))
                work = workspace(partial_release, 'complete-work')
                print('isolated: importing source-backed replacement and publishing complete successor', flush=True)
                arsiv.load_comparison(work, complete_payload)
                complete_release = arsiv.publish_release(work, refresh=True)
                self.assertEqual(arsiv.audit_release(complete_release), complete_release)
                self.assertTrue(arsiv.validate_phase_three(complete_release, 'complete'))
                result = json.loads((arsiv.DATA / 'releases' / complete_release / 'records.json').read_text())
                self.assertEqual(result['comparison_contract'][0]['taxonomy_version'], self.taxonomy)
                self.assertEqual(result['comparison_contract'][0]['stage'], 'complete')
                self.assertEqual(result['comparison_completion'], self.reviewed['comparison_completion'])
                self.assertIn('test-tip-kapitalizm-context-field', {f['id'] for f in result['comparison_field']})
                self.assertIn('test-tip-kapitalizm-replacement-field', {f['id'] for f in result['comparison_field']})
                visible = arsiv.comparison_render_data(result)
                self.assertNotIn(link['old_row_id'], {r['id'] for r in visible['comparison_row']})
                self.assertIn(link['new_row_id'], {r['id'] for r in visible['comparison_row']})
                self.assertTrue(arsiv.validate_comparison_descent(partial_data, result))
                self.assertEqual(preserved, {p.name: arsiv.sha(p) for p in folder.iterdir() if p.is_file()})
                # STRUCTURAL FUTURE: the prior missing/search records are synthetic;
                # the bounded negative is the already existing real TİP source scope.
                # This does not claim a discovery for Yeni Yol or for TİP.
                gap_data, _, _, _, gap_link, decision, registration, new_cell, old_cell, assertion = self.structural_gap_fixture()
                gap_row = old_cell['source_judgment_record']
                missing = next(m for m in gap_data['missing'] if m['id'] == 'test-structural-program-gap')
                attempt = next(a for a in gap_data['attempt'] if a['id'] == 'test-structural-search')
                gap_source = arsiv.DATA / 'comparisons/test-structural-gap.json'
                gap_source.write_text(arsiv.canonical_json({'records': [
                    dict(kind='attempt', values=attempt), dict(kind='missing', values=missing),
                    dict(kind='comparison_row', values=gap_row)]}), encoding='utf-8')
                correction_file = arsiv.DATA / 'comparisons/test-structural-correction.json'
                correction_file.write_text(registration['origin']['content'], encoding='utf-8')
                current = result['comparison_completion_revision'][-1]
                current_head = next(b for b in result['comparison_completion_basis'] if b['id'] == current['basis_id'])
                source_basis, risk_universe = arsiv.decode_completion_basis(current_head, result['comparison_coverage_disposition'])
                old_cell = dict(old_cell, source_judgment=dict(path='data/comparisons/test-structural-gap.json', pointer='/records/2/values'),
                                mapping_refs=[], inventory_section_indexes=[], fulfilment_locator_only=gap_row['id'])
                gap_id = old_cell['basis_ids'][0]
                source_basis['cells'].append(old_cell)
                source_basis['source_assertions'][gap_id] = assertion
                for item in source_basis['universe']:
                    if (item['topic_id'], item['party_id']) == (gap_row['topic_id'], gap_row['party_id']):
                        item['cell_ids'].append(old_cell['id'])
                source_basis['source_documents'].append(dict(path='data/comparisons/test-structural-gap.json',
                    sha256=arsiv.sha(gap_source), role='source_research_or_mapping', original_status=None))
                created = dt.datetime.now(dt.timezone.utc).isoformat()
                gap_head, gap_cells = arsiv.completion_basis_records(source_basis, risk_universe, 'test-structural-gap-basis', created,
                    current['basis_id'], reading_registry=source_basis['_reading_registry'], correction_registry=source_basis['_correction_registry'])
                selected = json.loads(current['selection'])
                selected['rows'].append(gap_row)
                gap_revision = dict(current, id='test-structural-gap-partial', epoch=current['epoch'] + 1,
                    parent_revision_id=current['id'], basis_id=gap_head['id'], stage='partial', created_at=created,
                    selection=arsiv.canonical_json(selected), reason='STRUCTURAL FUTURE: synthetic earlier missing document.')
                gap_payload = dict(contract_version=2, taxonomy_version=self.taxonomy, stage='partial', records=[
                    dict(kind='attempt', values=attempt), dict(kind='missing', values=missing),
                    dict(kind='comparison_row', values=gap_row), dict(kind='comparison_completion_basis', values=gap_head),
                    *[dict(kind='comparison_coverage_disposition', values=c) for c in gap_cells],
                    dict(kind='comparison_completion_revision', values=gap_revision)])
                gap_work = workspace(complete_release, 'structural-gap-work')
                arsiv.load_comparison(gap_work, gap_payload)
                gap_partial = arsiv.export_db(gap_work / 'records.sqlite3', 'structural-gap-work')
                self.assertEqual(gap_partial['comparison_contract'][0]['stage'], 'partial')
                source_basis['source_documents'].append(dict(path=registration['origin']['path'],
                    sha256=registration['origin']['sha256'], role='source_research_or_mapping', original_status=None))
                source_basis['_correction_registry'].append(registration)
                next_head, next_cells = arsiv.completion_basis_records(source_basis, risk_universe, 'test-structural-corrected-basis', created,
                    gap_head['id'], reading_registry=source_basis['_reading_registry'], correction_registry=source_basis['_correction_registry'])
                selected['rows'] = [r for r in selected['rows'] if r['id'] != gap_row['id']]
                corrected = dict(gap_revision, id='test-structural-gap-complete', epoch=gap_revision['epoch'] + 1,
                    parent_revision_id=gap_revision['id'], basis_id=next_head['id'], stage='complete',
                    selection=arsiv.canonical_json(selected), reason='STRUCTURAL FUTURE: reassessment of bounded real source scope.')
                gap_link = dict(gap_link, revision_id=corrected['id'])
                corrected_payload = dict(contract_version=2, taxonomy_version=self.taxonomy, stage='complete', records=[
                    dict(kind='comparison_completion_basis', values=next_head),
                    *[dict(kind='comparison_coverage_disposition', values=c) for c in next_cells],
                    dict(kind='comparison_completion_revision', values=corrected),
                    dict(kind='comparison_completion_supersession', values=gap_link)])
                arsiv.load_comparison(gap_work, corrected_payload)
                gap_complete = arsiv.export_db(gap_work / 'records.sqlite3', 'structural-gap-work')
                self.assertTrue(arsiv.validate_comparisons(gap_complete))
                self.assertTrue(arsiv.validate_comparison_descent(gap_partial, gap_complete))
                self.assertIn(gap_row['id'], {r['id'] for r in gap_complete['comparison_row']})
                self.assertNotIn(gap_row['id'], {r['id'] for r in arsiv.comparison_render_data(gap_complete)['comparison_row']})
                gap_release = arsiv.publish_release(gap_work, refresh=True)
                self.assertEqual(arsiv.audit_release(gap_release), gap_release)
                self.assertTrue(arsiv.validate_phase_three(gap_release, 'complete'))
                manifest_path = arsiv.DATA / 'releases' / complete_release / 'manifest.json'
                original_manifest = manifest_path.read_bytes()
                try:
                    manifest = json.loads(original_manifest)
                    manifest['comparison_completion_review_sha256'] = '0' * 64
                    manifest_path.write_text(json.dumps(manifest))
                    with self.assertRaisesRegex(ValueError, 'revizyon manifesti'):
                        arsiv.audit_release(complete_release)
                finally:
                    manifest_path.write_bytes(original_manifest)
                print('isolated: audited complete successor', complete_release, flush=True)
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
                                                     'test-basis', '2026-11-15T16:52:28Z',
                                                     reading_registry={'initial': risk['decisions'], 'additional': []})
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
        self.assertTrue(arsiv.validate_completion(data))
        target = '04-03-v3-0304-tip-charter-scope-aday-tanitim-html-row'
        # Model a first v2 closure without an adopted v1 marker. Its candidate
        # selection is edited in step with the omitted row; the independent
        # source basis still requires the TİP scope and organ.
        data['comparison_completion'] = []
        data['comparison_row'] = [r for r in data['comparison_row'] if r['id'] != target]
        revision = dict(data['comparison_completion_revision'][0])
        selection = json.loads(revision['selection'])
        selection['rows'] = [r for r in selection['rows'] if r['id'] != target]
        revision['selection'] = arsiv.canonical_json(selection)
        revision['legacy_anchor'] = None
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

