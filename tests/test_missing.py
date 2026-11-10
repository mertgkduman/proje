import shutil
import tempfile
import unittest
from pathlib import Path
import arsiv


class MissingContract(unittest.TestCase):
    def test_access_failure_requires_identified_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
                work = arsiv.open_workspace(tmp)
                attempt = dict(id='a', party_id='yeni-parti', heading='B', topic_id='t', type='access', query='belirsiz', attempted_at='2026-11-10T15:00:00+00:00', result='failure', reason='Yanıt alınamadı')
                arsiv.record_attempt(work, attempt)
                with self.assertRaises(ValueError):
                    arsiv.record_missing(work, dict(id='m', party_id='yeni-parti', heading='B', topic_id='t', status='Erişilemedi', attempt_id='a', reason='Belgeye erişim sağlanamadı'))
            finally: arsiv.DATA = old
