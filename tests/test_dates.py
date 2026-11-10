import json
from pathlib import Path
import shutil
import tempfile
import unittest

import arsiv


class DateContract(unittest.TestCase):
    def test_cutoff_is_fixed_to_verified_tbmm_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(old, arsiv.DATA)
                work = arsiv.open_workspace(tmp)
                self.assertTrue(callable(getattr(arsiv, 'freeze_cutoff', None)))
                cutoff = arsiv.freeze_cutoff(work, 'tbmm-scope-v1')
                self.assertEqual(cutoff, '2026-11-10T14:38:46.154751+00:00')
                self.assertEqual(arsiv.freeze_cutoff(work, 'tbmm-scope-v1'), cutoff)
                with self.assertRaises(ValueError):
                    arsiv.freeze_cutoff(work, 'registry-365-v1')
                self.assertEqual(arsiv.validate_dates('2026-07-23', 'day', '2026-07-24', cutoff), 'outside')
                self.assertEqual(arsiv.validate_dates('2026-11-10', 'day', '2026-07-24', cutoff), 'uncertain')
                self.assertEqual(arsiv.validate_dates('2026-08-01', 'day', '2026-07-24', cutoff), 'inside')
                self.assertEqual(arsiv.validate_dates('2026-11-11', 'day', '2026-07-24', cutoff), 'outside')
                arsiv.publish_release(work)
            finally:
                arsiv.DATA = old
