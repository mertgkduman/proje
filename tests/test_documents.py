import unittest
import tempfile
import shutil
from pathlib import Path
import arsiv


class DocumentContract(unittest.TestCase):
    def test_wrong_party_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
                work = arsiv.open_workspace(tmp)
                db = arsiv.connect(work / 'records.sqlite3')
                db.execute("UPDATE finding SET party_id='tip' WHERE id='kurulus-quote'")
                db.commit()
                db.close()
                with self.assertRaises(ValueError):
                    arsiv.export_db(work / 'records.sqlite3', 'test')
            finally:
                arsiv.DATA = old
