import json
from pathlib import Path
import shutil
import tempfile
import unittest

import arsiv


class PublicationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_data = arsiv.DATA
        arsiv.DATA = Path(self.tmp.name) / 'data'
        shutil.copytree(self.old_data, arsiv.DATA)

    def tearDown(self):
        arsiv.DATA = self.old_data
        self.tmp.cleanup()

    def test_detects_corrupt_readable_archive(self):
        release = arsiv.current()
        records = json.loads((arsiv.DATA / 'releases' / release / 'records.json').read_text())
        (arsiv.DATA / records['document_version'][0]['readable_path']).write_text('hasarlı')
        with self.assertRaises(ValueError):
            arsiv.audit_release(release)
