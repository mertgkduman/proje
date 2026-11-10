"""Gerçek sürüm ve yalıtılmış bozuk veriler için faz kabulü."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import arsiv


class PhaseOneAcceptance(unittest.TestCase):
    def test_current_snapshot_passes(self):
        audit = getattr(arsiv, 'validate_phase_one', None)
        self.assertTrue(callable(audit), 'Faz 1 kabul denetimi sağlanmalı')
        self.assertEqual(audit('current'), arsiv.current())

    def test_missing_pilot_heading_is_rejected(self):
        audit = getattr(arsiv, 'validate_phase_one_workspace', None)
        self.assertTrue(callable(audit), 'Çalışma alanı kabul denetimi sağlanmalı')
        with tempfile.TemporaryDirectory() as directory:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(directory) / 'data'
                shutil.copytree(old, arsiv.DATA)
                work = arsiv.open_workspace(directory)
                db = arsiv.connect(Path(work) / 'records.sqlite3')
                db.execute("DELETE FROM missing WHERE heading='Tüzük'")
                db.commit(); db.close()
                with self.assertRaises(ValueError):
                    audit(work)
            finally:
                arsiv.DATA = old


if __name__ == '__main__':
    unittest.main()
