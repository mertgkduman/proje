"""Technical merge persistence fixtures, never research or human acceptance."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from test_practice_merge_engine import MergeEngine, raw, digest
import uygulamalar
import arsiv


class MergePersistence(unittest.TestCase):
    def test_real_snapshot_preview_roundtrip_and_audit(self):
        inventory = json.loads((arsiv.DATA / 'practices/04-inventory.json').read_text())
        source = (arsiv.DATA / 'practices/04-coverage-tracer.json').read_bytes()
        package = json.loads(source)
        base = package['base_release']
        original = json.loads((arsiv.DATA / 'releases' / base / 'records.json').read_text())
        event = package['practice_records']['practice_event'][0]['id']
        passage = package['practice_records']['practice_event_evidence'][0]['passage_id']
        version = next(row['version_id'] for row in original['passage'] if row['id'] == passage)
        review = dict(subject_kind='practice_event', subject_id=event, reviewer_kind='agent',
                      reviewed_at='2026-11-18T12:00:00+00:00', source_version_ids=json.dumps([version]),
                      passage_ids=json.dumps([passage]), inspected_sections=json.dumps(['Technical fixture section']),
                      supported_claim='Technical fixture only; no research assertion.',
                      limitations='Technical test metadata does not certify source content.',
                      result='reviewed', reason='Fixture tests origin serialization.')
        package['practice_records'].update(practice_source_review_contract=[dict(version=1)],
            practice_source_review=[review], practice_source_review_revision_contract=[dict(version=2)],
            practice_source_review_revision=[dict(review, revision=2, reviewed_at='2026-11-18T13:00:00+00:00')])
        package['source_review_refs'] = [dict(subject_kind='practice_event', subject_id=event)]
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
        self.assertTrue(uygulamalar.validate_practice_merge(snapshot))
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
