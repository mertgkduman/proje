import unittest
import tempfile
import shutil
from pathlib import Path
import arsiv


class TopicContract(unittest.TestCase):
    def test_real_dictionary_contains_a_sourced_verified_topic(self):
        release = arsiv.current()
        data = arsiv.export_db(arsiv.DATA / 'releases' / release / 'records.sqlite3', release)
        verified = [t for t in data.get('topic', []) if t['status'] == 'verified']
        self.assertTrue(verified, 'En az bir gerçek belge dayanağı bulunan konu gerekli')
        self.assertTrue(all(any(b['topic_id'] == t['id'] and b['taxonomy_version'] == t['taxonomy_version'] for b in data['topic_basis']) for t in verified))

    def test_verified_topic_without_basis_is_rejected_on_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
                work = arsiv.open_workspace(tmp)
                arsiv.record_topic(work, dict(id='fake', label='Sahte', taxonomy_version=2, valid_from='2026-11-10', status='verified', change_reason='Test'))
                with self.assertRaises(ValueError):
                    arsiv.export_db(work / 'records.sqlite3', 'test')
            finally:
                arsiv.DATA = old

    def test_unrelated_party_cannot_authorize_charter(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
                work = arsiv.open_workspace(tmp)
                db = arsiv.connect(work / 'records.sqlite3')
                db.execute("UPDATE document_authority SET registry_party_id='yeni-parti' WHERE version_id='tip-charter-v1'")
                db.commit()
                db.close()
                with self.assertRaises(ValueError):
                    arsiv.export_db(work / 'records.sqlite3', 'test')
            finally:
                arsiv.DATA = old
