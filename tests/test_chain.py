import unittest
from pathlib import Path
import tempfile
import shutil
import arsiv


class ChainContract(unittest.TestCase):
    def test_pending_lead_blocks_closure(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
                work = arsiv.open_workspace(tmp)
                lead = dict(id='a', party_id='yeni-parti', heading='A', topic_id='t', url='https://example.org/path?x=1&utm_source=a#ref', relevance_reason='İlgili')
                self.assertEqual(arsiv.enqueue_lead(work, lead), 'a')
                self.assertEqual(arsiv.enqueue_lead(work, dict(lead, id='duplicate', url='https://example.org/path?x=1#other')), 'a')
                self.assertNotEqual(arsiv.normalize_url('https://example.org/path?x=1'), arsiv.normalize_url('https://example.org/path?x=2'))
                db = arsiv.connect(work / 'records.sqlite3')
                version = dict(db.execute("SELECT * FROM document_version WHERE id='registry-365-v1'").fetchone())
                db.close()
                same = dict(version, id='alias', original_url='https://example.org/alias', final_url='https://example.org/final')
                self.assertEqual(arsiv.record(work, 'document_version', same), 'registry-365-v1')
                changed = dict(same, id='new-version', sha256='0' * 64)
                arsiv.record(work, 'document_version', changed)
                db = arsiv.connect(work / 'records.sqlite3')
                self.assertEqual(db.execute("SELECT version_id FROM url_alias WHERE original_url='https://example.org/alias' ORDER BY rowid").fetchone()[0], 'registry-365-v1')
                self.assertIsNotNone(db.execute("SELECT 1 FROM document_version WHERE id='new-version'").fetchone())
                db.close()
                arsiv.record(work, 'edge', dict(from_version_id='registry-365-v1', to_lead_id='a', relation='reference', relevance_reason='İlgili bağlantı'))
                with self.assertRaises(Exception): arsiv.record(work, 'edge', dict(from_version_id='registry-365-v1', to_lead_id='a', relation='reference', relevance_reason='Yinelenen bağlantı'))
                close = dict(id='c', topic_id='t', closed_at='2026-11-10T15:00:00+00:00', reason='Tüm uçlar denendi', residual_leads='Erişim engeli')
                with self.assertRaises(ValueError): arsiv.close_topic(work, close)
                arsiv.record_attempt(work, dict(id='try', lead_id='a', party_id='yeni-parti', heading='A', topic_id='t', type='access', query=lead['url'], attempted_at='2026-11-10T15:00:00+00:00', result='failure', reason='Bağlantı kesildi'))
                arsiv.close_topic(work, close)
                original = dict(version, id='registry-new', sha256='f' * 64)
                registry_lead = dict(lead, id='registry-lead', topic_id='registry-topic', url=version['original_url'])
                arsiv.enqueue_lead(work, registry_lead)
                arsiv.record_attempt(work, dict(id='registry-try', lead_id='registry-lead', party_id='yeni-parti', heading='A', topic_id='registry-topic', type='access', query=version['original_url'], attempted_at='2026-11-10T15:00:00+00:00', result='examined', reason='Kayıt incelendi', source_version_id=version['id']))
                arsiv.close_topic(work, dict(close, id='registry-close', topic_id='registry-topic'))
                arsiv.record(work, 'document_version', original)
                db = arsiv.connect(work / 'records.sqlite3')
                self.assertEqual(db.execute("SELECT state FROM topic_search WHERE topic_id='registry-topic'").fetchone()[0], 'in_progress')
                self.assertEqual(db.execute("SELECT status FROM lead WHERE id='registry-lead'").fetchone()[0], 'pending')
                db.close()
                arsiv.enqueue_lead(work, dict(lead, id='b', url='https://example.org/next'))
                db = arsiv.connect(work / 'records.sqlite3')
                self.assertEqual(db.execute('SELECT state FROM topic_search WHERE topic_id=?', ('t',)).fetchone()[0], 'in_progress')
                self.assertEqual(db.execute("SELECT lead_id FROM reopen WHERE closure_id='c'").fetchone()[0], 'b')
                db.close()
                with self.assertRaises(ValueError): arsiv.close_topic(work, dict(close, id='c2'))
            finally: arsiv.DATA = old


if __name__ == '__main__':
    unittest.main()
