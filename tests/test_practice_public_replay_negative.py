"""Public replay rejection of altered merge records; synthetic fixture only."""
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import arsiv
import uygulamalar


class PublicReplayNegative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='gsd-public-replay-negative-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.inventory = json.loads((arsiv.DATA / 'practices/04-inventory.json').read_text())
        cache = Path(os.environ['GSD_PUBLIC_REPLAY_FIXTURE']) if os.environ.get('GSD_PUBLIC_REPLAY_FIXTURE') else None
        if cache is not None and cache.exists():
            raw_cache = cache.read_bytes()
            expected = cache.with_suffix(cache.suffix + '.sha256').read_text().strip()
            if hashlib.sha256(raw_cache).hexdigest() != expected:
                raise ValueError('Technical fixture digest mismatch')
            cls.merged = json.loads(raw_cache)
        else:
            cls.merged = cls.build_reviewed_merge()
            if cache is not None:
                raw_cache = json.dumps(cls.merged, ensure_ascii=False, sort_keys=True).encode()
                cache.write_bytes(raw_cache)
                cache.with_suffix(cache.suffix + '.sha256').write_text(hashlib.sha256(raw_cache).hexdigest() + '\n')
        cls.pointer = arsiv.sha(arsiv.DATA / 'current.json')
        cls.db = arsiv.DATA / 'releases' / arsiv.current() / 'records.sqlite3'
        cls.db_hash = arsiv.sha(cls.db)

    @classmethod
    def build_reviewed_merge(cls):
        package = json.loads((arsiv.DATA / 'practices/04-coverage-tracer.json').read_text())
        base = json.loads((arsiv.DATA / 'releases' / package['base_release'] / 'records.json').read_text())
        review_data = copy.deepcopy(base)
        for table, rows in package['practice_records'].items():
            existing = review_data.setdefault(table, [])
            for row in rows:
                if row not in existing:
                    existing.append(row)
        passages = {p['id']: p for p in review_data['passage']}
        reviews = []
        for (kind, identity), (refs, _) in uygulamalar.practice_review_targets(review_data, package['practice_records']).items():
            reviews.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent',
                reviewed_at='2026-11-18T12:00:00+00:00',
                source_version_ids=json.dumps(sorted({passages[p]['version_id'] for p in refs})),
                passage_ids=json.dumps(sorted(refs)), inspected_sections=json.dumps(['Technical fixture ' + kind]),
                supported_claim='Technical fixture subject ' + identity, limitations='Synthetic fixture only.',
                result='reviewed', reason='Temporary validation fixture.'))
        package['practice_records'].update(practice_source_review_contract=[dict(version=1)], practice_source_review=reviews)
        package['source_review_refs'] = [dict(subject_kind=r['subject_kind'], subject_id=r['subject_id']) for r in reviews]
        raw = json.dumps(package, ensure_ascii=False).encode()
        inputs = [dict(identity='reviewed.json', raw=raw)]
        decisions = json.dumps(dict(version=1, inventory_digest=uygulamalar._digest(cls.inventory),
            input_digests={'reviewed.json': hashlib.sha256(raw).hexdigest()}, decisions=[])).encode()
        return uygulamalar.merge_practice_packages(cls.inventory, inputs, decisions)

    def reject(self, mutate):
        payload = copy.deepcopy(self.merged)
        mutate(payload['practice_records'])
        out = self.root / self._testMethodName
        with self.assertRaisesRegex(ValueError, 'Birleşme paketi doğrulanmış özgün girdilerle uyuşmuyor'):
            uygulamalar.render_practice_preview(payload, out, self.inventory)
        self.assertFalse(out.exists())
        self.assertEqual(arsiv.sha(arsiv.DATA / 'current.json'), self.pointer)
        self.assertEqual(arsiv.sha(self.db), self.db_hash)
        self.assertFalse((arsiv.DATA / '.write.lock').exists())

    def test_lost_alias_rejected(self):
        self.reject(lambda records: records['practice_event_alias'].pop())

    def test_dangling_alias_rejected(self):
        def mutate(records):
            records['practice_event_alias'][0]['canonical_event_id'] = 'missing-technical-event'
        self.reject(mutate)

    def test_lost_evidence_rejected(self):
        self.reject(lambda records: records['practice_event_evidence'].pop())

    def test_lost_contribution_rejected(self):
        self.reject(lambda records: records['practice_contribution'].pop())

    def test_lost_review_origin_rejected(self):
        def remove(records):
            rows = records['practice_merge_origin']
            rows.remove(next(row for row in rows if row['origin_kind'] == 'review_origins'))
        self.reject(remove)

    def test_forged_review_origin_rejected(self):
        def forge(records):
            row = next(row for row in records['practice_merge_origin'] if row['origin_kind'] == 'review_origins')
            self.assertIn('Technical fixture subject', row['original_json'])
            row['original_json'] = row['original_json'].replace('Technical fixture subject', 'Forged fixture subject')
        self.reject(forge)

    def test_accepted_base_contribution_mutation_rejected(self):
        def mutate(records):
            records['practice_contribution'][0]['responsibility_limit'] += ' altered'
        self.reject(mutate)


class PublicInputNegative(unittest.TestCase):
    def test_private_source_path_escape_rejected_without_overwriting(self):
        package = json.loads((arsiv.DATA / 'practices/04-coverage-tracer.json').read_text())
        inventory_path = arsiv.DATA / 'practices/04-inventory.json'
        inventory = json.loads(inventory_path.read_text())
        package['entries'] = [dict(kind='document_version', values=dict(
            id='technical-escape', sha256='a' * 64, original_path='objects/' + 'a' * 64 + '/../../escape',
            readable_path='objects/' + 'a' * 64 + '/readable.html'))]
        pointer = arsiv.sha(arsiv.DATA / 'current.json')
        db = arsiv.DATA / 'releases' / arsiv.current() / 'records.sqlite3'
        db_hash = arsiv.sha(db)
        with tempfile.TemporaryDirectory(prefix='gsd-public-escape-') as tmp:
            root = Path(tmp)
            source = root / 'input.json'
            source.write_text(json.dumps(package), encoding='utf-8')
            decision = root / 'decisions.json'
            decision.write_text(json.dumps(dict(version=1, inventory_digest=uygulamalar._digest(inventory),
                input_digests={source.name: hashlib.sha256(source.read_bytes()).hexdigest()}, decisions=[])))
            out = root / 'existing.json'
            out.write_bytes(b'existing output')
            result = subprocess.run([sys.executable, str(arsiv.ROOT / 'src/arsiv.py'), 'practice-merge',
                '--inventory', str(inventory_path), '--inputs', str(source), '--event-decisions', str(decision),
                '--source-root', source.name + '=' + str(root), '--out', str(out)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Kaynak nesne yolu veya özeti geçersiz', result.stderr)
            self.assertEqual(out.read_bytes(), b'existing output')
        self.assertEqual(arsiv.sha(arsiv.DATA / 'current.json'), pointer)
        self.assertEqual(arsiv.sha(db), db_hash)
        self.assertFalse((arsiv.DATA / '.write.lock').exists())
