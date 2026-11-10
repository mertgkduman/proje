import unittest
import tempfile
import shutil
from pathlib import Path
import arsiv


class MatchContract(unittest.TestCase):
    def test_match_without_statement_and_occurrence_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
                work = arsiv.open_workspace(tmp)
                with self.assertRaises(ValueError):
                    getattr(arsiv, 'record_match', lambda *_: None)(work, {})
            finally:
                arsiv.DATA = old
