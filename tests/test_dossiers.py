import sqlite3
import shutil
import tempfile
import unittest
from pathlib import Path

import arsiv


class DossierTracer(unittest.TestCase):
    def test_archived_tip_registry_foundation_has_party_contract(self):
        release = arsiv.DATA / 'releases' / arsiv.current() / 'records.sqlite3'
        db = sqlite3.connect(release)
        db.row_factory = sqlite3.Row
        try:
            identity = db.execute("SELECT * FROM identity_observation WHERE entity_id='tip'").fetchone()
            passage = db.execute('SELECT v.original_path FROM passage p JOIN document_version v ON v.id=p.version_id WHERE p.id=?', (identity['passage_id'],)).fetchone()
            source = (arsiv.DATA / passage['original_path']).read_text(encoding='utf-8')
            self.assertIn('07.11.2017', source)
            self.assertTrue(hasattr(arsiv, 'foundation_for_party'), 'Partiye özgü kuruluş sözleşmesi eksik')
            self.assertEqual(arsiv.foundation_for_party(db, 'tip'), identity['valid_from'])
        finally:
            db.close()

    def test_event_dates_respect_party_and_foundation(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_data = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(old_data, arsiv.DATA)
                work = arsiv.open_workspace(tmp)
                event = dict(id='tip-foundation', party_id='tip', passage_id='tip-registry-name',
                             event_at='2017-11-07', date_precision='day',
                             date_unknown_reason=None, scope_status='inside')
                arsiv.record(work, 'event_date', event)
                for changes in (dict(id='before', event_at='2017-11-06'),
                                dict(id='wrong-owner', passage_id='kurulus'),
                                dict(id='after', event_at='2026-11-11')):
                    with self.assertRaises(ValueError):
                        arsiv.record(work, 'event_date', dict(event, **changes))
            finally:
                arsiv.DATA = old_data
