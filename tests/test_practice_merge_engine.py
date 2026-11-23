"""Technical, in-memory merge fixtures; these are not political research."""
import copy
import hashlib
import json
import unittest

try:
    from uygulama_birlestirme import merge_packages, MergeError
except ImportError:
    merge_packages = None
    MergeError = ValueError


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def package(event, party, passage):
    return dict(contract_version=1, base_release='base', taxonomy_version=4, stage='partial',
        party_id=party, scope_inventory=[], tranches=[], entries=[dict(kind='passage', values=dict(id=passage))],
        source_review_refs=[dict(subject_kind='practice_event', subject_id=event)],
        practice_records=dict(practice_event=[dict(id=event, common_event_key='key', title='same')],
            practice_event_evidence=[dict(event_id=event, passage_id=passage, stage='action')],
            practice_contribution=[dict(id='contribution-'+party, event_id=event)],
            practice_relation=[dict(id='relation-'+party, event_id=event)],
            practice_legacy_link=[dict(legacy_id=party, event_id=event)],
            practice_unmatched=[dict(id='unmatched-'+party, event_id=event)],
            practice_evidence_assessment=[dict(event_id=event, passage_id=passage, stage='action')],
            practice_dispute=[dict(id='dispute-'+party, event_id=event)],
            practice_candidate=[dict(id='candidate-'+party, event_id=event)],
            practice_candidate_revision=[dict(id='revision-'+party, event_id=event)],
            practice_source_review=[dict(subject_kind='practice_event', subject_id=event, passage_ids=json.dumps([passage]))],
            practice_source_review_revision=[dict(subject_kind='practice_event', subject_id=event, revision=2, passage_ids=json.dumps([passage]))]))


class MergeEngine(unittest.TestCase):
    def setUp(self):
        self.inventory = {'technical': True}
        self.inputs = [dict(identity='one', raw=raw(package('e1', 'p1', 's1'))),
                       dict(identity='two', raw=raw(package('e2', 'p2', 's2')))]
        self.refs = [dict(input_package_sha256=digest(x['raw']), event_id=e) for x, e in zip(self.inputs, ['e1', 'e2'])]

    def decision(self, kind='same'):
        return dict(version=1, inventory_digest=digest(raw(self.inventory)),
            input_digests={x['identity']: digest(x['raw']) for x in self.inputs},
            decisions=[dict(id='d', candidate_keys=['key'], event_refs=self.refs, decision=kind,
                canonical_event_id='e1' if kind == 'same' else None, overlap_reason='Technical fixture overlap',
                source_passage_ids=['s1', 's2'], reviewed_at='2026-11-18T12:00:00+00:00', reviewer_kind='agent')])

    def merge(self, decision=None, inputs=None, base=None):
        data = raw(self.decision() if decision is None else decision)
        return merge_packages(self.inventory, self.inputs if inputs is None else inputs, data,
                              decisions_sha256=digest(data), base_records=base or {})

    def test_same_preserves_every_reference_and_original_readings(self):
        self.assertTrue(callable(merge_packages), 'deterministic merge engine must exist')
        result = self.merge(base={'practice_event': [package('e1', 'p1', 's1')['practice_records']['practice_event'][0]]})
        self.assertEqual(result, self.merge(inputs=list(reversed(self.inputs)), base={'practice_event': [package('e1', 'p1', 's1')['practice_records']['practice_event'][0]]}))
        records = result['payload']['practice_records']
        for name in ('practice_event_evidence', 'practice_contribution', 'practice_relation', 'practice_legacy_link', 'practice_unmatched', 'practice_evidence_assessment', 'practice_dispute', 'practice_candidate', 'practice_candidate_revision'):
            self.assertEqual(len(records[name]), 2, name)
            self.assertEqual({r['event_id'] for r in records[name]}, {'e1'})
        self.assertEqual(len(result['review_origins']), 4)
        self.assertEqual({x['original']['subject_id'] for x in result['review_origins']}, {'e1', 'e2'})
        self.assertEqual({x['canonical_subject_id'] for x in result['review_origins']}, {'e1'})
        self.assertNotIn('practice_source_review', records)
        self.assertEqual(len(result['payload']['entries']), 2)

    def test_distinct_and_unresolved_remain_separate(self):
        for kind in ('distinct', 'unresolved'):
            result = self.merge(self.decision(kind))
            self.assertEqual({x['canonical_event_id'] for x in result['aliases']}, {'e1', 'e2'})
            self.assertEqual(result['decisions'][0]['decision'], kind)

    def test_rejects_missing_forged_conflicting_and_field_conflicts(self):
        for mutate in ('missing', 'digest', 'inventory', 'extra', 'source', 'field', 'canonical'):
            d = copy.deepcopy(self.decision())
            inputs = copy.deepcopy(self.inputs)
            if mutate == 'missing': d['decisions'] = []
            if mutate == 'digest': d['input_digests']['one'] = '0'*64
            if mutate == 'inventory': d['inventory_digest'] = '0'*64
            if mutate == 'extra': d['decisions'].append(dict(d['decisions'][0], id='extra'))
            if mutate == 'source': d['decisions'][0]['source_passage_ids'] = ['fake']
            if mutate == 'canonical': d['decisions'][0]['canonical_event_id'] = 'missing'
            if mutate == 'field':
                p = json.loads(inputs[1]['raw']); p['practice_records']['practice_event'][0]['title'] = 'different'
                inputs[1]['raw'] = raw(p); d['input_digests']['two'] = digest(inputs[1]['raw']); d['decisions'][0]['event_refs'][1]['input_package_sha256'] = digest(inputs[1]['raw'])
            with self.subTest(mutate=mutate), self.assertRaises(MergeError): self.merge(d, inputs)
        with self.assertRaises(MergeError): merge_packages(self.inventory, self.inputs, raw(self.decision()), decisions_sha256='0'*64, base_records={})

    def test_event_evidence_review_history_remaps_without_changing_original(self):
        inputs = copy.deepcopy(self.inputs)
        p = json.loads(inputs[1]['raw'])
        for table in ('practice_source_review', 'practice_source_review_revision'):
            p['practice_records'][table][0].update(subject_kind='practice_event_evidence', subject_id='e2|s2|action')
        p['source_review_refs'] = [dict(subject_kind='practice_event_evidence', subject_id='e2|s2|action')]
        inputs[1]['raw'] = raw(p)
        d = self.decision(); d['input_digests']['two'] = digest(inputs[1]['raw']); d['decisions'][0]['event_refs'][1]['input_package_sha256'] = digest(inputs[1]['raw'])
        result = self.merge(d, inputs)
        origins = [x for x in result['review_origins'] if x['party_id'] == 'p2']
        self.assertEqual(len(origins), 2)
        self.assertTrue(all(x['original']['subject_id'] == 'e2|s2|action' and x['canonical_subject_id'] == 'e1|s2|action' for x in origins))
        self.assertEqual(next(x for x in result['review_ref_origins'] if x['party_id'] == 'p2')['canonical_subject_id'], 'e1|s2|action')

    def test_rejects_rewriting_base_row_and_unknown_event_reference(self):
        base_row = package('e2', 'p2', 's2')['practice_records']['practice_relation'][0]
        with self.assertRaisesRegex(MergeError, 'base row'):
            self.merge(base={'practice_relation': [base_row]})
        inputs = copy.deepcopy(self.inputs)
        p = json.loads(inputs[1]['raw']); p['practice_records']['practice_relation'][0]['related_event_id'] = 'e2'
        inputs[1]['raw'] = raw(p)
        d = self.decision(); d['input_digests']['two'] = digest(inputs[1]['raw']); d['decisions'][0]['event_refs'][1]['input_package_sha256'] = digest(inputs[1]['raw'])
        with self.assertRaisesRegex(MergeError, 'Unknown event'):
            self.merge(d, inputs)

    def test_distinct_colliding_ids_preserve_base_identity(self):
        inputs = copy.deepcopy(self.inputs)
        p = json.loads(inputs[1]['raw'])
        def rename(value):
            if isinstance(value, dict): return {k: rename(v) for k, v in value.items()}
            if isinstance(value, list): return [rename(v) for v in value]
            return 'e1' if value == 'e2' else value
        inputs[1]['raw'] = raw(rename(p))
        d = self.decision('distinct'); d['input_digests']['two'] = digest(inputs[1]['raw'])
        d['decisions'][0]['event_refs'][1] = dict(input_package_sha256=digest(inputs[1]['raw']), event_id='e1')
        base_event = package('e1', 'p1', 's1')['practice_records']['practice_event'][0]
        # Identical base rows in both inputs cannot be declared distinct without
        # replacing an accepted identity.
        with self.assertRaises(MergeError): self.merge(d, inputs, {'practice_event': [base_event]})
        result = self.merge(d, inputs)
        self.assertEqual(len({x['canonical_event_id'] for x in result['aliases']}), 2)

    def test_base_only_event_reference_is_preserved_without_invented_candidate(self):
        p = package('base-event', 'p1', 's1')
        event = p['practice_records'].pop('practice_event')[0]
        p['practice_records']['practice_event_evidence'] = []
        inp = [dict(identity='one', raw=raw(p))]
        d = dict(version=1, inventory_digest=digest(raw(self.inventory)),
                 input_digests={'one': digest(inp[0]['raw'])}, decisions=[])
        result = self.merge(d, inp, {'practice_event': [event]})
        self.assertEqual(result['payload']['practice_records']['practice_relation'][0]['event_id'], 'base-event')
        self.assertEqual(result['review_origins'][0]['canonical_subject_id'], 'base-event')
        self.assertFalse(result['decisions'])
        self.assertEqual(result['aliases'], [dict(input_package_sha256=digest(inp[0]['raw']),
            input_event_id='base-event', canonical_event_id='base-event', decision_id=None)])
        with self.assertRaises(MergeError):
            self.merge(d, inp, {})

    def test_rejects_conflicting_entry_identity(self):
        inputs = copy.deepcopy(self.inputs)
        p = json.loads(inputs[1]['raw']); p['entries'][0]['values']['id'] = 's1'; p['entries'][0]['values']['extra'] = 'different'
        inputs[1]['raw'] = raw(p)
        d = self.decision(); d['input_digests']['two'] = digest(inputs[1]['raw']); d['decisions'][0]['event_refs'][1]['input_package_sha256'] = digest(inputs[1]['raw'])
        with self.assertRaisesRegex(MergeError, 'entry identity'): self.merge(d, inputs)

    def test_persistence_retains_actor_and_manual_passage_entries(self):
        from uygulama_merge_kayit import materialize_practice_merge, validate_practice_merge

        item = package('e1', 'p1', 's1')
        item['source_review_refs'] = []
        for table in ('practice_source_review', 'practice_source_review_revision'):
            del item['practice_records'][table]
        item['entries'].extend([
            dict(kind='manual_passage', values=dict(passage_id='s1')),
            dict(kind='person', values=dict(id='person-1')),
            dict(kind='actor', values=dict(id='actor-1', person_id='person-1')),
        ])
        inputs = [dict(identity='one', raw=raw(item))]
        decisions = raw(dict(version=1, inventory_digest=digest(raw(self.inventory)),
                             input_digests={'one': digest(inputs[0]['raw'])}, decisions=[]))
        outcome = merge_packages(self.inventory, inputs, decisions,
                                 decisions_sha256=digest(decisions), base_records={})
        data = dict(outcome['payload']['practice_records'])
        data.update(materialize_practice_merge(self.inventory, inputs, decisions, {}, outcome))
        data['practice_coverage_contract'] = [dict(inventory_json=raw(self.inventory).decode())]
        for entry in outcome['payload']['entries']:
            data.setdefault(entry['kind'], []).append(entry['values'])

        self.assertTrue(validate_practice_merge(data))
        data['actor'].clear()
        with self.assertRaisesRegex(ValueError, 'Birleşme girdisi kayıp'):
            validate_practice_merge(data)


if __name__ == '__main__': unittest.main()
