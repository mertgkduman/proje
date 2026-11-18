"""Contract checks for sourced practice disputes and evidence stages."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import arsiv
from test_practice_tracer import tracer_input
from uygulamalar import _load_practice_copy, validate_practice_descent, validate_practices


class PracticeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = arsiv.DATA / 'releases' / 'f67ca0a35e634035bf3aa83a46571f50'
        cls.data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))

    def test_initiative_evidence_does_not_support_a_result(self):
        data = copy.deepcopy(self.data)
        relation = data['practice_relation'][0]
        relation['result_finding_id'] = data['practice_contribution'][0]['finding_id']
        data['practice_event_evidence'][0]['stage'] = 'initiative'
        with self.assertRaisesRegex(ValueError, 'sonuç|Sonuç'):
            validate_practices(data)

    def test_initiative_source_can_predate_the_later_event(self):
        data = copy.deepcopy(self.data)
        data['practice_event_evidence'][0]['stage'] = 'initiative'
        next(v for v in data['document_version'] if v['id'] == '0105-cesme-v1')['document_date'] = '2026-09-26'
        validate_practices(data)

    def test_dispute_is_visible_with_source_in_both_views(self):
        data = copy.deepcopy(self.data)
        data['practice_dispute'] = [dict(id='d1', event_id='tracer-cesme', supported_points='Desteklenen teknik nokta', disputed_points='Tartışılan teknik nokta', unresolved_points='Çözülemeyen teknik nokta', summary_finding_id='tracer-event')]
        data['practice_dispute_evidence'] = [dict(dispute_id='d1', passage_id='0105-cesme-p', point='Teknik nokta', source_position='Teknik kaynak anlatımı', role='conflict')]
        html = arsiv.render_comparison_snapshot(data, arsiv.render_report)
        self.assertEqual(html.count('Desteklenen teknik nokta'), 2)
        self.assertEqual(html.count('Tartışılan teknik nokta'), 2)
        self.assertEqual(html.count('Çözülemeyen teknik nokta'), 2)

    def test_evidence_extension_load_export_and_guards(self):
        base = '9003e475ee5d49b29a1310c0bfe2007d'
        package = tracer_input(base)
        records = package['practice_records']
        for entry in list(package['entries']):
            values = entry['values']
            if entry['kind'] == 'finding' and values.get('id') == 'tracer-relation':
                package['entries'].append(dict(kind='finding', values=dict(values, id='change-explanation', pair_id='change-explanation')))
            elif entry['kind'] in ('finding_evidence', 'verification') and values.get('finding_id') == 'tracer-relation':
                package['entries'].append(dict(kind=entry['kind'], values=dict(values, finding_id='change-explanation')))
            elif entry['kind'] == 'review' and values.get('subject_id') == 'tracer-relation':
                package['entries'].append(dict(kind='review', values=dict(values, id='review-change-explanation', subject_id='change-explanation')))
        records['practice_variant_contract'] = [dict(version=1, inventory_json=json.dumps(package['scope_inventory'], sort_keys=True, ensure_ascii=False, separators=(',', ':')))]
        records['practice_scope'] = []
        records['practice_attempt'] = []
        records['practice_unmatched'] = []
        records['practice_evidence_contract'] = [dict(version=1)]
        records['practice_evidence_assessment'] = [dict(event_id='tracer-cesme', passage_id='0105-cesme-p', stage='action', basis_kind='independent_report')]
        records['practice_actor_period'] = []
        records['practice_dispute'] = [dict(id='dispute', event_id='tracer-cesme', supported_points='Teknik destek', disputed_points='Teknik ihtilaf', unresolved_points='Teknik belirsizlik', summary_finding_id='tracer-event')]
        records['practice_dispute_evidence'] = [dict(dispute_id='dispute', passage_id='0105-cesme-p', point='Teknik nokta', source_position='Kaynak anlatımı', role=role) for role in ('conflict', 'reply')]
        records['practice_statement'].append(dict(records['practice_statement'][0], id='earlier-statement', statement_at='2026-08-03', summary_finding_id='tracer-event', quote_finding_id='tracer-quote', version_id='0105-cesme-v1'))
        records['practice_position_change'] = [dict(id='change', party_id='yeni-parti', topic_id='organ-secim-yontemi', before_statement_id='earlier-statement', after_statement_id='tracer-statement', comparison_conditions='Aynı teknik konu ve koşullar.', explanation_finding_id='change-explanation', uncertainty_reason='Teknik örnek; neden bilinmiyor.')]
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            shutil.copyfile(arsiv.DATA / 'releases' / base / 'records.sqlite3', work / 'records.sqlite3')
            _load_practice_copy(work, package, base)
            exported = arsiv.export_db(work / 'records.sqlite3', 'fixture')
            for name in ('practice_dispute', 'practice_dispute_evidence', 'practice_position_change'):
                self.assertEqual(exported[name], records[name])
            html = arsiv.render_comparison_snapshot(exported, arsiv.render_report)
            for text in ('Teknik destek', 'Teknik ihtilaf', 'Teknik belirsizlik', 'Kaynak anlatımı', 'Aynı teknik konu ve koşullar.'):
                self.assertGreaterEqual(html.count(text), 2)
            for mutation in ('role', 'source', 'period', 'topic', 'marker', 'result', 'repetition'):
                bad = copy.deepcopy(exported)
                if mutation == 'role': bad['practice_dispute_evidence'][0]['role'] = 'unknown'
                if mutation == 'source': bad['practice_dispute_evidence'][0]['passage_id'] = '03-v2-tip-instrument-passage'
                if mutation == 'period': bad['practice_position_change'][0]['after_statement_id'] = 'earlier-statement'
                if mutation == 'topic': bad['practice_position_change'][0]['topic_id'] = 'demokrasi-katilim'
                if mutation == 'marker': bad.pop('practice_evidence_contract')
                if mutation == 'result': bad['practice_relation'][0]['result_finding_id'] = 'tracer-event'
                if mutation == 'repetition': bad['practice_evidence_assessment'][0]['basis_kind'] = 'party_announcement'
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    validate_practices(bad)
            old_shape = {k: v for k, v in exported.items() if k not in ('practice_evidence_contract', 'practice_evidence_assessment', 'practice_dispute', 'practice_dispute_evidence', 'practice_position_change')}
            with self.assertRaises(ValueError): validate_practice_descent(exported, old_shape)
            mp = copy.deepcopy(exported)
            actor = next(a for a in mp['actor'] if a['id'] == mp['practice_contribution'][0]['actor_id'])
            actor.update(kind='individual_mp', person_id='technical-person')
            mp['person'].append(dict(id='technical-person', name='Teknik Kişi'))
            template = next(p for p in mp['passage'] if p['id'] == '0105-cesme-p')
            party_name = next(p['legal_name'] for p in mp['party'] if p['id'] == 'yeni-parti')
            mp['passage'].extend([dict(template, id='technical-identity', exact='Teknik Kişi kimlik kaydı'), dict(template, id='technical-membership', exact='Teknik Kişi ' + party_name + ' üyeliği')])
            mp['practice_actor_period'] = [dict(contribution_id='tracer-contribution', valid_from='2026-01-01', valid_to='2026-12-31', identity_passage_id='technical-identity')]
            mp['practice_contribution'][0]['membership_passage_id'] = 'technical-membership'
            validate_practices(mp)
            rendered = arsiv.render_comparison_snapshot(mp, arsiv.render_report)
            self.assertEqual(rendered.count('Bireysel milletvekili faaliyeti'), 2)
            uncertain = copy.deepcopy(mp)
            uncertain['practice_event'][0].update(event_at=None, date_precision='unknown', date_unknown_reason='Olay tarihi bilinmiyor.')
            validate_practices(uncertain)
            self.assertEqual(arsiv.render_comparison_snapshot(uncertain, arsiv.render_report).count('çakışması doğrulanamadı'), 2)
            for change in ('identity', 'membership', 'period'):
                bad = copy.deepcopy(mp)
                if change == 'identity': bad['practice_actor_period'][0]['identity_passage_id'] = 'technical-membership'
                if change == 'membership': bad['practice_contribution'][0]['membership_passage_id'] = None
                if change == 'period': bad['practice_actor_period'][0]['valid_to'] = '2026-09-01'
                with self.subTest(change=change), self.assertRaises(ValueError): validate_practices(bad)


if __name__ == '__main__':
    unittest.main()
