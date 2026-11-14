"""Explicit source-side claims for the versioned synthesis contract."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import arsiv
import test_comparisons


def fixture():
    synthesis = {'id': 'claim', 'topic_id': 'hours', 'taxonomy_version': 3,
                 'text': 'Kaynaklara dayalı karşılaştırma.'}
    data = {
        'comparison_row': [
            {'id': 'a', 'party_id': 'a', 'topic_id': 'hours', 'taxonomy_version': 3,
             'state': 'evidence', 'version_id': 'va', 'scope_id': None, 'missing_id': None},
            {'id': 'b', 'party_id': 'b', 'topic_id': 'hours', 'taxonomy_version': 3,
             'state': 'evidence', 'version_id': 'vb', 'scope_id': None, 'missing_id': None},
            {'id': 'c', 'party_id': 'c', 'topic_id': 'hours', 'taxonomy_version': 3,
             'state': 'no_explicit_statement', 'version_id': 'vc', 'scope_id': 'sc', 'missing_id': None},
            {'id': 'd', 'party_id': 'd', 'topic_id': 'hours', 'taxonomy_version': 3, 'source_role': 'program',
             'state': 'document_missing', 'version_id': None, 'scope_id': None, 'missing_id': 'md'},
        ],
        'comparison_field': [
            {'row_id': 'a', 'summary_finding_id': 'fa', 'quote_finding_id': 'qa'},
            {'row_id': 'b', 'summary_finding_id': 'fb', 'quote_finding_id': 'qb'},
        ],
        'finding_evidence': [
            {'finding_id': 'fa', 'passage_id': 'pa'}, {'finding_id': 'qa', 'passage_id': 'pa'},
            {'finding_id': 'fb', 'passage_id': 'pb'}, {'finding_id': 'qb', 'passage_id': 'pb'},
        ],
        'passage': [{'id': 'pa', 'version_id': 'va'}, {'id': 'pa2', 'version_id': 'va'},
                    {'id': 'pb', 'version_id': 'vb'}],
        'comparison_review_scope': [{'id': 'sc', 'party_id': 'c', 'version_id': 'vc',
                                     'sections': 'Bölüm', 'query_terms': 'süre',
                                     'reviewed_at': '2026-11-14T00:00:00+00:00',
                                     'result': 'no_explicit_statement', 'reason': 'dar kapsam'}],
        'missing': [{'id': 'md', 'party_id': 'd', 'attempt_id': 'ad',
                     'heading': 'Program', 'topic_id': 'belge', 'status': 'Bulunamadı',
                     'reason': 'arama sonucu'}],
        'attempt': [{'id': 'ad', 'party_id': 'd', 'heading': 'Program',
                     'topic_id': 'belge', 'type': 'search', 'result': 'no_result'}],
        'comparison_synthesis_evidence': [
            {'synthesis_id': 'claim', 'passage_id': 'pa'},
            {'synthesis_id': 'claim', 'passage_id': 'pb'},
        ],
        'comparison_semantic_review': [],
    }
    decision = {'contract_version': 2, 'claim_type': 'multi_positive',
                'explanation': 'İki gerçek pasaj ve dar kapsam ayrı değerlendirildi.',
                'sides': [{'party_id': 'a', 'row_id': 'a', 'support': 'passage', 'refs': ['pa']},
                          {'party_id': 'b', 'row_id': 'b', 'support': 'passage', 'refs': ['pb']},
                          {'party_id': 'c', 'row_id': 'c', 'support': 'scope', 'refs': ['sc']},
                          {'party_id': 'd', 'row_id': 'd', 'support': 'missing', 'refs': ['md', 'ad']}]}
    data['comparison_semantic_review'].append(
        {'subject_kind': 'comparison_synthesis', 'subject_id': 'claim', 'reviewer_kind': 'agent',
         'reviewed_at': '2026-11-14T00:00:00+00:00', 'result': 'reviewed',
         'reason': json.dumps(decision, ensure_ascii=False)})
    return data, synthesis, decision


class SynthesisContractTest(unittest.TestCase):
    def test_versioned_contract_accepts_one_passage_with_real_scoped_status(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        data['comparison_contract'][0].update(version=2, taxonomy_version=3, stage='partial')
        for table in ('comparison_topic', 'comparison_row', 'comparison_synthesis'):
            for record in data[table]: record['taxonomy_version'] = 3
        data['topic'].append(dict(id='merkez-yonetimi-secimi', taxonomy_version=3, status='verified'))
        data['topic_basis'].append(dict(topic_id='merkez-yonetimi-secimi', taxonomy_version=3,
            passage_id='03-tip-pm', source_role='charter', rationale='Gerçek pasaj'))
        row = next(r for r in data['comparison_row'] if r['party_id'] == 'iyi')
        row.update(state='no_explicit_statement', scope_id='scoped-iyi')
        data['comparison_field'] = [f for f in data['comparison_field'] if f['row_id'] != row['id']]
        data['comparison_change'] = [c for c in data['comparison_change'] if c['row_id'] != row['id']]
        data['comparison_review_scope'].append(dict(id='scoped-iyi', party_id='iyi',
            version_id=row['version_id'], sections='Seçim maddesi', query_terms='seçim',
            reviewed_at='2026-11-14T00:00:00+00:00', result='no_explicit_statement', reason='dar kapsam'))
        s = data['comparison_synthesis'][0]
        s['text'] = 'TİP seçimi belirtir; İYİ için belirtilen kapsam incelendi.'
        data['comparison_synthesis_evidence'] = [e for e in data['comparison_synthesis_evidence']
                                                 if e['passage_id'] == '03-tip-pm']
        decision = dict(contract_version=2, claim_type='one_positive', explanation='Pasaj ve dar kapsam incelendi.',
            sides=[dict(party_id='tip', row_id='03-tip-merkez', support='passage', refs=['03-tip-pm']),
                   dict(party_id='iyi', row_id=row['id'], support='scope', refs=['scoped-iyi'])])
        data['comparison_semantic_review'].append(dict(subject_kind='comparison_synthesis',
            subject_id=s['id'], reviewer_kind='agent', reviewed_at='2026-11-14T00:00:00+00:00',
            result='reviewed', reason=json.dumps(decision, ensure_ascii=False)))
        self.assertTrue(arsiv.validate_comparisons(data))
        data['comparison_review_scope'][-1]['result'] = 'not_researched'
        with self.assertRaises(ValueError): arsiv.validate_comparisons(data)

    def check(self, data, synthesis, decision):
        data['comparison_semantic_review'][0]['reason'] = json.dumps(decision, ensure_ascii=False)
        return arsiv.validate_synthesis_v2(data, synthesis)

    def test_multiple_positive_parties_need_their_own_real_passages(self):
        data, synthesis, decision = fixture()
        self.assertTrue(self.check(data, synthesis, decision))
        for mutation in ('same_owner', 'wrong_topic', 'wrong_party', 'missing_passage'):
            d, s, claim = copy.deepcopy((data, synthesis, decision))
            if mutation == 'same_owner':
                claim['sides'][1].update(row_id='a', refs=['pa2'])
                d['comparison_synthesis_evidence'][1]['passage_id'] = 'pa2'
            elif mutation == 'wrong_topic': d['comparison_row'][1]['topic_id'] = 'other'
            elif mutation == 'wrong_party': claim['sides'][1]['party_id'] = 'a'
            else: claim['sides'][1]['refs'] = ['pa']
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): self.check(d, s, claim)

    def test_single_positive_and_all_status_claims_use_actual_scope_and_attempt(self):
        data, synthesis, claim = fixture()
        claim['claim_type'] = 'one_positive'
        claim['sides'].pop(1)
        data['comparison_synthesis_evidence'].pop()
        self.assertTrue(self.check(data, synthesis, claim))
        bad = copy.deepcopy(claim); bad['sides'][1]['refs'] = ['wrong-scope']
        with self.assertRaises(ValueError): self.check(data, synthesis, bad)
        bad = copy.deepcopy(data); bad['comparison_row'][2]['state'] = 'not_researched'
        with self.assertRaises(ValueError): self.check(bad, synthesis, claim)
        claim['claim_type'] = 'status_only'
        claim['sides'].pop(0)
        data['comparison_synthesis_evidence'].clear()
        self.assertTrue(self.check(data, synthesis, claim))
        bad = copy.deepcopy(claim); bad['sides'][-1]['refs'] = ['md', 'wrong-attempt']
        with self.assertRaises(ValueError): self.check(data, synthesis, bad)

    def test_old_subject_and_unsupported_claim_do_not_count_as_review(self):
        data, synthesis, claim = fixture()
        data['comparison_semantic_review'][0]['subject_id'] = 'old-claim'
        with self.assertRaises(ValueError): self.check(data, synthesis, claim)
        data['comparison_semantic_review'][0]['subject_id'] = 'claim'
        claim['sides'].pop(1)
        data['comparison_synthesis_evidence'].pop()
        with self.assertRaises(ValueError): self.check(data, synthesis, claim)

    def test_missing_review_and_wrong_source_role_are_rejected(self):
        data, synthesis, claim = fixture()
        data['comparison_semantic_review'][0]['result'] = 'unreviewed'
        with self.assertRaises(ValueError): self.check(data, synthesis, claim)
        data['comparison_semantic_review'][0]['result'] = 'reviewed'
        data['comparison_review_scope'][0]['result'] = 'not_researched'
        with self.assertRaises(ValueError): self.check(data, synthesis, claim)
        data['comparison_review_scope'][0]['result'] = 'no_explicit_statement'
        data['comparison_review_scope'][0]['reviewed_at'] = 'unknown'
        with self.assertRaises(ValueError): self.check(data, synthesis, claim)
        data['comparison_review_scope'][0]['reviewed_at'] = '2026-11-14T00:00:00+00:00'
        data['comparison_row'][-1]['source_role'] = 'charter'
        with self.assertRaises(ValueError): self.check(data, synthesis, claim)

    def test_old_contract_still_requires_two_owners(self):
        data = test_comparisons.ComparisonReleaseTest.comparison_data()
        self.assertTrue(arsiv.validate_comparisons(data))
        data['comparison_synthesis_evidence'].pop()
        with self.assertRaises(ValueError): arsiv.validate_comparisons(data)

    def test_contract_descent_is_forward_only_and_preserves_old_records(self):
        base = test_comparisons.ComparisonReleaseTest.comparison_data()
        candidate = copy.deepcopy(base)
        candidate['comparison_contract'][0].update(version=2, taxonomy_version=3)
        self.assertTrue(arsiv.validate_comparison_descent(base, candidate))
        tampered = copy.deepcopy(candidate)
        tampered['comparison_synthesis'][0]['text'] = 'değiştirildi'
        with self.assertRaises(ValueError): arsiv.validate_comparison_descent(base, tampered)
        with self.assertRaises(ValueError): arsiv.validate_comparison_descent(candidate, base)

    def test_contract_upgrade_is_atomic_and_cannot_be_downgraded(self):
        original_data = arsiv.DATA
        source = original_data / 'releases' / arsiv.current() / 'records.sqlite3'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); work = root / 'work'; work.mkdir()
            arsiv.DATA = root / 'data'; arsiv.DATA.mkdir()
            try:
                shutil.copyfile(source, work / 'records.sqlite3')
                (work / 'workspace.json').write_text(json.dumps({'token': 'test'}))
                (arsiv.DATA / '.write.lock').write_text(json.dumps({'token': 'test'}))
                db = arsiv.connect(work / 'records.sqlite3')
                try:
                    db.execute('UPDATE comparison_contract SET taxonomy_version=3')
                    db.commit()
                    before_count = db.execute('SELECT count(*) FROM comparison_row').fetchone()[0]
                finally: db.close()
                # The full export validator has separate real-source integration coverage;
                # here the copied SQLite database exercises the atomic version transition.
                with patch.object(arsiv, 'export_db', return_value={}):
                    arsiv.load_comparison(work, dict(contract_version=2, taxonomy_version=3,
                                                     stage='partial', records=[]))
                    db = arsiv.connect_readonly(work / 'records.sqlite3')
                    try:
                        self.assertEqual(db.execute('SELECT version FROM comparison_contract').fetchone()[0], 2)
                        self.assertEqual(db.execute('SELECT count(*) FROM comparison_row').fetchone()[0], before_count)
                    finally: db.close()
                    digest = arsiv.sha(work / 'records.sqlite3')
                    with self.assertRaises(ValueError):
                        arsiv.load_comparison(work, dict(contract_version=1, taxonomy_version=3,
                                                         stage='partial', records=[]))
                    self.assertEqual(arsiv.sha(work / 'records.sqlite3'), digest)
            finally:
                arsiv.DATA = original_data


if __name__ == '__main__':
    unittest.main()
