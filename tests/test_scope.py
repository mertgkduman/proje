import unittest
import arsiv
import tempfile
import shutil
import sqlite3
import json
from pathlib import Path


class ScopeContract(unittest.TestCase):
    def test_scope_writer_exists(self):
        self.assertTrue(callable(getattr(arsiv, 'record_scope', None)))

    def test_approved_list_is_separate_from_observations(self):
        root = arsiv.DATA / 'releases' / arsiv.current()
        data = json.loads((root / 'records.json').read_text())
        self.assertEqual([x['approved_order'] for x in data['scope_party']], list(range(1, 10)))
        self.assertEqual(len(data['scope_exclusion']), 7)
        self.assertEqual(len(data['scope_observation']), 9)
        self.assertTrue(all(x['source_passage_id'] for x in data['scope_observation']))

    def test_identity_is_bound_to_registry_key_and_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(previous, arsiv.DATA)
                work = arsiv.open_workspace(tmp)
                arsiv.record(work, 'party', dict(id='same-name-old', legal_name='YENİ PARTİ', registry_key='old-same-name'))
                arsiv.record_identity(work, 'identity_observation', dict(entity_id='same-name-old', entity_kind='party', registry_key='old-same-name', valid_from=None, valid_to=None, passage_id='kurulus'))
                with self.assertRaises(ValueError):
                    arsiv.record_identity(work, 'identity_observation', dict(entity_id='yeni-parti', entity_kind='party', registry_key='old-same-name', valid_from=None, valid_to=None, passage_id='kurulus'))
                with self.assertRaises(sqlite3.IntegrityError):
                    arsiv.record_scope(work, 'scope_observation', dict(id='bad', party_id='yeni-parti', observed_at='2026-11-10', source_passage_id='missing', representation_kind='party', discrepancy_reason=None))
                arsiv.publish_release(work)
            finally:
                arsiv.DATA = previous
