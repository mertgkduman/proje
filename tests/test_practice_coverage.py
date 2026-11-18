"""Coverage must be derived from the selected archive, not a package claim."""
import copy
import json
import unittest
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import subprocess

import arsiv
import uygulamalar


class PracticeCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release = arsiv.current()
        cls.data = json.loads((arsiv.DATA / 'releases' / cls.release / 'records.json').read_text())

    def test_inventory_is_the_selected_universe(self):
        self.assertTrue(hasattr(uygulamalar, 'build_practice_inventory'), 'canonical inventory builder is required')
        self.assertTrue(hasattr(uygulamalar, 'validate_practice_coverage'), 'canonical coverage validator is required')
        from uygulamalar import build_practice_inventory, validate_practice_coverage
        inventory = build_practice_inventory(self.data)
        self.assertEqual(json.loads((arsiv.DATA / 'practices' / '04-inventory.json').read_text(encoding='utf-8')), inventory)
        selection = json.loads(max(self.data['comparison_completion_revision'], key=lambda x: x['epoch'])['selection'])
        topics = {x['topic_id'] for x in selection['topics']}
        parties = {x['party_id'] for x in self.data['scope_party']}
        expected = {(p, t, k) for p in parties for t in topics for k in ('statement', 'event')}
        actual = {(x['party_id'], x['topic_id'], x['research_kind']) for x in inventory['cells']}
        self.assertEqual(actual, expected)
        self.assertEqual(len(inventory['cells']), len(expected))
        self.assertTrue(all(x['state'] == 'not_researched' for x in inventory['cells']))
        db = arsiv.connect_readonly(arsiv.DATA / 'releases' / self.release / 'records.sqlite3')
        try:
            for party in parties:
                expected_start = arsiv.foundation_for_party(db, party)
                self.assertEqual({x['period_start'] for x in inventory['cells'] if x['party_id'] == party}, {expected_start})
        finally:
            db.close()
        self.assertTrue(validate_practice_coverage(self.data, inventory))
        narrowed = copy.deepcopy(inventory)
        narrowed['cells'].pop()
        with self.assertRaises(ValueError):
            validate_practice_coverage(self.data, narrowed)

    def test_real_archived_chain_is_bounded(self):
        for command, options in (('practice-inventory', ('--release', '--out')), ('practice-coverage', ('--inventory', '--input', '--party', '--complete'))):
            result = subprocess.run([sys.executable, str(arsiv.ROOT / 'src' / 'arsiv.py'), command, '--help'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for option in options:
                self.assertIn(option, result.stdout)
        closure = next(x for x in self.data['closure'] if x['id'] == '0105-organ-closure')
        attempt = next(x for x in self.data['attempt'] if x['id'] == '0105-cesme-access')
        self.assertEqual(attempt['source_version_id'], '0105-cesme-v1')
        self.assertIn('doğrulanamadı', closure['residual_leads'])
        self.assertTrue(any(x['closure_id'] == closure['id'] for x in self.data['reopen']))
        self.assertTrue(hasattr(uygulamalar, 'validate_practice_closure'),
                        'party-specific closure must be validated against the full scope')

    def test_preview_inventory_remains_bound_to_accepted_history(self):
        inventory = uygulamalar.build_practice_inventory(self.data)
        accepted = copy.deepcopy(self.data)
        accepted['practice_coverage_contract'] = [dict(version=2, inventory_json=json.dumps(inventory))]
        accepted['practice_inventory_revision'] = []
        immediate_base = 'a' * 32
        snapshot = dict(accepted, release_id='b' * 32)
        self.assertTrue(uygulamalar.validate_preview_inventory(snapshot, accepted, immediate_base, inventory, []))
        # A package cannot assert an arbitrary older inventory or narrow it.
        altered = copy.deepcopy(inventory)
        altered['cells'].pop()
        with self.assertRaises(ValueError):
            uygulamalar.validate_preview_inventory(snapshot, accepted, immediate_base, altered, [])
        forged = copy.deepcopy(inventory)
        forged['base_release'] = 'c' * 32
        with self.assertRaises(ValueError):
            uygulamalar.validate_preview_inventory(snapshot, accepted, immediate_base, forged, [])

    def test_extension_backscans_every_party(self):
        from uygulamalar import build_practice_inventory, validate_practice_coverage
        extension = dict(id='technical-test-extension', parent_topic_id='organ-secim-yontemi',
                         definition='Temporary test topic', basis_passage_ids=['0105-cesme-p'], reason='Technical fixture')
        inventory = build_practice_inventory(self.data, [extension])
        cells = [x for x in inventory['cells'] if x['topic_id'] == extension['id']]
        self.assertEqual({(x['party_id'], x['research_kind']) for x in cells},
                         {(p['party_id'], kind) for p in self.data['scope_party'] for kind in ('statement', 'event')})
        self.assertTrue(validate_practice_coverage(self.data, inventory, [extension]))
        bad = copy.deepcopy(extension)
        bad['basis_passage_ids'] = ['nonexistent']
        with self.assertRaises(ValueError):
            build_practice_inventory(self.data, [bad])

    def test_temporary_closure_and_reopen_require_real_scoped_attempt(self):
        from uygulamalar import build_practice_inventory, validate_practice_closure, practice_coverage_states
        data = copy.deepcopy(self.data)
        inventory = build_practice_inventory(data)
        cell = next(c for c in inventory['cells'] if (c['party_id'], c['topic_id'], c['research_kind']) == ('yeni-parti', 'organ-secim-yontemi', 'event'))
        scope = {k: cell[k] for k in ('party_id', 'topic_id', 'taxonomy_version', 'period_start', 'cutoff_at', 'research_kind')}
        scope.update(id=cell['cell_id'], boundary_reason='Temporary technical fixture')
        original = next(a for a in data['attempt'] if a['id'] == '0105-cesme-access')
        old_lead = next(x for x in data['lead'] if x['id'] == original['lead_id'])
        data['lead'].append(dict(old_lead, id='temporary-old-lead', topic_id=scope['topic_id']))
        fixture = dict(original, id='temporary-scope-attempt', lead_id='temporary-old-lead', topic_id=scope['topic_id'])
        data['attempt'].append(fixture)
        search = dict(fixture, id='temporary-scope-search', lead_id=None, type='search', query='Temporary technical query', result='results', source_version_id=None)
        data['attempt'].append(search)
        attempt = {k: fixture[k] for k in ('id', 'attempted_at', 'query', 'result', 'reason', 'source_version_id')}
        attempt.update(scope_id=scope['id'], url=fixture['query'])
        search_attempt = {k: search[k] for k in ('id', 'attempted_at', 'query', 'result', 'reason', 'source_version_id')}
        search_attempt.update(scope_id=scope['id'], url=None)
        lead = dict(id='temporary-old-lead', scope_id=scope['id'], url=fixture['query'], relevance_reason='Technical fixture', state='examined', attempt_ids=json.dumps([attempt['id'], search_attempt['id']]))
        closure = dict(id='technical-closure', scope_id=scope['id'], closed_at='2026-11-10T16:10:00+00:00', reason='Temporary fixture only', residual_lead_ids='[]')
        source = dict(scope_id=scope['id'], version_id='0105-cesme-v1', inspected_sections='Temporary fixture', inspected_at='2026-11-10T16:05:00+00:00')
        data.update(practice_scope_v2=[scope], practice_attempt_v2=[attempt, search_attempt], practice_lead=[lead], practice_closure=[closure], practice_reopen=[], practice_scope_source=[source], practice_candidate=[])
        self.assertTrue(validate_practice_closure(data, inventory))
        old_attempt = next(a for a in self.data['attempt'] if a['id'] == '0105-cesme-access')
        narrowed = copy.deepcopy(data)
        narrowed_attempt = {k: old_attempt[k] for k in ('id', 'attempted_at', 'query', 'result', 'reason', 'source_version_id')}
        narrowed_attempt.update(scope_id=scope['id'], url=old_attempt['query'])
        narrowed['practice_attempt_v2'] = [narrowed_attempt]
        with self.assertRaises(ValueError):
            validate_practice_closure(narrowed, inventory)
        pending = copy.deepcopy(data)
        pending['practice_lead'][0]['state'] = 'pending'
        with self.assertRaises(ValueError):
            validate_practice_closure(pending, inventory)
        wrong_party = copy.deepcopy(data)
        wrong_party['attempt'][-2]['party_id'] = 'tip'
        with self.assertRaises(ValueError):
            validate_practice_closure(wrong_party, inventory)
        fake = copy.deepcopy(data)
        fake['attempt'][-2]['result'] = fake['practice_attempt_v2'][0]['result'] = 'no_result'
        fake['attempt'][-2]['type'] = 'search'
        with self.assertRaises(ValueError):
            validate_practice_closure(fake, inventory)
        genuine_missing = copy.deepcopy(data)
        genuine_missing['attempt'][-1]['result'] = 'no_result'
        genuine_missing['practice_attempt_v2'] = [dict(search_attempt, result='no_result')]
        genuine_missing['practice_lead'] = []
        genuine_missing['lead'] = [x for x in genuine_missing['lead'] if x['id'] != 'temporary-old-lead']
        genuine_missing['practice_scope_source'] = []
        genuine_missing['missing'].append(dict(id='technical-missing', party_id=scope['party_id'], topic_id=scope['topic_id'], heading=search['heading'], status='Bulunamadı', attempt_id=search['id'], reason='Temporary recorded search'))
        self.assertTrue(validate_practice_closure(genuine_missing, inventory))
        pending['practice_reopen'] = [dict(id='technical-reopen', closure_id=closure['id'], lead_id=lead['id'], opened_at='2026-11-10T17:00:00+00:00', reason='New technical lead')]
        self.assertTrue(validate_practice_closure(pending, inventory))
        self.assertEqual(next(x['state'] for x in practice_coverage_states(pending, inventory) if x['cell_id'] == scope['id']), 'open')
        self.assertEqual(pending['practice_closure'][0], closure)
        revision = copy.deepcopy(data)
        revision['practice_lead_revision'] = [dict(id='revision', lead_id=lead['id'], recorded_at='2026-11-10T17:00:00+00:00', state='pending', attempt_ids=lead['attempt_ids'], reason='New technical lead')]
        with self.assertRaises(ValueError):
            validate_practice_closure(revision, inventory)
        revision['practice_reopen'] = pending['practice_reopen']
        self.assertTrue(validate_practice_closure(revision, inventory))
        self.assertEqual(revision['practice_lead'][0], lead)
        new_source = copy.deepcopy(data)
        new_source['practice_scope_source'].append(dict(source, inspected_at='2026-11-10T17:00:00+00:00', inspected_sections='Newly inspected section'))
        with self.assertRaises(ValueError):
            validate_practice_closure(new_source, inventory)
        new_source['practice_reopen'] = pending['practice_reopen']
        self.assertTrue(validate_practice_closure(new_source, inventory))
        self.assertEqual(new_source['practice_closure'][0], closure)
        new_version = copy.deepcopy(data)
        version = next(v for v in new_version['document_version'] if v['id'] == '0105-cesme-v1')
        new_version['document_version'].append(dict(version, id='temporary-new-version'))
        passage = next(p for p in new_version['passage'] if p['id'] == '0105-cesme-p')
        new_version['passage'].append(dict(passage, id='temporary-new-passage', version_id='temporary-new-version'))
        new_version['practice_source_party'].append(dict(version_id='temporary-new-version', party_id=scope['party_id'], passage_id='temporary-new-passage', scope_reason='Temporary source fixture'))
        new_attempt = dict(attempt, id='temporary-new-attempt', attempted_at='2026-11-10T17:00:00+00:00', source_version_id='temporary-new-version')
        new_version['practice_attempt_v2'].append(new_attempt)
        new_version['practice_scope_source'].append(dict(source, version_id='temporary-new-version', inspected_at='2026-11-10T17:00:00+00:00'))
        new_version['practice_lead'].append(dict(lead, id='temporary-new-lead', attempt_ids=json.dumps([new_attempt['id']])))
        with self.assertRaises(ValueError):
            validate_practice_closure(new_version, inventory)
        new_version['practice_reopen'] = [dict(id='temporary-new-reopen', closure_id=closure['id'], lead_id='temporary-new-lead', opened_at='2026-11-10T17:01:00+00:00', reason='Temporary new source')]
        self.assertTrue(validate_practice_closure(new_version, inventory))
        candidate_data = copy.deepcopy(data)
        candidate_data['practice_scope_source'] = [dict(scope_id=scope['id'], version_id='0105-cesme-v1', inspected_sections='Temporary fixture', inspected_at='2026-11-10T16:05:00+00:00')]
        candidate_data['practice_candidate'] = [dict(id='technical-candidate', scope_id=scope['id'], event_id='tracer-cesme', relation_id='tracer-relation-id', state='unverified', reason='Temporary fixture', passage_ids='["0105-cesme-p"]')]
        candidate_data['practice_candidate_revision'] = [dict(id='candidate-revision', candidate_id='technical-candidate', recorded_at='2026-11-10T17:00:00+00:00', event_id='tracer-cesme', relation_id='tracer-relation-id', state='eligible', reason='Technical review', passage_ids='["0105-cesme-p"]')]
        with self.assertRaises(ValueError):
            validate_practice_closure(candidate_data, inventory)
        candidate_data['practice_reopen'] = pending['practice_reopen']
        self.assertTrue(validate_practice_closure(candidate_data, inventory))
        self.assertEqual(candidate_data['practice_candidate'][0]['state'], 'unverified')
        wrong_relation_scope = copy.deepcopy(candidate_data)
        wrong_relation_scope['practice_relation'][0]['scope_id'] = 'another-party-scope'
        with self.assertRaises(ValueError):
            validate_practice_closure(wrong_relation_scope, inventory)
        candidate_data['practice_coverage_contract'] = [dict(version=2, inventory_json=json.dumps(inventory, ensure_ascii=False))]
        candidate_data['practice_inventory_revision'] = []
        html = arsiv.render_comparison_snapshot(candidate_data, arsiv.render_report)
        self.assertIn('Technical review', html)
        self.assertIn('Kaynak bağlantısı', html)

    def test_real_bounded_history_reaches_database_and_both_views(self):
        from uygulamalar import _load_practice_copy, practice_coverage_states
        inventory = json.loads((arsiv.DATA / 'practices' / '04-inventory.json').read_text(encoding='utf-8'))
        cell = next(c for c in inventory['cells'] if (c['party_id'], c['topic_id'], c['research_kind']) == ('yeni-parti', 'organ-secim-yontemi', 'event'))
        package = json.loads((arsiv.DATA / 'practices' / '04-coverage-tracer.json').read_text(encoding='utf-8'))
        scope = package['practice_records']['practice_scope_v2'][0]
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            def json_roundtrip(snapshot):
                path = work / 'records.json'
                path.write_text(json.dumps(snapshot, ensure_ascii=False), encoding='utf-8')
                return json.loads(path.read_text(encoding='utf-8'))
            shutil.copyfile(arsiv.DATA / 'releases' / self.release / 'records.sqlite3', work / 'records.sqlite3')
            with patch.object(arsiv, 'validate_phase_one_workspace', return_value=True):
                _load_practice_copy(work, package, self.release)
            data = json_roundtrip(arsiv.export_db(work / 'records.sqlite3', 'temporary-coverage-test'))
            states = practice_coverage_states(data, inventory)
            self.assertEqual(next(x['state'] for x in states if x['cell_id'] == cell['cell_id']), 'open')
            forged_closure = copy.deepcopy(data)
            fake_search = dict(id='temporary-pilot-search', lead_id=None, party_id='yeni-parti', heading='Söylem ve uygulama', topic_id=scope['topic_id'], type='search', query='Temporary technical query', attempted_at='2026-11-11T16:00:00+00:00', result='no_result', reason='Temporary fixture', source_version_id=None)
            forged_closure['attempt'].append(fake_search)
            forged_closure['missing'].append(dict(id='temporary-pilot-missing', party_id='yeni-parti', heading=fake_search['heading'], topic_id=fake_search['topic_id'], status='Bulunamadı', attempt_id=fake_search['id'], reason='Temporary fixture'))
            forged_closure['practice_attempt_v2'] = [dict(id=fake_search['id'], scope_id=scope['id'], attempted_at=fake_search['attempted_at'], query=fake_search['query'], url=None, result='no_result', reason=fake_search['reason'], source_version_id=None)]
            forged_closure['practice_closure'] = [dict(id='temporary-pilot-closure', scope_id=scope['id'], closed_at='2026-11-11T16:10:00+00:00', reason='Temporary fixture', residual_lead_ids='[]')]
            with self.assertRaisesRegex(ValueError, 'kayıtlı uçlar'):
                uygulamalar.validate_practice_closure(forged_closure, inventory)
            other = next(x for x in states if (x['party_id'], x['topic_id'], x['research_kind']) == ('tip', cell['topic_id'], 'event'))
            self.assertEqual(other['state'], 'not_researched')
            html = arsiv.render_comparison_snapshot(data, arsiv.render_report)
            self.assertIn('party-coverage-' + scope['id'], html)
            self.assertIn('comparison-coverage-' + scope['id'], html)
            self.assertIn('0105-cesme-p', html)
            self.assertIn('geniş kapsamlı araştırma sürüyor', html)
            tip_name = next(p['legal_name'] for p in self.data['party'] if p['id'] == 'tip')
            self.assertIn(f'{tip_name} — Söylem ve olay kapsamı: Henüz incelenmedi', html)
            argv = ['arsiv.py', 'practice-coverage', '--inventory', str(arsiv.DATA / 'practices' / '04-inventory.json'), '--input', str(arsiv.DATA / 'practices' / '04-coverage-tracer.json'), '--complete']
            with patch.object(sys, 'argv', argv), patch.object(uygulamalar, '_load_practice_copy'), patch.object(arsiv, 'export_db', return_value=data):
                with self.assertRaisesRegex(ValueError, 'bütün parti ve konular'):
                    arsiv.main()
            missing_table = dict(data)
            del missing_table['practice_reopen']
            with self.assertRaises(ValueError):
                uygulamalar.validate_practices(missing_table)
            narrowed_snapshot = copy.deepcopy(data)
            reduced_inventory = copy.deepcopy(inventory)
            reduced_inventory['cells'].pop()
            narrowed_snapshot['practice_coverage_contract'][0]['inventory_json'] = json.dumps(reduced_inventory, ensure_ascii=False)
            with self.assertRaises(ValueError):
                uygulamalar.validate_practices(narrowed_snapshot)
            wrong_party = copy.deepcopy(data)
            other_cell = next(c for c in inventory['cells'] if (c['party_id'], c['topic_id'], c['research_kind']) == ('tip', cell['topic_id'], 'event'))
            wrong_party['practice_scope_v2'][0].update(id=other_cell['cell_id'], party_id='tip', period_start=other_cell['period_start'])
            wrong_party['practice_legacy_scope'][0]['scope_id'] = other_cell['cell_id']
            with self.assertRaises(ValueError):
                uygulamalar.validate_practices(wrong_party)
            expanded = copy.deepcopy(data)
            extension = dict(id='technical-extension', parent_topic_id='organ-secim-yontemi', definition='Technical test', basis_passage_ids=['0105-cesme-p'], reason='Temporary fixture')
            extended_inventory = uygulamalar.build_practice_inventory(dict(data, release_id=self.release), [extension])
            expanded['practice_topic_extension'] = [dict(extension, basis_passage_ids=json.dumps(extension['basis_passage_ids']))]
            expanded['practice_inventory_revision'] = [dict(epoch=1, inventory_json=json.dumps(extended_inventory, ensure_ascii=False), reason='Temporary fixture')]
            self.assertTrue(uygulamalar.validate_practices(expanded))
            extension_html = arsiv.render_comparison_snapshot(expanded, arsiv.render_report)
            self.assertIn('Technical test', extension_html)
            self.assertIn(f'{tip_name} — Söylem ve olay kapsamı: Henüz incelenmedi', extension_html)
            # A second party is used only inside this temporary database to
            # prove the full closure path; it is never research evidence.
            technical = copy.deepcopy(package)
            technical['party_id'] = None
            tip_cell = other_cell
            tip_scope = {k: tip_cell[k] for k in ('party_id', 'topic_id', 'taxonomy_version', 'period_start', 'cutoff_at', 'research_kind')}
            tip_scope.update(id=tip_cell['cell_id'], boundary_reason='Temporary technical fixture only')
            search = dict(id='temporary-db-search', lead_id=None, party_id='tip', heading='Söylem ve uygulama', topic_id=tip_cell['topic_id'], type='search', query='Temporary technical query', attempted_at='2026-11-10T16:00:00+00:00', result='no_result', reason='Temporary fixture', source_version_id=None)
            missing = dict(id='temporary-db-missing', party_id='tip', heading=search['heading'], topic_id=search['topic_id'], status='Bulunamadı', attempt_id=search['id'], reason='Temporary fixture')
            technical['entries'] = [dict(kind='attempt', values=search), dict(kind='missing', values=missing)]
            technical['practice_records']['practice_scope_v2'].append(tip_scope)
            technical['practice_records']['practice_attempt_v2'] = [dict(id=search['id'], scope_id=tip_scope['id'], attempted_at=search['attempted_at'], query=search['query'], url=None, result=search['result'], reason=search['reason'], source_version_id=None)]
            technical['practice_records']['practice_closure'] = [dict(id='temporary-db-closure', scope_id=tip_scope['id'], closed_at='2026-11-10T16:10:00+00:00', reason='Temporary fixture only', residual_lead_ids='[]')]
            wrong_package = copy.deepcopy(technical)
            wrong_package['party_id'] = 'yeni-parti'
            with self.assertRaises(ValueError):
                _load_practice_copy(work, wrong_package, self.release)
            with patch.object(arsiv, 'validate_phase_one_workspace', return_value=True):
                _load_practice_copy(work, technical, self.release)
            technical_data = json_roundtrip(arsiv.export_db(work / 'records.sqlite3', 'temporary-coverage-test'))
            technical_states = practice_coverage_states(technical_data, inventory)
            self.assertEqual(next(x['state'] for x in technical_states if x['cell_id'] == tip_scope['id']), 'closed')
            self.assertEqual(next(x['state'] for x in technical_states if x['cell_id'] == scope['id']), 'open')
            technical_html = arsiv.render_comparison_snapshot(technical_data, arsiv.render_report)
            for view in ('party', 'comparison'):
                self.assertIn(view + '-scope-' + tip_scope['id'], technical_html)
            self.assertIn('Belirtilen kapsam incelendi', technical_html)
            documents = {d['id']: d for d in technical_data['document']}
            version = next(v for v in technical_data['document_version'] if documents[v['document_id']]['party_id'] == 'tip' and v['original_url'].startswith('https://'))
            reopen_package = copy.deepcopy(technical)
            reopen_package['entries'] = []
            new_attempt = dict(id='temporary-db-access', scope_id=tip_scope['id'], attempted_at='2026-11-10T17:00:00+00:00', query=version['original_url'], url=version['original_url'], result='examined', reason='Temporary source fixture', source_version_id=version['id'])
            reopen_package['practice_records']['practice_attempt_v2'].append(new_attempt)
            reopen_package['practice_records']['practice_scope_source'] = [dict(scope_id=tip_scope['id'], version_id=version['id'], inspected_sections='Temporary fixture', inspected_at='2026-11-10T17:01:00+00:00')]
            reopen_package['practice_records']['practice_lead'] = [dict(id='temporary-db-new-lead', scope_id=tip_scope['id'], url=version['original_url'], relevance_reason='Temporary fixture', state='examined', attempt_ids=json.dumps([new_attempt['id']]))]
            reopen_package['practice_records']['practice_reopen'] = [dict(id='temporary-db-reopen', closure_id='temporary-db-closure', lead_id='temporary-db-new-lead', opened_at='2026-11-10T17:02:00+00:00', reason='Temporary new source')]
            with patch.object(arsiv, 'validate_phase_one_workspace', return_value=True):
                _load_practice_copy(work, reopen_package, self.release)
            reopened = json_roundtrip(arsiv.export_db(work / 'records.sqlite3', 'temporary-coverage-test'))
            self.assertEqual(next(x['state'] for x in practice_coverage_states(reopened, inventory) if x['cell_id'] == tip_scope['id']), 'open')
            self.assertEqual(reopened['practice_closure'][0]['id'], 'temporary-db-closure')
            reopened_html = arsiv.render_comparison_snapshot(reopened, arsiv.render_report)
            self.assertGreaterEqual(reopened_html.count('Temporary new source'), 2)


if __name__ == '__main__':
    unittest.main()
