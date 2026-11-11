import sqlite3
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
