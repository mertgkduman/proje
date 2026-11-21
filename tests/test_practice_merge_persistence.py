"""Technical merge persistence fixtures, never research or human acceptance."""
import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_practice_merge_engine import MergeEngine, raw, digest
import uygulamalar
import arsiv


class MergePersistence(unittest.TestCase):
    def test_promoted_merge_still_requires_complete_review_and_coverage(self):
        from uygulama_birlestirme import merge_packages
        inventory = json.loads((arsiv.DATA / 'practices/04-inventory.json').read_text())
        package = json.loads((arsiv.DATA / 'practices/04-coverage-tracer.json').read_text())
        base = package['base_release']
        data = json.loads((arsiv.DATA / 'releases' / base / 'records.json').read_text())
        schemas = (uygulamalar.PRACTICE_TABLES | uygulamalar.PRACTICE_VARIANT_TABLES |
                   uygulamalar.PRACTICE_EVIDENCE_TABLES | uygulamalar.PRACTICE_COVERAGE_TABLES |
                   uygulamalar.PRACTICE_SOURCE_REVIEW_TABLES | uygulamalar.PRACTICE_SOURCE_REVIEW_REVISION_TABLES)
        base_records = {name: data[name] for name in schemas if name in data}
        package['stage'] = package['practice_records']['practice_contract'][0]['stage'] = 'partial'
        inputs = [dict(identity='technical', raw=raw(package))]
        decisions = raw(dict(version=1, inventory_digest=uygulamalar._digest(inventory),
                             input_digests={'technical': digest(inputs[0]['raw'])}, decisions=[]))
        outcome = merge_packages(inventory, inputs, decisions, decisions_sha256=digest(decisions), base_records=base_records)
        for name, rows in outcome['payload']['practice_records'].items():
            if name == 'practice_contract':
                data[name] = copy.deepcopy(rows)
            else:
                data.setdefault(name, [])
                for row in rows:
                    if row not in data[name]: data[name].append(row)
        data.update(uygulamalar.materialize_practice_merge(inventory, inputs, decisions, base_records, outcome))
        data['practice_contract'][0]['stage'] = 'complete'
        # The real inventory has open cells; its coverage gate must reject first.
        with self.assertRaisesRegex(ValueError, 'bütün kanonik kapsamlar'):
            uygulamalar.validate_practices(data)
        # Simulate closed cells only: genuine ordinary review validation must
        # still reject missing readings and accept complete technical readings.
        with patch('uygulamalar.practice_coverage_states', return_value=[]):
            with self.assertRaisesRegex(ValueError, 'kaynak incelemesi gerektirir'):
                uygulamalar.validate_practices(data)
            passages = {row['id']: row for row in data['passage']}
            reviews = []
            for (kind, identity), (refs, _) in uygulamalar.practice_review_targets(data).items():
                reviews.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent',
                    reviewed_at='2026-11-18T12:00:00+00:00',
                    source_version_ids=json.dumps(sorted({passages[p]['version_id'] for p in refs})),
                    passage_ids=json.dumps(sorted(refs)), inspected_sections=json.dumps(['Technical section ' + kind + identity]),
                    supported_claim='Technical fixture claim ' + kind + identity,
                    limitations='Synthetic test fixture only.', result='reviewed',
                    reason='Technical fixture validates ' + kind + identity))
            data['practice_source_review_contract'] = [dict(version=1)]
            data['practice_source_review'] = reviews
            self.assertTrue(uygulamalar.validate_practices(data))

    def test_real_snapshot_preview_roundtrip_and_audit(self):
        inventory = json.loads((arsiv.DATA / 'practices/04-inventory.json').read_text())
        source = (arsiv.DATA / 'practices/04-coverage-tracer.json').read_bytes()
        package = json.loads(source)
        base = package['base_release']
        original = json.loads((arsiv.DATA / 'releases' / base / 'records.json').read_text())
        event = package['practice_records']['practice_event'][0]['id']
        passage = package['practice_records']['practice_event_evidence'][0]['passage_id']
        review_data = copy.deepcopy(original)
        records = package['practice_records']
        new_passages = {row['passage_id'] for row in records.get('practice_event_evidence', [])
                        if row not in original.get('practice_event_evidence', [])}
        for kind, rows in records.items():
            existing = review_data.setdefault(kind, [])
            for row in rows:
                if row not in existing:
                    existing.append(row)
        passages = {row['id']: row for row in review_data['passage']}
        reviews = []
        for (kind, identity), (refs, _) in uygulamalar.practice_review_package_targets(
                review_data, records, new_passages, package.get('party_id')).items():
            reviews.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent',
                reviewed_at='2026-11-18T12:00:00+00:00',
                source_version_ids=json.dumps(sorted({passages[p]['version_id'] for p in refs})),
                passage_ids=json.dumps(sorted(refs)), inspected_sections=json.dumps(['Technical section ' + kind]),
                supported_claim='Technical fixture subject ' + identity,
                limitations='Technical test metadata does not certify source content.',
                result='reviewed', reason='Fixture tests origin serialization.'))
        review = next(row for row in reviews if (row['subject_kind'], row['subject_id']) == ('practice_event', event))
        package['practice_records'].update(practice_source_review_contract=[dict(version=1)],
            practice_source_review=reviews, practice_source_review_revision_contract=[dict(version=2)],
            practice_source_review_revision=[dict(review, revision=2, reviewed_at='2026-11-18T13:00:00+00:00',
                reason='Fixture verifies revised review origin serialization.')])
        package['source_review_refs'] = [dict(subject_kind=r['subject_kind'], subject_id=r['subject_id']) for r in reviews]
        source = raw(package)
        schemas = (uygulamalar.PRACTICE_TABLES | uygulamalar.PRACTICE_VARIANT_TABLES |
                   uygulamalar.PRACTICE_EVIDENCE_TABLES | uygulamalar.PRACTICE_COVERAGE_TABLES |
                   uygulamalar.PRACTICE_SOURCE_REVIEW_TABLES | uygulamalar.PRACTICE_SOURCE_REVIEW_REVISION_TABLES)
        base_records = {name: original[name] for name in schemas if name in original}
        inputs = [dict(identity='technical-package', raw=source),
                  dict(identity='technical-copy', raw=json.dumps(package, ensure_ascii=False, indent=2).encode())]
        decision_raw = raw(dict(version=1, inventory_digest=uygulamalar._digest(inventory),
            input_digests={item['identity']: digest(item['raw']) for item in inputs}, decisions=[dict(
                id='technical-same', candidate_keys=[package['practice_records']['practice_event'][0]['common_event_key']],
                event_refs=[dict(input_package_sha256=digest(item['raw']), event_id=event) for item in inputs],
                decision='same', canonical_event_id=event, overlap_reason='Technical fixture duplicates the same source package.',
                source_passage_ids=[passage], reviewed_at='2026-11-18T14:00:00+00:00', reviewer_kind='agent')]))
        from uygulama_birlestirme import merge_packages
        result = merge_packages(inventory, inputs, decision_raw, decisions_sha256=digest(decision_raw), base_records=base_records)
        payload = result['payload']
        payload['practice_records'].update(uygulamalar.materialize_practice_merge(inventory, inputs, decision_raw, base_records, result))
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'preview'
            uygulamalar.render_practice_preview(payload, target, inventory)
            folder, = (target / 'releases').iterdir()
            release = folder.name
            snapshot = json.loads((folder / 'records.json').read_text())
            self.assertEqual(snapshot, arsiv.export_db(folder / 'records.sqlite3', release, storage_root=target))
            self.assertEqual(len(snapshot['practice_event_alias']), 2)
            self.assertEqual(snapshot['practice_event_decision'][0]['decision'], 'same')
            self.assertEqual(len(snapshot['practice_merge_provenance']), 1)
            origins = [json.loads(row['original_json']) for row in snapshot['practice_merge_origin'] if row['origin_kind'] == 'review_origins']
            self.assertEqual({row['original']['reviewed_at'] for row in origins}, {'2026-11-18T12:00:00+00:00', '2026-11-18T13:00:00+00:00'})
            self.assertNotIn('practice_source_review', snapshot)
            manifest = json.loads((folder / 'manifest.json').read_text())
            self.assertEqual(manifest['practice_merge_provenance_sha256'], uygulamalar.practice_manifest_fields(snapshot)['practice_merge_provenance_sha256'])
            arsiv.audit_release(release, storage_root=target)

    def test_replay_rejects_lost_alias_evidence_and_origin_even_if_rehashed(self):
        fixture = MergeEngine(); fixture.setUp()
        decision = fixture.decision()
        for index, item in enumerate(fixture.inputs):
            package = json.loads(item['raw'])
            package['practice_records']['practice_contract'] = [dict(version=1, taxonomy_version=4,
                method_version=1, inventory_digest='a' * 64, stage='partial')]
            for table in ('practice_source_review', 'practice_source_review_revision'):
                package['practice_records'][table][0]['source_version_ids'] = json.dumps(['v' + str(index + 1)])
            item['raw'] = raw(package)
            decision['input_digests'][item['identity']] = digest(item['raw'])
            decision['decisions'][0]['event_refs'][index]['input_package_sha256'] = digest(item['raw'])
        decisions = raw(decision)
        outcome = fixture.merge(decision)
        extension = uygulamalar.materialize_practice_merge(
            fixture.inventory, fixture.inputs, decisions, {}, outcome)
        snapshot = copy.deepcopy(outcome['payload']['practice_records'])
        for entry in outcome['payload']['entries']:
            snapshot.setdefault(entry['kind'], []).append(entry['values'])
        for index, passage in enumerate(snapshot['passage']):
            passage['version_id'] = 'v' + passage['id'][1:]
        snapshot['document_version'] = [dict(id='v1', document_id='d1'), dict(id='v2', document_id='d2')]
        snapshot['document'] = [dict(id='d1', party_id='p1'), dict(id='d2', party_id='p2')]
        snapshot['practice_coverage_contract'] = [dict(version=2, inventory_json=json.dumps(fixture.inventory))]
        snapshot.update(extension)
        # Exercise the persisted representation, not just materializer output.
        with sqlite3.connect(':memory:') as db:
            for table, definition in uygulamalar.PRACTICE_MERGE_TABLES.items():
                db.execute('CREATE TABLE ' + table + ' (' + definition + ')')
                for row in extension[table]:
                    db.execute('INSERT INTO ' + table + ' (' + ','.join(row) + ') VALUES (' + ','.join('?' for _ in row) + ')', list(row.values()))
            db.row_factory = sqlite3.Row
            for table in extension:
                snapshot[table] = [dict(row) for row in db.execute('SELECT * FROM ' + table)]
        self.assertTrue(uygulamalar.validate_practice_merge(snapshot))
        promoted = copy.deepcopy(snapshot)
        promoted['practice_contract'][0]['stage'] = 'complete'
        self.assertTrue(uygulamalar.validate_practice_merge(promoted))
        for key, value in [('stage', 'tracer'), ('stage', 'unknown'), ('version', 2),
                           ('taxonomy_version', 5), ('method_version', 2), ('inventory_digest', 'b' * 64)]:
            broken = copy.deepcopy(promoted)
            broken['practice_contract'][0][key] = value
            with self.subTest(contract_field=key, value=value), self.assertRaises(ValueError):
                uygulamalar.validate_practice_merge(broken)
        review_origins = [json.loads(row['original_json']) for row in snapshot['practice_merge_origin'] if row['origin_kind'] == 'review_origins']
        self.assertEqual(len(review_origins), 4)
        self.assertEqual({row['table'] for row in review_origins}, {'practice_source_review', 'practice_source_review_revision'})
        self.assertEqual({row['canonical_subject_id'] for row in review_origins}, {'e1'})
        self.assertNotIn('practice_source_review', snapshot)
        for table in ('practice_event_alias', 'practice_merge_origin', 'practice_event_evidence'):
            broken = copy.deepcopy(snapshot)
            broken[table].pop()
            with self.subTest(table=table), self.assertRaises(ValueError):
                uygulamalar.validate_practice_merge(broken)
        broken = copy.deepcopy(snapshot)
        broken['practice_event_alias'][0]['canonical_event_id'] = 'unknown'
        with self.assertRaises(ValueError):
            uygulamalar.validate_practice_merge(broken)
        broken = copy.deepcopy(snapshot)
        broken['practice_coverage_contract'][0]['inventory_json'] = '{}'
        with self.assertRaises(ValueError):
            uygulamalar.validate_practice_merge(broken)
        broken = copy.deepcopy(snapshot)
        broken['practice_merge_input'][0]['raw_hex'] = raw({'forged': True}).hex()
        broken['practice_merge_input'][0]['input_package_sha256'] = digest(raw({'forged': True}))
        with self.assertRaises(ValueError):
            uygulamalar.validate_practice_merge(broken)
        with self.assertRaises(ValueError):
            uygulamalar.validate_practice_descent(snapshot, {k: v for k, v in snapshot.items() if k not in extension})


if __name__ == '__main__': unittest.main()
