import json
import shutil
import tempfile
import unittest
from pathlib import Path

import arsiv
from rapor import render_report


class FinanceContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = arsiv.DATA
        arsiv.DATA = Path(self.tmp.name) / 'data'
        shutil.copytree(self.old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
        self.work = arsiv.open_workspace(self.tmp.name)
        self.db = arsiv.connect(self.work / 'records.sqlite3')
        self.db.execute("INSERT INTO document VALUES ('finance-fixture','yeni-parti','Test raporu','news')")
        obj = arsiv.DATA / 'objects' / 'finance-fixture'
        obj.mkdir(); original = obj / 'original.html.bin'; original.write_text('Yeni Parti Kocaeli il örgütü: 2026-08-01 ile 2026-10-23 döneminde 0 TL')
        (obj / 'readable.html').write_bytes(arsiv.readable_bytes(original.read_bytes(), 'html'))
        self.db.execute("INSERT INTO document_version (id,document_id,original_url,final_url,document_date,accessed_at,verified_at,mime,sha256,original_path,readable_path,date_precision) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", ('finance-fixture','finance-fixture','https://example.org/finance','https://example.org/finance','2026-10-24','2026-11-10T15:00:00+00:00','2026-11-10T15:00:00+00:00','text/html',arsiv.sha(original),str(original.relative_to(arsiv.DATA)),str((obj/'readable.html').relative_to(arsiv.DATA)),'day'))
        self.db.execute("INSERT INTO passage (id,version_id,exact) VALUES (?,?,?)", ('finance-fixture','finance-fixture',original.read_text()))
        self.db.execute("INSERT INTO accounting_period VALUES ('fixture-period','yeni-parti','finance-fixture','2026-08-01','2026-10-23','day',NULL)")
        self.db.commit()
        self.row = dict(id='f1',party_id='yeni-parti',version_id='finance-fixture',category='gelir',amount='0',currency='TRY',period_start='2026-08-01',period_end='2026-10-23',organization_scope='Kocaeli il örgütü',published_at='2026-10-24',passage_id='finance-fixture',missing_id=None)

    def tearDown(self):
        self.db.close()
        arsiv.DATA = self.old
        self.tmp.cleanup()

    def test_identity_period_and_required_metadata(self):
        arsiv.check_financial(self.db, self.row)
        for changes in ({'party_id':'tip'}, {'period_start':'2009-01-01'}, {'period_end':'2026-11-11'}, {'currency':''}, {'organization_scope':''}, {'amount':0.0}, {'version_id':'missing'}, {'passage_id':'missing'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                arsiv.check_financial(self.db, dict(self.row, **changes))

    def test_null_and_documented_zero_are_distinct(self):
        self.db.execute("INSERT INTO attempt (id,party_id,heading,topic_id,type,query,attempted_at,result,reason) VALUES ('finance-missing-attempt','yeni-parti','Finansman ve harcamalar','test','verification','test','2026-11-10T15:00:00+00:00','inconclusive','Test')")
        self.db.execute("INSERT INTO missing VALUES ('finance-missing','yeni-parti','Finansman ve harcamalar','test','Doğrulanamadı','finance-missing-attempt','Test')")
        self.db.commit()
        self.db.close()
        arsiv.record_financial(self.work, self.row)
        arsiv.record_financial(self.work, dict(self.row,id='f-null',amount=None,passage_id=None,missing_id='finance-missing'))
        self.db = arsiv.connect(self.work / 'records.sqlite3')
        payload = arsiv.export_db(self.work / 'records.sqlite3', 'fixture')
        self.assertEqual(next(r['amount'] for r in json.loads(json.dumps(payload))['financial'] if r['id']=='f1'), '0')
        self.assertIsNone(next(r['amount'] for r in payload['financial'] if r['id']=='f-null'))
        self.assertIn('0 TRY', render_report(payload))
        self.assertIn('Bilinmiyor TRY', render_report(payload))
        with self.assertRaises(ValueError): arsiv.check_financial(self.db, dict(self.row, id='f2', amount=None))

    def test_current_pilot_has_researched_finance(self):
        release = arsiv.current()
        arsiv.audit_finance(arsiv.DATA / 'releases' / release / 'records.sqlite3')

