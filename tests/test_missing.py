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

    def test_statuses_bind_matching_attempt_and_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
                work = arsiv.open_workspace(tmp)
                arsiv.record(work, 'research_state', dict(party_id='yeni-parti', heading='D', state='not_researched'))
                db = arsiv.connect(work / 'records.sqlite3')
                self.assertEqual(db.execute("SELECT state FROM research_state WHERE heading='D'").fetchone()[0], 'not_researched')
                self.assertEqual(db.execute("SELECT COUNT(*) FROM missing WHERE heading='D'").fetchone()[0], 0)
                db.close()
                arsiv.enqueue_lead(work, dict(id='l', party_id='yeni-parti', heading='B', topic_id='t', url='https://example.org/', relevance_reason='Denenecek kaynak'))
                base = dict(party_id='yeni-parti', heading='B', topic_id='t', query='Belirli sorgu', attempted_at='2026-11-10T15:00:00+00:00', reason='Deneme kaydı')
                for aid, typ, result, status in [('search','search','no_result','Bulunamadı'), ('access','access','failure','Erişilemedi'), ('verify','verification','inconclusive','Doğrulanamadı')]:
                    attempt = dict(base, id=aid, type=typ, result=result)
                    if aid == 'access': attempt['lead_id'] = 'l'
                    arsiv.record_attempt(work, attempt)
                    missing = dict(id='m-'+aid, party_id='yeni-parti', heading='B', topic_id='t', status=status, attempt_id=aid, reason='Deneme sonucu')
                    arsiv.record_missing(work, missing)
                    with self.assertRaises(ValueError): arsiv.record_missing(work, dict(missing, id='bad-'+aid, topic_id='different'))
                    with self.assertRaises(ValueError): arsiv.record_missing(work, dict(missing, id='bad-status-'+aid, status='Henüz incelenmedi'))
                with self.assertRaises(Exception):
                    arsiv.record_missing(work, dict(id='no-attempt', party_id='yeni-parti', heading='B', topic_id='t', status='Bulunamadı', attempt_id='absent', reason='yok'))
            finally: arsiv.DATA = old
